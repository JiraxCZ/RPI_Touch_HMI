import unittest

from relay_controller import RelayController


class FakeGPIO:
    BCM = "BCM"
    OUT = "OUT"
    HIGH = 1
    LOW = 0

    def __init__(self):
        self.mode = None
        self.warnings_enabled = None
        self.setup_calls = []
        self.output_calls = []
        self.outputs = {}
        self.cleaned_up = False

    def setmode(self, mode):
        self.mode = mode

    def setwarnings(self, enabled):
        self.warnings_enabled = enabled

    def setup(self, pin, mode):
        self.setup_calls.append((pin, mode))

    def output(self, pin, value):
        self.output_calls.append((pin, value))
        self.outputs[pin] = value

    def cleanup(self):
        self.cleaned_up = True


class FailingGPIO(FakeGPIO):
    def __init__(self, failing_pin):
        super().__init__()
        self.failing_pin = failing_pin

    def output(self, pin, value):
        if pin == self.failing_pin:
            raise RuntimeError(f"GPIO failure on pin {pin}")
        super().output(pin, value)


class RelayControllerTest(unittest.TestCase):
    def test_setup_initializes_all_relays_off_for_active_low(self):
        gpio = FakeGPIO()
        controller = RelayController([17, 27], active_low=True, gpio=gpio)

        controller.setup()

        self.assertEqual(gpio.mode, gpio.BCM)
        self.assertFalse(gpio.warnings_enabled)
        self.assertEqual(gpio.setup_calls, [(17, gpio.OUT), (27, gpio.OUT)])
        self.assertEqual(gpio.outputs[17], gpio.HIGH)
        self.assertEqual(gpio.outputs[27], gpio.HIGH)
        self.assertFalse(controller.get_state(17))
        self.assertFalse(controller.get_state(27))

    def test_toggle_flips_explicit_state_on_each_press(self):
        gpio = FakeGPIO()
        controller = RelayController([17], active_low=True, gpio=gpio)
        controller.setup()

        self.assertTrue(controller.toggle(17))
        self.assertTrue(controller.get_state(17))
        self.assertEqual(gpio.outputs[17], gpio.LOW)

        self.assertFalse(controller.toggle(17))
        self.assertFalse(controller.get_state(17))
        self.assertEqual(gpio.outputs[17], gpio.HIGH)

    def test_all_off_and_cleanup_work_without_hardware(self):
        gpio = FakeGPIO()
        controller = RelayController([17, 27], active_low=False, gpio=gpio)
        controller.setup()
        controller.toggle(17)
        controller.toggle(27)

        controller.all_off()
        controller.cleanup_gpio()

        self.assertFalse(controller.get_state(17))
        self.assertFalse(controller.get_state(27))
        self.assertEqual(gpio.outputs[17], gpio.LOW)
        self.assertEqual(gpio.outputs[27], gpio.LOW)
        self.assertTrue(gpio.cleaned_up)

    def test_all_off_attempts_remaining_relays_after_failure(self):
        gpio = FailingGPIO(failing_pin=17)
        controller = RelayController([17, 27], active_low=True, gpio=gpio)
        controller.states[17] = True
        controller.states[27] = True

        with self.assertRaisesRegex(RuntimeError, "pin 17"):
            controller.all_off()

        self.assertEqual(gpio.outputs[27], gpio.HIGH)


if __name__ == "__main__":
    unittest.main()
