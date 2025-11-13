import paho.mqtt.client as paho
import time
import streamlit as st
import json
import platform

# ===================== MQTT LÓGICA (igual que antes) =====================
st.set_page_config(page_title="Cabina Domótica – Botones", page_icon="🛰️", layout="centered")

values = 0.0
act1 = "OFF"

def on_publish(client, userdata, result):
    print("el dato ha sido publicado \n")
    pass

def on_message(client, userdata, message):
    global message_received
    time.sleep(2)
    message_received = str(message.payload.decode("utf-8"))
    st.write(message_received)

broker = "broker.mqttdashboard.com"
port = 1883
client1 = paho.Client("LucesCSC")
client1.on_message = on_message

# ===================== ESTILO CÓSMICO =====================
st.markdown("""
<style>
/* Fondo similar al de la cabina de voz */
html, body, [data-testid="stAppViewContainer"] {
  background:
    radial-gradient(1200px 700px at 15% 10%, #1b2440 0%, transparent 60%),
    radial-gradient(900px 500px at 85% 20%, #211b43 0%, transparent 60%),
    linear-gradient(180deg, #020617 0%, #020617 100%) !important;
}

[data-testid="stHeader"], [data-testid="stToolbar"] {
  background: transparent !important;
  box-shadow: none !important;
}

/* Layout general */
.main > div { padding-top: 0rem; }
.container-botones { max-width: 780px; margin: 0 auto; }

/* Tarjetas glass */
.glass-card {
  background: rgba(15,23,42,.88);
  border-radius: 22px;
  padding: 1.6rem 1.8rem;
  border: 1px solid rgba(148,163,253,.35);
  box-shadow:
    0 24px 60px rgba(15,23,42,.95),
    0 0 0 1px rgba(148,163,253,.18) inset;
  backdrop-filter: blur(14px);
}

/* Hero/encabezado */
.hero-mini {
  text-align:center;
  margin-top: 1.4rem;
  margin-bottom: 1.2rem;
}
.hero-mini h1 {
  font-size: 1.4rem;
  letter-spacing: .12em;
  text-transform: uppercase;
  margin-bottom: .3rem;
  color: #e5e7eb;
}
.hero-mini h1 span {
  font-size: 1.1rem;
}
.hero-mini p {
  color: #9ca3af;
  font-size: 0.95rem;
}

/* Badge versión Python */
.badge-ver {
  display:inline-flex;
  align-items:center;
  gap:6px;
  padding:4px 10px;
  border-radius:999px;
  border:1px solid rgba(148,163,253,.5);
  background: rgba(15,23,42,.9);
  color:#c7d2fe;
  font-size:0.78rem;
  margin-bottom: 0.4rem;
}

/* Títulos internos */
h3 {
  color:#e5e7eb !important;
  text-align:left;
  margin-bottom: .8rem;
}

/* Fila de botones ON/OFF */
.btn-row {
  display:flex;
  gap:1rem;
  flex-wrap:wrap;
  justify-content:center;
  margin-bottom: 1.1rem;
}

/* Estilo base de TODOS los botones de Streamlit en esta página */
.stButton > button {
  border-radius: 999px;
  border: none;
  padding: 0.6rem 1.5rem;
  font-weight: 700;
  font-size: 0.96rem;
  cursor: pointer;
  transition: transform .12s ease, box-shadow .12s ease, filter .12s ease;
}

/* ON = primario cósmico */
.btn-on .stButton > button {
  background: radial-gradient(130% 130% at 20% 0%, #22c55e 0%, #16a34a 40%, #065f46 100%);
  color:white;
  box-shadow:
    0 14px 32px rgba(22,163,74,.55),
    0 0 0 1px rgba(187,247,208,.45) inset;
}

/* OFF = botón de alerta suave */
.btn-off .stButton > button {
  background: radial-gradient(130% 130% at 20% 0%, #f97373 0%, #ef4444 45%, #7f1d1d 100%);
  color:#fef2f2;
  box-shadow:
    0 14px 32px rgba(248,113,113,.55),
    0 0 0 1px rgba(254,226,226,.4) inset;
}

/* Botón enviar analógico = morado/azul */
.btn-analog .stButton > button {
  background: radial-gradient(130% 130% at 20% 0%, #6366f1 0%, #7c3aed 45%, #1e293b 100%);
  color:#e5e7eb;
  box-shadow:
    0 14px 32px rgba(129,140,248,.55),
    0 0 0 1px rgba(191,219,254,.4) inset;
}

/* Hover efecto */
.stButton > button:hover {
  transform: translateY(-1px) scale(1.01);
  filter: brightness(1.05);
}

/* Slider card */
.slider-card {
  margin-top: 1.1rem;
  padding: 1rem 1rem 0.4rem;
  border-radius: 18px;
  border: 1px solid rgba(148,163,253,.35);
  background: radial-gradient(circle at 0 0, rgba(129,140,248,.35), transparent 55%),
              rgba(15,23,42,.9);
}
.slider-card label {
  color:#e5e7eb;
  font-weight:600;
}

/* Texto general */
p, span, label {
  color:#cbd5f5;
}
</style>
""", unsafe_allow_html=True)

# ===================== UI =====================

st.markdown("<div class='container-botones'>", unsafe_allow_html=True)

# Hero
st.markdown(
    f"""
<div class="hero-mini">
  <div class="badge-ver">⚙️ Python {platform.python_version()}</div>
  <h1>MQTT CONTROL <span>🛰️</span></h1>
  <p>Panel de botones para controlar tu constelación domótica vía <b>MQTT</b>.</p>
</div>
""",
    unsafe_allow_html=True,
)

# Tarjeta principal
st.markdown("<div class='glass-card'>", unsafe_allow_html=True)

st.markdown("### 🌗 Encendido / apagado")

# Fila de botones ON / OFF
st.markdown("<div class='btn-row'>", unsafe_allow_html=True)

col_on, col_off = st.columns(2)

with col_on:
    st.markdown("<div class='btn-on'>", unsafe_allow_html=True)
    if st.button("ON", key="btn_on"):
        act1 = "ON"
        client1 = paho.Client("LucesCSC")
        client1.on_publish = on_publish
        client1.connect(broker, port)
        message = json.dumps({"Act1": act1})
        ret = client1.publish("voice_ctrlCSC", message)
    st.markdown("</div>", unsafe_allow_html=True)

with col_off:
    st.markdown("<div class='btn-off'>", unsafe_allow_html=True)
    if st.button("OFF", key="btn_off"):
        act1 = "OFF"
        client1 = paho.Client("LucesCSC")
        client1.on_publish = on_publish
        client1.connect(broker, port)
        message = json.dumps({"Act1": act1})
        ret = client1.publish("voice_ctrlCSC", message)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)  # cierre btn-row

# Slider + botón analógico
st.markdown("### 🌌 Valor analógico", unsafe_allow_html=True)
with st.container():
    st.markdown("<div class='slider-card'>", unsafe_allow_html=True)
    values = st.slider("Selecciona el rango de valores", 0.0, 100.0, value=values)
    st.write("Values:", values)

    st.markdown("<div class='btn-analog'>", unsafe_allow_html=True)
    if st.button("Enviar valor analógico", key="btn_analog"):
        client1 = paho.Client("LucesCSC")
        client1.on_publish = on_publish
        client1.connect(broker, port)
        message = json.dumps({"Analog": float(values)})
        ret = client1.publish("voice_ctrlCSC", message)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)  # slider-card

st.markdown("</div>", unsafe_allow_html=True)  # glass-card
st.markdown("</div>", unsafe_allow_html=True)  # container-botones
