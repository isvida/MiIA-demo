import json
import os
import subprocess
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "ejemplos"))
from config import cargar_config
from agent_core import run_agent


class ConfigTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "config.json"
        self.data = {
            "base_url": "https://example.test/v1",
            "api_key": "${TEST_KEY}",
            "model": "external-model",
            "temperature": 0.7,
            "no_think": False,
        }
        self.write_config()

    def write_config(self):
        self.path.write_text(json.dumps(self.data), encoding="utf-8")

    def test_external_config_and_override(self):
        with patch.dict(os.environ, {"MIIA_CONFIG": str(self.path), "TEST_KEY": "test-key"}, clear=True):
            config = cargar_config()
            self.assertEqual(config.base_url, self.data["base_url"])
            self.assertEqual(config.api_key, "test-key")
            self.assertEqual(config.model, "external-model")
            self.assertEqual(config.temperature, 0.7)
            self.assertEqual(config.no_think_suffix, "")
            self.assertNotIn("test-key", repr(config))
            os.environ["MODEL"] = "override"
            os.environ["OPENAI_API_KEY"] = "override-key"
            os.environ["NO_THINK"] = "1"
            config = cargar_config()
            self.assertEqual((config.model, config.api_key, config.no_think_suffix),
                             ("override", "override-key", " /no_think"))

    def test_default_and_missing_key(self):
        self.data["api_key"] = "${TEST_KEY:-demo}"
        self.write_config()
        with patch.dict(os.environ, {"MIIA_CONFIG": str(self.path)}, clear=True):
            self.assertEqual(cargar_config().api_key, "demo")
            self.data["api_key"] = "${TEST_KEY}"
            self.write_config()
            with self.assertRaisesRegex(ValueError, "TEST_KEY"):
                cargar_config()

    def test_invalid_configuration(self):
        with patch.dict(os.environ, {"MIIA_CONFIG": str(self.path), "TEST_KEY": "test"}, clear=True):
            for key, value in (("temperature", 3), ("temperature", True), ("no_think", "false"),
                               ("base_url", "file:///etc/passwd"), ("model", "")):
                original = self.data[key]
                self.data[key] = value
                self.write_config()
                with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                    cargar_config()
                self.data[key] = original

    def test_tool_calling_against_openai_compatible_server(self):
        requests = []

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                length = int(self.headers["Content-Length"])
                body = json.loads(self.rfile.read(length))
                requests.append((self.path, self.headers.get("Authorization"), body))
                if len(requests) == 1:
                    message = {"role": "assistant", "content": None, "tool_calls": [{
                        "id": "call_1", "type": "function",
                        "function": {"name": "ects_desde_horas", "arguments": '{"horas":450}'},
                    }]}
                    finish = "tool_calls"
                else:
                    message = {"role": "assistant", "content": "18 ECTS"}
                    finish = "stop"
                response = json.dumps({
                    "id": "mock", "object": "chat.completion", "created": 1,
                    "model": "external-model",
                    "choices": [{"index": 0, "message": message, "finish_reason": finish}],
                }).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(response)))
                self.end_headers()
                self.wfile.write(response)

            def log_message(self, format, *args):
                pass

        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            self.data["base_url"] = f"http://127.0.0.1:{server.server_port}/v1"
            self.write_config()
            env = os.environ.copy()
            for key in ("OPENAI_BASE_URL", "OPENAI_API_KEY", "MODEL", "NO_THINK"):
                env.pop(key, None)
            env.update({"MIIA_CONFIG": str(self.path), "TEST_KEY": "test-key"})
            result = subprocess.run(
                [sys.executable, str(ROOT / "ejemplos/04_tool_calling.py")],
                env=env, capture_output=True, text=True, timeout=30,
            )
        finally:
            server.shutdown()
            thread.join()
            server.server_close()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("18 ECTS", result.stdout)
        self.assertEqual(len(requests), 2)
        for path, authorization, body in requests:
            self.assertEqual(path, "/v1/chat/completions")
            self.assertEqual(authorization, "Bearer test-key")
            self.assertEqual(body["model"], "external-model")
            self.assertEqual(body["temperature"], 0.7)
            self.assertNotIn("/no_think", json.dumps(body))
        self.assertEqual(requests[1][2]["messages"][-1]["tool_call_id"], "call_1")


class AgentConfigTests(unittest.IsolatedAsyncioTestCase):
    async def test_temperature_and_thinking_reach_agent_request(self):
        requests = []

        async def create(**kwargs):
            requests.append(kwargs)
            return SimpleNamespace(choices=[SimpleNamespace(
                message=SimpleNamespace(tool_calls=[], content="listo")
            )])

        client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))
        async def dispatch(name, arguments):
            raise AssertionError("No debería invocar herramientas")

        result = await run_agent(client, "modelo", "tarea", [], dispatch,
                                 temperature=0.7, no_think=False)
        self.assertEqual(result, "listo")
        self.assertEqual(requests[0]["temperature"], 0.7)
        self.assertNotIn("/no_think", requests[0]["messages"][0]["content"])


if __name__ == "__main__":
    unittest.main()
