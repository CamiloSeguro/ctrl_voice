# app.py — Chimba Voice Control (versión corregida con grilla limpia de comandos)
import os
import time
import json
import base64
import random
import string
import streamlit as st
from PIL import Image
from bokeh.models import Button, CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
import paho.mqtt.client as paho
from gtts import gTTS

# ───────────────────────────────────────────────────────────────
# CONFIGURACIÓN BÁSICA
# ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="Chimba Voice Control", page_icon="🎙️", layout="wide")

# CSS mejorado (ajustado + grilla limpia)
st.markdown("""
<style>
.main {
  background: radial-gradient(circle at 20% 20%, #0e1628 0%, #03060d 100%);
  color: #e7ecff !important;
}
.glass {
  background: linear-gradient(180deg, rgba(255,255,255,.08), rgba(255,255,255,.03));
  backdrop-filter: blur(18px) saturate(140%);
  border: 1px solid rgba(255,255,255,.12);
  border-radius: 20px;
  padding: 18px 22px;
  box-shadow: 0 10px 30px rgba(0,0,0,.4), inset 0 1px 1px rgba(255,255,255,.05);
}
h1, h2, h3 { color: #a5b9ff !important; text-shadow: 0 0 12px rgba(91,140,255,.25); }
small, p, label, .stCaption, .stSubheader { color: #cfd7f0 !important; }

.bk-btn {
  border-radius: 999px !important;
  padding: 16px 26px !important;
  font-weight: 700 !important;
  border: 1px solid rgba(255,255,255,.15) !important;
  background: linear-gradient(145deg, #6b8cff, #935dff) !important;
  color: white !important;
  transition: all 0.35s ease;
}
.bk-btn:hover {
  transform: scale(1.03);
  box-shadow: 0 0 24px 6px rgba(140,100,255,.35);
}

.pill {
  display:inline-flex;align-items:center;gap:.45rem;
  padding:.35rem .8rem;border-radius:999px;
  border:1px solid rgba(255,255,255,.18);
  background: rgba(109,159,255,.15);
  color:#dfe4ff; font-weight:600;
}

.wave {
  display:flex;align-items:flex-end;gap:4px;height:36px;justify-content:center;
}
.wave span{
  width:6px;border-radius:3px;
  background: linear-gradient(180deg,#8a9dff,#b07dff);
  animation: bounce .9s ease-in-out infinite;
}
.wave span:nth-child(2){animation-delay:.1s}
.wave span:nth-child(3){animation-delay:.2s}
.wave span:nth-child(4){animation-delay:.3s}
.wave span:nth-child(5){animation-delay:.4s}
@keyframes bounce {
  0%,100%{height:8px;opacity:.5}
  50%{height:36px;opacity:1}
}

.bubble {
  padding:.7rem 1rem;
  border-radius:16px;
  border:1px solid rgba(255,255,255,.1);
  background: rgba(255,255,255,.07);
  color:#e5eaff;
}
.bubble.me { background: rgba(90,140,255,.18); border-color: rgba(91,140,255,.4); }
.bubble.sys { background: rgba(155, 107, 255, .18); border-color: rgba(155,107,255,.35); }

section.main div[data-testid="column"] button {
  border-radius: 12px !important;
  padding: .45rem .75rem !important;
  font-weight: 600 !important;
  background: rgba(255,255,255,.06) !important;
  border: 1px solid rgba(255,255,255,.14) !important;
  color: #e6eaff !important;
}
section.main div[data-testid="column"] button:hover {
  background: linear-gradient(120deg,#617cff,#9a6dff) !important;
  color: #fff !important;
  border-color: rgba(140,100,255,.5) !important;
  transform: translateY(-1px);
  transition: all .18s ease;
}
</style>
""", unsafe_allow_html=True)

# ───────────────────────────────────────────────────────────────
# FUNCIONES AUXILIARES
# ───────────────────────────────────────────────────────────────
def random_id(n=6): return ''.join(random.choices(string.ascii_lowercase + string.digits, k=n))

def speak(text: str, lang="es"):
    tts = gTTS(text=text, lang=lang)
    path = f"tts_{int(time.time())}.mp3"
    tts.save(path)
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    st.markdown(f"""<audio autoplay controls><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>""", unsafe_allow_html=True)
    os.remove(path)

def mqtt_publish(broker, port, topic, payload, client_id=None):
    import paho.mqtt.client as paho
    client_id = client_id or f"voice-{random_id()}"
    c = paho.Client(client_id)
    try:
        c.connect(broker, int(port))
        c.publish(topic, json.dumps(payload))
        return True, None
    except Exception as e:
        return False, str(e)
    finally:
        try: c.disconnect()
        except: pass

# ───────────────────────────────────────────────────────────────
# ESTADO
# ───────────────────────────────────────────────────────────────
if "logs" not in st.session_state: st.session_state.logs = []
if "listening" not in st.session_state: st.session_state.listening = False

# ───────────────────────────────────────────────────────────────
# SIDEBAR
# ───────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Configuración")
    broker = st.text_input("Broker MQTT", value="broker.mqttdashboard.com")
    port = st.number_input("Puerto", 1, 65535, 1883)
    topic = st.text_input("Tópico", value="voice_ctrl")
    lang_tts = st.selectbox("Idioma respuesta (TTS)", ["es", "en", "pt", "fr"], index=0)
    st.toggle("Traducir comando a español para hablar", value=False)
    st.caption("Usa un broker público o tu broker local. El TTS se reproduce de inmediato.")

# ───────────────────────────────────────────────────────────────
# HEADER
# ───────────────────────────────────────────────────────────────
c1, c2 = st.columns([1, 2], vertical_alignment="center")
with c1:
    st.markdown("### 🎙️ **Chimba Voice Control**")
    st.markdown('<div class="pill">En línea ✅</div>', unsafe_allow_html=True)
with c2:
    st.markdown('<div class="glass">Pulsa el micrófono, habla y enviamos el comando por MQTT. También te respondo con voz. 😎</div>', unsafe_allow_html=True)

st.markdown("---")

# ───────────────────────────────────────────────────────────────
# MICRÓFONO + COMANDOS RÁPIDOS
# ───────────────────────────────────────────────────────────────
left, right = st.columns([1, 2])
with left:
    st.markdown("#### 🎤 Micrófono")
    mic_btn = Button(label="🎙️ Tap to Speak", width=260)
    mic_btn.js_on_event("button_click", CustomJS(code="""
        var recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
        recognition.lang = 'es-ES';
        recognition.continuous = false;
        recognition.interimResults = false;

        recognition.onstart = () => document.dispatchEvent(new CustomEvent("LISTENING", {detail: true}));
        recognition.onend = () => document.dispatchEvent(new CustomEvent("LISTENING", {detail: false}));

        recognition.onresult = e => {
            let text = "";
            for (let i = e.resultIndex; i < e.results.length; ++i)
                if (e.results[i].isFinal) text += e.results[i][0].transcript;
            if (text) document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: text}));
        };
        recognition.start();
    """))
    events = streamlit_bokeh_events(mic_btn, events="GET_TEXT,LISTENING", key="stt", refresh_on_update=False, override_height=80)
    if events and "LISTENING" in events: st.session_state.listening = bool(events["LISTENING"])

    st.markdown('<div class="glass" style="display:flex;justify-content:center;align-items:center;min-height:70px;">', unsafe_allow_html=True)
    if st.session_state.listening:
        st.markdown('<div class="wave">' + ''.join(['<span></span>' for _ in range(5)]) + '</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="opacity:.7;color:#cbd5ff">Silencio…</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with right:
    st.markdown("#### ⚡ Comandos rápidos")
    chip_labels = ["Encender Luz", "Apagar Luz", "Subir Volumen", "Bajar Volumen", "Abrir Puerta", "Cerrar Puerta"]
    N_PER_ROW = 4
    for i in range(0, len(chip_labels), N_PER_ROW):
        row = chip_labels[i:i + N_PER_ROW]
        cols = st.columns(len(row), vertical_alignment="center")
        for col, label in zip(cols, row):
            with col:
                if st.button(label, key=f"chip_{label.replace(' ', '_').lower()}", use_container_width=True):
                    ok, err = mqtt_publish(broker, port, topic, {"command": label.lower()})
                    st.session_state.logs.insert(0, {"role":"me","text":label,"ts":time.strftime("%H:%M:%S")})
                    if ok: st.toast(f"📡 Enviado: {label}")
                    else: st.error(f"MQTT error: {err}")

# ───────────────────────────────────────────────────────────────
# PROCESAR COMANDOS DE VOZ
# ───────────────────────────────────────────────────────────────
if events and "GET_TEXT" in events:
    text = events.get("GET_TEXT", "").strip()
    if text:
        st.session_state.logs.insert(0, {"role":"me","text":text,"ts":time.strftime("%H:%M:%S")})
        ok, err = mqtt_publish(broker, port, topic, {"command": text})
        if ok: st.toast("✅ Comando enviado por MQTT", icon="📡")
        else: st.error(f"MQTT error: {err}")
        speak(f"Comando recibido: {text}", lang=lang_tts)

# ───────────────────────────────────────────────────────────────
# HISTORIAL
# ───────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 🗂️ Historial")
if not st.session_state.logs:
    st.info("Aún no hay mensajes. Usa el micrófono o los comandos rápidos.")
else:
    for item in st.session_state.logs[:30]:
        who = "Tú" if item["role"]=="me" else "Sistema"
        st.markdown(
            f"<div class='glass bubble {item['role']}'><b>{who}</b> · <small>{item['ts']}</small><br>{item['text']}</div>",
            unsafe_allow_html=True
        )

st.markdown("---")
st.caption("Hecho con ❤️ · Streamlit · Web Speech API · MQTT · gTTS · by Camilo")
