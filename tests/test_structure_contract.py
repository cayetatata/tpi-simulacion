import unittest


class StructureContractTests(unittest.TestCase):
    def test_explanatory_modules_are_importable(self):
        import lomiteria.eventos.llegada_cliente as evento_llegada_cliente
        import lomiteria.eventos.fin_atencion_caja as evento_fin_atencion_caja
        import lomiteria.eventos.fin_preparacion_mostrador as evento_fin_preparacion_mostrador
        import lomiteria.eventos.fin_permanencia_rojo as evento_fin_permanencia_rojo
        import lomiteria.eventos.fin_permanencia_azul as evento_fin_permanencia_azul
        import lomiteria.eventos.control_cola_mostrador_15min as evento_control_cola_mostrador_15min
        import lomiteria.eventos.control_salones_30min as evento_control_salones_30min
        import lomiteria.aleatorios.distribuciones as formulas_aleatorias
        import lomiteria.simulacion.vector_estado as vector_estado

        self.assertTrue(evento_llegada_cliente.generar_proxima_llegada)
        self.assertTrue(evento_fin_atencion_caja.ejecutar_fin_atencion_caja)
        self.assertTrue(evento_fin_preparacion_mostrador.ejecutar_fin_preparacion_mostrador)
        self.assertTrue(evento_fin_permanencia_rojo.ejecutar_fin_permanencia_rojo)
        self.assertTrue(evento_fin_permanencia_azul.ejecutar_fin_permanencia_azul)
        self.assertTrue(evento_control_cola_mostrador_15min.ejecutar_control_cola_mostrador_15min)
        self.assertTrue(evento_control_salones_30min.ejecutar_control_salones_30min)
        self.assertTrue(formulas_aleatorias.uniforme)
        self.assertTrue(vector_estado.COLUMNAS_EVENTOS)


if __name__ == "__main__":
    unittest.main()
