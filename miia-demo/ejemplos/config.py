"""Configuración compartida de los ejemplos OpenAI-compatible."""
import json
import math
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlsplit


@dataclass(frozen=True)
class Config:
    base_url: str
    api_key: str = field(repr=False)
    model: str
    temperature: float
    no_think: bool

    @property
    def no_think_suffix(self) -> str:
        return " /no_think" if self.no_think else ""


def cargar_config() -> Config:
    path = Path(os.environ.get("MIIA_CONFIG", Path(__file__).with_name("config.json")))
    try:
        with path.open(encoding="utf-8") as file:
            data = json.load(file)
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"No se puede leer la configuración {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"La configuración {path} debe ser un objeto JSON.")

    values = {}
    for key, env in (("base_url", "OPENAI_BASE_URL"), ("model", "MODEL"), ("api_key", "OPENAI_API_KEY")):
        value = os.environ.get(env, data.get(key))
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"El campo {key} debe ser una cadena no vacía.")
        values[key] = value.strip()

    reference = re.fullmatch(r"\$\{([A-Za-z_][A-Za-z0-9_]*)(?::-([^}]*))?\}", values["api_key"])
    if reference:
        variable, default = reference.groups()
        key_value = os.environ.get(variable, default)
        if not key_value or not key_value.strip():
            raise ValueError(f"Falta la variable de entorno {variable} para la clave API.")
        values["api_key"] = key_value.strip()
    url = urlsplit(values["base_url"])
    if url.scheme not in ("http", "https") or not url.netloc or url.username or url.password:
        raise ValueError("base_url debe ser una URL HTTP(S) sin credenciales.")

    temperature = data.get("temperature")
    if isinstance(temperature, bool) or not isinstance(temperature, (int, float)):
        raise ValueError("temperature debe ser un número entre 0 y 2.")
    if not math.isfinite(temperature) or not 0 <= temperature <= 2:
        raise ValueError("temperature debe ser un número entre 0 y 2.")

    no_think = data.get("no_think")
    if not isinstance(no_think, bool):
        raise ValueError("no_think debe ser true o false.")
    if "NO_THINK" in os.environ:
        if os.environ["NO_THINK"] not in ("0", "1"):
            raise ValueError("NO_THINK debe ser 0 o 1.")
        no_think = os.environ["NO_THINK"] == "1"
    return Config(values["base_url"], values["api_key"], values["model"], float(temperature), no_think)
