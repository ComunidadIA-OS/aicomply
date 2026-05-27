# Copyright 2026 AIComply Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations

import ipaddress
import logging
import socket
import threading
import time
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

# ── Defensa contra prompt injection ──────────────────────────────────────────
# Los marcadores delimitan el bloque de datos del usuario para que el modelo
# los trate como contenido a analizar y no como instrucciones.

_MARCADOR_INICIO = "<<<DOCUMENTO_DEL_USUARIO_INICIO>>>"
_MARCADOR_FIN    = "<<<DOCUMENTO_DEL_USUARIO_FIN>>>"


def envolver_contenido_no_confiable(texto: str) -> str:
    """Envuelve contenido de usuario entre marcadores explícitos.

    Neutraliza secuencias que imiten nuestros delimitadores para evitar que
    el modelo interprete el texto del usuario como instrucciones del sistema.
    """
    texto = texto.strip()
    # Reemplazar <<< y >>> para que el texto no pueda imitar los marcadores
    texto = texto.replace("<<<", "«««").replace(">>>", "»»»")
    return f"{_MARCADOR_INICIO}\n{texto}\n{_MARCADOR_FIN}"


# ── C1: Mensajes de error seguros ─────────────────────────────────────────────

_KW_CONEXION = ("Connection refused", "ConnectError", "ConnectionError", "connect timeout", "Connection reset")
_KW_RATE = ("429", "rate_limit", "Too Many Requests")
_KW_AUTH = ("401", "403", "authentication_error", "permission_denied", "Invalid API Key")


def mensaje_error_seguro(exc: Exception) -> str:
    """Devuelve un mensaje seguro para el usuario sin filtrar detalles internos.

    El detalle completo se registra en el log del servidor.
    """
    raw = str(exc)
    exc_name = type(exc).__name__
    logger.error("Provider error [%s]: %s", exc_name, raw)

    if any(k in raw for k in _KW_CONEXION) or "Connect" in exc_name:
        return "No se puede conectar con el proveedor de IA. Compruebe la configuración en la barra lateral."

    if any(k in raw for k in _KW_RATE) or "RateLimit" in exc_name:
        return "El proveedor ha alcanzado el límite de peticiones. Espere unos segundos e inténtelo de nuevo."

    if any(k in raw for k in _KW_AUTH) or "Authentication" in exc_name:
        return "Credenciales inválidas. Compruebe la clave API en la configuración."

    return "Error al procesar la solicitud. Inténtelo de nuevo o compruebe la configuración del proveedor."


# ── M3: Validación SSRF ────────────────────────────────────────────────────────

# Rangos privados y de enlace local que deben bloquearse en modo hosted
_RANGOS_PRIVADOS = [
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"),  # metadata AWS/GCP/Azure
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),
]
_NOMBRES_LOOPBACK = {"localhost", "localhost.localdomain"}


def validar_base_url(url: str, modo: str) -> str | None:
    """Valida la URL base del provider. Devuelve un mensaje de error o None si es válida.

    En modo 'local' permite cualquier URL (incluido localhost).
    En modo 'hosted' bloquea loopback, RFC1918, metadata IP y esquemas no HTTP(S).
    """
    if not url:
        return "La URL base no puede estar vacía."

    try:
        parsed = urlparse(url)
    except Exception:
        return "URL con formato no válido."

    if parsed.scheme not in ("http", "https"):
        return f"Esquema no permitido: '{parsed.scheme}'. Use http o https."

    if modo != "hosted":
        return None

    # En modo hosted: bloquear destinos internos
    host = (parsed.hostname or "").lower().strip("[]")  # elimina [] de IPv6

    if host in _NOMBRES_LOOPBACK:
        return "En modo hosted no se permiten conexiones a localhost."

    try:
        ip = ipaddress.ip_address(host)
        if any(ip in rango for rango in _RANGOS_PRIVADOS):
            return "En modo hosted no se permiten conexiones a direcciones IP privadas o de loopback."
    except ValueError:
        # No es una IP literal — resolver el hostname y comprobar la IP resultante
        try:
            ip_resuelta = socket.gethostbyname(host)
            ip = ipaddress.ip_address(ip_resuelta)
            if any(ip in rango for rango in _RANGOS_PRIVADOS):
                return "En modo hosted no se permiten conexiones a direcciones IP privadas o de loopback."
        except OSError:
            return "No se puede resolver el hostname. Compruebe la URL."

    return None


# ── M2: Rate limiting por sesión (token bucket) ────────────────────────────────
# Estado en memoria de proceso. No persiste entre reinicios del servidor.
# Para producción multiusuario real, use Redis/Upstash como almacén compartido.

class TokenBucketSesion:
    """Rate limiter por sesión usando token bucket en memoria de proceso.

    Cada sesión tiene su propio bucket. El estado sobrevive recargas de
    Streamlit (mismo proceso) pero no reinicios del servidor.
    """

    _buckets: dict[str, dict] = {}
    _lock = threading.Lock()

    def __init__(self, capacidad: int = 10, tasa_recarga: float = 1.0):
        """
        capacidad: tokens máximos por sesión.
        tasa_recarga: tokens por segundo que se recargan.
        """
        self.capacidad = capacidad
        self.tasa_recarga = tasa_recarga

    def _obtener_bucket(self, session_id: str) -> dict:
        if session_id not in self._buckets:
            self._buckets[session_id] = {
                "tokens": float(self.capacidad),
                "ultimo": time.monotonic(),
            }
        return self._buckets[session_id]

    def consumir(self, session_id: str, coste: int = 1) -> bool:
        """Intenta consumir `coste` tokens. Devuelve True si se permite la acción."""
        with self._lock:
            bucket = self._obtener_bucket(session_id)
            ahora = time.monotonic()
            recargados = (ahora - bucket["ultimo"]) * self.tasa_recarga
            bucket["tokens"] = min(self.capacidad, bucket["tokens"] + recargados)
            bucket["ultimo"] = ahora
            if bucket["tokens"] >= coste:
                bucket["tokens"] -= coste
                return True
            return False


# Instancia compartida: burst de 30 mensajes, recarga 1 token/2 s (30/min en steady state).
# Para producción multiusuario real, sustituir por almacén compartido (Redis/Upstash).
rate_limiter = TokenBucketSesion(capacidad=30, tasa_recarga=0.5)
