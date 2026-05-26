import os

import streamlit as st
from dotenv import load_dotenv
from google import genai

from rag_engine import RAGEngine

load_dotenv()

MODEL = "gemini-2.0-flash"
KB_PATH = "knowledge/milkmate_kb.txt"


@st.cache_resource
def load_rag():
    return RAGEngine(KB_PATH)


def get_gemini_client():
    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        return None

    return genai.Client(api_key=api_key)


def fallback_answer(question: str, context: str) -> str:
    """
    ใช้ตอบแทนเมื่อ Gemini ใช้งานไม่ได้ เช่น quota หมด
    โดยยังอ้างอิงจากข้อมูลร้าน Milk Mate
    """
    question = question.strip()

    out_of_menu_keywords = [
        "พิซซ่า",
        "pizza",
        "ข้าว",
        "ก๋วยเตี๋ยว",
        "เบอร์เกอร์",
        "burger",
        "ไก่ทอด",
        "เฟรนช์ฟรายส์",
        "อาหาร",
        "ส้มตำ",
        "หมูกระทะ",
        "ชาบู",
    ]

    if any(word in question.lower() for word in out_of_menu_keywords):
        return """
ขอโทษค่ะ Milk Mate ไม่มีเมนูนี้นะคะ 🥛

ตอนนี้ร้านมีเฉพาะเครื่องดื่มกลุ่มนมสด ชา โกโก้ และกาแฟนมค่ะ
ตัวอย่างเมนู เช่น นมสด นมชมพู นมสดคาราเมล โกโก้ ชาไทย ชาเขียวนม เนสกาแฟ โอวัลติน และไมโลค่ะ ✨
""".strip()

    if "เมนู" in question or "ขายอะไร" in question or "มีอะไร" in question:
        return """
Milk Mate มีเมนูหลัก ๆ 3 กลุ่มค่ะ 🥛

🍼 เมนูนมสด:
- นมสด
- นมชมพู / นมเย็น
- นมสดวานิลลา
- นมสดคาราเมล
- นมสดน้ำผึ้ง

🍫 เมนูชาและโกโก้:
- โกโก้ / ช็อกโกแลต
- ชาไทย / ชานมเย็น
- ชาเขียวนม
- เผือกหอมนมสด
- แคนตาลูปนมสด

☕ เมนูกาแฟนม:
- เนสกาแฟ
- โอวัลติน / ไมโล

💰 ราคา:
- ร้อน 25 บาท
- เย็น 30 บาท
- ปั่น 35 บาทค่ะ ✨
""".strip()

    if "นมสด" in question and "ราคา" in question:
        return "นมสดราคา ร้อน 25 บาท เย็น 30 บาท และปั่น 35 บาทค่ะ 🥛"

    if ("นมชมพู" in question or "นมเย็น" in question) and "ราคา" in question:
        return "นมชมพูหรือนมเย็นราคา ร้อน 25 บาท เย็น 30 บาท และปั่น 35 บาทค่ะ 💗"

    if "คาราเมล" in question and "ราคา" in question:
        return "นมสดคาราเมลราคา ร้อน 25 บาท เย็น 30 บาท และปั่น 35 บาทค่ะ ✨"

    if "น้ำผึ้ง" in question and "ราคา" in question:
        return "นมสดน้ำผึ้งราคา ร้อน 25 บาท เย็น 30 บาท และปั่น 35 บาทค่ะ 🍯"

    if ("โกโก้" in question or "ช็อกโกแลต" in question) and "ราคา" in question:
        return "โกโก้หรือช็อกโกแลตราคา ร้อน 25 บาท เย็น 30 บาท และปั่น 35 บาทค่ะ 🍫"

    if ("ชาไทย" in question or "ชานมเย็น" in question) and "ราคา" in question:
        return "ชาไทยหรือชานมเย็นราคา ร้อน 25 บาท เย็น 30 บาท และปั่น 35 บาทค่ะ 🧡"

    if "ชาเขียว" in question and "ราคา" in question:
        return "ชาเขียวนมราคา ร้อน 25 บาท เย็น 30 บาท และปั่น 35 บาทค่ะ 🍵"

    if "เนสกาแฟ" in question and "ราคา" in question:
        return "เนสกาแฟราคา ร้อน 25 บาท เย็น 30 บาท และปั่น 35 บาทค่ะ ☕"

    if ("โอวัลติน" in question or "ไมโล" in question) and "ราคา" in question:
        return "โอวัลตินหรือไมโลราคา ร้อน 25 บาท เย็น 30 บาท และปั่น 35 บาทค่ะ ☕"

    if "ปั่น" in question:
        return "มีเมนูปั่นค่ะ ทุกเมนูสามารถสั่งแบบปั่นได้ ราคา 35 บาทค่ะ ✨"

    if "ร้อน" in question:
        return "มีเมนูร้อนค่ะ ทุกเมนูสามารถสั่งแบบร้อนได้ ราคา 25 บาทค่ะ ☕"

    if "เย็น" in question:
        return "มีเมนูเย็นค่ะ ทุกเมนูสามารถสั่งแบบเย็นได้ ราคา 30 บาทค่ะ 🧊"

    if "ราคา" in question:
        return """
ราคาของ Milk Mate แบ่งตามรูปแบบเครื่องดื่มค่ะ 🥛

- ร้อน 25 บาท
- เย็น 30 บาท
- ปั่น 35 บาท
""".strip()

    return f"""
Demi ขออ้างอิงจากข้อมูลร้าน Milk Mate ที่มีในระบบนะคะ 🥛

{context}
""".strip()


def generate_answer(question: str, context: str) -> str:
    """
    Generate step
    ใช้ Gemini ตอบจาก context ที่ค้นมา
    ถ้า Gemini quota หมด จะ fallback เป็นคำตอบจาก knowledge base แทน
    """
    client = get_gemini_client()

    full_prompt = f"""
คุณคือ Demi ผู้ช่วย AI ของร้าน Milk Mate

ให้ตอบคำถามลูกค้าจากข้อมูลร้านด้านล่างเท่านั้น
ถ้าข้อมูลด้านล่างไม่มีคำตอบ ให้ตอบว่า "ขอโทษค่ะ Demi ยังไม่มีข้อมูลนี้ในระบบนะคะ"

ข้อมูลร้าน:
{context}

คำถามจากลูกค้า:
{question}

ตอบเป็นภาษาไทย แบบสุภาพ เป็นกันเอง และกระชับ
"""

    if client is None:
        return fallback_answer(question, context)

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=full_prompt,
        )
        return response.text

    except Exception:
        return fallback_answer(question, context)


st.set_page_config(
    page_title="Milk Mate Demi Chatbot",
    page_icon="🥛",
)

st.title("🥛 Demi ผู้ช่วย AI ของ Milk Mate")
st.caption("ถามเรื่องเมนู ราคา หรือข้อมูลร้าน Milk Mate ได้เลย")

rag = load_rag()

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.header("ตัวอย่างคำถาม")
    st.write("- ร้านมีเมนูอะไรบ้าง")
    st.write("- นมสดราคาเท่าไหร่")
    st.write("- โกโก้ราคาเท่าไหร่")
    st.write("- มีเมนูปั่นไหม")
    st.write("- มีเมนูร้อนไหม")
    st.write("- มีพิซซ่าขายไหม")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

prompt = st.chat_input("ถามอะไรเกี่ยวกับ Milk Mate ได้เลย...")

if prompt:
    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )

    with st.chat_message("user"):
        st.write(prompt)

    context_chunks = rag.search(prompt, top_k=3)
    context = "\n---\n".join(context_chunks)

    answer = generate_answer(prompt, context)

    st.session_state.messages.append(
        {"role": "assistant", "content": answer}
    )

    with st.chat_message("assistant"):
        st.write(answer)