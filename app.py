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

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

st.set_page_config(page_title="AI英语口语陪练", page_icon="🗣️", layout="wide")
st.title("🗣️ AI英语口语陪练（增强版）")
st.caption("语音 + 场景对话 + 纠错 + 评分趋势 + 练习统计 + 错误排行榜")

@st.cache_resource(show_spinner=False)
def load_whisper():
    return WhisperModel(
        "tiny.en",
        device="auto",
        compute_type="int8"
    )

with st.spinner("🚀 正在加载语音识别模型（首次启动约10秒）..."):
    whisper_model = load_whisper()

st.session_state.setdefault("messages", [])
st.session_state.setdefault("scene", "点餐")
st.session_state.setdefault("mistakes", [])
st.session_state.setdefault("grammar_scores", [])
st.session_state.setdefault("fluency_scores", [])
st.session_state.setdefault("vocabulary_scores", [])
st.session_state.setdefault("word_counts", [])
st.session_state.setdefault("practice_minutes", 0)

SCENES = {
    "点餐": "You are a restaurant waiter talking with a customer.",
    "面试": "You are an interviewer conducting a job interview.",
    "会议": "You are a meeting host leading a discussion.",
    "旅游": "You are a hotel receptionist helping a traveler."
}

def record_audio(duration=3, fs=16000):
    st.info("🎤 Speak now...")

    audio = sd.rec(
        int(duration * fs),
        samplerate=fs,
        channels=1,
        dtype="int16"
    )

    sd.wait()

    temp_file = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".wav"
    )

    write(
        temp_file.name,
        fs,
        audio
    )

    return temp_file.name

def transcribe(file_path):
    segments, _ = whisper_model.transcribe(
        file_path,
        language="en",
        beam_size=1,
        vad_filter=True
    )

    text = " ".join(
        seg.text.strip()
        for seg in segments
    )

    return text.strip()

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

def generate_report():
    conversation = "\n".join(f"{m['role']}: {m['content']}" for m in st.session_state.messages)
    prompt = [{
        "role": "user",
        "content": f"Analyze English speaking performance:\n\n{conversation}\n\nReturn JSON:\n{{\n \"overall_score\":0,\n \"common_mistakes\":[],\n \"good_expressions\":[],\n \"vocabulary_tips\":[],\n \"summary\":\"\"\n}}"
    }]
    return call_llm(prompt, temperature=0.3)

with st.sidebar:
    st.header("⚙️ 设置")
    scene = st.selectbox("场景", list(SCENES.keys()))
    if scene != st.session_state.scene:
        st.session_state.scene = scene
        st.session_state.messages.clear()
        st.rerun()

    if st.button("🎤 开始语音输入"):
        wav_file = record_audio(duration=3)
        text = transcribe(wav_file)
        st.success(f"识别结果：{text}")

        st.session_state.messages.append({"role": "user", "content": text})
        result = get_chat_response(text)
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
        st.session_state.word_counts.append(len(text.split()))
        st.session_state.practice_minutes += 1
        st.rerun()

    if st.button("🗑️ 清空"):
        for k in ["messages", "mistakes", "grammar_scores", "fluency_scores", "vocabulary_scores", "word_counts"]:
            st.session_state[k] = []
        st.session_state.practice_minutes = 0
        st.rerun()

# ======================
# 1️⃣ 练习统计卡片
# ======================
if st.session_state.word_counts:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("练习时长", f"{st.session_state.practice_minutes} 分钟")
    col2.metric("总词数", sum(st.session_state.word_counts))
    col3.metric("平均词数/轮", round(np.mean(st.session_state.word_counts), 1))
    col4.metric("对话轮数", len(st.session_state.messages) // 2)

# ======================
# 2️⃣ 评分趋势折线图
# ======================
if len(st.session_state.grammar_scores) >= 2:
    st.subheader("📈 学习趋势（评分变化）")
    df_trend = pd.DataFrame({
        "轮次": list(range(1, len(st.session_state.grammar_scores) + 1)),
        "语法评分": st.session_state.grammar_scores,
        "流利度评分": st.session_state.fluency_scores,
        "词汇评分": st.session_state.vocabulary_scores
    })
    st.line_chart(df_trend.set_index("轮次"))

# ======================
# 3️⃣ 错误类型排行榜
# ======================
if st.session_state.mistakes:
    st.subheader("🔁 错误类型排行榜")
    counter = Counter(st.session_state.mistakes)
    df_mistakes = pd.DataFrame(counter.items(), columns=["错误类型", "次数"]).sort_values("次数", ascending=False)
    st.bar_chart(df_mistakes.set_index("错误类型"))

# ======================
# 对话记录 + 输入
# ======================
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.write(m["content"])
        if m.get("correction"):
            with st.expander("纠错"):
                st.write(m["correction"])

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
    st.session_state.word_counts.append(len(user_input.split()))
    st.session_state.practice_minutes += 1
    st.rerun()

# ======================
# 学习报告
# ======================
if st.button("📊 学习报告"):
    report = generate_report()
    st.subheader("📊 学习报告")
    st.metric("总评分", report.get("overall_score", 0))
    st.write("### 常见错误")
    for i in report.get("common_mistakes", []):
        st.write(f"• {i}")
    st.write("### 优秀表达")
    for i in report.get("good_expressions", []):
        st.write(f"• {i}")
    st.write("### 建议")
    for i in report.get("vocabulary_tips", []):
        st.write(f"• {i}")
    st.success(report.get("summary", "Keep practicing!"))