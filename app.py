import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import time
import paho.mqtt.client as paho
import json
from gtts import gTTS
from googletrans import Translator

def on_publish(client,userdata,result):
    print("el dato ha sido publicado \n")
    pass

def on_message(client, userdata, message):
    global message_received
    time.sleep(2)
    message_received = str(message.payload.decode("utf-8"))
    st.write(message_received)

broker="broker.mqttdashboard.com"
port=1883
client1= paho.Client("LucesCSC")
client1.on_message = on_message

# ===================== ESTILO =====================
st.set_page_config(page_title="Interfaces Multimodales", page_icon="🎙", layout="centered")
st.markdown("""
<style>
body {
    background: radial-gradient(circle at top, #0f172a 0%, #020617 100%);
}
.main > div {
    padding-top: 0rem;
}
.container {
    max-width: 760px;
    margin: 0 auto;
}
.glass-card {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 20px;
    padding: 2rem;
    box-shadow: 0 0 25px rgba(0,0,0,0.3);
    backdrop-filter: blur(12px);
    text-align: center;
}
h1 {
    color: #f8fafc !important;
    text-align: center;
    font-weight: 700;
    letter-spacing: 1px;
    margin-bottom: 0.2rem;
}
h3, h2, h4 {
    color: #cbd5e1 !important;
    text-align: center;
}
p, .stMarkdown {
    color: #94a3b8 !important;
    font-size: 0.95rem;
}
img {
    display: block;
    margin: 0 auto;
    border-radius: 14px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.4);
}
.voice-btn .bk.bk-btn {
    background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%) !important;
    border: none !important;
    color: white !important;
    font-weight: 600 !important;
    border-radius: 16px !important;
    padding: 0.6rem 2rem !important;
    font-size: 1rem !important;
    box-shadow: 0 4px 14px rgba(124, 58, 237, 0.3);
    transition: all 0.2s ease;
}
.voice-btn .bk.bk-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 18px rgba(124, 58, 237, 0.5);
}
.footer {
    margin-top: 1.5rem;
    color: #64748b;
    font-size: 0.85rem;
    text-align: center;
}
code {
    background: rgba(15,23,42,0.3);
    padding: 3px 7px;
    border-radius: 6px;
    font-size: 0.8rem;
    color: #a5b4fc;
}
</style>
""", unsafe_allow_html=True)
# ========================================================

st.markdown("<div class='container'>", unsafe_allow_html=True)
st.title("INTERFACES MULTIMODALES")
st.subheader("CONTROL POR VOZ")

image = Image.open('voice_ctrl.jpg')
st.image(image, width=200)

st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
st.markdown("### 🎙 Pulsa el botón y habla")
st.markdown("Convierte tu voz en texto y publícalo en MQTT → <code>voice_ctrlCSC</code>", unsafe_allow_html=True)

# ============== Botón Bokeh ==============
st.markdown("<div class='voice-btn'>", unsafe_allow_html=True)
stt_button = Button(label="🎧 Iniciar reconocimiento", width=240)

stt_button.js_on_event("button_click", CustomJS(code="""
    var recognition = new webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;

    recognition.onresult = function (e) {
        var value = "";
        for (var i = e.resultIndex; i < e.results.length; ++i) {
            if (e.results[i].isFinal) {
                value += e.results[i][0].transcript;
            }
        }
        if (value != "") {
            document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
        }
    }
    recognition.start();
"""))

result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0)
st.markdown("</div>", unsafe_allow_html=True)

# ============== Lógica MQTT (sin tocar) ==============
if result:
    if "GET_TEXT" in result:
        st.write(result.get("GET_TEXT"))
        client1.on_publish = on_publish
        client1.connect(broker, port)
        message = json.dumps({"Act1": result.get("GET_TEXT").strip()})
        ret = client1.publish("voice_ctrlCSC", message)

    try:
        os.mkdir("temp")
    except:
        pass

st.markdown("</div>", unsafe_allow_html=True)  # glass-card
st.markdown("<p class='footer'>Camilo Seguro-Eafit-2025</p>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)  # container
