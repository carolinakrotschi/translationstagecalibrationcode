import importlib
import unittest


class MainImportTests(unittest.TestCase):
    def test_main_module_imports(self):
        module = importlib.import_module("main")
        self.assertTrue(hasattr(module, "InterferometerApp"))


if __name__ == "__main__":
    unittest.main()
