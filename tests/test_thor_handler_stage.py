import unittest
from unittest.mock import patch

import thor_handler_stage


class ThorHandlerStageSerialTests(unittest.TestCase):
    def test_resolve_serial_prefers_configured_serial_when_available(self):
        controller = thor_handler_stage.StageController("45517804")

        with patch.object(
            controller,
            "_get_discovered_serial_numbers",
            return_value=["45874437", "45517804"],
        ):
            self.assertEqual(controller._resolve_serial_number(), "45517804")

    def test_resolve_serial_falls_back_to_first_discovered_device(self):
        controller = thor_handler_stage.StageController("")

        with patch.object(
            controller,
            "_get_discovered_serial_numbers",
            return_value=["45874437"],
        ):
            self.assertEqual(controller._resolve_serial_number(), "45874437")


if __name__ == "__main__":
    unittest.main()
