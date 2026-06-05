import os
import json
import tempfile
import numpy as np
import streamlit as st
import sounddevice as sd
from scipy.io.wavfile import write
from dotenv import load_dotenv
from openai import OpenAI
from faster_whisper import WhisperModel
from collections import Counter
import pandas as pd

# ======================
# init
# ======================
load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

st.set_page_config(
    page_title="AI英语口语陪练",
    page_icon="🗣️",
    layout="wide"
)

st.title("🗣️ AI英语口语陪练（Whisper版）")
st.caption("语音 + 场景对话 + 错误分析 + 学习报告")

# ======================
# whisper model（M4优化）
# ======================
@st.cache_resource
def load_whisper():
    return WhisperModel(
        "tiny",
        device="cpu",
        compute_type="int8",
        download_root="./models"
    )

whisper_model = load_whisper()

# ======================
# session state
# ======================
st.session_state.setdefault("messages", [])
st.session_state.setdefault("scene", "点餐")
st.session_state.setdefault("mistakes", [])
st.session_state.setdefault("grammar_scores", [])
st.session_state.setdefault("fluency_scores", [])
st.session_state.setdefault("vocabulary_scores", [])

SCENES = {
    "点餐": "You are a restaurant waiter talking with a customer.",
    "面试": "You are an interviewer conducting a job interview.",
    "会议": "You are a meeting host leading a discussion.",
    "旅游": "You are a hotel receptionist helping a traveler."
}

# ======================
# whisper speech to text
# ======================
def record_audio(duration=5, fs=16000):
    st.info("🎤 Recording... Speak now")

    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype="int16")
    sd.wait()

    file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    write(file.name, fs, audio)

    return file.name


def transcribe(file_path):
    segments, _ = whisper_model.transcribe(
        file_path,
        language="en",
        task="transcribe",
        beam_size=5,
        best_of=5,
        temperature=0.0
    )

    text = " ".join([seg.text for seg in segments])
    return text.strip()

# ======================
# LLM
# ======================
def call_llm(messages, temperature=0.7):
    try:
        res = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            temperature=temperature,
            response_format={"type": "json_object"}
        )
        return json.loads(res.choices[0].message.content)
    except Exception as e:
        return {
            "reply": f"Error: {e}",
            "correction": "",
            "mistake_type": "None",
            "grammar_score": 0,
            "fluency_score": 0,
            "vocabulary_score": 0,
        }

# ======================
# chat
# ======================
def get_chat_response(text):

    history = st.session_state.messages[-6:]

    messages = [{
        "role": "system",
        "content": f"""
{SCENES[st.session_state.scene]}

You are an English speaking coach.

Return JSON ONLY:

{{
 "reply": "",
 "correction": "",
 "mistake_type": "Grammar|Tense|Article|Preposition|Vocabulary|Word Order|None",
 "grammar_score": 0-100,
 "fluency_score": 0-100,
 "vocabulary_score": 0-100
}}
"""
    }]

    for m in history:
        messages.append(m)

    messages.append({"role": "user", "content": text})

    return call_llm(messages)

# ======================
# report
# ======================
def generate_report():

    text = "\n".join(
        f"{m['role']}: {m['content']}"
        for m in st.session_state.messages
    )

    prompt = [{
        "role": "user",
        "content": f"""
Analyze English speaking performance:

{text}

Return JSON:
{{
 "overall_score":0,
 "common_mistakes":[],
 "good_expressions":[],
 "vocabulary_tips":[],
 "summary":""
}}
"""
    }]

    return call_llm(prompt, temperature=0.3)

# ======================
# sidebar
# ======================
with st.sidebar:
    st.header("⚙️ 设置")

    scene = st.selectbox("场景", list(SCENES.keys()))

    if scene != st.session_state.scene:
        st.session_state.scene = scene
        st.session_state.messages.clear()
        st.rerun()

    if st.button("🎤 开始语音输入"):
        wav_file = record_audio(duration=5)
        text = transcribe(wav_file)

        st.success(f"识别结果：{text}")

        st.session_state.messages.append({
            "role": "user",
            "content": text
        })

        result = get_chat_response(text)

        st.session_state.messages.append({
            "role": "assistant",
            "content": result["reply"],
            "correction": result["correction"]
        })

        # stats
        mt = result.get("mistake_type", "None")
        if mt != "None":
            st.session_state.mistakes.append(mt)

        st.session_state.grammar_scores.append(result["grammar_score"])
        st.session_state.fluency_scores.append(result["fluency_score"])
        st.session_state.vocabulary_scores.append(result["vocabulary_score"])

        st.rerun()

    if st.button("🗑️ 清空"):
        st.session_state.clear()
        st.rerun()

# ======================
# dashboard
# ======================
if st.session_state.grammar_scores:
    c1, c2, c3 = st.columns(3)

    c1.metric("Grammar", f"{np.mean(st.session_state.grammar_scores):.1f}")
    c2.metric("Fluency", f"{np.mean(st.session_state.fluency_scores):.1f}")
    c3.metric("Vocabulary", f"{np.mean(st.session_state.vocabulary_scores):.1f}")

# ======================
# chat history
# ======================
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.write(m["content"])
        if m.get("correction"):
            with st.expander("纠错"):
                st.write(m["correction"])

# ======================
# text input
# ======================
user_input = st.chat_input("输入英语或使用语音...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    result = get_chat_response(user_input)

    st.session_state.messages.append({
        "role": "assistant",
        "content": result["reply"],
        "correction": result["correction"]
    })

    mt = result.get("mistake_type", "None")
    if mt != "None":
        st.session_state.mistakes.append(mt)

    st.session_state.grammar_scores.append(result["grammar_score"])
    st.session_state.fluency_scores.append(result["fluency_score"])
    st.session_state.vocabulary_scores.append(result["vocabulary_score"])

    st.rerun()

# ======================
# report
# ======================
if st.button("📊 学习报告"):

    report = generate_report()

    st.subheader("学习报告")

    st.metric("总评分", report.get("overall_score", 0))

    if st.session_state.mistakes:
        st.write("### 错误统计")
        c = Counter(st.session_state.mistakes)
        df = pd.DataFrame({"type": c.keys(), "count": c.values()})
        st.bar_chart(df.set_index("type"))

    st.write("### 常见错误")
    for i in report.get("common_mistakes", []):
        st.write("•", i)

    st.write("### 优秀表达")
    for i in report.get("good_expressions", []):
        st.write("•", i)

    st.write("### 建议")
    for i in report.get("vocabulary_tips", []):
        st.write("•", i)

    st.success(report.get("summary", "Keep practicing!"))