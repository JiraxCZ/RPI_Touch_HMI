class RelayController:
    """Hardware-independent relay state and GPIO control logic."""

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
        if pin not in self.relay_pins:
            raise ValueError(f'Unknown relay pin: {pin}')

        is_on = bool(is_on)
        self._apply_state(pin, is_on)
        self.states[pin] = is_on
        return is_on

    def toggle(self, pin):
        return self.set_state(pin, not self.is_on(pin))

    def all_off(self):
        first_error = None
        for pin in self.relay_pins:
            try:
                self.set_state(pin, False)
            except Exception as error:
                if first_error is None:
                    first_error = error

        if first_error is not None:
            raise first_error

    def cleanup_gpio(self):
        self.gpio.cleanup()
