# app.py — Voice Control "chimba" (Streamlit + Bokeh STT + MQTT + TTS)
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

# Traducción (opcional)
try:
    from googletrans import Translator
    translator = Translator()
except Exception:
    translator = None

# ───────────────────────────────────────────────────────────────
# SETUP
# ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="Chimba Voice Control", page_icon="🎙️", layout="wide")

# CSS con glassmorphism, gradientes y animaciones
st.markdown("""
<style>
/* Fondo gradiente profundo */
.main {
  background: radial-gradient(circle at 20% 20%, #0e1628 0%, #03060d 100%);
  color: #e7ecff !important;
}

/* --- Tarjetas y contenedores --- */
.glass {
  background: linear-gradient(180deg, rgba(255,255,255,.08), rgba(255,255,255,.03));
  backdrop-filter: blur(18px) saturate(140%);
  border: 1px solid rgba(255,255,255,.12);
  border-radius: 20px;
  padding: 18px 22px;
  box-shadow: 0 10px 30px rgba(0,0,0,.4), inset 0 1px 1px rgba(255,255,255,.05);
  transition: all 0.3s ease;
}
.glass:hover {
  border-color: rgba(91,140,255,.35);
  box-shadow: 0 12px 38px rgba(91,140,255,.25);
}

/* --- Títulos --- */
h1, h2, h3 {
  color: #a5b9ff !important;
  text-shadow: 0 0 12px rgba(91,140,255,.25);
}
small, p, label, .stCaption, .stSubheader {
  color: #cfd7f0 !important;
}

/* --- Botón del micrófono --- */
.bk-btn {
  border-radius: 999px !important;
  padding: 16px 26px !important;
  font-weight: 700 !important;
  border: 1px solid rgba(255,255,255,.15) !important;
  background: linear-gradient(145deg, #6b8cff, #935dff) !important;
  color: white !important;
  box-shadow: 0 0 0 rgba(91,140,255,.4);
  transition: all 0.35s ease;
}
.bk-btn:hover {
  transform: scale(1.03);
  box-shadow: 0 0 24px 6px rgba(140,100,255,.35);
}

/* --- Pills y etiquetas --- */
.pill {
  display:inline-flex;align-items:center;gap:.45rem;
  padding:.35rem .8rem;border-radius:999px;
  border:1px solid rgba(255,255,255,.18);
  background: rgba(109,159,255,.15);
  color:#dfe4ff; font-weight:600;
  box-shadow: inset 0 0 10px rgba(91,140,255,.25);
}

/* --- Chips de comando --- */
.chips { display:flex; gap:.55rem; flex-wrap:wrap; }
.chip {
  border:1px solid rgba(255,255,255,.15);
  border-radius:999px;
  padding:.4rem .9rem;
  color:#e5eaff;
  background: rgba(255,255,255,.06);
  transition: all 0.25s ease;
}
.chip:hover {
  background: linear-gradient(120deg,#617cff,#9a6dff);
  color:white;
  box-shadow: 0 0 16px rgba(109,159,255,.4);
  transform: scale(1.05);
}

/* --- Animación de ondas --- */
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

/* --- Burbuja del historial --- */
.bubble {
  padding:.7rem 1rem;
  border-radius:16px;
  border:1px solid rgba(255,255,255,.1);
  background: rgba(255,255,255,.07);
  color:#e5eaff;
  box-shadow: inset 0 0 10px rgba(255,255,255,.05);
}
.bubble.me { background: rgba(90,140,255,.18); border-color: rgba(91,140,255,.4); }
.bubble.sys { background: rgba(155, 107, 255, .18); border-color: rgba(155,107,255,.35); }

/* --- Audio player --- */
audio { width: 100%; margin-top: .6rem; border-radius:10px; }

/* --- Scrollbar suave --- */
::-webkit-scrollbar {width:10px;}
::-webkit-scrollbar-thumb {
  background: rgba(109,159,255,.25);
  border-radius:6px;
}
::-webkit-scrollbar-thumb:hover {
  background: rgba(109,159,255,.5);
}
</style>
""", unsafe_allow_html=True)


# ───────────────────────────────────────────────────────────────
# Helpers
# ───────────────────────────────────────────────────────────────
def random_id(n=6):
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=n))

def speak(text: str, lang: str = "es"):
    tts = gTTS(text=text, lang=lang)
    path = f"tts_{int(time.time())}.mp3"
    tts.save(path)
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    st.markdown(
        f"""
        <audio autoplay controls>
          <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
        """,
        unsafe_allow_html=True
    )
    try:
        os.remove(path)
    except Exception:
        pass

def mqtt_publish(broker, port, topic, payload, client_id=None):
    client_id = client_id or f"voice-{random_id()}"
    c = paho.Client(client_id)
    try:
        c.connect(broker, int(port))
        c.publish(topic, json.dumps(payload))
        return True, None
    except Exception as e:
        return False, str(e)
    finally:
        try:
            c.disconnect()
        except Exception:
            pass

# ───────────────────────────────────────────────────────────────
# Estado
# ───────────────────────────────────────────────────────────────
if "logs" not in st.session_state:
    st.session_state.logs = []  # [{role:'me/sys', text:'...', ts:'...'}]
if "listening" not in st.session_state:
    st.session_state.listening = False

# ───────────────────────────────────────────────────────────────
# Sidebar – Config
# ───────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Configuración")
    broker = st.text_input("Broker MQTT", value="broker.mqttdashboard.com")
    port = st.number_input("Puerto", 1, 65535, 1883)
    topic = st.text_input("Tópico", value="voice_ctrl")
    lang_tts = st.selectbox("Idioma respuesta (TTS)", ["es", "en", "pt", "fr"], index=0)
    auto_translate = st.toggle("Traducir comando a español para hablar", value=True)
    st.caption("Usa un broker público o tu broker local. El TTS se reproduce de inmediato.")

# ───────────────────────────────────────────────────────────────
# Header
# ───────────────────────────────────────────────────────────────
c1, c2 = st.columns([1, 2], vertical_alignment="center")
with c1:
    st.markdown("### 🎙️ **Chimba Voice Control**")
    st.markdown('<div class="pill">En línea ✅</div>', unsafe_allow_html=True)
with c2:
    st.markdown('<div class="glass">Pulsa el micrófono, habla y enviamos el comando por MQTT. También te respondo con voz. 😎</div>', unsafe_allow_html=True)

st.markdown("---")

# ───────────────────────────────────────────────────────────────
# Mic + visual EQ
# ───────────────────────────────────────────────────────────────
left, right = st.columns([1, 2])
with left:
    st.markdown("#### 🎤 Micrófono")
    mic_btn = Button(label="🎙️ Tap to Speak", width=260)
    # Web Speech API (solo Chrome/Edge)
    mic_btn.js_on_event("button_click", CustomJS(code="""
        var recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
        recognition.lang = 'es-ES';
        recognition.continuous = false;
        recognition.interimResults = false;

        recognition.onstart = function() {
            document.dispatchEvent(new CustomEvent("LISTENING", {detail: true}));
        };

        recognition.onend = function() {
            document.dispatchEvent(new CustomEvent("LISTENING", {detail: false}));
        };

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

    events = streamlit_bokeh_events(
        mic_btn,
        events="GET_TEXT,LISTENING",
        key="stt",
        refresh_on_update=False,
        override_height=80,
        debounce_time=0,
    )

    # Estado visual "ondas"
    if events and "LISTENING" in events:
        st.session_state.listening = bool(events["LISTENING"])

    st.markdown('<div class="glass" style="display:flex;justify-content:center;align-items:center;min-height:70px;">', unsafe_allow_html=True)
    if st.session_state.listening:
        st.markdown('<div class="wave">' + ''.join(['<span></span>' for _ in range(5)]) + '</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="opacity:.7;color:#cbd5ff">Silencio…</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with right:
    st.markdown("#### ⚡ Comandos rápidos")
    chips = ["encender luz", "apagar luz", "subir volumen", "bajar volumen", "abrir puerta", "cerrar puerta"]
    st.markdown('<div class="glass"><div class="chips">', unsafe_allow_html=True)
    chip_cols = st.columns(len(chips))
    for i, txt in enumerate(chips):
        if chip_cols[i].button(txt.title(), key=f"chip_{i}"):
            # Publica directo
            ok, err = mqtt_publish(broker, port, topic, {"command": txt})
            st.session_state.logs.insert(0, {"role":"me","text":txt,"ts":time.strftime("%H:%M:%S")})
            if ok:
                st.toast(f"📡 Enviado: {txt}")
            else:
                st.error(f"MQTT error: {err}")
                st.session_state.logs.insert(0, {"role":"sys","text":f"Error MQTT: {err}","ts":time.strftime("%H:%M:%S")})
    st.markdown('</div></div>', unsafe_allow_html=True)

# ───────────────────────────────────────────────────────────────
# Procesar voz → MQTT → TTS
# ───────────────────────────────────────────────────────────────
if events and "GET_TEXT" in events:
    user_text_raw = events.get("GET_TEXT", "").strip()
    if user_text_raw:
        st.session_state.logs.insert(0, {"role":"me","text":user_text_raw,"ts":time.strftime("%H:%M:%S")})

        # Publicar MQTT
        ok, err = mqtt_publish(broker, port, topic, {"command": user_text_raw})
        if ok:
            st.toast("✅ Comando enviado por MQTT", icon="📡")
        else:
            st.error(f"MQTT error: {err}")
            st.session_state.logs.insert(0, {"role":"sys","text":f"Error MQTT: {err}","ts":time.strftime("%H:%M:%S")})

        # Texto para hablar
        say_text = user_text_raw
        if auto_translate and translator is not None:
            try:
                lang_src = translator.detect(user_text_raw).lang
                if lang_src != "es":
                    say_text = translator.translate(user_text_raw, src=lang_src, dest="es").text
            except Exception:
                pass

        st.markdown("#### 🔊 Respuesta")
        speak(f"Comando recibido: {say_text}", lang=lang_tts)

# ───────────────────────────────────────────────────────────────
# Historial tipo chat
# ───────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 🗂️ Historial")
if not st.session_state.logs:
    st.info("Aún no hay mensajes. Usa el micrófono o los comandos rápidos.")
else:
    for item in st.session_state.logs[:30]:
        role = item["role"]
        cls = "me" if role == "me" else "sys"
        who = "Tú" if role == "me" else "Sistema"
        st.markdown(
            f"<div class='glass bubble {cls}'><b>{who}</b> · <small>{item['ts']}</small><br>{item['text']}</div>",
            unsafe_allow_html=True
        )

# ───────────────────────────────────────────────────────────────
# Footer
# ───────────────────────────────────────────────────────────────
st.markdown("---")
st.caption("Hecho con ❤️ · Streamlit · Web Speech API · MQTT · gTTS · by Camilo (más chimba que nunca)")
