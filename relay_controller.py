DEFAULT_RELAY_PINS = [17, 27, 22, 23]
DEFAULT_ACTIVE_LOW = True


class RelayController:
    def __init__(self, relay_pins, active_low=True, gpio=None):
        if gpio is None:
            raise ValueError("A GPIO backend must be provided")

        self.gpio = gpio
        self.relay_pins = list(relay_pins)
        self.active_low = active_low
        self.states = {pin: False for pin in self.relay_pins}

    def setup(self):
        self.gpio.setmode(self.gpio.BCM)
        self.gpio.setwarnings(False)

        for pin in self.relay_pins:
            self.gpio.setup(pin, self.gpio.OUT)
            self.set_state(pin, False)

    def get_state(self, pin):
        return self.states[pin]

    def set_state(self, pin, is_on):
        state = bool(is_on)
        self.states[pin] = state
        self.gpio.output(pin, self._gpio_value_for_state(state))
        return state

    def toggle(self, pin):
        return self.set_state(pin, not self.states[pin])

    def all_off(self):
        for pin in self.relay_pins:
            self.set_state(pin, False)

    def cleanup_gpio(self):
        self.gpio.cleanup()

    def _gpio_value_for_state(self, is_on):
        if self.active_low:
            return self.gpio.LOW if is_on else self.gpio.HIGH
        return self.gpio.HIGH if is_on else self.gpio.LOW
