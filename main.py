import atexit

from kivy.app import App
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.uix.gridlayout import GridLayout
from kivy.uix.togglebutton import ToggleButton

from relay_controller import DEFAULT_ACTIVE_LOW, DEFAULT_RELAY_PINS, RelayController

try:
    import RPi.GPIO as GPIO
except ModuleNotFoundError:
    class MockGPIO:
        BCM = "BCM"
        OUT = "OUT"
        HIGH = 1
        LOW = 0

        def setmode(self, mode):
            self.mode = mode

        def setwarnings(self, enabled):
            self.warnings_enabled = enabled

        def setup(self, pin, mode):
            pass

        def output(self, pin, value):
            pass

        def cleanup(self):
            pass

    GPIO = MockGPIO()

# Display setup
Window.size = (720, 720)
Window.borderless = True
Window.fullscreen = "auto"
Window.clearcolor = (0.08, 0.09, 0.12, 1)

# GPIO pins for 4 relays (BCM numbering)
RELAY_PINS = DEFAULT_RELAY_PINS

# Most relay modules are active-low
ACTIVE_LOW = DEFAULT_ACTIVE_LOW


class RelayButton(ToggleButton):
    def __init__(self, relay_index, pin, **kwargs):
        kwargs.setdefault("background_normal", "")
        kwargs.setdefault("background_down", "")
        kwargs.setdefault("background_disabled_normal", "")
        kwargs.setdefault("background_disabled_down", "")
        super().__init__(**kwargs)

        self.relay_index = relay_index
        self.pin = pin
        self.relay_is_on = False
        self.font_size = 42
        self.bold = True
        self.color = (1, 1, 1, 1)
        self.halign = "center"
        self.valign = "middle"
        self.bind(size=self._update_text_size)
        self.update_ui(False)

    def _update_text_size(self, *_args):
        self.text_size = self.size

    def update_ui(self, is_on):
        self.relay_is_on = bool(is_on)
        self.text = f"RELE {self.relay_index + 1}\n{'ON' if self.relay_is_on else 'OFF'}"
        self.background_color = (0.14, 0.62, 0.28, 1) if self.relay_is_on else (0.78, 0.18, 0.18, 1)
        self.state = "down" if self.relay_is_on else "normal"


class RelayGrid(GridLayout):
    def __init__(self, controller, **kwargs):
        super().__init__(**kwargs)
        self.cols = 2
        self.rows = 2
        self.padding = 24
        self.spacing = 24

        with self.canvas.before:
            Color(0.08, 0.09, 0.12, 1)
            self.background_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_background, size=self._update_background)

        self.controller = controller

        self.buttons = []
        for relay_index, pin in enumerate(RELAY_PINS):
            button = RelayButton(relay_index, pin)
            button.bind(on_release=self.toggle_relay)
            self.buttons.append(button)
            self.add_widget(button)

        self.sync_buttons()

    def _update_background(self, *_args):
        self.background_rect.pos = self.pos
        self.background_rect.size = self.size

    def sync_buttons(self):
        for button in self.buttons:
            button.update_ui(self.controller.get_state(button.pin))

    def toggle_relay(self, button):
        button.update_ui(self.controller.toggle(button.pin))

    def all_off(self):
        self.controller.all_off()
        self.sync_buttons()

    def cleanup(self):
        self.all_off()
        self.controller.cleanup_gpio()


class RelayApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.grid = None
        self.controller = RelayController(RELAY_PINS, active_low=ACTIVE_LOW, gpio=GPIO)
        self._cleaned_up = False
        self._cleanup_in_progress = False
        self._relays_powered_down = False
        self._gpio_cleaned = False
        atexit.register(self._cleanup_gpio)

    def build(self):
        self.controller.setup()
        self.grid = RelayGrid(controller=self.controller)
        return self.grid

    def _cleanup_gpio(self):
        if self._cleaned_up or self._cleanup_in_progress:
            return
        self._cleanup_in_progress = True
        try:
            if not self._relays_powered_down:
                if self.grid is not None:
                    self.grid.all_off()
                else:
                    self.controller.all_off()
                self._relays_powered_down = True

            if self._relays_powered_down and not self._gpio_cleaned:
                self.controller.cleanup_gpio()
                self._gpio_cleaned = True

            self._cleaned_up = True
        finally:
            self._cleanup_in_progress = False

    def on_stop(self):
        self._cleanup_gpio()


if __name__ == "__main__":
    RelayApp().run()
