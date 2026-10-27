import html
import os
import re
import unicodedata
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

import openpyxl
import streamlit as st

# إعدادات الصفحة
st.set_page_config(
    page_title="Rimal X | Knowledge",
    page_icon="rimal_x_icon_corrected.png",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# مسارات الملفات محلياً على السحابة
PROJECT_DIR = Path(__file__).resolve().parent
DOCUMENTS_DIR = PROJECT_DIR / "documents"
EXCEL_PATH = DOCUMENTS_DIR / "محتوى مساعد المعرفة.xlsx"

PUBLIC_AUDIENCE = "الكل"
MIN_SCORE = 0.50

ROLES = ["الكل", "موظف", "مبيعات", "مدير", "مؤسس"]

# --- منطق البحث والتحليل (مدمج بالكامل ليعمل بدون API خارجي) ---

STOP_WORDS = {
    "هل", "ما", "ماذا", "كيف", "كم", "متى", "من",
    "انا", "لي", "في", "على", "عن", "الى", "و", "او",
    "اقدر", "استطيع", "يمكنني", "ابي", "ابغى", "اريد",
    "هو", "هي", "هذا", "هذه", "منه", "عندي",
    "تم", "يتم", "كان", "كانت", "يكون",
    "مع", "بعد", "قبل", "اذا", "عند", "كل",
}

SYNONYMS = {
    "تنزل": "صرف", "ينزل": "صرف", "تنزلون": "صرف", "تصرف": "صرف", "تصرفون": "صرف", "يصرف": "صرف", "صرف": "صرف",
    "عمولتي": "عمولة", "عمولتك": "عمولة", "عمولته": "عمولة", "عمولتها": "عمولة", "العمولات": "عمولة", "عمولات": "عمولة", "العمولة": "عمولة",
    "العضويات": "عضوية", "عضويات": "عضوية", "العضوية": "عضوية", "بعت": "بيع", "ابيع": "بيع",
    "مواعيد": "موعد", "نسبه": "نسبة", "احسب": "حساب", "احسبها": "حساب", "حسابي": "حساب",
}

PREFIXES = ("وال", "بال", "فال", "كال", "لل", "ال")

def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKC", str(text)).casefold()
    text = re.sub(r"[\u064b-\u065f\u0670]", "", text)
    text = text.replace("ـ", "")
    text = re.sub(r"[إأآٱ]", "ا", text)
    text = text.replace("ى", "ي")
    text = re.sub(r"[^\w\s]", " ", text)
    return " ".join(text.split())

def keywords(text: str) -> set[str]:
    result = set()
    for word in normalize(text).split():
        if len(word) <= 1 or word in STOP_WORDS:
            continue
        word = SYNONYMS.get(word, word)
        for prefix in PREFIXES:
            if word.startswith(prefix) and len(word) >= len(prefix) + 3:
                word = word[len(prefix):]
                break
        word = SYNONYMS.get(word, word)
        result.add(word)
    return result

def get_cell(row, index):
    if index is None or index >= len(row):
        return ""
    value = row[index]
    if value is None:
        return ""
    if isinstance(value, (datetime, Path)):
        return value.strftime("%Y-%m-%d")
    return str(value).strip()

def split_alternatives(text: str) -> list[str]:
    return [part.strip() for part in re.split(r"[|؛;\n]+", text) if part.strip()]

def similarity(q_words: set[str], c_words: set[str]) -> float:
    if not q_words or not c_words:
        return 0.0
    overlap = q_words & c_words
    if not overlap:
        return 0.0
    return 0.65 * (len(overlap) / len(q_words)) + 0.35 * (len(overlap) / len(c_words))

def is_allowed(audience_cell: str, role: str) -> bool:
    allowed = {normalize(a) for a in split_alternatives(audience_cell)}
    if not allowed:
        return False
    return normalize(PUBLIC_AUDIENCE) in allowed or normalize(role) in allowed

def search_knowledge(question: str, role: str):
    q_words = keywords(question)
    if not q_words:
        return {"status": "no_answer", "answer": None, "sources": []}
    if not EXCEL_PATH.exists():
        return {"status": "no_answer", "answer": None, "sources": []}

    matches = []
    try:
        workbook = openpyxl.load_workbook(EXCEL_PATH, read_only=True, data_only=True)
        sheet = workbook.active
        headers = [normalize(cell.value or "") for cell in sheet[1]]
        column_map = {h: i for i, h in enumerate(headers) if h}

        def find_col(*names):
            for name in names:
                if normalize(name) in column_map:
                    return column_map[normalize(name)]
            return None

        orig_col = find_col("السؤال الأصلي", "السؤال")
        alt_col = find_col("الصيغ البديلة", "صيغ بديلة")
        ans_col = find_col("الإجابة", "الإجابة المعتمدة")
        src_col = find_col("المصدر", "رابط المصدر")
        id_col = find_col("معرّف السؤال", "معرف السؤال", "ID")
        kw_col = find_col("الكلمات المفتاحية", "كلمات مفتاحية")
        aud_col = find_col("الفئة المسموحة", "الصلاحية", "الجمهور")
        upd_col = find_col("تاريخ آخر تحديث", "تاريخ التحديث")

        if orig_col is None or ans_col is None:
            return {"status": "no_answer", "answer": None, "sources": []}

        for row_num, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
            original = get_cell(row, orig_col)
            answer = get_cell(row, ans_col)
            if not original or not answer:
                continue

            allowed = True
            if aud_col is not None:
                allowed = is_allowed(get_cell(row, aud_col), role)

            candidates = [original] + split_alternatives(get_cell(row, alt_col))
            best_score = max((similarity(q_words, keywords(c)) for c in candidates), default=0.0)

            if best_score > 0 and kw_col is not None:
                kw_overlap = q_words & keywords(get_cell(row, kw_col))
                if kw_overlap:
                    best_score = min(1.0, best_score + 0.2 * len(kw_overlap) / len(q_words))

            if best_score <= 0 or not allowed:
                continue

            matches.append({
                "score": best_score,
                "file": EXCEL_PATH.name,
                "line": row_num,
                "question": original,
                "answer": answer,
                "source": get_cell(row, src_col),
                "id": get_cell(row, id_col),
                "updated": get_cell(row, upd_col),
            })
        workbook.close()
    except Exception:
        return {"status": "no_answer", "answer": None, "sources": []}

    if not matches or matches[0]["score"] < MIN_SCORE:
        return {"status": "no_answer", "answer": None, "sources": []}

    matches.sort(key=lambda x: x["score"], reverse=True)
    best = matches[0]

    return {
        "status": "ok",
        "answer": best["answer"],
        "sources": [{
            "file": best["file"],
            "line": best["line"],
            "text": best["question"],
            "source": best["source"],
            "id": best["id"],
            "updated": best["updated"],
        }]
    }

# --- واجهة المستخدم (Streamlit) ---

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@400;500;600;700&display=swap');
:root { --purple: #734F96; --purple-dark: #4E3565; --orange: #EDA155; --paper: #FAF7F2; --white: #FFFFFF; --ink: #30253A; --muted: #82778A; --line: #E9E1EB; --green: #477653; }
html, body, [class*="css"] { font-family: 'IBM Plex Sans Arabic', sans-serif; }
.stApp { background: radial-gradient(ellipse at 90% 0%, #F0E7F5 0%, transparent 35%), var(--paper); color: var(--ink); }
.block-container { max-width: 790px; padding-top: 2rem; padding-bottom: 2rem; }
#MainMenu, footer { visibility: hidden; }
section[data-testid="stMain"] { direction: rtl; }
.brand-row { display: flex; align-items: center; justify-content: space-between; padding: 0.25rem 0 1.3rem; border-bottom: 1px solid var(--line); margin-bottom: 3.1rem; direction: ltr; }
.brand { display: flex; align-items: center; gap: 12px; }
.brand-mark { display: flex; align-items: center; justify-content: center; width: 43px; height: 43px; border-radius: 15px; background: var(--purple); color: white; font-size: 21px; font-weight: 700; }
.brand-name { color: var(--ink); font-size: 17px; font-weight: 700; }
.brand-caption { color: var(--muted); font-size: 10px; letter-spacing: 1.6px; }
.status-pill { background: #EAF1E8; color: #477653; border-radius: 100px; padding: 7px 12px; font-size: 11px; }
.hero-title { font-size: clamp(30px, 5vw, 43px); font-weight: 700; color: var(--ink); }
.hero-title span { color: var(--purple); }
.answer-card { background: var(--white); border: 1px solid var(--line); border-radius: 20px; padding: 23px 24px; position: relative; overflow: hidden; }
.answer-card::before { content: ""; position: absolute; right: 0; top: 0; bottom: 0; width: 4px; background: var(--orange); }
.answer-text { color: var(--ink); font-size: 21px; line-height: 1.8; font-weight: 700; }
.source-card { background: #F4EFF7; border: 1px solid #E8DDED; border-radius: 15px; padding: 16px; margin-top: 12px; text-align: right; }
.empty-card { background: var(--white); border: 1px solid var(--line); border-radius: 17px; padding: 22px; text-align: right; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="brand-row">
    <div class="brand">
        <div class="brand-mark">R</div>
        <div>
            <div class="brand-name">Rimal X</div>
            <div class="brand-caption">KNOWLEDGE ASSISTANT</div>
        </div>
    </div>
    <div class="status-pill">المساعد الداخلي</div>
</div>
<div style="text-align: right; margin-bottom: 2rem;">
    <h1 class="hero-title">مساعد <span>داخلي</span></h1>
    <p style="color: var(--muted); font-size: 15px;">ابحثي في السياسات والإجراءات والمعلومات الداخلية من مستندات المعرفة المتاحة.</p>
</div>
""", unsafe_allow_html=True)

with st.form("knowledge_search"):
    question = st.text_input("اكتبي سؤالك", placeholder="مثال: متى تنزل العمولات؟", label_visibility="collapsed")
    role = st.selectbox("الدور (تجريبي)", ROLES)
    search_clicked = st.form_submit_button("⌕   ابحثي في المعرفة", use_container_width=True)

def safe_text(val):
    return html.escape(str(val or ""))

def safe_url(val):
    val = str(val or "").strip()
    p = urlparse(val)
    return val if p.scheme == "https" and p.netloc else ""

if search_clicked:
    if not question.strip():
        st.warning("اكتبي سؤالك أولًا حتى نبحث في المستندات.")
    else:
        with st.spinner("نبحث في مستندات المعرفة..."):
            data = search_knowledge(question.strip(), role)

        if data.get("status") == "ok" and data.get("answer"):
            st.markdown("""
            <div style="margin-top: 2rem; text-align: right;">
                <div style="color: #477653; font-size: 12px; font-weight: 600; margin-bottom: 12
