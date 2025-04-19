import streamlit as st
import google.generativeai as genai
from pinecone import Pinecone

# ---------------- Configuración -----------------
GENAI_API_KEY = "AIzaSyCPhvLFkQlhVyKsXsgR9EZi09QmmlN3V-k"
PINECONE_API_KEY = "pcsk_2bRoe6_3Nysegtmsfj3NT4D2Zemd2Vd5KPAniF6hjCRRqgyLeStcGZvrBAMgZaunAE4ohF"
INDEX_NAME = "documentacion-edificacion"
MIN_SIMILARITY_SCORE = 0.50  # 70%

genai.configure(api_key=GENAI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(INDEX_NAME)

# ---------------- Estilos -----------------
st.set_page_config(
    page_title="Asistente Técnico Inteligente para Construcción", 
    page_icon="🔍", 
    layout="wide"
)

st.markdown("""
    <style>
        body {
            font-family: 'Inter', sans-serif;
            color: #333;
            background-color: #f8f9fa;
        }
        .fragment-container {
            margin-top: 10px;
            border-left: 3px solid #0066cc;
            padding-left: 15px;
            background-color: #f0f5ff;
            border-radius: 5px;
            margin-bottom: 10px;
            padding: 15px;
        }
        .fragment-source {
            font-weight: 600;
            color: #0066cc;
            font-size: 0.85rem;
            margin-bottom: 5px;
        }
        .fragment-score {
            font-size: 0.85rem;
            color: #555;
            margin-bottom: 6px;
        }
        .fragment-content {
            font-size: 0.9rem;
            color: #333;
            white-space: pre-wrap;
        }
        .stTextInput input {
            border-radius: 4px;
            border: 1px solid #ddd;
        }
        h1, h2, h3 {
            font-weight: 600;
            color: #0066cc;
        }
    </style>
""", unsafe_allow_html=True)

# ---------------- Prompt Base -----------------
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

# ---------------- Estado -----------------
if "conversation" not in st.session_state:
    st.session_state.conversation = []

# ---------------- Funciones ----------------
def display_fragments(fragments):
    if not fragments:
        st.info("No se encontraron fragmentos relevantes para esta consulta.")
        return
    for fragment in fragments:
        st.markdown(f"""
        <div class="fragment-container">
            <div class="fragment-source">📄 Documento: {fragment['documento']}</div>
            <div class="fragment-score">🔍 Similitud: {fragment['score']:.2%}</div>
            <div class="fragment-content">{fragment['texto']}</div>
        </div>
        """, unsafe_allow_html=True)

def format_conversation_history(conversation):
    formatted_history = ""
    for msg in conversation:
        formatted_history += f"{msg['role']}: {msg['content']}\n\n"
    return formatted_history

# ---------------- Interfaz Principal ----------------
st.title("🔍 Asistente Inteligente de Documentación Técnica")
st.markdown("Consulta cualquier información técnica de la documentación de edificación.")

# Mostrar historial completo
for msg in st.session_state.conversation:
    with st.chat_message(msg["role"].lower()):
        st.markdown(msg["content"])
        if msg["role"] == "Asistente" and "fragments" in msg:
            with st.expander("📚 Mostrar fragmentos recuperados"):
                display_fragments(msg["fragments"])

# Entrada del usuario
user_message = st.chat_input("Escribe tu consulta técnica aquí...")

if user_message:
    st.session_state.conversation.append({"role": "Usuario", "content": user_message})

    with st.chat_message("usuario"):
        st.markdown(user_message)

    with st.spinner("Analizando documentación..."):
        embed_result = genai.embed_content(
            model="models/text-embedding-004",
            content=user_message
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
                    metadata = match.get("metadata", {})
                    texto = metadata.get("texto", "")
                    documento = metadata.get("documento", "Documento sin nombre")
                    if texto:
                        retrieved_segments.append({
                            "texto": texto,
                            "documento": documento,
                            "score": score  # guardamos el score
                        })

            retrieved_context = "\n---\n".join([f"[{seg['documento']}]: {seg['texto']}" for seg in retrieved_segments])
            conversation_history = st.session_state.conversation[:-1] if len(st.session_state.conversation) > 1 else []
            formatted_history = format_conversation_history(conversation_history)

            full_prompt = (
                f"{custom_prompt}\n\n"
                f"📜 **Historial de la conversación:**\n{formatted_history}\n"
                f"📚 **Fragmentos de documentación relevantes para responder a la consulta:**\n{retrieved_context}\n\n"
                f"👤 **Consulta actual del usuario:** {user_message}"
            )

            response = model.generate_content(full_prompt)
            response_text = response.candidates[0].content.parts[0].text

            # Guardar respuesta y fragmentos
            st.session_state.conversation.append({
                "role": "Asistente",
                "content": response_text,
                "fragments": retrieved_segments
            })

            with st.chat_message("asistente"):
                st.markdown(response_text)
                with st.expander("📚 Mostrar fragmentos recuperados"):
                    display_fragments(retrieved_segments)

# ---------------- Sidebar ----------------
with st.sidebar:
    st.subheader("Sobre esta herramienta")
    st.markdown("""
    Esta herramienta de consulta utiliza Inteligencia Artificial para buscar y recuperar información específica de la documentación técnica de los proyectos.
    
    **Características:**
    - Búsqueda semántica en toda la documentación
    - Respuestas basadas en documentos oficiales
    - Visualización de las fuentes originales
    
    **Instrucciones:**
    1. Escriba su consulta técnica en el cuadro de texto
    2. Revise la respuesta generada
    3. Consulte los fragmentos recuperados debajo de cada respuesta
    """)
