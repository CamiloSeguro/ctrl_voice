import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import time
import paho.mqtt.client as paho
import json

# ---------- MQTT callbacks ----------
def on_publish(client, userdata, result):
    print("el dato ha sido publicado \n")
    pass

def on_message(client, userdata, message):
    global message_received
    time.sleep(2)
    message_received = str(message.payload.decode("utf-8"))
    st.write(message_received)

# ---------- MQTT setup ----------
broker = "broker.mqttdashboard.com"
port = 1883
client1 = paho.Client("LucesCSC")
client1.on_message = on_message

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="Control por voz", page_icon="🎙", layout="centered")

# ---------- GLOBAL STYLES ----------
st.markdown("""
<style>
body {
    background: radial-gradient(circle at top, #0f172a 0%, #020617 45%, #020617 100%);
}
.main > div {
    padding-top: 0rem;
}
.app-container {
    max-width: 680px;
    margin: 0 auto;
}
.card {
    background: rgba(2,6,23,0.35);
    border: 1px solid rgba(148,163,184,.18);
    border-radius: 18px;
    padding: 1.8rem 1.5rem 1.5rem 1.5rem;
    backdrop-filter: blur(10px);
}
h1, h2, h3, h4, h5, h6, p {
    color: #e2e8f0 !important;
}
.small-hint {
    font-size: 0.8rem;
    color: rgba(226,232,240,0.45);
}
.bokeh button, .bk.bk-btn {
    background: linear-gradient(135deg, #1d4ed8 0%, #6366f1 100%) !important;
    border: none !important;
    color: white !important;
    font-weight: 600 !important;
    border-radius: 14px !important;
    padding: 0.35rem 1.5rem !important;
}
.button-wrapper {
    display: flex;
    justify-content: center;
    margin-top: 1rem;
    margin-bottom: .5rem;
}
</style>
""", unsafe_allow_html=True)

# ---------- HEADER ----------
st.markdown("<div class='app-container'>", unsafe_allow_html=True)
st.markdown("<h1 style='text-align:center; margin-bottom:0.2rem;'>INTERFACES MULTIMODALES</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; margin-bottom:1.2rem; color:#94a3b8;'>CONTROL POR VOZ → MQTT</p>", unsafe_allow_html=True)

# ---------- IMAGE + CARD ----------
image = Image.open('voice_ctrl.jpg')

col1, col2, col3 = st.columns([1,2,1])
with col2:
    st.image(image, width=190)

st.markdown("<div class='card'>", unsafe_allow_html=True)
st.markdown("### 🎙 Toca el botón y habla")
st.markdown(
    "<p class='small-hint'>El audio se convierte en texto y se envía al tópico MQTT <code>voice_ctrlCSC</code>.</p>",
    unsafe_allow_html=True
)

# ---------- BOKEH VOICE BUTTON ----------
stt_button = Button(label="🎤 Iniciar reconocimiento", width=240)

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

# centramos el botón
st.markdown("<div class='button-wrapper'>", unsafe_allow_html=True)
result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0
)
st.markdown("</div>", unsafe_allow_html=True)

# ---------- RESULTADOS ----------
if result:
    if "GET_TEXT" in result:
        texto = result.get("GET_TEXT").strip()
        st.markdown("#### Texto reconocido")
        st.code(texto)

        # publicar en MQTT
        client1.on_publish = on_publish
        client1.connect(broker, port)
        message = json.dumps({"Act1": texto})
        ret = client1.publish("voice_ctrlCSC", message)

    # crear carpeta temp si no existe
    try:
        os.mkdir("temp")
    except:
        pass

st.markdown("</div>", unsafe_allow_html=True)  # card
st.markdown("</div>", unsafe_allow_html=True)  # app-container
