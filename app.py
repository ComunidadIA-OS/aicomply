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

import json
import streamlit as st
import streamlit.components.v1 as _components

import uuid
from datetime import datetime

from config import (
    AICOMPLY_MODE,
    ANTHROPIC_API_KEY,
    ANTHROPIC_MODEL,
    DISCLAIMER_INICIAL,
    OPENAI_COMPATIBLE_API_KEY,
    OPENAI_COMPATIBLE_BASE_URL,
    OPENAI_COMPATIBLE_MODEL,
)
from src.chatbot import AIComplyChat
from src.llm.factory import crear_provider, crear_provider_desde_env
from src.security import mensaje_error_seguro, validar_base_url
from src.tabs.cumplimiento import _inicializar_chatbot_cumplimiento, mostrar_tab_cumplimiento
from src.tabs.evaluador import mostrar_tab_evaluador
from src.tabs.informe import mostrar_tab_informe

st.set_page_config(
    page_title="AIComply — Evaluación AI Act",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Ocultar el indicador de ejecución (bicicleta/persona) y definir rueda de carga
st.markdown(
    """<style>
[data-testid='stStatusWidget']{visibility:hidden}
@keyframes _ac_spin{to{transform:rotate(360deg)}}
._ac_thinking{display:inline-flex;align-items:center;gap:8px;color:#666;font-size:0.9em;padding:4px 0}
._ac_spinner{width:16px;height:16px;border:2px solid #ddd;border-top-color:#555;border-radius:50%;animation:_ac_spin .8s linear infinite;flex-shrink:0}

/* ── Theme toggle bar ── */
#ac-tb{position:fixed;top:.35rem;right:2.7rem;z-index:999999;display:flex;gap:0;align-items:center}
.ac-t{all:unset;cursor:pointer;width:2rem;height:2rem;display:flex;align-items:center;justify-content:center;border-radius:.25rem;color:rgba(49,51,63,.45);transition:color .12s}
.ac-t:hover,.ac-t[data-active="1"]{color:rgba(49,51,63,.9)}
.ac-t svg{width:15px;height:15px;pointer-events:none}
@media(prefers-color-scheme:dark){
  .ac-t{color:rgba(250,250,250,.45)}
  .ac-t:hover,.ac-t[data-active="1"]{color:rgba(250,250,250,.9)}}
body.ac-dark .ac-t{color:rgba(250,250,250,.45)!important}
body.ac-dark .ac-t:hover,body.ac-dark .ac-t[data-active="1"]{color:rgba(250,250,250,.9)!important}

/* ── Dark overrides ── */
body.ac-dark .stApp{background-color:#0e1117!important}
body.ac-dark [data-testid="stSidebar"]>div:first-child{background-color:#262730!important}
body.ac-dark [data-testid="stHeader"]{background-color:#0e1117!important}
body.ac-dark [data-testid="stBottomBlockContainer"]{background-color:#0e1117!important}
body.ac-dark .stMarkdown p,body.ac-dark .stMarkdown li,body.ac-dark .stMarkdown h1,body.ac-dark .stMarkdown h2,body.ac-dark .stMarkdown h3,body.ac-dark .stMarkdown span{color:#fafafa!important}
body.ac-dark [data-testid="stChatMessage"]{background-color:#1a1d27!important}
body.ac-dark [data-testid="stChatInput"] textarea{background-color:#262730!important;color:#fafafa!important}
body.ac-dark .stTextInput input{background-color:#262730!important;color:#fafafa!important}
body.ac-dark .stRadio label,body.ac-dark .stCaption{color:rgba(250,250,250,.7)!important}

/* ── Light overrides ── */
body.ac-light .stApp{background-color:#ffffff!important}
body.ac-light [data-testid="stSidebar"]>div:first-child{background-color:#f0f2f6!important}
body.ac-light [data-testid="stHeader"]{background-color:#ffffff!important}
body.ac-light [data-testid="stBottomBlockContainer"]{background-color:#ffffff!important}
</style>
<div id="ac-tb">
  <button class="ac-t" id="ac-t-auto" onclick="acT('auto')" title="Automático (sistema)">
    <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round">
      <circle cx="8" cy="8" r="5.5"/>
      <path d="M8 2.5A5.5 5.5 0 0 1 8 13.5z" fill="currentColor" stroke="none"/>
    </svg>
  </button>
  <button class="ac-t" id="ac-t-light" onclick="acT('light')" title="Modo día">
    <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round">
      <circle cx="8" cy="8" r="2.8"/>
      <line x1="8" y1="1.2" x2="8" y2="3"/><line x1="8" y1="13" x2="8" y2="14.8"/>
      <line x1="1.2" y1="8" x2="3" y2="8"/><line x1="13" y1="8" x2="14.8" y2="8"/>
      <line x1="3.2" y1="3.2" x2="4.4" y2="4.4"/><line x1="11.6" y1="11.6" x2="12.8" y2="12.8"/>
      <line x1="12.8" y1="3.2" x2="11.6" y2="4.4"/><line x1="4.4" y1="11.6" x2="3.2" y2="12.8"/>
    </svg>
  </button>
  <button class="ac-t" id="ac-t-dark" onclick="acT('dark')" title="Modo noche">
    <svg viewBox="0 0 16 16" fill="currentColor" stroke="none">
      <path d="M6 2.5a5.5 5.5 0 1 0 7.5 7.5A5 5 0 0 1 6 2.5z"/>
    </svg>
  </button>
</div>
<script>
(function(){
  function setT(m){
    document.body.classList.remove('ac-dark','ac-light');
    if(m==='dark') document.body.classList.add('ac-dark');
    else if(m==='light') document.body.classList.add('ac-light');
    ['auto','light','dark'].forEach(function(id){
      var b=document.getElementById('ac-t-'+id);
      if(b) b.setAttribute('data-active',m===id?'1':'0');
    });
  }
  window.acT=function(m){localStorage.setItem('ac_theme',m);setT(m);};
  setT(localStorage.getItem('ac_theme')||'auto');
  new MutationObserver(function(){setT(localStorage.getItem('ac_theme')||'auto');})
    .observe(document.body,{attributes:true,attributeFilter:['class']});
})();
</script>""",
    unsafe_allow_html=True,
)

# Selector de tema (claro / oscuro / sistema) visible junto a los 3 puntitos
_components.html(
    """<script>
(function(){
  var p=window.parent, doc=p.document;
  if(doc.getElementById('_ac_ts')) return;

  var wrap=doc.createElement('div');
  wrap.id='_ac_ts';

  [['☀️','Light','Claro'],['🌙','Dark','Oscuro'],['🖥️','System','Sistema']].forEach(function(m){
    var b=doc.createElement('button');
    b.title=m[2]; b.textContent=m[0];
    b.style.cssText='background:none;border:none;cursor:pointer;font-size:15px;'
      +'width:28px;height:28px;padding:0;border-radius:5px;opacity:.6;'
      +'transition:opacity .15s,background .15s;display:flex;align-items:center;justify-content:center;';
    b.onmouseover=function(){this.style.opacity='1';this.style.background='rgba(128,128,128,.15)';};
    b.onmouseout =function(){this.style.opacity='.6';this.style.background='none';};
    b.onclick=function(){_acT(m[1]);};
    wrap.appendChild(b);
  });

  var tb=doc.querySelector('[data-testid="stToolbar"]');
  if(tb){
    wrap.style.cssText='display:flex;gap:1px;align-items:center;margin-right:4px;';
    tb.insertBefore(wrap,tb.firstChild);
  } else {
    wrap.style.cssText='position:fixed;top:8px;right:54px;z-index:99999;display:flex;gap:1px;';
    doc.body.appendChild(wrap);
  }

  p._acT=function(name){
    var ls=p.localStorage;
    var val=name==='System'?null:JSON.stringify({name:name});
    if(val) ls.setItem('stActiveTheme',val); else ls.removeItem('stActiveTheme');
    p.dispatchEvent(new StorageEvent('storage',{
      key:'stActiveTheme',newValue:val,storageArea:ls,bubbles:true
    }));
  };
})();
</script>""",
    height=0,
)

# ── Avisos de privacidad por provider y plan ───────────────────────────────────
_AVISOS: dict[str, tuple[str, str]] = {
    "groq": (
        "warning",
        "Sus datos se procesan en servidores de Groq (EE. UU.). "
        "Groq NO entrena sus modelos con los datos de los usuarios. "
        "Los modelos disponibles son de código abierto (Meta Llama). "
        "Límite gratuito: ~1.000 req/día. Obtenga su clave en console.groq.com.",
    ),
    "mistral_free": (
        "error",
        "Sus datos se procesan en servidores de Mistral AI (Francia, UE). "
        "ATENCIÓN: el plan gratuito PUEDE usar sus conversaciones para entrenar modelos. "
        "NO recomendado para información confidencial o sensible. "
        "Límite gratuito: ~1.000 M tokens/mes. Clave gratuita en console.mistral.ai.",
    ),
    "anthropic_api": (
        "warning",
        "Sus datos se procesan en servidores de Anthropic (EE. UU.). "
        "Los datos NO se usan para entrenamiento de modelos. "
        "DPA disponible bajo petición. "
        "Recomendado para uso empresarial con documentación no crítica.",
    ),
    "anthropic_enterprise": (
        "info",
        "Mayor nivel de privacidad. Sus datos no se usan para entrenamiento. "
        "Acuerdo DPA incluido en el contrato. "
        "Recomendado para documentación confidencial empresarial.",
    ),
    "openai_free": (
        "error",
        "Sus datos se procesan en servidores de OpenAI (EE. UU.). "
        "OpenAI PUEDE usar sus datos para mejorar sus modelos. "
        "NO recomendado para documentación confidencial o sensible.",
    ),
    "openai_paid": (
        "warning",
        "Sus datos se procesan en servidores de OpenAI (EE. UU.). "
        "Datos NO usados para entrenamiento por defecto. "
        "Revise el DPA antes de enviar documentación confidencial.",
    ),
    "openai_enterprise": (
        "info",
        "Máxima privacidad. Acuerdo DPA incluido en el contrato. "
        "Sus datos no se usan para entrenamiento. "
        "Recomendado para documentación confidencial empresarial.",
    ),
    "openai_compatible_local": (
        "success",
        "Máxima privacidad: ningún dato sale de su infraestructura (LM Studio, vLLM, llama.cpp, Ollama). "
        "Aviso de capacidad: los modelos locales pequeños (7-8B parámetros) ofrecen una calidad de "
        "razonamiento jurídico limitada. Para uso serio se recomienda un modelo de 70B o superior, "
        "o cuantizaciones de calidad (Q5_K_M+) con hardware adecuado.",
    ),
    "openai_compatible_external": (
        "warning",
        "Sus datos se envían a servidores externos. "
        "Revise la política de privacidad del proveedor elegido "
        "antes de enviar documentación confidencial.",
    ),
}


def _mostrar_aviso(clave: str) -> None:
    nivel, texto = _AVISOS[clave]
    getattr(st, nivel)(f"**Condiciones de privacidad:** {texto}")


# ── Persistencia de sesión ────────────────────────────────────────────────────
_CLAVES_SESION = (
    "clasificacion_data",
    "cumplimiento_data",
    "mensajes_evaluador",
    "mensajes_cumplimiento",
    "evaluacion_completada",
    "cumplimiento_completado",
    "acceso_directo_cumplimiento",
    "informe_md_clasificacion",
    "informe_md_cumplimiento",
    "informe_md_completo",
)


def _exportar_sesion() -> bytes:
    datos: dict = {"_version": "1", "_app": "aicomply"}
    for k in _CLAVES_SESION:
        datos[k] = st.session_state.get(k)
    return json.dumps(datos, ensure_ascii=False, indent=2).encode("utf-8")


def _importar_sesion(raw: bytes, provider) -> None:
    datos = json.loads(raw.decode("utf-8"))
    for k in _CLAVES_SESION:
        if k in datos:
            st.session_state[k] = datos[k]

    chatbot_eval = AIComplyChat(provider=provider)
    chatbot_eval.historial = list(datos.get("mensajes_evaluador") or [])
    chatbot_eval.evaluacion_completa = bool(datos.get("evaluacion_completada"))
    st.session_state.chatbot_evaluador = chatbot_eval

    mensajes_cumpl = datos.get("mensajes_cumplimiento") or []
    clas_data = datos.get("clasificacion_data") or {}
    if mensajes_cumpl or datos.get("cumplimiento_completado"):
        chatbot_cumpl = _inicializar_chatbot_cumplimiento(provider, clas_data)
        chatbot_cumpl.historial = list(mensajes_cumpl)
        st.session_state.chatbot_cumplimiento = chatbot_cumpl


# ── Inicialización del estado de sesión ───────────────────────────────────────
def _init_session() -> None:
    if "provider_configurado" not in st.session_state:
        provider_env = crear_provider_desde_env()
        if provider_env:
            st.session_state.provider = provider_env
            st.session_state.provider_configurado = True
        else:
            st.session_state.provider = None
            st.session_state.provider_configurado = False

    if "disclaimer_aceptado" not in st.session_state:
        st.session_state.disclaimer_aceptado = False

    # Claves de las tres pestañas
    for clave in ("mensajes_evaluador", "mensajes_cumplimiento"):
        if clave not in st.session_state:
            st.session_state[clave] = []

    for clave in ("clasificacion_data", "cumplimiento_data"):
        if clave not in st.session_state:
            st.session_state[clave] = {}

    for clave in ("evaluacion_completada", "cumplimiento_completado", "acceso_directo_cumplimiento"):
        if clave not in st.session_state:
            st.session_state[clave] = False

    for clave in ("informe_md_clasificacion", "informe_md_cumplimiento", "informe_md_completo"):
        if clave not in st.session_state:
            st.session_state[clave] = None

    if "chatbot_evaluador" not in st.session_state:
        if st.session_state.get("provider_configurado") and st.session_state.get("provider"):
            st.session_state.chatbot_evaluador = AIComplyChat(provider=st.session_state.provider)
        else:
            st.session_state.chatbot_evaluador = None

    if "chatbot_cumplimiento" not in st.session_state:
        st.session_state.chatbot_cumplimiento = None

    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())


_init_session()


# ════════════════════════════════════════════════════════════════════════════════
# PANTALLA 1: CONFIGURACIÓN DEL PROVIDER
# ════════════════════════════════════════════════════════════════════════════════
def mostrar_selector_provider() -> None:
    st.title("AIComply")
    st.subheader("Configuración del modelo de lenguaje")
    st.markdown(
        "Seleccione cómo quiere ejecutar AIComply. "
        "Lea atentamente las condiciones de privacidad antes de confirmar su elección."
    )
    st.divider()

    proveedor = st.radio(
        "Proveedor de IA",
        [
            "Groq (gratuito, modelos open source, nube EE. UU.)",
            "Mistral (gratuito con límites, nube Francia)",
            "Anthropic Claude (API de pago)",
            "OpenAI (API de pago)",
            "API compatible con OpenAI (LM Studio, vLLM...)",
        ],
        index=0,
    )

    config_provider: dict = {}
    privacidad_valida = True

    # ── Groq ──────────────────────────────────────────────────────────────────
    if proveedor.startswith("Groq"):
        _mostrar_aviso("groq")
        st.markdown("**Configuración de Groq:**")

        api_key = st.text_input(
            "API Key de Groq",
            type="password",
            help="Clave gratuita en https://console.groq.com/keys",
        )
        modelo = st.selectbox(
            "Modelo",
            ["llama-3.3-70b-versatile", "llama-4-scout-17b-16e-instruct", "mixtral-8x7b-32768"],
            index=0,
            help="llama-3.3-70b-versatile ofrece la mejor calidad para el árbol de decisión.",
        )

        if not api_key:
            st.warning("Introduzca su API key de Groq para continuar.")
            privacidad_valida = False

        config_provider = {
            "provider": "openai_compatible",
            "api_key": api_key,
            "base_url": "https://api.groq.com/openai/v1",
            "model": modelo,
        }

    # ── Mistral ───────────────────────────────────────────────────────────────
    elif proveedor.startswith("Mistral"):
        _mostrar_aviso("mistral_free")
        st.markdown("**Configuración de Mistral:**")

        api_key = st.text_input(
            "API Key de Mistral",
            type="password",
            help="Clave gratuita en https://console.mistral.ai/",
        )
        modelo = st.selectbox(
            "Modelo",
            ["mistral-small-latest", "mistral-large-latest"],
            index=0,
            help="mistral-small-latest es suficiente para la mayoría de evaluaciones.",
        )

        if not api_key:
            st.warning("Introduzca su API key de Mistral para continuar.")
            privacidad_valida = False

        config_provider = {
            "provider": "openai_compatible",
            "api_key": api_key,
            "base_url": "https://api.mistral.ai/v1",
            "model": modelo,
        }

    # ── Anthropic ─────────────────────────────────────────────────────────────
    elif proveedor.startswith("Anthropic"):
        plan = st.radio(
            "Plan / tipo de cuenta",
            ["API de pago (individual / empresa)", "Claude for Business / Enterprise"],
        )
        _mostrar_aviso("anthropic_api" if "pago" in plan else "anthropic_enterprise")

        api_key = st.text_input(
            "API Key de Anthropic",
            type="password",
            value=ANTHROPIC_API_KEY,
            help="Obtenga su API key en https://console.anthropic.com/",
        )
        modelo = st.selectbox(
            "Modelo",
            ["claude-sonnet-4-6", "claude-opus-4-7", "claude-haiku-4-5-20251001"],
            index=0,
        )

        if not api_key:
            st.warning("Introduzca su API key para continuar.")
            privacidad_valida = False

        config_provider = {"provider": "anthropic", "api_key": api_key, "model": modelo}

    # ── OpenAI ────────────────────────────────────────────────────────────────
    elif proveedor.startswith("OpenAI"):
        plan = st.radio(
            "Plan / tipo de cuenta",
            ["Cuenta gratuita", "API de pago (Tier 1+)", "ChatGPT Enterprise"],
        )
        clave_aviso = {
            "Cuenta gratuita": "openai_free",
            "API de pago (Tier 1+)": "openai_paid",
            "ChatGPT Enterprise": "openai_enterprise",
        }[plan]
        _mostrar_aviso(clave_aviso)

        api_key = st.text_input(
            "API Key de OpenAI",
            type="password",
            help="Obtenga su API key en https://platform.openai.com/",
        )
        modelo = st.selectbox(
            "Modelo",
            ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"],
            index=0,
        )

        if not api_key:
            st.warning("Introduzca su API key para continuar.")
            privacidad_valida = False

        config_provider = {
            "provider": "openai_compatible",
            "api_key": api_key,
            "base_url": "https://api.openai.com/v1",
            "model": modelo,
        }

    # ── API compatible con OpenAI ──────────────────────────────────────────────
    else:
        subtipo = st.radio(
            "Tipo de API",
            [
                "Local (LM Studio, vLLM, llama.cpp) — datos en su infraestructura",
                "Servicio externo (Groq, Together AI, Mistral API, Anyscale...)",
            ],
        )
        _mostrar_aviso(
            "openai_compatible_local" if subtipo.startswith("Local") else "openai_compatible_external"
        )

        base_url = st.text_input(
            "URL base de la API",
            value=OPENAI_COMPATIBLE_BASE_URL,
            help="Ejemplo LM Studio: http://localhost:1234/v1  |  Groq: https://api.groq.com/openai/v1",
        )
        api_key = st.text_input(
            "API Key (dejar vacío si no es necesaria)",
            type="password",
            value=OPENAI_COMPATIBLE_API_KEY,
        )
        modelo = st.text_input(
            "Nombre del modelo",
            value=OPENAI_COMPATIBLE_MODEL,
            help="Ejemplo: llama-3.1-8b-instruct, mistral-7b-instruct, deepseek-r1",
        )

        if not base_url or not modelo:
            st.warning("Introduzca la URL base y el nombre del modelo para continuar.")
            privacidad_valida = False
        elif error_url := validar_base_url(base_url, AICOMPLY_MODE):
            st.error(error_url)
            privacidad_valida = False

        config_provider = {
            "provider": "openai_compatible",
            "api_key": api_key or "dummy",
            "base_url": base_url,
            "model": modelo,
        }

    st.divider()
    privacidad_aceptada = st.checkbox(
        "He leído y entiendo las condiciones de privacidad descritas arriba"
    )
    puede_continuar = privacidad_valida and privacidad_aceptada

    if st.button(
        "Configurar y continuar",
        type="primary",
        use_container_width=True,
        disabled=not puede_continuar,
    ):
        try:
            provider = crear_provider(config_provider)
            st.session_state.provider = provider
            st.session_state.provider_configurado = True
            st.session_state.chatbot_evaluador = AIComplyChat(provider=provider)
            st.rerun()
        except Exception as exc:
            st.error(mensaje_error_seguro(exc))


if not st.session_state.provider_configurado:
    mostrar_selector_provider()
    st.stop()


# ════════════════════════════════════════════════════════════════════════════════
# PANTALLA 2: AVISO LEGAL
# ════════════════════════════════════════════════════════════════════════════════
def mostrar_disclaimer() -> None:
    st.title("AIComply")
    st.subheader("Evaluación de cumplimiento del AI Act europeo para PYMEs industriales")
    st.markdown(DISCLAIMER_INICIAL)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button(
            "Acepto las condiciones y quiero continuar",
            use_container_width=True,
            type="primary",
        ):
            st.session_state.disclaimer_aceptado = True
            st.rerun()


if not st.session_state.disclaimer_aceptado:
    mostrar_disclaimer()
    st.stop()


# ════════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ════════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.title("AIComply")
    st.caption("Evaluación AI Act para PYMEs industriales")
    st.divider()

    provider = st.session_state.provider
    st.caption(
        f"Modelo: **{provider.nombre_modelo}**  \n"
        f"Provider: **{provider.nombre_provider}**"
    )
    st.divider()

    # Progreso de la evaluación
    st.caption("**Progreso:**")
    eval_ok = (
        st.session_state.get("evaluacion_completada", False)
        or st.session_state.get("acceso_directo_cumplimiento", False)
    )
    cumpl_ok = st.session_state.get("cumplimiento_completado", False)
    informe_ok = bool(
        st.session_state.get("informe_md_clasificacion")
        or st.session_state.get("informe_md_cumplimiento")
        or st.session_state.get("informe_md_completo")
    )

    st.caption(f"{'✓' if eval_ok else '○'} Evaluación y clasificación")
    st.caption(f"{'✓' if cumpl_ok else '○'} Análisis de cumplimiento")
    st.caption(f"{'✓' if informe_ok else '○'} Informe generado")

    if eval_ok:
        datos = st.session_state.clasificacion_data
        clasificacion = datos.get("clasificacion", "?")
        st.metric("Clasificación", clasificacion)

    st.divider()

    if st.button("Nueva evaluación", use_container_width=True):
        for clave in ("mensajes_evaluador", "mensajes_cumplimiento"):
            st.session_state[clave] = []
        for clave in ("clasificacion_data", "cumplimiento_data"):
            st.session_state[clave] = {}
        for clave in ("informe_md_clasificacion", "informe_md_cumplimiento", "informe_md_completo"):
            st.session_state[clave] = None
        st.session_state.evaluacion_completada = False
        st.session_state.cumplimiento_completado = False
        st.session_state.acceso_directo_cumplimiento = False
        st.session_state.chatbot_evaluador = AIComplyChat(provider=provider)
        st.session_state.chatbot_cumplimiento = None
        st.rerun()

    # ── Guardar / cargar sesión ───────────────────────────────────────────────
    tiene_datos = bool(
        st.session_state.get("mensajes_evaluador")
        or st.session_state.get("clasificacion_data")
    )
    if tiene_datos:
        fecha = datetime.now().strftime("%Y-%m-%d_%H%M")
        st.download_button(
            "Guardar sesión",
            data=_exportar_sesion(),
            file_name=f"aicomply_sesion_{fecha}.json",
            mime="application/json",
            use_container_width=True,
        )

    with st.expander("Cargar sesión guardada"):
        st.caption("⚠ El fichero puede contener información confidencial de su evaluación.")
        archivo_sesion = st.file_uploader(
            "Fichero .json de sesión",
            type=["json"],
            label_visibility="collapsed",
            key="upload_sesion",
        )
        if archivo_sesion and st.button("Restaurar sesión", use_container_width=True):
            try:
                _importar_sesion(archivo_sesion.read(), provider)
                st.rerun()
            except Exception as exc:
                st.error(f"No se pudo cargar la sesión: {exc}")

    if st.button("Cambiar proveedor de IA", use_container_width=True):
        for clave in list(st.session_state.keys()):
            del st.session_state[clave]
        # Evita que _init_session() reconfigure automáticamente desde las variables
        # de entorno (ANTHROPIC_API_KEY etc.) y salte el selector de proveedor.
        st.session_state["provider_configurado"] = False
        st.rerun()

    st.divider()
    st.caption(
        "AIComply es una herramienta auxiliar de orientación. "
        "Los resultados no constituyen asesoramiento legal."
    )


# ════════════════════════════════════════════════════════════════════════════════
# PESTAÑAS PRINCIPALES
# ════════════════════════════════════════════════════════════════════════════════
tab1, tab2, tab3 = st.tabs(
    ["Evaluador y clasificador", "Cumplimiento", "Informe"]
)

with tab1:
    mostrar_tab_evaluador(provider)

with tab2:
    mostrar_tab_cumplimiento(provider)

with tab3:
    mostrar_tab_informe()
