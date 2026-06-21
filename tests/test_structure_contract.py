import unittest


class StructureContractTests(unittest.TestCase):
    def test_explanatory_modules_are_importable(self):
        import lomiteria.distributions as distributions
        import lomiteria.object_definitions as object_definitions
        import lomiteria.state_vector as state_vector

        self.assertTrue(distributions.RANDOM_SOURCE_NOTES)
        self.assertTrue(object_definitions.OBJECT_DEFINITIONS)
        self.assertTrue(state_vector.EVENT_COLUMNS)


if __name__ == "__main__":
    unittest.main()
