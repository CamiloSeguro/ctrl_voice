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
st.set_page_config(page_title="Interfaces Multimodales", page_icon="🌌", layout="centered")
st.markdown("""
<style>
/* ---------- FONDO GALÁCTICO + CAPAS DE ESTRELLAS ---------- */
body {
  background:
    radial-gradient(1200px 700px at 15% 10%, #1b2440 0%, transparent 60%),
    radial-gradient(900px 500px at 85% 20%, #211b43 0%, transparent 60%),
    linear-gradient(180deg, #0b1120 0%, #020617 100%);
}
#stars, #stars2, #stars3 {
  position: fixed; inset: 0; z-index: -3; background: transparent; background-repeat: repeat;
}
#stars  { background-image: radial-gradient(2px 2px at 20px 30px, #ffffffa6, transparent 40%); animation: animStar 120s linear infinite; opacity: .45; }
#stars2 { background-image: radial-gradient(1px 1px at 40px 60px, #a5b4fccc, transparent 40%); animation: animStar 180s linear infinite; opacity: .35; }
#stars3 { background-image: radial-gradient(1.5px 1.5px at 80px 120px, #93c5fdcc, transparent 40%); animation: animStar 240s linear infinite; opacity: .28; }
@keyframes animStar { from{background-position: 0 0;} to{background-position: -10000px 10000px;} }

/* ---------- ESTRELLAS FUGACES ---------- */
.shooting-wrap { position: fixed; pointer-events: none; inset: 0; z-index: -2; overflow: hidden; }
.shooting {
  position: absolute; top: -10px; left: 110%;
  width: 2px; height: 2px; background: white; box-shadow: 0 0 12px 4px #c4b5fd;
  transform: translate(-50%, -50%) rotate(-35deg);
  animation: shoot 6s linear infinite;
  opacity: .85;
}
.shooting:after {
  content: ""; position: absolute; width: 180px; height: 2px;
  background: linear-gradient(90deg, #a78bfa 0%, transparent 100%);
  right: 2px; top: 0; opacity: .7;
}
.s2 { animation-delay: 1.8s; top: 10%; }
.s3 { animation-delay: 3.1s; top: 30%; }
.s4 { animation-delay: 4.6s; top: 55%; }
@keyframes shoot {
  0%   { transform: translate(0,0) rotate(-35deg); left: 110%; top: -10%; }
  100% { transform: translate(-160%, 160%) rotate(-35deg); left: -10%; top: 110%; }
}

/* ---------- LAYOUT ---------- */
.main > div { padding-top: 0rem; }
.container { max-width: 780px; margin: 0 auto; }

/* ---------- HERO CABINA ---------- */
.hero {
  position: relative; margin-top: 1rem; padding: 1.4rem 1.1rem; border-radius: 22px;
  background: linear-gradient(180deg, rgba(255,255,255,.08), rgba(255,255,255,.04));
  border: 1px solid rgba(255,255,255,.14); box-shadow: 0 14px 48px rgba(0,0,0,.38);
  backdrop-filter: blur(10px); text-align: center;
}
.hero:before {
  content: ""; position: absolute; inset: -1px; border-radius: 24px;
  background: conic-gradient(from 180deg at 50% 50%, #7c3aed55, #2563eb55, #22d3ee44, #7c3aed55);
  filter: blur(28px); opacity: .28;
}

/* ---------- LOGO CONSTELACIÓN ---------- */
.logo-wrap { display:flex; justify-content:center; margin-bottom:.45rem; }
.logo-constellation { width: 90px; height: 90px; }
.spark {
  filter: drop-shadow(0 0 6px #93c5fd) drop-shadow(0 0 12px #7c3aed);
  animation: twinkle 2.4s ease-in-out infinite;
}
@keyframes twinkle { 0%,100%{opacity:.85; transform:scale(1)} 50%{opacity:1; transform:scale(1.08)} }

/* ---------- TIPOGRAFÍA + ARCOÍRIS ---------- */
h1 {
  text-align:center; font-weight: 900; letter-spacing:.6px; margin:.1rem 0 .2rem 0;
  background: linear-gradient(90deg,#c7d2fe, #a5b4fc, #93c5fd, #c7d2fe);
  -webkit-background-clip: text; background-clip: text; color: transparent;
}
h2, h3, h4 { color: #dbeafe !important; text-align:center; }
p, .stMarkdown { color:#a3b2cc !important; font-size: 1.0rem; }
small, .muted { color: #8ea0c7 !important; }
.rainbow-underline {
  background-image: linear-gradient(90deg,#f472b6,#a78bfa,#60a5fa,#34d399,#fbbf24);
  background-size: 100% 2px; background-repeat:no-repeat; background-position: 0 100%;
  padding-bottom: 3px;
}

/* ---------- TARJETAS, CHIPS, BOTONES ---------- */
.glass-card {
  background: rgba(255,255,255,.07); border: 1px solid rgba(255,255,255,.15);
  border-radius: 22px; padding: 1.6rem; box-shadow: 0 0 28px rgba(0,0,0,.35);
  backdrop-filter: blur(12px); text-align: center;
}
.badge {
  display:inline-flex; align-items:center; gap:8px; padding:6px 12px; border-radius:999px;
  border:1px solid rgba(255,255,255,.18); background: rgba(255,255,255,.06);
  color:#e9d5ff; font-weight:700; font-size:.86rem;
}
.badge small { color:#b3a5ff; font-weight:600; }
.chips { display:flex; flex-wrap:wrap; gap:.5rem; justify-content:center; }
.chip {
  padding:.45rem .7rem; border-radius:999px; border:1px solid rgba(255,255,255,.18);
  background: linear-gradient(180deg, rgba(255,255,255,.08), rgba(255,255,255,.03));
  color:#dbeafe; font-weight:700; font-size:.85rem; box-shadow: 0 8px 22px rgba(0,0,0,.35);
}

.voice-center {
    display: flex;
    flex-direction: column;
    align-items: center;    /* ⭐ Centra horizontalmente */
    justify-content: center;
    text-align: center;     /* ⭐ Centra el caption */
    width: 100%;
}

/* Botón mic */
.voice-btn .bk.bk-btn{
  background: radial-gradient(120% 120% at 30% 20%, #2563eb 0%, #7c3aed 60%, #a855f7 100%) !important;
  border:none !important; color:white !important; font-weight:800 !important;
  border-radius:16px !important; padding:.8rem 2.1rem !important; font-size:1.02rem !important;
  box-shadow: 0 16px 40px rgba(124,58,237,.45), 0 0 0 3px rgba(124,58,237,.18) inset;
  transition: transform .12s ease, box-shadow .12s ease;
}
.voice-btn .bk.bk-btn:hover{
  transform: translateY(-2px) scale(1.015);
  box-shadow: 0 20px 48px rgba(124,58,237,.58), 0 0 0 4px rgba(124,58,237,.22) inset;
}

/* ---------- ÓRBITAS DECORATIVAS ---------- */
.orbit-wrap { position: relative; height: 190px; margin: .6rem auto 1.1rem; width: 190px; }
.planet { position:absolute; top:50%; left:50%; width:20px; height:20px; background:#93c5fd;
  border-radius:50%; transform: translate(-50%,-50%); box-shadow: 0 0 22px #93c5fd, 0 0 40px #a78bfa; }
.orbit {
  position:absolute; top:50%; left:50%; border:1px dashed rgba(255,255,255,.24);
  border-radius:50%; transform: translate(-50%,-50%);
}
.o1 { width:170px; height:170px; animation: spin 20s linear infinite; }
.o2 { width:128px; height:128px; animation: spin 14s linear infinite reverse; }
.o3 { width:88px;  height:88px;  animation: spin 9s linear infinite; }
@keyframes spin { to { transform: translate(-50%, -50%) rotate(360deg);} }

/* ---------- DETALLES ---------- */
.hr { height: 1px; background: linear-gradient(90deg, transparent, #ffffff33, transparent); margin: 1rem 0; }
.tip {
  background: rgba(59,130,246,.12); border:1px solid rgba(59,130,246,.28);
  padding:.7rem .9rem; border-radius:12px; color:#dbeafe;
}
.footer { margin-top:1.6rem; color:#93a5c9; font-size:.88rem; text-align:center; }
code { background: rgba(15,23,42,.42); padding: 3px 7px; border-radius: 6px; font-size: .85rem; color: #a5b4fc; }

/* ---- Animación reducida si el usuario lo pide ---- */
@media (prefers-reduced-motion: reduce) {
  #stars, #stars2, #stars3, .shooting, .o1, .o2, .o3 { animation: none !important; }
}
</style>

<!-- Capas de estrellas / fugaces (tu set actual) -->
<div id="stars"></div><div id="stars2"></div><div id="stars3"></div>
<div class="shooting-wrap">
  <span class="shooting"></span>
  <span class="shooting s2"></span>
  <span class="shooting s3"></span>
  <span class="shooting s4"></span>
</div>
""", unsafe_allow_html=True)

# —— FONDO CÓSMICO EXTRA + AURORA (debajo de todo, no toca lógica)
st.markdown("""
<div id="cosmic-bg"></div>
<div id="aurora"></div>
<style>
  /* Nebulosa multicolor fija (base) */
  #cosmic-bg{
    position: fixed;
    inset: 0;
    z-index: -5; /* más al fondo que #stars (-3) */
    background:
      radial-gradient(1200px 900px at 8% 12%,   #6d28d9 0%, transparent 60%),
      radial-gradient(1000px 700px at 88% 20%,  #2563eb 0%, transparent 62%),
      radial-gradient(900px 600px at 50% 85%,   #06b6d4 0%, transparent 64%),
      radial-gradient(720px 520px at 22% 78%,   #f59e0b 0%, transparent 66%),
      radial-gradient(640px 480px at 78% 72%,   #ef4444 0%, transparent 68%),
      linear-gradient(180deg, #0b1120 0%, #020617 100%);
    filter: saturate(1.22) brightness(0.98) contrast(1.02);
    pointer-events: none;
  }

  /* Capa aurora animada — movimiento muy lento para “vivo” */
  #aurora{
    position: fixed;
    inset: -10%;
    z-index: -4;
    background:
      conic-gradient(from 120deg at 30% 40%, rgba(168,85,247,.28), rgba(59,130,246,.22), rgba(34,197,94,.18), rgba(168,85,247,.28)),
      radial-gradient(60% 40% at 70% 20%, rgba(99,102,241,.28), transparent 60%),
      radial-gradient(50% 35% at 20% 80%, rgba(16,185,129,.22), transparent 65%);
    mix-blend-mode: screen;
    animation: drift 60s linear infinite;
    opacity: .65;
    pointer-events: none;
    filter: blur(14px) saturate(1.1);
  }
  @keyframes drift {
    0%   { transform: translate3d(0,0,0) rotate(0deg); }
    50%  { transform: translate3d(-2%, -1%, 0) rotate(2deg); }
    100% { transform: translate3d(0,0,0) rotate(0deg); }
  }
</style>
""", unsafe_allow_html=True)
# ================================================================

st.markdown("<div class='container'>", unsafe_allow_html=True)

# ---------- HERO + LOGO + NARRATIVA ----------
st.markdown("""
<div class="hero">
  <div class="badge">🛰️ <span>Cabina de mando • <small>Streamlit → MQTT → Wokwi</small></span></div>

  <div class="logo-wrap">
    <!-- LOGO CONSTELACIÓN (SVG inline, minimal) -->
    <svg class="logo-constellation" viewBox="0 0 120 120" fill="none" xmlns="http://www.w3.org/2000/svg" aria-label="Constelación">
      <!-- Líneas -->
      <path d="M20 92 L48 70 L78 78 L100 26" stroke="url(#g1)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" opacity="0.95"/>
      <path d="M48 70 L62 40" stroke="url(#g2)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" opacity="0.85"/>
      <!-- Nodos -->
      <circle class="spark" cx="20" cy="92" r="3.6" fill="#a5b4fc"/>
      <circle class="spark" cx="48" cy="70" r="4.2" fill="#93c5fd"/>
      <circle class="spark" cx="62" cy="40" r="3.4" fill="#c7d2fe"/>
      <circle class="spark" cx="78" cy="78" r="4.6" fill="#a5b4fc"/>
      <circle class="spark" cx="100" cy="26" r="5.0" fill="#93c5fd"/>
      <defs>
        <linearGradient id="g1" x1="20" y1="92" x2="100" y2="26">
          <stop offset="0" stop-color="#7c3aed"/><stop offset="1" stop-color="#2563eb"/>
        </linearGradient>
        <linearGradient id="g2" x1="48" y1="70" x2="62" y2="40">
          <stop offset="0" stop-color="#22d3ee"/><stop offset="1" stop-color="#7c3aed"/>
        </linearGradient>
      </defs>
    </svg>
  </div>

  <h1>INTERFACES MULTIMODALES</h1>
  <h3>🌌 Control por voz — <em class="rainbow-underline">Constelación Domótica</em> ✨</h3>
  <p>
    Bienvenid@ a la <b>cabina estelar</b> 🚀. Tu voz es la órbita que enciende constelaciones:<br/>
    prueba con <i>“enciende luz azul”</i> 💙, <i>“apaga todas”</i> 🌑, o <i>“verde on”</i> 💚 y observa cómo responde tu galaxia.
  </p>

  <div class="orbit-wrap">
    <div class="orbit o1"></div>
    <div class="orbit o2"></div>
    <div class="orbit o3"></div>
    <div class="planet"></div>
  </div>
</div>
""", unsafe_allow_html=True)

st.subheader("CONTROL POR VOZ 🎙️")

st.markdown("<div class='voice-center'>", unsafe_allow_html=True)

image = Image.open('voice_ctrl.jpg')
st.image(
    image,
    width=230,
    caption="🎧 Dile algo al universo y deja que viaje por MQTT"
)

st.markdown("</div>", unsafe_allow_html=True)

# ============== Botón Bokeh ==============
st.markdown("<div class='voice-btn'>", unsafe_allow_html=True)
stt_button = Button(label="🎤 Iniciar reconocimiento", width=260)

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
st.markdown("<p class='footer'>🌠 Camilo Seguro & Laura Orozco • EAFIT • 2025</p>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)  # container
