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
.container-botones { max-width: 820px; margin: 0 auto 2rem auto; }

/* Tarjetas glass */
.glass-card {
  background: rgba(15,23,42,.9);
  border-radius: 22px;
  padding: 1.7rem 1.9rem 1.5rem;
  border: 1px solid rgba(148,163,253,.4);
  box-shadow:
    0 24px 70px rgba(15,23,42,.97),
    0 0 0 1px rgba(30,64,175,.6) inset;
  backdrop-filter: blur(18px);
}

/* Hero/encabezado */
.hero-mini {
  text-align:center;
  margin-top: 1.4rem;
  margin-bottom: 1.2rem;
  padding: 1.2rem 1.3rem 1.4rem;
  border-radius: 22px;
  border: 1px solid rgba(148,163,253,.35);
  background:
    radial-gradient(circle at 0 0, rgba(129,140,248,.4), transparent 55%),
    rgba(15,23,42,.92);
  box-shadow: 0 20px 60px rgba(15,23,42,.95);
}
.hero-mini h1 {
  font-size: 1.5rem;
  letter-spacing: .16em;
  text-transform: uppercase;
  margin-bottom: .4rem;
  color: #e5e7eb;
}
.hero-mini h1 span {
  font-size: 1.1rem;
}
.hero-mini p {
  color: #9ca3af;
  font-size: 0.95rem;
  margin-bottom: .7rem;
}

/* Badge versión Python */
.badge-ver {
  display:inline-flex;
  align-items:center;
  gap:6px;
  padding:4px 10px;
  border-radius:999px;
  border:1px solid rgba(148,163,253,.6);
  background: rgba(15,23,42,.9);
  color:#c7d2fe;
  font-size:0.78rem;
  margin-bottom: 0.45rem;
}

/* Status pills (broker, puerto, tópico) */
.status-row {
  display:flex;
  flex-wrap:wrap;
  gap:.5rem;
  justify-content:center;
  margin-top:.3rem;
}
.status-pill {
  display:inline-flex;
  align-items:center;
  gap:.35rem;
  padding:.28rem .7rem;
  border-radius:999px;
  font-size:.78rem;
  border:1px solid rgba(148,163,184,.7);
  background: radial-gradient(circle at 0 0, rgba(56,189,248,.25), rgba(15,23,42,.95));
  color:#e5e7eb;
}
.status-pill span {
  font-weight:600;
  color:#bfdbfe;
}

/* Títulos internos */
h3 {
  color:#e5e7eb !important;
  text-align:left;
  margin-bottom: .6rem;
}

/* Subtítulos sección */
.section-label {
  font-size: .78rem;
  letter-spacing: .18em;
  text-transform: uppercase;
  color:#9ca3af;
  margin-bottom:.4rem;
}

/* Fila de botones ON/OFF */
.btn-row {
  display:flex;
  gap:1rem;
  flex-wrap:wrap;
  justify-content:center;
  margin-top: 0.8rem;
  margin-bottom: 1.1rem;
}

/* Estilo base de TODOS los botones de Streamlit en esta página */
.stButton > button {
  border-radius: 999px;
  border: none;
  padding: 0.65rem 1.7rem;
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
  margin-top: 0.4rem;
  padding: 1rem 1.1rem 0.5rem;
  border-radius: 18px;
  border: 1px solid rgba(148,163,253,.35);
  background: radial-gradient(circle at 0 0, rgba(129,140,248,.35), transparent 55%),
              rgba(15,23,42,.94);
}
.slider-card label {
  color:#e5e7eb;
  font-weight:600;
}

/* Línea divisora suave */
.hr-soft {
  margin: 1.1rem 0 1.0rem;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(148,163,253,.55), transparent);
}

/* Texto general */
p, span, label {
  color:#cbd5f5;
}

/* Footer */
.footer {
  margin-top: 1.3rem;
  text-align:center;
  font-size: .83rem;
  color:#9ca3af;
}

/* Responsive */
@media (max-width: 768px) {
  .glass-card {
    padding: 1.4rem 1.2rem 1.3rem;
  }
  .hero-mini {
    padding: 1rem 1rem 1.1rem;
  }
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
  <h1>CABINA DOMÓTICA <span>🛰️</span></h1>
  <p>Panel de <b>botones físicos</b> para tu constelación domótica vía <b>MQTT</b>.<br/>
     Ideal para pruebas rápidas junto a la cabina de voz.</p>
  <div class="status-row">
    <div class="status-pill">📡 Broker <span>{broker}</span></div>
    <div class="status-pill">🔌 Puerto <span>{port}</span></div>
    <div class="status-pill">📨 Tópico <span>voice_ctrlCSC</span></div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

# Tarjeta principal
st.markdown("<div class='glass-card'>", unsafe_allow_html=True)

# --------- Sección digital ON/OFF ---------
st.markdown("<div class='section-label'>MÓDULO DIGITAL</div>", unsafe_allow_html=True)
st.markdown("### 🌗 Encendido / apagado")

st.markdown(
    "Activa o apaga el universo domótico con comandos directos sobre "
    "<code>Act1</code>.",
    unsafe_allow_html=True,
)

# Fila de botones ON / OFF
st.markdown("<div class='btn-row'>", unsafe_allow_html=True)

col_on, col_off = st.columns(2)

with col_on:
    st.markdown("<div class='btn-on'>", unsafe_allow_html=True)
    if st.button("🔆 ON", key="btn_on"):
        act1 = "ON"
        client1 = paho.Client("LucesCSC")
        client1.on_publish = on_publish
        client1.connect(broker, port)
        message = json.dumps({"Act1": act1})
        ret = client1.publish("voice_ctrlCSC", message)
    st.markdown("</div>", unsafe_allow_html=True)

with col_off:
    st.markdown("<div class='btn-off'>", unsafe_allow_html=True)
    if st.button("🌑 OFF", key="btn_off"):
        act1 = "OFF"
        client1 = paho.Client("LucesCSC")
        client1.on_publish = on_publish
        client1.connect(broker, port)
        message = json.dumps({"Act1": act1})
        ret = client1.publish("voice_ctrlCSC", message)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)  # cierre btn-row

st.markdown(
    f"<p style='font-size:.86rem; color:#9ca3af;'>Estado lógico actual: "
    f"<b>{act1}</b></p>",
    unsafe_allow_html=True,
)

st.markdown("<div class='hr-soft'></div>", unsafe_allow_html=True)

# --------- Sección analógica ---------
st.markdown("<div class='section-label'>MÓDULO ANALÓGICO</div>", unsafe_allow_html=True)
st.markdown("### 🌌 Valor analógico")

st.markdown(
    "Envía un valor flotante para probar intensidades, dimmers o parámetros graduales "
    "sobre tu montaje.",
    unsafe_allow_html=True,
)

with st.container():
    st.markdown("<div class='slider-card'>", unsafe_allow_html=True)
    values = st.slider("Selecciona el rango de valores", 0.0, 100.0, value=values)
    st.write("Values:", values)

    st.markdown("<div class='btn-analog'>", unsafe_allow_html=True)
    if st.button("📡 Enviar valor analógico", key="btn_analog"):
        client1 = paho.Client("LucesCSC")
        client1.on_publish = on_publish
        client1.connect(broker, port)
        message = json.dumps({"Analog": float(values)})
        ret = client1.publish("voice_ctrlCSC", message)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)  # slider-card

st.markdown("</div>", unsafe_allow_html=True)  # glass-card
st.markdown("<p class='footer'>🌠 Panel de botones — Cabina Domótica 2025</p>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)  # container-botones

