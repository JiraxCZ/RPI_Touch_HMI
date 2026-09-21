import unittest

from relay_controller import RelayController


class FakeGPIO:
    BCM = 1
    OUT = 0
    HIGH = 1
    LOW = 0

    def __init__(self):
        self.outputs = {}
        self.cleaned_up = False

    def setmode(self, mode):
        self.mode = mode

    def setwarnings(self, value):
        self.warnings_enabled = value

    def setup(self, pin, mode):
        self.outputs.setdefault(pin, self.LOW)

    def output(self, pin, value):
        self.outputs[pin] = value

    def cleanup(self):
        self.cleaned_up = True


class RelayControllerTest(unittest.TestCase):
    def test_setup_initializes_active_low_relays_off(self):
        gpio = FakeGPIO()
        controller = RelayController([17, 27], active_low=True, gpio=gpio)

        controller.setup()

        self.assertFalse(controller.is_on(17))
        self.assertFalse(controller.is_on(27))
        self.assertEqual(gpio.outputs[17], gpio.HIGH)
        self.assertEqual(gpio.outputs[27], gpio.HIGH)

    def test_toggle_uses_explicit_state(self):
        gpio = FakeGPIO()
        controller = RelayController([17], active_low=True, gpio=gpio)
        controller.setup()

        self.assertTrue(controller.toggle(17))
        self.assertTrue(controller.is_on(17))
        self.assertEqual(gpio.outputs[17], gpio.LOW)

        self.assertFalse(controller.toggle(17))
        self.assertFalse(controller.is_on(17))
        self.assertEqual(gpio.outputs[17], gpio.HIGH)

    def test_all_off_turns_every_relay_off(self):
        gpio = FakeGPIO()
        controller = RelayController([17, 27], active_low=False, gpio=gpio)
        controller.setup()
        controller.set_state(17, True)
        controller.set_state(27, True)

        controller.all_off()

        self.assertFalse(controller.is_on(17))
        self.assertFalse(controller.is_on(27))
        self.assertEqual(gpio.outputs[17], gpio.LOW)
        self.assertEqual(gpio.outputs[27], gpio.LOW)


if __name__ == '__main__':
    unittest.main()
