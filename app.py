# streamlit_app.py
import streamlit as st
from google import genai
from google.genai.types import TextPrompt

# Configuración del modelo
MODEL_NAME = "image-preview-2.0"  # Modelo Image 2 Preview

# Inicializar cliente de Gemini
client = genai.Client()

# Configuración de la página
st.set_page_config(
    page_title="Generador de Imágenes - Alicorp",
    page_icon="🌶️",
    layout="centered",
)

# --- Estilo personalizado ---
st.markdown(
    """
    <style>
    .main {
        background-color: #ffffff;
    }
    .stButton>button {
        background-color: #e62020;
        color: white;
        font-weight: bold;
    }
    .stTextArea>div>textarea {
        border: 2px solid #e62020;
        border-radius: 5px;
        padding: 5px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Título ---
st.title("Generador de Imágenes con IA - Alicorp")
st.markdown(
    "Genera imágenes de alta calidad para productos **Alicorp**. "
    "Introduce la descripción de la escena y el modelo generará la imagen."
)

# --- Input del usuario ---
prompt_input = st.text_area(
    "Describe la escena que deseas generar",
    value=(
        "Escena de alta gama para campaña publicitaria de ají Tari, "
        "capturada en un entorno cálido, sofisticado y acogedor. "
        "El fondo muestra una mesa de madera de tono cálido y natural..."
    ),
    height=200
)

# Botón para generar imagen
if st.button("Generar Imagen"):
    if prompt_input.strip() == "":
        st.error("Por favor ingresa un prompt válido")
    else:
        with st.spinner("Generando imagen, por favor espera..."):
            try:
                # Construir prompt
                prompt = TextPrompt(text=prompt_input)

                # Llamado al modelo
                response = client.images.generate(
                    model=MODEL_NAME,
                    prompt=prompt,
                    size="1024x1024"
                )

                # Mostrar la imagen
                img_url = response.data[0].url
                st.image(img_url, caption="Imagen generada por IA", use_column_width=True)

            except Exception as e:
                st.error(f"Ocurrió un error generando la imagen: {e}")