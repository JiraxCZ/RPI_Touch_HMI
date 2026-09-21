from kivy.app import App
from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout

import RPi.GPIO as GPIO

from relay_controller import RelayController

# Display setup
Window.size = (720, 720)
Window.borderless = True
Window.fullscreen = 'auto'
Window.clearcolor = (0.06, 0.08, 0.12, 1.0)

# GPIO pins for 4 relays (BCM numbering)
RELAY_PINS = [17, 27, 22, 23]

# Most relay modules are active-low
ACTIVE_LOW = True


class RelayButton(Button):
    def __init__(self, relay_number, pin, controller, **kwargs):
        super().__init__(**kwargs)
        self.relay_number = relay_number
        self.pin = pin
        self.controller = controller
        self.is_on = False

        # Do not use Kivy's default textured button background.
        self.background_normal = ''
        self.background_down = ''
        self.font_size = 26
        self.bold = True
        self.color = (1, 1, 1, 1)
        self.bind(on_press=self._handle_press)
        self.refresh()

    def _handle_press(self, _instance):
        self.is_on = self.controller.toggle(self.pin)
        self.refresh()

    def refresh(self):
        state_text = 'ON' if self.is_on else 'OFF'
        self.text = f'RELÉ {self.relay_number}\n{state_text}'
        self.background_color = (
            (0.22, 0.82, 0.38, 1.0)
            if self.is_on
            else (0.76, 0.20, 0.20, 1.0)
        )


class RelayPanel(GridLayout):
    def __init__(self, controller, **kwargs):
        super().__init__(**kwargs)
        self.cols = 2
        self.rows = 2
        self.padding = 20
        self.spacing = 20

        self.buttons = []
        for relay_number, pin in enumerate(RELAY_PINS, start=1):
            button = RelayButton(relay_number, pin, controller)
            self.buttons.append(button)
            self.add_widget(button)

        self.sync_buttons()

    def sync_buttons(self):
        for button in self.buttons:
            button.is_on = button.controller.is_on(button.pin)
            button.refresh()


class RelayApp(App):
    def build(self):
        self.controller = RelayController(
            RELAY_PINS,
            active_low=ACTIVE_LOW,
            gpio=GPIO,
        )
        self.controller.setup()
        return RelayPanel(self.controller)

    def on_stop(self):
        try:
            self.controller.all_off()
        finally:
            self.controller.cleanup_gpio()


if __name__ == '__main__':
    RelayApp().run()
