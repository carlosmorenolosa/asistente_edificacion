# --------------------------------------------------
# Asistente Técnico Inteligente para Construcción
# Versión: UI Mejorada (abril 2025)
# --------------------------------------------------
# 👉 La lógica de negocio RAG se mantiene intacta; solo se han aplicado
#    mejoras sustanciales en diseño y experiencia de usuario.
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

# NB: Misma configuración de recuperación

# ---------------- Inicialización -----------------
genai.configure(api_key=GENAI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(INDEX_NAME)

# ---------------- Estilos globales -----------------
st.set_page_config(
    page_title="Asistente Técnico Inteligente",
    page_icon="🏗️",
    layout="wide",
    menu_items={
        "Report a bug": "mailto:soporte@tuempresa.com",
        "About": "### Asistente Técnico\nHerramienta IA para consulta de documentación de edificación."
    },
)

PRIMARY_COLOR = "#0066cc"

st.markdown(
    f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
        html, body, [class*="css"]  {{
            font-family: 'Inter', sans-serif;
            scroll-behavior: smooth;
        }}
        .block-container {{
            padding-top: 1.5rem;
            padding-bottom: 2rem;
        }}
        /* Encabezado */
        .app-header {{
            background: linear-gradient(90deg, {PRIMARY_COLOR} 0%, #3e8eff 100%);
            padding: 1.2rem 2rem;
            border-radius: 0 0 12px 12px;
            color: #fff;
            margin-bottom: 1.2rem;
        }}
        .app-header h1 {{
            font-weight: 600;
            font-size: 1.75rem;
            margin: 0;
        }}
        /* Fragmentos */
        .fragment-container {{
            border-left: 4px solid {PRIMARY_COLOR};
            background-color: #f5f9ff;
            padding: 0.8rem 1rem;
            border-radius: 6px;
            margin-bottom: 0.75rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }}
        .fragment-source {{
            font-weight: 600;
            color: {PRIMARY_COLOR};
            font-size: 0.85rem;
            margin-bottom: 2px;
        }}
        .fragment-score {{
            font-size: 0.75rem;
            color: #666;
            margin-bottom: 4px;
        }}
        .fragment-content {{
            font-size: 0.88rem;
            white-space: pre-wrap;
        }}
        /* Chat message tweaks */
        .stChatMessage .stMarkdown p {{
            margin-bottom: 0.5rem;
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
    """Renderiza los pasajes recuperados en un contenedor elegante."""
    if not fragments:
        st.info("No se encontraron fragmentos relevantes para esta consulta.")
        return
    for frag in fragments:
        badge_color = "#28a745" if frag["score"] >= 0.8 else ("#ffc107" if frag["score"] >= 0.6 else "#dc3545")
        st.markdown(
            f"""
            <div class="fragment-container">
                <div class="fragment-source">📄 {frag['documento']}</div>
                <div class="fragment-score"><span style='background:{badge_color};color:#fff;padding:2px 6px;border-radius:4px'>Similitud {frag['score']:.0%}</span></div>
                <div class="fragment-content">{frag['texto']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def format_conversation_history(history):
    return "\n\n".join(f"{m['role']}: {m['content']}" for m in history)

# ---------------- Encabezado custom -----------------
with st.container():
    st.markdown(
        """
        <div class="app-header">
            <h1>🏗️ Asistente Técnico Inteligente para Construcción</h1>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ---------------- Sidebar -----------------
with st.sidebar:
    st.header("ℹ️ Guía rápida")
    st.markdown(
        """
        1. Formula tu **consulta técnica** en el cuadro inferior.
        2. Revisa la respuesta (fuente citada).
        3. Expande *📚 Fragmentos recuperados* para ver el contexto.
        """
    )
    st.divider()
    st.caption("Versión UI Mejorada – {:%d %b %Y}.".format(datetime.utcnow()))
    st.write("© 2025 Tu Empresa")

# ---------------- Mostrar historial -----------------
for msg in st.session_state.conversation:
    role = "assistant" if msg["role"] == "Asistente" else "user"
    with st.chat_message(role):
        st.markdown(msg["content"])
        if role == "assistant" and "fragments" in msg:
            with st.expander("📚 Mostrar fragmentos recuperados"):
                display_fragments(msg["fragments"])

# ---------------- Entrada del usuario -----------------
user_message = st.chat_input("Escribe tu consulta técnica aquí…")

if user_message:
    st.session_state.conversation.append({"role": "Usuario", "content": user_message})
    with st.chat_message("user"):
        st.markdown(user_message)

    with st.spinner("🔎 Analizando documentación…"):
        # (lógica de embedding / búsqueda SIN CAMBIOS)
        embed_result = genai.embed_content(
            model="models/text-embedding-004",
            content=user_message,
        )
        query_vector = embed_result.get("embedding")

        if not query_vector:
            st.error("Error al generar el vector de embedding de la consulta.")
        else:
            query_response = index.query(vector=query_vector, top_k=10, include_metadata=True)
            retrieved_segments = []
            for match in query_response.get("matches", []):
                score = match.get("score", 0)
                if score >= MIN_SIMILARITY_SCORE:
                    md = match.get("metadata", {})
                    texto = md.get("texto", "")
                    doc = md.get("documento", "Documento sin nombre")
                    if texto:
                        retrieved_segments.append({
                            "texto": texto,
                            "documento": doc,
                            "score": score,
                        })

            retrieved_context = "\n---\n".join([
                f"[{seg['documento']}]: {seg['texto']}" for seg in retrieved_segments
            ])
            history_for_prompt = st.session_state.conversation[:-1] if len(st.session_state.conversation) > 1 else []
            formatted_history = format_conversation_history(history_for_prompt)

            full_prompt = (
                f"{custom_prompt}\n\n"
                f"📜 **Historial de la conversación:**\n{formatted_history}\n"
                f"📚 **Fragmentos de documentación relevantes:**\n{retrieved_context}\n\n"
                f"👤 **Consulta actual del usuario:** {user_message}"
            )

            response = model.generate_content(full_prompt)
            response_text = response.candidates[0].content.parts[0].text

            # Guardar respuesta y fragmentos
            st.session_state.conversation.append(
                {
                    "role": "Asistente",
                    "content": response_text,
                    "fragments": retrieved_segments,
                }
            )

    # Mostrar respuesta
    with st.chat_message("assistant"):
        st.markdown(response_text)
        with st.expander("📚 Mostrar fragmentos recuperados"):
            display_fragments(retrieved_segments)
        st.toast("✅ Respuesta generada", icon="🤖")
