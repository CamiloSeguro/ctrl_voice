# app.py — Control por Voz (Streamlit + Bokeh + MQTT + TTS)
import os
import time
import json
import base64
import streamlit as st
from PIL import Image
from bokeh.models import Button, CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
import paho.mqtt.client as paho
from gtts import gTTS
from googletrans import Translator

# ───────────────────────────────────────────────────────────────
# CONFIGURACIÓN
# ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="Control por Voz", page_icon="🎙️", layout="centered")

st.title("🎙️ INTERFACES MULTIMODALES")
st.subheader("Control por Voz con MQTT + TTS")

# Imagen de encabezado
try:
    image = Image.open("voice_ctrl.jpg")
    st.image(image, width=240)
except Exception:
    st.warning("No se encontró 'voice_ctrl.jpg'. Puedes agregar una imagen de portada.")

# ───────────────────────────────────────────────────────────────
# CONFIG MQTT
# ───────────────────────────────────────────────────────────────
BROKER = "broker.mqttdashboard.com"
PORT = 1883
TOPIC = "voice_ctrl"
CLIENT_ID = f"voice-client-{int(time.time())}"

def on_publish(client, userdata, result):
    print("📤 Mensaje publicado correctamente.")

def on_message(client, userdata, message):
    payload = message.payload.decode("utf-8")
    st.toast(f"📩 Mensaje recibido: {payload}")

# Inicialización del cliente MQTT
client = paho.Client(CLIENT_ID)
client.on_publish = on_publish
client.on_message = on_message

# ───────────────────────────────────────────────────────────────
# CONFIG TRANSLATOR Y TTS
# ───────────────────────────────────────────────────────────────
translator = Translator()

def speak_text(text: str, lang: str = "es"):
    """Convierte texto a voz y reproduce directamente en Streamlit."""
    tts = gTTS(text=text, lang=lang)
    tts.save("temp_voice.mp3")
    with open("temp_voice.mp3", "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
        md = f"""
        <audio autoplay controls>
        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
        """
        st.markdown(md, unsafe_allow_html=True)

# ───────────────────────────────────────────────────────────────
# UI – RECONOCIMIENTO DE VOZ
# ───────────────────────────────────────────────────────────────
st.markdown("### 🎤 Presiona el botón y habla")

stt_button = Button(label="🎙️ Iniciar reconocimiento de voz", width=300, button_type="success")
stt_button.js_on_event("button_click", CustomJS(code="""
    var recognition = new webkitSpeechRecognition();
    recognition.lang = 'es-ES';
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onresult = function (e) {
        var text = "";
        for (var i = e.resultIndex; i < e.results.length; ++i) {
            if (e.results[i].isFinal) {
                text += e.results[i][0].transcript;
            }
        }
        if (text) {
            document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: text}));
        }
    };
    recognition.start();
"""))

result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    debounce_time=0,
    override_height=80,
)

# ───────────────────────────────────────────────────────────────
# PROCESAMIENTO DE VOZ → MQTT → RESPUESTA
# ───────────────────────────────────────────────────────────────
if result and "GET_TEXT" in result:
    user_text = result.get("GET_TEXT").strip().lower()
    st.success(f"🗣️ Has dicho: **{user_text}**")

    # Enviar comando por MQTT
    try:
        client.connect(BROKER, PORT)
        message = json.dumps({"command": user_text})
        client.publish(TOPIC, message)
        st.toast(f"Comando enviado al broker MQTT ✅\nTópico: `{TOPIC}`", icon="📡")
    except Exception as e:
        st.error(f"Error al conectar con el broker MQTT: {e}")

    # Detectar idioma y traducir al español si no lo está
    try:
        detected_lang = translator.detect(user_text).lang
        translated_text = (
            translator.translate(user_text, src=detected_lang, dest="es").text
            if detected_lang != "es" else user_text
        )
    except Exception:
        translated_text = user_text

    # Generar respuesta hablada
    st.markdown("### 🔊 Respuesta hablada")
    speak_text(f"Comando recibido: {translated_text}", lang="es")

# ───────────────────────────────────────────────────────────────
# FOOTER
# ───────────────────────────────────────────────────────────────
st.markdown("---")
st.caption("Desarrollado por Camilo Seguro · Streamlit + MQTT + Bokeh + gTTS + Google Translate")
