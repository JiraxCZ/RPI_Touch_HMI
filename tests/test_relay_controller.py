class RelayController:
    def __init__(self, relay_pins, active_low=True, gpio=None):
        self.relay_pins = list(relay_pins)
        self.active_low = active_low
        self.gpio = gpio
        self.states = {}

        if self.gpio is None:
            import RPi.GPIO as gpio_module
            self.gpio = gpio_module

    def setup(self):
        self.gpio.setmode(self.gpio.BCM)
        self.gpio.setwarnings(False)

        for pin in self.relay_pins:
            self.gpio.setup(pin, self.gpio.OUT)
            self.states[pin] = False
            self._apply_state(pin, False)

    def _apply_state(self, pin, is_on):
        if self.active_low:
            value = self.gpio.LOW if is_on else self.gpio.HIGH
        else:
            value = self.gpio.HIGH if is_on else self.gpio.LOW
        self.gpio.output(pin, value)

    def is_on(self, pin):
        return bool(self.states.get(pin, False))

    def set_state(self, pin, is_on):
        self.states[pin] = bool(is_on)
        self._apply_state(pin, bool(is_on))
        return self.states[pin]

    def toggle(self, pin):
        new_state = not self.is_on(pin)
        return self.set_state(pin, new_state)

    def all_off(self):
        errors = []
        for pin in self.relay_pins:
            try:
                self.set_state(pin, False)
            except Exception as exc:
                errors.append(exc)

        if errors:
            raise errors[0]

    def cleanup_gpio(self):
        self.gpio.cleanup()
