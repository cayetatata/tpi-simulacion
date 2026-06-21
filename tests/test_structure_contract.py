import unittest


class StructureContractTests(unittest.TestCase):
    def test_explanatory_modules_are_importable(self):
        import lomiteria.distributions as distributions
        import lomiteria.object_definitions as object_definitions
        import lomiteria.state_vector as state_vector

        self.assertTrue(distributions.NOTAS_ORIGEN_RND)
        self.assertTrue(object_definitions.DEFINICIONES_OBJETOS)
        self.assertTrue(state_vector.COLUMNAS_EVENTOS)


if __name__ == "__main__":
    unittest.main()
