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

# ===================== ESTILO DASHBOARD =====================
st.set_page_config(page_title="Interfaces Multimodales", page_icon="🎙", layout="wide")
st.markdown("""
<style>
:root {
    --bg: #0f172a;
    --bg-elevated: #111827;
    --card: #111827;
    --border: rgba(255,255,255,0.06);
    --text: #e2e8f0;
    --muted: #94a3b8;
    --accent: #f43f5e;
    --radius-lg: 20px;
}
html, body, .stApp {
    background: #0f172a;
}
.block-container {
    padding-top: 1.2rem;
    padding-bottom: 0rem;
    max-width: 1100px;
}
h1, h2, h3 {
    color: var(--text);
}
.dashboard-title {
    font-size: 2.2rem;
    font-weight: 700;
    color: #e2e8f0;
    margin-bottom: 1rem;
}
.rooms-row {
    display: flex;
    gap: 1.5rem;
    width: 100%;
}
.room-card {
    flex: 1;
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 1.4rem 1.4rem 1rem 1.4rem;
    display: flex;
    flex-direction: column;
    gap: .5rem;
    min-height: 170px;
}
.room-header {
    display: flex;
    align-items: center;
    gap: .7rem;
}
.room-title {
    font-size: 1.6rem;
    font-weight: 700;
    color: #e2e8f0;
}
.badge-light {
    width: 34px;
    height: 34px;
    border-radius: 999px;
    box-shadow: inset 0 -4px 6px rgba(0,0,0,0.25);
}
.badge-sala { background: radial-gradient(circle, #facc15 0%, #eab308 50%, #ca8a04 100%); }
.badge-cocina { background: radial-gradient(circle, #e2e8f0 0%, #cbd5e1 60%, #94a3b8 100%); }
.badge-hab { background: radial-gradient(circle, #2563eb 0%, #1d4ed8 70%, #1e3a8a 100%); }

.room-desc {
    color: var(--muted);
    font-size: .9rem;
}
.toggle-row {
    margin-top: 1.2rem;
    display: flex;
    align-items: center;
    gap: .6rem;
}
.fake-toggle {
    width: 48px;
    height: 24px;
    background: #0f172a;
    border-radius: 9999px;
    border: 1px solid rgba(255,255,255,0.08);
    position: relative;
}
.fake-toggle::after {
    content: "";
    position: absolute;
    top: 2px;
    left: 2px;
    width: 20px;
    height: 20px;
    background: #e2e8f0;
    border-radius: 999px;
    box-shadow: 0 4px 8px rgba(0,0,0,.3);
}
.room-state {
    color: #e2e8f0;
    font-weight: 500;
}
.divider {
    width: 100%;
    height: 1px;
    background: rgba(255,255,255,0.03);
    margin: 1.5rem 0 1.1rem 0;
}
.voice-btn .bk.bk-btn {
    width: 100% !important;
    background: #f43f5e !important;
    border: none !important;
    color: white !important;
    font-weight: 600 !important;
    border-radius: 16px !important;
    padding: 0.7rem 1.2rem !important;
    font-size: 1rem !important;
    box-shadow: 0 8px 20px rgba(244,63,94,0.45);
}
.voice-btn .bk.bk-btn:hover {
    filter: brightness(1.05);
}
.scenes-title {
    display: flex;
    align-items: center;
    gap: .5rem;
    font-size: 1.7rem;
    font-weight: 700;
    color: #e2e8f0;
}
.scenes-row {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
}
.scene-btn {
    flex: 1;
    background: #0f172a;
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 16px;
    padding: .7rem 1rem;
    color: #e2e8f0;
    font-weight: 500;
    display: flex;
    gap: .5rem;
    align-items: center;
    justify-content: center;
    min-width: 140px;
}
.footer {
    margin-top: 1.5rem;
    color: #64748b;
    font-size: 0.85rem;
    text-align: left;
}
.hidden-img { display: none; }
@media (max-width: 900px) {
    .rooms-row { flex-direction: column; }
    .scenes-row { flex-direction: column; }
}
</style>
""", unsafe_allow_html=True)
# ========================================================

st.markdown("<div class='dashboard-title'>Habitaciones</div>", unsafe_allow_html=True)

# ================== FILA DE HABITACIONES ==================
st.markdown("<div class='rooms-row'>", unsafe_allow_html=True)

# Sala
st.markdown("""
<div class='room-card'>
    <div class='room-header'>
        <div class='badge-light badge-sala'></div>
        <div class='room-title'>Sala</div>
    </div>
    <div class='room-desc'>Encender o apagar la luz principal</div>
    <div class='toggle-row'>
        <div class='fake-toggle'></div>
        <div class='room-state'>Encendida</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Cocina
st.markdown("""
<div class='room-card'>
    <div class='room-header'>
        <div class='badge-light badge-cocina'></div>
        <div class='room-title'>Cocina</div>
    </div>
    <div class='room-desc'>Control de la luz de cocina</div>
    <div class='toggle-row'>
        <div class='fake-toggle'></div>
        <div class='room-state'>Encendida</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Habitación
st.markdown("""
<div class='room-card'>
    <div class='room-header'>
        <div class='badge-light badge-hab'></div>
        <div class='room-title'>Habitación</div>
    </div>
    <div class='room-desc'>Control de la luz de habitación</div>
    <div class='toggle-row'>
        <div class='fake-toggle'></div>
        <div class='room-state'>Encendida</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# ====== separador ======
st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# Imagen original (la dejo pero oculta para no romper el layout)
image = Image.open('voice_ctrl.jpg')
st.markdown("<div class='hidden-img'>", unsafe_allow_html=True)
st.image(image, width=200)
st.markdown("</div>", unsafe_allow_html=True)

# ============== Botón Bokeh (maquillado como barra roja) ==============
st.markdown("<div class='voice-btn'>", unsafe_allow_html=True)
stt_button = Button(label="🚀 Enviar estado", width=400)

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

# ====== Escenas rápidas ======
st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
st.markdown("<div class='scenes-title'>🕹 Escenas rápidas</div>", unsafe_allow_html=True)
st.markdown("<div class='scenes-row'>", unsafe_allow_html=True)
st.markdown("<div class='scene-btn'>🌙 Noche</div>", unsafe_allow_html=True)
st.markdown("<div class='scene-btn'>🧠 Trabajo</div>", unsafe_allow_html=True)
st.markdown("<div class='scene-btn'>🌞 Todo ON</div>", unsafe_allow_html=True)
st.markdown("<div class='scene-btn'>🌒 Todo OFF</div>", unsafe_allow_html=True)
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

# estado actual simulado (como en tu imagen)
st.markdown(
    "<p class='footer'>Estado actual (MQTT): {'sala': False, 'cocina': False, 'habitacion': False}</p>",
    unsafe_allow_html=True
)
st.markdown("<p class='footer'>Camilo Seguro - EAFIT - 2025</p>", unsafe_allow_html=True)
