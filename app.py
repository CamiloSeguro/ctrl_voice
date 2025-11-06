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

def on_publish(client,userdata,result):             #create function for callback
    print("el dato ha sido publicado \n")
    pass

def on_message(client, userdata, message):
    global message_received
    time.sleep(2)
    message_received=str(message.payload.decode("utf-8"))
    st.write(message_received)

broker="broker.mqttdashboard.com"
port=1883
client1= paho.Client("LucesCSC")
client1.on_message = on_message

# ================== SOLO VISUAL ==================
st.set_page_config(page_title="Interfaces Multimodales", page_icon="🎙", layout="centered")
st.markdown("""
<style>
body {
    background: radial-gradient(circle at top, #020617 0%, #000 60%);
}
.main > div {
    padding-top: 0rem;
}
.wrapper {
    max-width: 720px;
    margin: 0 auto;
}
.block {
    background: rgba(2,6,23,0.45);
    border: 1px solid rgba(148,163,184,0.25);
    border-radius: 18px;
    padding: 1.6rem 1.3rem 1.2rem 1.3rem;
    backdrop-filter: blur(10px);
}
h1, h2, h3, h4, h5, h6, p, .stMarkdown {
    color: #e2e8f0 !important;
}
.small {
    font-size: 0.78rem;
    color: rgba(226,232,240,0.55);
    margin-bottom: 0.5rem;
}
img {
    border-radius: 14px;
}
.bk.bk-btn, .bokeh button {
    background: linear-gradient(140deg, #1d4ed8 0%, #6366f1 50%, #a855f7 100%) !important;
    border: none !important;
    color: #fff !important;
    font-weight: 600 !important;
    border-radius: 14px !important;
    padding: 0.4rem 1.5rem !important;
    cursor: pointer !important;
    transition: transform .15s ease-out;
}
.bk.bk-btn:hover, .bokeh button:hover {
    transform: translateY(-1px);
}
.centered {
    text-align: center;
}
.code-inline {
    background: rgba(15,23,42,.35);
    padding: .15rem .5rem;
    border-radius: .5rem;
    font-size: .7rem;
}
</style>
""", unsafe_allow_html=True)
# ================================================

st.markdown("<div class='wrapper'>", unsafe_allow_html=True)

st.title("INTERFACES MULTIMODALES")
st.subheader("CONTROL POR VOZ")

image = Image.open('voice_ctrl.jpg')
st.image(image, width=200)

st.markdown("<div class='block'>", unsafe_allow_html=True)
st.write("Toca el Botón y habla ")
st.markdown("<p class='small'>Lo que digas se manda al tópico <span class='code-inline'>voice_ctrlCSC</span></p>", unsafe_allow_html=True)

stt_button = Button(label=" Inicio ", width=200)

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
        if ( value != "") {
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

if result:
    if "GET_TEXT" in result:
        st.write(result.get("GET_TEXT"))
        client1.on_publish = on_publish                            
        client1.connect(broker,port)  
        message =json.dumps({"Act1":result.get("GET_TEXT").strip()})
        ret= client1.publish("voice_ctrlCSC", message)

    try:
        os.mkdir("temp")
    except:
        pass

st.markdown("</div>", unsafe_allow_html=True)  # block
st.markdown("</div>", unsafe_allow_html=True)  # wrapper
