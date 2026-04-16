import os
import streamlit as st
import base64
from openai import OpenAI
from PIL import Image
import numpy as np
from streamlit_drawable_canvas import st_canvas
import io

# ---------------- CONFIG ----------------
st.set_page_config(page_title="FlagMaster AI", layout="wide")

# Fondo bonito sin imágenes
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #232526, #414345);
    color: white;
}
h1 {
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# ---------------- TITULO ----------------
st.title("🌍🎨 FlagMaster AI")
st.markdown("Dibuja una **bandera** y la IA intentará reconocer el país, su comida típica y su idioma.")

# ---------------- SIDEBAR ----------------
st.sidebar.header("Opciones de dibujo")

stroke_width = st.sidebar.slider("Grosor del lápiz", 1, 25, 5)

color = st.sidebar.selectbox(
    "Colores (para banderas)",
    ["Rojo", "Azul", "Amarillo", "Verde", "Blanco", "Negro"]
)

colores = {
    "Rojo": "#FF0000",
    "Azul": "#0000FF",
    "Amarillo": "#FFD700",
    "Verde": "#00FF00",
    "Blanco": "#FFFFFF",
    "Negro": "#000000"
}

stroke_color = colores[color]

fondo = st.sidebar.selectbox("Fondo", ["Blanco", "Negro"])
bg_color = "#FFFFFF" if fondo == "Blanco" else "#000000"

# ---------------- CANVAS ----------------
canvas_result = st_canvas(
    fill_color="rgba(255,255,255,0.1)",
    stroke_width=stroke_width,
    stroke_color=stroke_color,
    background_color=bg_color,
    height=500,
    width=900,
    drawing_mode="freedraw",
    key="canvas",
)

# ---------------- API ----------------
api_key = st.text_input("Ingresa tu API Key", type="password")

if not api_key:
    st.warning("Ingresa tu API Key para activar el reconocimiento")
    st.stop()

try:
    client = OpenAI(api_key=api_key)
except Exception as e:
    st.error("Error inicializando cliente OpenAI")
    st.stop()

# ---------------- FUNCION ----------------
def encode_image(image):
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode()

# ---------------- BOTON ----------------
if st.button("🔍 Analizar dibujo"):

    if canvas_result.image_data is None:
        st.warning("Primero dibuja una bandera")
    else:
        with st.spinner("Analizando..."):

            try:
                # Convertir imagen correctamente
                img_array = np.array(canvas_result.image_data)

                if img_array.shape[2] == 4:
                    img_array = img_array[:, :, :3]

                image = Image.fromarray(img_array.astype('uint8'), 'RGB')

                base64_image = encode_image(image)

                prompt = """
                Esta imagen es un dibujo de una bandera.

                Identifica la bandera y responde EXACTAMENTE en este formato:

                País:
                Comida típica:
                Idioma:

                No agregues nada más.
                """

                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/png;base64,{base64_image}"
                                    },
                                },
                            ],
                        }
                    ],
                    max_tokens=200,
                )

                resultado = response.choices[0].message.content

                st.success("Resultado:")
                st.write(resultado)

            except Exception as e:
                st.error("❌ Error de conexión con la API")
                st.write("Detalle:", e)
