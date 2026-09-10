from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.togglebutton import ToggleButton
from kivy.core.window import Window
from kivy.clock import Clock

import RPi.GPIO as GPIO

# Display setup
Window.size = (720, 720)
Window.borderless = True
Window.fullscreen = 'auto'

# GPIO pins for 4 relays (BCM numbering)
RELAY_PINS = [17, 27, 22, 23]

# Most relay modules are active-low
ACTIVE_LOW = True


class RelayButton(ToggleButton):
    def __init__(self, relay_index, pin, **kwargs):
        super().__init__(**kwargs)
        self.relay_index = relay_index
        self.pin = pin
        self.font_size = 42
        self.bold = True
        self.update_ui(False)

    def update_ui(self, is_on: bool):
        if is_on:
            self.text = f"RELE {self.relay_index + 1}\nON"
            self.background_color = (0.1, 0.7, 0.2, 1)
            self.state = "down"
        else:
            self.text = f"RELE {self.relay_index + 1}\nOFF"
            self.background_color = (0.8, 0.2, 0.2, 1)
            self.state = "normal"


class RelayGrid(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cols = 2
        self.rows = 2
        self.padding = 20
        self.spacing = 20

        self.buttons = []

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        for i, pin in enumerate(RELAY_PINS):
            GPIO.setup(pin, GPIO.OUT)

            # Default OFF
            self.set_relay(pin, False)

            btn = RelayButton(i, pin)
            btn.bind(on_press=self.toggle_relay)
            self.buttons.append(btn)
            self.add_widget(btn)

    def set_relay(self, pin: int, is_on: bool):
        if ACTIVE_LOW:
            GPIO.output(pin, GPIO.LOW if is_on else GPIO.HIGH)
        else:
            GPIO.output(pin, GPIO.HIGH if is_on else GPIO.LOW)

    def toggle_relay(self, button):
        # on_press fires during state transition
        is_on = button.state == "normal"
        self.set_relay(button.pin, is_on)
        Clock.schedule_once(lambda dt: button.update_ui(is_on), 0)

    def all_off(self):
        for btn in self.buttons:
            self.set_relay(btn.pin, False)
            btn.update_ui(False)


class RelayApp(App):
    def build(self):
        self.grid = RelayGrid()
        return self.grid

    def on_stop(self):
        # Ensure all relays are off when app exits
        self.grid.all_off()
        GPIO.cleanup()


if __name__ == "__main__":
    RelayApp().run()
