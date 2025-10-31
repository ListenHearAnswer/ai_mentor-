import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv
from datetime import datetime
import random
import time

# 🔑 Naloži OpenAI ključ
load_dotenv(dotenv_path="C:/apps/.env")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ⚙️ Nastavitve strani
st.set_page_config(page_title="AI Mentor za Smisel", page_icon="spirala.png", layout="centered")

# --- Inicializacija stanja ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "topic" not in st.session_state:
    st.session_state.topic = None
if "step" not in st.session_state:
    st.session_state.step = "welcome"

# --- Zbirka Franklovih citatov ---
frankl_quotes = [
    "Ko situacije ne moremo spremeniti, smo izzvani, da spremenimo sebe.",
    "Življenje nikoli ne preneha imeti pomena — tudi v trpljenju in smrti.",
    "Tisti, ki ima zakaj živeti, prenese skoraj vsak kako.",
    "Med dražljajem in odzivom je prostor. V tem prostoru je naša moč in svoboda.",
    "Sreča ni nekaj, kar se zasleduje, temveč nekaj, kar sledi smislu."
]

# --- Uvodni zaslon ---
if st.session_state.step == "welcome":
    st.title("spirala.png AI Mentor za Smisel")
    st.markdown("""
    Dobrodošel/a v **AI Mentorju za Smisel** 🌱  
    Tvoj mentor govori z glasom **Viktorja Frankla** –  
    mirno, človeško, in z vero v moč smisla tudi sredi trpljenja.
    """)

    if st.button("Začni pot"):
        st.session_state.step = "topic"
        st.rerun()

# --- Izbira teme ---
elif st.session_state.step == "topic":
    st.header("Kaj želiš raziskati danes?")
    st.markdown("Izberi temo ali napiši svojo:")

    topics = [
        "Smisel v delu", "Trpljenje in rast", "Notranji mir",
        "Samozavedanje", "Svoboda in odgovornost", "Odnosi"
    ]

    cols = st.columns(3)
    for i, t in enumerate(topics):
        if cols[i % 3].button(t):
            st.session_state.topic = t
            st.session_state.step = "chat"
            st.session_state.messages = []
            st.rerun()

    custom = st.text_input("Ali želiš vpisati svojo temo?")
    if st.button("Potrdi temo"):
        st.session_state.topic = custom or "Splošna refleksija"
        st.session_state.step = "chat"
        st.session_state.messages = []
        st.rerun()

# --- Pogovor ---
elif st.session_state.step == "chat":
    st.title("💬 Pogovor z mentorjem – Viktor Frankl")
    st.caption(f"Tema: *{st.session_state.topic}*")
    st.divider()

    # 🪶 Prikaži naključni Franklov citat (samo ob začetku pogovora)
    if len(st.session_state.messages) == 0:
        quote = random.choice(frankl_quotes)
        st.info(f"💭 »{quote}« — Viktor Frankl")

    # Prikaži vsa prejšnja sporočila
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Uporabniški vnos
    if user_input := st.chat_input("Vpiši svojo misel ali vprašanje..."):
        st.session_state.messages.append({"role": "user", "content": user_input})

        # Prikaži uporabnikov tekst
        with st.chat_message("user"):
            st.markdown(user_input)

        # Sistem navodilo (Franklov ton)
        system_prompt = f"""
        Ti si Viktor Frankl, eksistencialni psihoterapevt in filozof smisla.
        Govori mirno, človeško in s sočutjem.
        Tema pogovora: '{st.session_state.topic}'.
        Pomagaj sogovorniku razumeti pomen svojega doživetja in najti smisel v njem.
        """

        # Prikaži odgovor mentorja v živo (počasi)
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""

            stream = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    *st.session_state.messages
                ],
                stream=True,
            )

            for chunk in stream:
                if chunk.choices[0].delta and chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
                    time.sleep(0.05)  # počasnejše “pisanje” – bilo je 0.025

            message_placeholder.markdown(full_response)

        # Shrani odgovor
        st.session_state.messages.append({"role": "assistant", "content": full_response})

        # Zapiši v dnevnik
        try:
            date_str = datetime.now().strftime("%Y-%m-%d")
            with open(f"dnevnik_{date_str}.txt", "a", encoding="utf-8") as f:
                f.write(f"TI: {user_input}\nMENTOR: {full_response}\n\n")
        except Exception as e:
            st.warning(f"Ni bilo mogoče shraniti dnevnika: {e}")

    st.divider()
    if st.button("🔄 Nova tema"):
        st.session_state.step = "topic"
        st.session_state.messages = []
        st.session_state.topic = None
        st.rerun()
