# --------------------------------------------------
# Asistente Técnico Inteligente para Construcción
# Versión: UI Premium (abril 2025)
# --------------------------------------------------
# 👉 La lógica de negocio RAG se mantiene intacta; solo se han aplicado
#    mejoras sustanciales en diseño y experiencia de usuario.
# --------------------------------------------------

import streamlit as st
import google.generativeai as genai
from pinecone import Pinecone
from datetime import datetime
import time

# ---------------- Configuración -----------------
GENAI_API_KEY = st.secrets["general"]["genai_api_key"]
PINECONE_API_KEY = st.secrets["general"]["pinecone_api_key"]
INDEX_NAME = "documentacion-edificacion"
MIN_SIMILARITY_SCORE = 0.50  # 50 %

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
    initial_sidebar_state="expanded",
    menu_items={
        "Report a bug": "mailto:soporte@tuempresa.com",
        "About": "### Asistente Técnico\nHerramienta IA para consulta de documentación de edificación."
    },
)

# Configuración de colores y UI
PRIMARY_COLOR = "#2E5EAA"
SECONDARY_COLOR = "#FFA630"
BACKGROUND_COLOR = "#FFFFFF"
ACCENT_COLOR = "#2E5EAA"
TEXT_COLOR = "#333333"
BORDER_RADIUS = "10px"

st.markdown(
    f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=DM+Sans:wght@400;500;700&display=swap');
        
        html, body, [class*="css"] {{
            font-family: 'Inter', sans-serif;
            scroll-behavior: smooth;
        }}
        
        .block-container {{
            padding-top: 0;
            padding-bottom: 2rem;
            max-width: 1200px;
        }}
        
        /* Encabezado */
        .app-header {{
            background: linear-gradient(90deg, {PRIMARY_COLOR} 0%, #1E3A6D 100%);
            padding: 1.8rem 2rem;
            border-radius: 0 0 16px 16px;
            color: #fff;
            margin-bottom: 2rem;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            position: relative;
            overflow: hidden;
        }}
        
        .app-header h1 {{
            font-family: 'DM Sans', sans-serif;
            font-weight: 700;
            font-size: 2rem;
            margin: 0;
            position: relative;
            z-index: 10;
        }}
        
        .app-header p {{
            margin: 0.5rem 0 0;
            font-size: 1rem;
            opacity: 0.9;
            position: relative;
            z-index: 10;
        }}
        
        /* Fragmentos */
        .fragment-container {{
            border-left: 4px solid {ACCENT_COLOR};
            background-color: #f8faff;
            padding: 1rem 1.2rem;
            border-radius: {BORDER_RADIUS};
            margin-bottom: 1rem;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            transition: all 0.2s ease;
        }}
        
        .fragment-container:hover {{
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
            transform: translateY(-2px);
        }}
        
        .fragment-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.5rem;
        }}
        
        .fragment-source {{
            font-weight: 600;
            color: {PRIMARY_COLOR};
            font-size: 0.9rem;
            display: flex;
            align-items: center;
            gap: 5px;
        }}
        
        .fragment-source-icon {{
            display: inline-block;
            width: 16px;
            height: 16px;
            background-color: {PRIMARY_COLOR};
            -webkit-mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E%3Cpath d='M2 3.5A1.5 1.5 0 0 1 3.5 2h9A1.5 1.5 0 0 1 14 3.5v9a1.5 1.5 0 0 1-1.5 1.5h-9A1.5 1.5 0 0 1 2 12.5v-9z'/%3E%3C/svg%3E") no-repeat center center / contain;
            mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E%3Cpath d='M2 3.5A1.5 1.5 0 0 1 3.5 2h9A1.5 1.5 0 0 1 14 3.5v9a1.5 1.5 0 0 1-1.5 1.5h-9A1.5 1.5 0 0 1 2 12.5v-9z'/%3E%3C/svg%3E") no-repeat center center / contain;
        }}
        
        .fragment-score {{
            font-size: 0.8rem;
            color: #555;
        }}
        
        .fragment-content {{
            font-size: 0.92rem;
            white-space: pre-wrap;
            line-height: 1.5;
        }}
        
        /* Chat message tweaks */
        .stChatMessage {{
            border-radius: {BORDER_RADIUS};
            padding: 1rem !important;
            margin-bottom: 1.2rem !important;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            border: 1px solid #eef2f8;
        }}
        
        .stChatMessageContent {{
            padding: 0 !important;
        }}
        
        div[data-testid="stChatMessageContent"] p {{
            margin-bottom: 0.8rem;
            line-height: 1.6;
        }}
        
        /* User chat message */
        .stChatMessage[data-testid="user-message"] {{
            background-color: #f0f7ff !important;
        }}
        
        /* Assistant chat message */
        .stChatMessage[data-testid="assistant-message"] {{
            background-color: #ffffff !important;
        }}
        
        /* Entrada de chat */
        .stChatInputContainer {{
            padding: 0.8rem !important;
            border-radius: {BORDER_RADIUS} !important;
            border: 1px solid #e1e4e8 !important;
            background: white !important;
            box-shadow: 0 2px 6px rgba(0,0,0,0.05);
        }}
        
        


        
        [data-testid="stSidebarUserContent"] {{
            padding-top: 2rem;
        }}
        
        .stSidebar [data-testid="stMarkdownContainer"] h1, 
        .stSidebar [data-testid="stMarkdownContainer"] h2, 
        .stSidebar [data-testid="stMarkdownContainer"] h3 {{
            color: {PRIMARY_COLOR};
        }}
        
        /* Expander */
        .streamlit-expanderHeader {{
            font-size: 0.95rem;
            font-weight: 500;
            color: {PRIMARY_COLOR};
            background-color: #f8f9fa;
            border-radius: 6px;
        }}
        
        /* Toast */
        .stToast {{
            background-color: {PRIMARY_COLOR} !important;
            color: white !important;
            font-size: 0.9rem !important;
            border-radius: 8px !important;
        }}
        
        /* Spinner */
        .stSpinner > div > div {{
            border-top-color: {PRIMARY_COLOR} !important;
        }}
        
        /* Botones */
        .stButton button {{
            background-color: {PRIMARY_COLOR};
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 6px;
            font-weight: 500;
            transition: all 0.2s ease;
        }}
        
        .stButton button:hover {{
            background-color: #264b85;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }}
        
        /* Progress bar */
        .stProgress > div > div > div {{
            background-color: {PRIMARY_COLOR} !important;
        }}
        
        /* Footer */
        .app-footer {{
            text-align: center;
            margin-top: 2rem;
            padding-top: 1.5rem;
            border-top: 1px solid #eaeaea;
            color: #666;
            font-size: 0.85rem;
        }}
        
        /* Badge styles */
        .badge {{
            display: inline-block;
            padding: 0.25em 0.6em;
            font-size: 0.75rem;
            font-weight: 600;
            line-height: 1;
            text-align: center;
            white-space: nowrap;
            vertical-align: baseline;
            border-radius: 10rem;
            color: #fff;
        }}
        
        .badge-success {{
            background-color: #28a745;
        }}
        
        .badge-warning {{
            background-color: #ffc107;
            color: #212529;
        }}
        
        .badge-danger {{
            background-color: #dc3545;
        }}
        
        /* Tooltip */
        .tooltip {{
            position: relative;
            display: inline-block;
            cursor: pointer;
        }}
        
        .tooltip .tooltip-text {{
            visibility: hidden;
            width: 200px;
            background-color: #333;
            color: #fff;
            text-align: center;
            border-radius: 6px;
            padding: 10px;
            position: absolute;
            z-index: 1;
            bottom: 125%;
            left: 50%;
            margin-left: -100px;
            opacity: 0;
            transition: opacity 0.3s;
            font-size: 0.8rem;
        }}
        
        .tooltip:hover .tooltip-text {{
            visibility: visible;
            opacity: 0.95;
        }}
        
        /* Separación de elementos */
        .spacer {{
            height: 1.5rem;
        }}
        
        /* Animaciones */
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        .fadein {{
            animation: fadeIn 0.5s ease forwards;
        }}
        
        /* Texto en mensaje de chat */
        .citation-highlight {{
            background-color: #fff8e1;
            padding: 0 3px;
            border-radius: 3px;
            font-weight: 500;
        }}
        
        /* Código en las respuestas */
        code {{
            background-color: #f6f8fa;
            border-radius: 4px;
            padding: 2px 5px;
            font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
            font-size: 0.9em;
            color: #24292e;
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

# ---------------- Estado de sesión -----------------
if "conversation" not in st.session_state:
    st.session_state.conversation = []
    
if "show_welcome" not in st.session_state:
    st.session_state.show_welcome = True

# ---------------- Funciones auxiliares -----------------

def display_fragments(fragments):
    """Renderiza los pasajes recuperados en un contenedor elegante."""
    if not fragments:
        st.info("📚 No se encontraron fragmentos relevantes para esta consulta.")
        return
    
    # Ordenar fragmentos por score (descendente)
    sorted_fragments = sorted(fragments, key=lambda x: x["score"], reverse=True)
    
    for frag in sorted_fragments:
        # Determinar el color del badge según el score
        if frag["score"] >= 0.8:
            badge_class = "badge-success"
            relevance_text = "Alta relevancia"
        elif frag["score"] >= 0.6:
            badge_class = "badge-warning"
            relevance_text = "Relevancia media" 
        else:
            badge_class = "badge-danger"
            relevance_text = "Baja relevancia"
            
        # Formatear el texto para mostrar
        texto_formateado = frag['texto'].replace('\n', '<br>')
        
        st.markdown(
            f"""
            <div class="fragment-container fadein">
                <div class="fragment-header">
                    <div class="fragment-source">
                        📄 {frag['documento']}
                    </div>
                    <div class="fragment-score">
                        <span class="badge {badge_class}">{relevance_text} ({frag['score']:.0%})</span>
                    </div>
                </div>
                <div class="fragment-content">{texto_formateado}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("""
        <style>
        /* Fondo gris oscuro de la sidebar */
        section[data-testid="stSidebar"] > div:first-child {
            background-color: #333333 !important;
        }
        
        /* Texto en blanco para contraste */
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3,
        section[data-testid="stSidebar"] li {
            color: #FFFFFF !important;
        }
        </style>
        """, unsafe_allow_html=True)



def format_conversation_history(history):
    return "\n\n".join(f"{m['role']}: {m['content']}" for m in history)


def display_typing_animation():
    """Muestra una animación de escritura para la respuesta del asistente."""
    with st.empty():
        for i in range(5):
            dots = "." * (i % 4)
            st.write(f"Generando respuesta{dots}")
            time.sleep(0.3)


# ---------------- Encabezado custom -----------------
with st.container():
    st.markdown(
        """
        <div class="app-header">
            <h1>🏗️ Asistente Técnico Inteligente para Construcción</h1>
            <p>Tu consultor experto en normativas, especificaciones técnicas y documentación de edificación</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ---------------- Sidebar -----------------
with st.sidebar:
    st.image("caeys_logo_3.png", use_container_width='auto') # <-- AÑADIDO: Muestra la imagen
    st.header("🏗️ Asistente Técnico")
    st.header("💡 Guía rápida")
    
    st.markdown("""
        <div style="background-color: #f1f7fe; padding: 15px; border-radius: 8px; border-left: 4px solid #2E5EAA;">
            <h4 style="margin-top: 0; color: #2E5EAA;">¿Cómo usar este asistente?</h4>
            <ol style="padding-left: 20px; margin-bottom: 0;">
                <li><strong>Formula tu consulta técnica</strong> en el cuadro de chat inferior</li>
                <li><strong>Revisa la respuesta</strong> que cita fuentes documentales específicas</li>
                <li><strong>Examina los fragmentos</strong> recuperados para más contexto</li>
                <li><strong>Haz preguntas de seguimiento</strong> para aclarar o profundizar</li>
            </ol>
        </div>
    """, unsafe_allow_html=True)
    
    st.subheader("🔍 Ejemplos de consultas")
    
    example_queries = [
        "¿Cuáles son los requisitos mínimos de resistencia al fuego en edificios residenciales?",
        "¿Qué normativa regula la instalación de sistemas de ventilación en sótanos?",
        "Explica las especificaciones para cimentaciones en terrenos arcillosos",
        "¿Cuáles son las dimensiones mínimas para escaleras de evacuación?",
    ]
    
    for query in example_queries:
        if st.button(f"📝 {query}", use_container_width=True, key=f"btn_{hash(query)}"):
            if "conversation" in st.session_state:
                st.session_state.conversation.append({"role": "Usuario", "content": query})
                st.experimental_rerun()

    st.divider()
    
    # Mostrar la versión y copyright
    col1, col2 = st.columns(2)
    with col1:
        st.caption("Versión: Demo Inicial")
    with col2:
        st.caption("{:%d-%m-%Y}".format(datetime.utcnow()))
    
    st.caption("© 2025 Caeys | Todos los derechos reservados")

# ---------------- Mensaje de bienvenida (solo la primera vez) -----------------
if st.session_state.show_welcome:
    st.info("""
    👋 **¡Bienvenido al Asistente Técnico Inteligente!**
    
    Estoy aquí para resolver tus dudas sobre normativas, regulaciones y especificaciones técnicas 
    en el ámbito de la construcción y edificación. Utilizo documentación técnica actualizada 
    como base para mis respuestas.
    
    📝 Puedes comenzar escribiendo tu consulta en el campo de abajo o seleccionar 
    uno de los ejemplos de la barra lateral.
    """)
    st.session_state.show_welcome = False

# ---------------- Mostrar historial -----------------
for msg in st.session_state.conversation:
    role = "assistant" if msg["role"] == "Asistente" else "user"
    
    with st.chat_message(role):
        st.markdown(msg["content"])
        if role == "assistant" and "fragments" in msg:
            with st.expander("📚 Ver fragmentos de documentación recuperados"):
                display_fragments(msg["fragments"])

# ---------------- Entrada del usuario -----------------
user_message = st.chat_input("Escribe tu consulta técnica aquí...")

if user_message:
    # Ocultar el mensaje de bienvenida cuando se inicia la conversación
    st.session_state.show_welcome = False
    
    # Añadir mensaje del usuario al historial
    st.session_state.conversation.append({"role": "Usuario", "content": user_message})
    
    # Mostrar mensaje del usuario
    with st.chat_message("user"):
        st.markdown(user_message)

    # Mostrar el spinner y respuesta
    with st.chat_message("assistant"):
        with st.spinner("🔎 Buscando en la documentación técnica..."):
            # Simular tiempos de procesamiento para mejorar la experiencia de usuario
            progress_text = "Analizando documentación técnica..."
            progress_bar = st.progress(0)
            
            # Simular progreso
            for i in range(101):
                if i < 30:
                    # Primera fase - Procesando consulta
                    progress_text = "Procesando consulta..."
                elif i < 60:
                    # Segunda fase - Buscando documentos relevantes
                    progress_text = "Buscando documentos relevantes..."
                elif i < 90:
                    # Tercera fase - Generando respuesta
                    progress_text = "Generando respuesta técnica..."
                else:
                    # Fase final
                    progress_text = "Finalizando..."
                    
                if i % 10 == 0:
                    progress_bar.progress(i, text=progress_text)
                    time.sleep(0.05)
            
            progress_bar.empty()
            
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
                    f"📜 **Historial de la conversación:**\n{formatted_history}\n"
                    f"📚 **Fragmentos de documentación relevantes:**\n{retrieved_context}\n\n"
                    f"👤 **Consulta actual del usuario:** {user_message}"
                )

                # Mostrar animación de "escribiendo..."
                typing_placeholder = st.empty()
                for i in range(3):
                    dots = "." * (i % 4)
                    typing_placeholder.markdown(f"*Redactando respuesta{dots}*")
                    time.sleep(0.4)
                typing_placeholder.empty()
                
                # Generar respuesta real
                response = model.generate_content(full_prompt)
                response_text = response.candidates[0].content.parts[0].text
                
                # Formatear la respuesta para resaltar las citas
                formatted_response = response_text
                
                # Guardar respuesta y fragmentos
                st.session_state.conversation.append(
                    {
                        "role": "Asistente",
                        "content": response_text,
                        "fragments": retrieved_segments,
                    }
                )
                
                # Mostrar respuesta
                st.markdown(formatted_response)
                
                # Mostrar fragmentos en un expander
                with st.expander("📚 Ver fragmentos de documentación recuperados"):
                    display_fragments(retrieved_segments)
                
                # Preguntar por valoración (opcional)
                feedback_col1, feedback_col2, feedback_col3 = st.columns([1, 1, 3])
                with feedback_col1:
                    st.button("👍 Útil", key=f"useful_{len(st.session_state.conversation)}")
                with feedback_col2:
                    st.button("👎 No útil", key=f"not_useful_{len(st.session_state.conversation)}")
                
                # Notificación de éxito
                st.toast("✅ Respuesta generada con éxito", icon="🤖")

# ---------------- Footer -----------------
st.markdown(
    """
    <div class="app-footer">
        <p>Asistente Técnico Inteligente para Construcción - Desarrollado por Caeys.es</p>
    </div>
    """,
    unsafe_allow_html=True,
)


