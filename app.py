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
/* Fondo con gradiente */
.main {
  background: radial-gradient(1200px 600px at 10% 10%, #1f2937 0%, #0b1220 40%, #05080f 100%);
}

/* Glass cards */
.glass {
  background: linear-gradient(180deg, rgba(255,255,255,.08), rgba(255,255,255,.03));
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255,255,255,.12);
  border-radius: 22px;
  padding: 18px 20px;
  box-shadow: 0 16px 48px rgba(0,0,0,.3), inset 0 1px 0 rgba(255,255,255,.05);
}

/* Títulos con brillo sutil */
h1, h2, h3 {
  color: #e5edff !important;
}
small, .stCaption, .stSubheader, label, p, .st-emotion-cache-1fv8s86 {
  color: #c9d2f0 !important;
}

/* Botón mic con glow */
.bk-btn {
  border-radius: 999px !important;
  padding: 14px 22px !important;
  font-weight: 700 !important;
  letter-spacing: .3px;
  border: 1px solid rgba(255,255,255,.16) !important;
  background: linear-gradient(135deg, #5b8cff, #8a5bff) !important;
  color: white !important;
  box-shadow: 0 8px 24px rgba(91,140,255,.45), 0 0 0 0 rgba(138,91,255,.35);
  transition: transform .06s ease, box-shadow .4s ease;
}
.bk-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 14px 36px rgba(91,140,255,.55), 0 0 24px 6px rgba(138,91,255,.3);
}

/* Estado pill */
.pill {
  display:inline-flex;align-items:center;gap:.5rem;
  padding:.35rem .7rem;border-radius:999px;
  border:1px solid rgba(255,255,255,.18);
  background: rgba(255,255,255,.08); color:#e8edff; font-weight:600;
}

/* Chips de comando */
.chips { display:flex; gap:.5rem; flex-wrap:wrap; }
.chip {
  border:1px solid rgba(255,255,255,.18); border-radius:999px; padding:.35rem .75rem;
  color:#e8edff; background: rgba(255,255,255,.06); cursor:pointer; user-select:none;
}
.chip:hover { background: rgba(255,255,255,.12); }

/* Ondas cuando escucha */
.wave {
  display:flex; align-items:flex-end; gap:4px; height:36px;
}
.wave span{
  width:6px; border-radius:3px;
  background: linear-gradient(180deg,#a6b6ff,#9b6bff);
  animation: bounce .9s ease-in-out infinite;
}
.wave span:nth-child(2){ animation-delay: .1s }
.wave span:nth-child(3){ animation-delay: .2s }
.wave span:nth-child(4){ animation-delay: .3s }
.wave span:nth-child(5){ animation-delay: .4s }

@keyframes bounce {
  0%, 100% { height: 6px; opacity:.5 }
  50% { height: 36px; opacity:1 }
}

/* Caja chat */
.bubble {
  padding:.7rem 1rem; border:1px solid rgba(255,255,255,.12);
  border-radius:16px; background: rgba(255,255,255,.06); color:#e9edff;
}
.bubble.me { background: rgba(109, 159, 255, .18); border-color: rgba(109,159,255,.4); }
.bubble.sys { background: rgba(155, 107, 255, .16); border-color: rgba(155,107,255,.38); }

/* Audio player limpio */
audio { width: 100%; margin-top: .5rem; filter: drop-shadow(0 8px 18px rgba(0,0,0,.35)); }
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
