import asyncio
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "ejemplos"))
spec = importlib.util.spec_from_file_location("agente_minimo", ROOT / "ejemplos/04_agente_minimo.py")
assert spec and spec.loader
agent = importlib.util.module_from_spec(spec)
spec.loader.exec_module(agent)


class AgenteMinimoTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.sandbox = Path(self.temp.name)
        self.settings = patch.multiple(
            agent,
            SANDBOX=self.sandbox,
            SKILLS={"informe-incidencias": ("informe", "instrucciones")},
            TAREA_PREDETERMINADA=True,
            AUTO=True,
        )
        self.settings.start()
        self.addCleanup(self.settings.stop)

    def run_with(self, workflow):
        with patch.object(agent, "run_agent", workflow), patch.object(agent, "AsyncOpenAI"):
            asyncio.run(agent.main())

    def test_informe_creado_con_skill(self):
        async def workflow(client, model, task, tools, dispatch, system, **kwargs):
            await dispatch("cargar_skill", {"nombre": "informe-incidencias"})
            await dispatch("escribir_fichero", {"ruta": "informe.md", "contenido": "informe"})
            return "Terminado"

        self.run_with(workflow)
        self.assertEqual((self.sandbox / "informe.md").read_text(), "informe")

    def test_denegacion_no_crea_archivo_y_falla(self):
        agent.AUTO = False

        async def workflow(client, model, task, tools, dispatch, system, **kwargs):
            await dispatch("cargar_skill", {"nombre": "informe-incidencias"})
            result = await dispatch("escribir_fichero", {"ruta": "informe.md", "contenido": "informe"})
            self.assertIn("denegado", result)
            return "Terminado"

        with patch("builtins.input", return_value="n"), self.assertRaises(SystemExit):
            self.run_with(workflow)
        self.assertFalse((self.sandbox / "informe.md").exists())

    def test_no_da_por_completada_tarea_sin_herramientas(self):
        async def workflow(client, model, task, tools, dispatch, system, **kwargs):
            return "Terminado"

        with self.assertRaises(SystemExit):
            self.run_with(workflow)

    def test_tarea_personalizada_no_exige_informe(self):
        agent.TAREA_PREDETERMINADA = False

        async def workflow(client, model, task, tools, dispatch, system, **kwargs):
            return "Terminado"

        self.run_with(workflow)


if __name__ == "__main__":
    unittest.main()
