import importlib
import unittest


class MainDiodeImportTests(unittest.TestCase):
    def test_main_diode_module_imports(self):
        module = importlib.import_module("main_diode")
        self.assertTrue(hasattr(module, "SideApp"))


if __name__ == "__main__":
    unittest.main()
