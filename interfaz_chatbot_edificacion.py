# --------------------------------------------------
# Asistente Técnico Inteligente para Construcción
# Versión: UI Minimalista Oscura (abril 2025)
# --------------------------------------------------
# 👉 Solo se modifican estilos y experiencia visual.
# --------------------------------------------------

import streamlit as st
import google.generativeai as genai
from pinecone import Pinecone
from datetime import datetime

# ---------------- Configuración -----------------
GENAI_API_KEY = st.secrets["general"]["genai_api_key"]
PINECONE_API_KEY = st.secrets["general"]["pinecone_api_key"]
INDEX_NAME = "documentacion-edificacion"
MIN_SIMILARITY_SCORE = 0.50  # 70 %

# ---------------- Inicialización -----------------
genai.configure(api_key=GENAI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(INDEX_NAME)

# ---------------- Estilos globales -----------------

ACCENT = "#1E88E5"           # azul acento
BG_DARK = "#0f1117"          # fondo principal
BG_ELEV = "#1a1d24"          # contenedores elevados
TEXT_LIGHT = "#e0e0e0"

st.set_page_config(
    page_title="Asistente Técnico Inteligente",
    page_icon="🏗️",
    layout="wide",
)

# Inyectamos CSS minimalista oscuro
st.markdown(
    f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
        html, body, [class*="css"]  {{
            font-family: 'Inter', sans-serif;
            background-color: {BG_DARK};
            color: {TEXT_LIGHT};
        }}
        .block-container {{
            padding-top: 1.5rem;
            padding-bottom: 2rem;
        }}
        /* Cabecera */
        .app-header {{
            background: linear-gradient(90deg, {ACCENT} 0%, #673ab7 100%);
            padding: 1rem 2rem;
            border-radius: 0 0 12px 12px;
            margin-bottom: 1.5rem;
        }}
        .app-header h1 {{
            font-weight: 600;
            font-size: 1.6rem;
            color: #fff;
            margin: 0;
        }}
        /* Fragmentos */
        .fragment-container {{
            border-left: 3px solid {ACCENT};
            background-color: {BG_ELEV};
            padding: 0.75rem 1rem;
            border-radius: 6px;
            margin-bottom: 0.75rem;
        }}
        .fragment-source {{
            font-weight: 600;
            color: {ACCENT};
            font-size: 0.8rem;
            margin-bottom: 2px;
        }}
        .fragment-score {{
            font-size: 0.7rem;
            color: #9e9e9e;
            margin-bottom: 4px;
        }}
        .fragment-content {{
            font-size: 0.85rem;
            white-space: pre-wrap;
        }}
        /* Chat tweaks */
        .stChatMessage {{
            background-color: transparent;
        }}
        .stChatMessage .stMarkdown p {{
            margin-bottom: 0.4rem;
        }}
        /* Sidebar oscuro */
        section[data-testid="stSidebar"] > div:first-child {{
            background-color: {BG_ELEV};
        }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------- Prompt Base (sin cambios) -----------------
custom_prompt = """
Eres un asistente técnico inteligente especializado en documentación de ingeniería civil y proyectos de construcción.
Tu objetivo es proporcionar respuestas precisas, técnicas y claras basadas únicamente en la documentación proporcionada.

Recibirás:
1. El historial de la conversación actual
2. La última consulta (la actual) del usuario, la cual tienes que responder.
3. Fragmentos relevantes de documentación técnica

Instrucciones:
- Utiliza el historial de la conversación para entender el contexto de la consulta
- Responde principalmente con información contenida en los fragmentos proporcionados
- Usa terminología técnica apropiada para ingenieros
- Si la documentación no contiene la información solicitada, indícalo claramente
- Sé conciso pero completo en tus respuestas
- Cita números de sección, especificaciones o normas técnicas cuando estén disponibles en los fragmentos
- Cuando identifiques la respuesta, cita textualmente de qué parte de la documentación la has sacado.

Tu estilo debe ser técnico, preciso y objetivo.
"""

# ---------------- Estado de sesión -----------------
if "conversation" not in st.session_state:
    st.session_state.conversation = []

# ---------------- Funciones auxiliares -----------------

def display_fragments(fragments):
    if not fragments:
        st.info("No se encontraron fragmentos relevantes para esta consulta.")
        return
    for frag in fragments:
        st.markdown(
            f"""
            <div class=\"fragment-container\">
                <div class=\"fragment-source\">📄 {frag['documento']}</div>
                <div class=\"fragment-score\">Similitud {frag['score']:.0%}</div>
                <div class=\"fragment-content\">{frag['texto']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def format_conversation_history(history):
    return "\n\n".join(f"{m['role']}: {m['content']}" for m in history)

# ---------------- Cabecera -----------------
with st.container():
    st.markdown(
        """
        <div class=\"app-header\">
            <h1>🏗️ Asistente Técnico Inteligente</h1>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ---------------- Sidebar -----------------
with st.sidebar:
    st.header("Guía rápida")
    st.caption("Formula tu consulta técnica. La IA buscará en la documentación oficial.")
    st.divider()
    st.caption(f"Versión UI Oscura – {datetime.utcnow():%b %Y}")

# ---------------- Historial -----------------
for m in st.session_state.conversation:
    role = "assistant" if m["role"] == "Asistente" else "user"
    with st.chat_message(role):
        st.markdown(m["content"])
        if role == "assistant" and "fragments" in m:
            with st.expander("📚 Fragmentos"):
                display_fragments(m["fragments"])

# ---------------- Entrada -----------------
user_message = st.chat_input("Pregunta algo sobre la normativa…")

if user_message:
    st.session_state.conversation.append({"role": "Usuario", "content": user_message})
    with st.chat_message("user"):
        st.markdown(user_message)

    with st.spinner("Consultando documentación…"):
        embed_result = genai.embed_content(
            model="models/text-embedding-004",
            content=user_message,
        )
        query_vector = embed_result.get("embedding")

        if not query_vector:
            st.error("Error al generar el vector de embedding.")
        else:
            qres = index.query(vector=query_vector, top_k=10, include_metadata=True)
            frags = []
            for m in qres.get("matches", []):
                score = m.get("score", 0)
                if score >= MIN_SIMILARITY_SCORE:
                    md = m.get("metadata", {})
                    texto = md.get("texto", "")
                    doc = md.get("documento", "Sin nombre")
                    if texto:
                        frags.append({"texto": texto, "documento": doc, "score": score})

            ctx = "\n---\n".join(f"[{f['documento']}]: {f['texto']}" for f in frags)
            history_for_prompt = st.session_state.conversation[:-1]
            full_prompt = (
                f"{custom_prompt}\n\n"
                f"Historial:\n{format_conversation_history(history_for_prompt)}\n\n"
                f"Fragmentos:\n{ctx}\n\n"
                f"Consulta: {user_message}"
            )
            resp = model.generate_content(full_prompt)
            text = resp.candidates[0].content.parts[0].text
            st.session_state.conversation.append({"role": "Asistente", "content": text, "fragments": frags})

    with st.chat_message("assistant"):
        st.markdown(text)
        with st.expander("📚 Fragmentos"):
            display_fragments(frags)
        st.toast("Respuesta lista ✔️", icon="🤖")

