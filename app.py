
import html
import os
from urllib.parse import urlparse

import requests
import streamlit as st


# إعدادات الصفحة
st.set_page_config(
    page_title="Rimal X | Knowledge",
    page_icon="rimal_x_icon_corrected.png",
    layout="centered",
    initial_sidebar_state="collapsed",
)

API_PORT = os.environ.get("RIMALX_API_PORT", "8000")
API_URL = f"http://127.0.0.1:{API_PORT}"

# أدوار تجريبية للنموذج الأولي فقط. عدّليها حسب فئات المستخدمين المعتمدة.
# في النسخة الفعلية يُحدَّد الدور من تسجيل الدخول على الخادم وليس من الواجهة.
ROLES = ["الكل", "موظف", "مبيعات", "مدير", "مؤسس"]


# الهوية البصرية
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@400;500;600;700&display=swap');

:root {
    --purple: #734F96;
    --purple-dark: #4E3565;
    --orange: #EDA155;
    --paper: #FAF7F2;
    --white: #FFFFFF;
    --ink: #30253A;
    --muted: #82778A;
    --line: #E9E1EB;
    --green: #477653;
}

html, body, [class*="css"] {
    font-family: 'IBM Plex Sans Arabic', sans-serif;
}

.stApp {
    background:
        radial-gradient(ellipse at 90% 0%, #F0E7F5 0%, transparent 35%),
        var(--paper);
    color: var(--ink);
}

.block-container {
    max-width: 790px;
    padding-top: 2rem;
    padding-bottom: 2rem;
}

#MainMenu, footer {
    visibility: hidden;
}

header[data-testid="stHeader"] {
    background: transparent;
}

section[data-testid="stMain"] {
    direction: rtl;
}

.brand-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.25rem 0 1.3rem;
    border-bottom: 1px solid var(--line);
    margin-bottom: 3.1rem;
    direction: ltr;
}

.brand {
    display: flex;
    align-items: center;
    gap: 12px;
}

.brand-mark {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 43px;
    height: 43px;
    border-radius: 15px;
    background: var(--purple);
    color: white;
    font-size: 21px;
    font-weight: 700;
    box-shadow: 0 5px 14px #734F9625;
}

.brand-name {
    color: var(--ink);
    font-size: 17px;
    font-weight: 700;
    line-height: 1.3;
}

.brand-caption {
    color: var(--muted);
    font-size: 10px;
    letter-spacing: 1.6px;
    margin-top: 3px;
}

.status-pill {
    background: #EAF1E8;
    color: #477653;
    border-radius: 100px;
    padding: 7px 12px;
    font-size: 11px;
    direction: rtl;
}

.hero {
    text-align: right;
    margin-bottom: 2rem;
}

.hero-kicker {
    display: inline-block;
    color: var(--purple);
    background: #EEE6F3;
    padding: 6px 12px;
    border-radius: 100px;
    font-size: 11px;
    font-weight: 600;
    margin-bottom: 1rem;
}

.hero-title {
    font-size: clamp(30px, 5vw, 43px);
    line-height: 1.45;
    letter-spacing: -1.2px;
    font-weight: 700;
    color: var(--ink);
    margin: 0 0 0.65rem;
}

.hero-title span {
    color: var(--purple);
}

.hero-description {
    color: var(--muted);
    font-size: 15px;
    line-height: 2;
    margin: 0;
}

.search-label {
    color: var(--ink);
    font-size: 13px;
    font-weight: 600;
    margin-bottom: 7px;
    text-align: right;
}

.stTextInput input {
    direction: rtl;
    text-align: right;
    min-height: 54px;
    background: var(--white) !important;
    color: var(--ink) !important;
    border: 1px solid #DED3E6 !important;
    border-radius: 15px !important;
    padding: 0 16px !important;
    font-family: 'IBM Plex Sans Arabic', sans-serif !important;
    font-size: 14px !important;
    box-shadow: 0 3px 12px #30253A05;
}

.stTextInput input:focus {
    border-color: var(--purple) !important;
    box-shadow: 0 0 0 3px #734F9617 !important;
}

.stTextInput input::placeholder {
    color: #A59BAA !important;
}

.stButton > button {
    min-height: 50px;
    width: 100%;
    border-radius: 14px;
    background: var(--purple) !important;
    color: white !important;
    border: 1px solid var(--purple) !important;
    font-family: 'IBM Plex Sans Arabic', sans-serif !important;
    font-size: 14px;
    font-weight: 600;
    transition: all 0.2s ease;
    box-shadow: 0 5px 14px #734F961C;
}

.stButton > button p,
.stButton > button span {
    color: white !important;
}

.stButton > button:hover {
    background: var(--purple-dark) !important;
    border-color: var(--purple-dark) !important;
    transform: translateY(-1px);
    box-shadow: 0 8px 18px #734F9625;
}

.result-wrap {
    margin-top: 2rem;
    direction: rtl;
    text-align: right;
}

.result-topline {
    display: flex;
    align-items: center;
    gap: 9px;
    margin-bottom: 12px;
    color: var(--green);
    font-size: 12px;
    font-weight: 600;
}

.result-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #61936B;
    box-shadow: 0 0 0 4px #61936B18;
}

.answer-card {
    background: var(--white);
    border: 1px solid var(--line);
    border-radius: 20px;
    padding: 23px 24px;
    box-shadow: 0 7px 24px #30253A07;
    position: relative;
    overflow: hidden;
}

.answer-card::before {
    content: "";
    position: absolute;
    right: 0;
    top: 0;
    bottom: 0;
    width: 4px;
    background: var(--orange);
}

.card-eyebrow {
    color: var(--muted);
    font-size: 12px;
    margin-bottom: 12px;
}

.answer-text {
    color: var(--ink);
    font-size: 23px;
    line-height: 1.8;
    font-weight: 700;
    overflow-wrap: anywhere;
}

.source-heading {
    font-size: 14px;
    font-weight: 700;
    color: var(--ink);
    margin: 23px 0 10px;
}

.source-card {
    background: #F4EFF7;
    border: 1px solid #E8DDED;
    border-radius: 15px;
    padding: 16px;
    direction: rtl;
    text-align: right;
}

.source-file {
    color: var(--ink);
    font-size: 13px;
    font-weight: 600;
    overflow-wrap: anywhere;
}

.source-meta {
    color: var(--muted);
    font-size: 11px;
    margin-top: 7px;
    line-height: 1.9;
}

.source-question {
    color: #675873;
    font-size: 12px;
    margin-top: 10px;
    line-height: 1.9;
}

.source-link {
    display: inline-block;
    color: var(--purple);
    font-size: 12px;
    font-weight: 600;
    text-decoration: none;
    margin-top: 10px;
}

.empty-card {
    margin-top: 1.5rem;
    padding: 22px;
    background: var(--white);
    border: 1px solid var(--line);
    border-radius: 17px;
    text-align: right;
}

.empty-title {
    font-size: 15px;
    font-weight: 700;
    color: var(--ink);
    margin-bottom: 7px;
}

.empty-description {
    color: var(--muted);
    font-size: 13px;
    line-height: 1.9;
}

.footer {
    margin-top: 3.5rem;
    border-top: 1px solid var(--line);
    padding-top: 18px;
    display: flex;
    justify-content: space-between;
    gap: 12px;
    flex-wrap: wrap;
    color: #9A909F;
    font-size: 10px;
    direction: rtl;
}

div[data-testid="stAlert"] {
    border-radius: 13px;
    direction: rtl;
    text-align: right;
}

div[data-testid="stSpinner"] {
    direction: rtl;
}

@media (max-width: 600px) {
    .block-container {
        padding: 1.2rem 1rem 2rem;
    }

    .brand-row {
        margin-bottom: 2.2rem;
    }

    .answer-card {
        padding: 19px;
    }

    .answer-text {
        font-size: 20px;
    }
}
</style>
""", unsafe_allow_html=True)


# رأس الصفحة
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

<div class="hero">
    <div class="hero-kicker">مساحة المعرفة</div>
    <h1 class="hero-title">مساعد <span>داخلي</span></h1>
    <p class="hero-description">
        ابحثي عن السياسات والإجراءات والمعلومات الداخلية
        من مستندات المعرفة المتاحة.
    </p>
</div>
""", unsafe_allow_html=True)


# نموذج البحث
with st.form("knowledge_search", clear_on_submit=False):
    st.markdown(
        '<div class="search-label">اكتب السؤال هنا</div>',
        unsafe_allow_html=True,
    )

    question = st.text_input(
        "اكتبي سؤالك",
        placeholder="مثال: متى تنزل العمولات؟",
        label_visibility="collapsed",
    )

    role = st.selectbox(
        "الدور (تجريبي)",
        ROLES,
        help="يحاكي صلاحية المستخدم. الصفوف خارج صلاحيته لا تظهر.",
    )

    search_clicked = st.form_submit_button(
        "⌕   ابحثي في المعرفة",
        use_container_width=True,
    )


def safe_text(value):
    return html.escape(str(value or ""))


def safe_source_url(value):
    value = str(value or "").strip()
    parsed = urlparse(value)

    if parsed.scheme == "https" and parsed.netloc:
        return value

    return ""


# تنفيذ البحث
if search_clicked:
    if not question.strip():
        st.warning("اكتبي سؤالك أولًا حتى نبحث في المستندات.")

    else:
        try:
            with st.spinner("نبحث في مستندات المعرفة..."):
                response = requests.post(
                    f"{API_URL}/search",
                    json={"question": question.strip(), "role": role},
                    timeout=15,
                )
                response.raise_for_status()
                data = response.json()

            if data.get("status") == "ok" and data.get("answer"):
                sources = data.get("sources") or []

                st.markdown("""
                <div class="result-wrap">
                    <div class="result-topline">
                        <span class="result-dot"></span>
                        تم العثور على إجابة في المستندات
                    </div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown(
                    f"""
                    <div class="answer-card">
                        <div class="card-eyebrow">الإجابة</div>
                        <div class="answer-text">{safe_text(data["answer"])}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                if sources:
                    st.markdown(
                        '<div class="source-heading">مصدر المعلومة</div>',
                        unsafe_allow_html=True,
                    )

                    for source in sources:
                        file_name = safe_text(
                            source.get("file", "غير محدد")
                        )
                        line_number = source.get("line")
                        source_id = safe_text(
                            source.get("id", "")
                        )
                        original_question = safe_text(
                            source.get("text", "")
                        )
                        source_url = safe_source_url(
                            source.get("source", "")
                        )

                        metadata = []
                        updated = source.get("updated")

                        if source_id:
                            metadata.append(f"المعرّف: {source_id}")

                        if updated:
                            metadata.append(f"آخر تحديث: {updated}")

                        if line_number is not None:
                            metadata.append(
                                f"رقم الصف في الملف: {line_number}"
                            )

                        metadata_text = " · ".join(metadata)

                        link_html = ""
                        if source_url:
                            link_html = (
                                f'<a class="source-link" '
                                f'href="{html.escape(source_url, quote=True)}" '
                                f'target="_blank" rel="noopener noreferrer">'
                                f'فتح المصدر ↗</a>'
                            )

                        question_html = ""
                        if original_question:
                            question_html = (
                                f'<div class="source-question">'
                                f'السؤال المعتمد: {original_question}'
                                f'</div>'
                            )

                        st.markdown(
                            f"""
                            <div class="source-card">
                                <div class="source-file">{file_name}</div>
                                <div class="source-meta">
                                    {safe_text(metadata_text)}
                                </div>
                                {question_html}
                                {link_html}
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                else:
                    st.warning(
                        "ظهرت إجابة دون مصدر مرفق. "
                        "تحققي من المعلومة قبل الاعتماد عليها."
                    )

            elif data.get("status") == "no_answer":
                st.markdown("""
                <div class="empty-card">
                    <div class="empty-title">
                        لم نجد إجابة مناسبة بعد
                    </div>
                    <div class="empty-description">
                        لم نعثر على معلومة مطابقة في المستندات المتاحة.
                        جرّبي صياغة أخرى أو كلمات أكثر تحديدًا.
                        لن نخمن إجابة من خارج المحتوى.
                    </div>
                </div>
                """, unsafe_allow_html=True)

            else:
                st.warning(
                    "وصل رد غير متوقع من النظام. "
                    "راجعي استجابة الـ API."
                )

        except requests.exceptions.ConnectionError:
            st.error(
                "تعذر الاتصال بالـ API. تأكدي أن خادم Uvicorn "
                "يعمل على المنفذ المحدد."
            )

        except requests.exceptions.Timeout:
            st.error("استغرق البحث وقتًا طويلًا. حاولي مرة أخرى.")

        except requests.exceptions.HTTPError as error:
            st.error(f"أعاد الـ API خطأ HTTP: {error}")

        except requests.exceptions.RequestException as error:
            st.error(f"حدث خطأ أثناء الاتصال: {error}")

        except ValueError:
            st.error("لم يُرجع الـ API بيانات JSON صالحة.")


# تذييل الصفحة
st.markdown("""
<div class="footer">
    <span>RIMAL X · INTERNAL KNOWLEDGE</span>
    <span>نموذج أولي للبحث</span>
</div>
""", unsafe_allow_html=True)
