import streamlit as st
from google import genai
from google.genai.types import Blob, Part, Content, GenerateContentConfig, Modality
from PIL import Image
from io import BytesIO
import datetime
import os
import mimetypes

# --- Inicialización de Vertex AI ---
client = genai.Client(
    vertexai=True,
    project="acpe-dev-uc-ai",  # Tu proyecto GCP
    location="us-central1"     # Asegúrate de que esta región es correcta
)

# --- Función para leer archivo e imagen ---
def read_image_bytes(path):
    mime, _ = mimetypes.guess_type(path)
    if mime is None:
        mime = "image/png" if path.lower().endswith(".png") else "image/jpeg"
    with open(path, "rb") as f:
        data = f.read()
    return data, mime

# --- Función para mejorar el prompt introducido ---
def improve_prompt(prompt):
    improved_prompt = (
        f"Genera una escena publicitaria de alta gama para **ají Tari**, capturada en un entorno cálido, sofisticado y acogedor. "
        f"El fondo muestra una mesa de madera de tono cálido y natural, con una textura visible que aporta un toque rústico y auténtico. "
        f"La luz suave de una ventana al fondo crea una atmósfera cálida, resaltando el **ají Tari** como el centro de atención. "
        f"La luz es delicada, con sombras suaves que caen perfectamente sobre la botella, dando un aspecto realista y tridimensional. "
        f"La botella de **ají Tari** está posicionada en el centro de la escena, ligeramente inclinada para resaltar su etiqueta vibrante, "
        f"con la tipografía visible y clara. La botella tiene una textura de vidrio pulido, reflejando sutilmente los destellos de luz, "
        f"con detalles visibles en el líquido dorado que sobresale, invitando al espectador a imaginar su sabor. "
        f"A su alrededor, un plato gourmet de **hamburguesas gourmet** perfectamente compuestas se ubica en la mesa. "
        f"Las hamburguesas están cubiertas con ingredientes frescos, como hojas de lechuga crujiente, tomates jugosos y un toque "
        f"de cebolla caramelizada que resalta su frescura. Las texturas de la carne son claramente visibles: jugosa, dorada en los bordes "
        f"y perfectamente cocinada. No debes alterar ninguna característica del producto. La composición se debe ver realista. "
        f"La hamburguesa está acompañada con un toque delicado de **ají Tari**, goteando de manera natural sobre la carne, añadiendo "
        f"un contraste de color rojo vibrante que destaca contra el dorado de la carne. El fondo es sutil, con una superficie de madera "
        f"que refleja la luz suave, aportando una sensación de elegancia sin distraer la atención del producto. Algunos elementos decorativos "
        f"discretos como un par de nueces y una rama de hierbas frescas agregan un toque natural y elegante a la escena. "
        f"La composición está cuidadosamente equilibrada, siguiendo la regla de los tercios, asegurando que el **ají Tari** sea el punto focal, "
        f"pero sin dejar de resaltar la textura y la frescura de los ingredientes acompañantes. Las sombras proyectadas por los ingredientes "
        f"y la botella aportan profundidad a la imagen, haciendo que la escena parezca real, como si se estuviera sirviendo directamente en una mesa. "
        f"La imagen final debe transmitir una sensación de **calidez, frescura y calidad gourmet**, invitando al espectador a disfrutar de un producto "
        f"que no solo es delicioso, sino también visualmente atractivo y realista."
    )
    return improved_prompt

# --- Función para generar imagen con el modelo Gemini (image-2.0-preview) ---
def generate_image(prompt, image_file):
    # Leer imagen de referencia
    image_data, mime_type = read_image_bytes(image_file)

    # Mejorar el prompt introducido
    improved_prompt = improve_prompt(prompt)

    # Construir contenido con el prompt mejorado + imagen de referencia
    contents = Content(
        role="user",
        parts=[
            Part(text=improved_prompt),
            Part(inline_data=Blob(mime_type=mime_type, data=image_data)),
        ]
    )

    # Configurar la generación
    config = GenerateContentConfig(response_modalities=[Modality.TEXT, Modality.IMAGE])

    # Crear carpeta de historial si no existe
    historial_folder = "historial_imagenes"
    os.makedirs(historial_folder, exist_ok=True)

    # Llamar al modelo
    response = client.models.generate_content(
        model="gemini-2.0-flash-preview-image-generation",
        contents=contents,
        config=config
    )

    # Guardar resultado con timestamp
    for part in response.candidates[0].content.parts:
        if part.text:
            print(part.text)
        elif part.inline_data:
            image = Image.open(BytesIO(part.inline_data.data))
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{historial_folder}/imagen_generada_{timestamp}.png"
            image.save(filename)
            print(f"✅ Imagen generada y guardada como '{filename}'")
            return filename

# --- Interfaz en Streamlit con diseño moderno y minimalista ---
def streamlit_interface():
    # Configurando la página de Streamlit
    st.set_page_config(page_title="Generador Publicidad Aji Tari", page_icon="🍴", layout="wide")

    # Colores personalizados basados en Alicorp
    primary_color = "#e62020"

    st.markdown(f"<h1 style='text-align:center; color:{primary_color};'>Generación de Imágenes con Gemini 2.0</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align:center; font-size:18px;'>Genera imágenes publicitarias de alta calidad para **Aji Tari** utilizando inteligencia artificial.</p>",
        unsafe_allow_html=True
    )

    # Caja de texto para el prompt
    prompt = st.text_area("Describe la escena que deseas generar (por ejemplo, la escena para la campaña de Aji Tari):", 
                          "Escena de alta gama para campaña publicitaria de **ají Tari**. Un fondo cálido, una mesa de madera con hamburguesas gourmet, y una botella de **ají Tari**.")
    
    # Cargar imagen de referencia
    image_file = st.file_uploader("Selecciona la imagen de referencia", type=["jpg", "png", "jpeg"])

    # Generar imagen
    if st.button("Generar Imagen", key="generate_button"):
        if image_file:
            # Generar imagen con el prompt y la imagen de referencia
            generated_image = generate_image(prompt, image_file)

            # Mostrar la imagen generada
            st.image(generated_image, caption="Imagen generada", use_column_width=True)
            st.success("¡Imagen generada exitosamente!")
        else:
            st.warning("Por favor, sube una imagen de referencia para generar la imagen.")

# Ejecutar la interfaz de Streamlit
if __name__ == "__main__":
    streamlit_interface()
