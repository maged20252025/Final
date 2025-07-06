import streamlit as st
import streamlit.components.v1 as components
from docx import Document
from docx.shared import Inches
import re
import uuid
import os
import time
import html
import csv
from io import BytesIO

# ----------------------------------------------------
# إعدادات الصفحة الأساسية
# ----------------------------------------------------
st.set_page_config(
    page_title="القوانين اليمنية بآخر تعديلاتها حتى عام 2025م",
    layout="wide", # هذه الخاصية حاسمة لتوسيع عرض الصفحة
    initial_sidebar_state="expanded"
)

# ----------------------------------------------------
# ثوابت ومتغيرات عامة
# ----------------------------------------------------
TRIAL_DURATION = 3 * 24 * 60 * 60  # 3 أيام (يمكنك تغييرها لاحقًا لاختبار أسرع)
TRIAL_USERS_FILE = "trial_users.txt"
DEVICE_ID_FILE = "device_id.txt"
ACTIVATED_FILE = "activated.txt"
ACTIVATION_CODES_FILE = "activation_codes.txt"
LAWS_DIR = "laws"

# ----------------------------------------------------
# دوال المساعدة
# ----------------------------------------------------
def get_device_id():
    if os.path.exists(DEVICE_ID_FILE):
        with open(DEVICE_ID_FILE, "r") as f:
            return f.read().strip()
    new_id = str(uuid.uuid4())
    with open(DEVICE_ID_FILE, "w") as f:
        f.write(new_id)
    return new_id

def get_trial_start(device_id):
    if not os.path.exists(TRIAL_USERS_FILE):
        return None
    with open(TRIAL_USERS_FILE, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            if row and row[0] == device_id:
                return float(row[1])
    return None

def register_trial(device_id):
    if not os.path.exists(TRIAL_USERS_FILE):
        with open(TRIAL_USERS_FILE, "w", newline='') as f:
            pass
    with open(TRIAL_USERS_FILE, "a", newline='') as f:
        writer = csv.writer(f)
        writer.writerow([device_id, time.time()])

def is_activated():
    return os.path.exists(ACTIVATED_FILE)

def activate_app(code):
    if not os.path.exists(ACTIVATION_CODES_FILE):
        return False
    with open(ACTIVATION_CODES_FILE, "r") as f:
        codes = [line.strip() for line in f.readlines()]
    if code in codes:
        codes.remove(code)
        with open(ACTIVATION_CODES_FILE, "w") as f:
            for c in codes:
                f.write(c + "\n")
        with open(ACTIVATED_FILE, "w") as f:
            f.write("activated")
        return True
    return False

def highlight_keywords(text, keywords):
    # استخدام str(text) للتعامل مع أي نوع بيانات قد يأتي
    text = str(text)
    # إزالة مسافات غير مرئية أو مشاكل ترميز
    text = text.replace('\xa0', ' ').replace('\u200b', '')
    
    for kw in keywords:
        # استخدام re.escape لضمان أن الكلمات المفتاحية التي تحتوي على أحرف خاصة لا تكسر regex
        # إضافة re.UNICODE للتعامل الصحيح مع أحرف اليونيكود العربية
        text = re.sub(f"({re.escape(kw)})", r"<mark>\1</mark>", text, flags=re.IGNORECASE | re.UNICODE)
    return text

def export_results_to_word(results, filename="نتائج_البحث.docx"):
    document = Document()
    document.add_heading('نتائج البحث في القوانين اليمنية', level=1)
    
    if not results:
        document.add_paragraph("لم يتم العثور على نتائج للكلمات المفتاحية المحددة.")
    else:
        for i, r in enumerate(results):
            document.add_heading(f"القانون: {r['law']} - المادة: {r['num']}", level=2)
            document.add_paragraph(r['plain']) # تصدير النص الأصلي غير الملون
            if i < len(results) - 1:
                document.add_page_break() 

    buffer = BytesIO()
    document.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()

def normalize_arabic_numbers(text):
    # تحويل الأرقام العربية إلى إنجليزية
    arabic_to_english = str.maketrans('٠١٢٣٤٥٦٧٨٩', '0123456789')
    return text.translate(arabic_to_english)

# ----------------------------------------------------
# وظيفة التطبيق الرئيسية (بعد التفعيل أو بدء التجربة)
# ----------------------------------------------------
def run_main_app():
    # إضافة CSS لتصحيح اتجاه مربع النص وزر التصدير والعداد
    # تم تبسيط هذا الجزء وإزالة الـ CSS الذي كان يحاول تجاوز عرض Streamlit الداخلي،
    # مع الاعتماد على 'layout="wide"' في 'st.set_page_config'
    components.html("""
    <style>
    /* CSS أزرار التمرير (حافظنا عليها) */
    .scroll-btn {
        position: fixed;
        left: 10px;
        padding: 12px;
        font-size: 24px;
        border-radius: 50%;
        background-color: #c5e1a5;
        color: black;
        cursor: pointer;
        z-index: 9999;
        border: none;
        box-shadow: 1px 1px 5px #888;
    }
    #scroll-top-btn { bottom: 80px; }
    #scroll-bottom-btn { bottom: 20px; }
    
    /* CSS لمكونات Streamlit لجعلها RTL (حافظنا عليها) */
    .rtl-metric {
        direction: rtl;
        text-align: right !important;
        margin-right: 0 !important;
    }
    .rtl-metric .stMetric {
        text-align: right !important;
        direction: rtl;
    }
    .rtl-metric .stMetricDelta {
        display: block !important;
        text-align: right !important;
        direction: rtl;
    }
    .rtl-download-btn {
        direction: rtl;
        text-align: right !important;
        margin-right: 0 !important;
        display: flex;
        flex-direction: row-reverse;
        justify-content: flex-start;
    }
    textarea, .stTextArea textarea {
        direction: rtl !important;
        text-align: right !important;
    }
    .stButton, .stDownloadButton, .stMetric {
        direction: rtl !important;
        text-align: right !important;
    }
    </style>
    <button class='scroll-btn' id='scroll-top-btn' onclick='window.scrollTo({top: 0, behavior: "smooth"});'>⬆️</button>
    <button class='scroll-btn' id='scroll-bottom-btn' onclick='window.scrollTo({top: document.body.scrollHeight, behavior: "smooth"});'>⬇️</button>
    """, height=1)

    if not os.path.exists(LAWS_DIR):
        st.error(f"⚠️ مجلد '{LAWS_DIR}/' غير موجود. يرجى التأكد من وجود ملفات القوانين.")
        return

    files = [f for f in os.listdir(LAWS_DIR) if f.endswith(".docx")]
    if not files:
        st.warning(f"📂 لا توجد ملفات قوانين في مجلد '{LAWS_DIR}/'.")
        return

    # -- نموذج البحث بمحاذاة يمين --
    st.markdown("""
        <div style="direction: rtl; text-align: right;">
        <h3 style="display: flex; align-items: center; gap: 10px;">🔎 نموذج البحث</h3>
        </div>
    """, unsafe_allow_html=True)
    with st.form("main_search_form"):
        # تخصيص تسمية الحقول مع اتجاه يمين
        st.markdown('<div style="direction: rtl; text-align: right;">اختر قانونًا للبحث:</div>', unsafe_allow_html=True)
        selected_file_form = st.selectbox("", ["الكل"] + files, key="main_file_select", label_visibility="collapsed")
        st.markdown('<div style="direction: rtl; text-align: right;">📌 اكتب كلمة أو جملة للبحث عنها:</div>', unsafe_allow_html=True)
        # مربع البحث يدعم اتجاه RTL تلقائياً عبر CSS
        keywords_form = st.text_area(
            "",
            key="main_keywords_input",
            help="أدخل الكلمات التي تريد البحث عنها، وافصل بينها بفاصلة إذا كانت أكثر من كلمة.",
        )
        # مربع رقم المادة مع استبدال الجملة
        st.markdown('<div style="direction: rtl; text-align: right;">أو أبحث برقم المادة:</div>', unsafe_allow_html=True)
        article_number_input = st.text_input(
            "",
            key="article_number_input",
            help="أدخل رقم المادة للبحث عنها مباشرة (يمكن استخدام أرقام عربية أو إنجليزية)."
        )
        # زر البحث مع أيقونة يمين
        search_btn_col = st.columns([1, 2, 12])
        with search_btn_col[2]:
            submitted = st.form_submit_button("🔍 بدء البحث", use_container_width=True)

    if "results" not in st.session_state:
        st.session_state.results = []
    if "search_done" not in st.session_state:
        st.session_state.search_done = False

    # تنفيذ البحث فقط إذا تم إرسال النموذج
    if submitted:
        results = []
        search_files = files if selected_file_form == "الكل" else [selected_file_form]
        kw_list = [k.strip() for k in keywords_form.split(",") if k.strip()] if keywords_form else []
        search_by_article = bool(article_number_input.strip())

        norm_article = normalize_arabic_numbers(article_number_input.strip()) if search_by_article else ""

        with st.spinner("جاري البحث في القوانين... قد يستغرق الأمر بعض الوقت."):
            for file in search_files:
                try:
                    doc = Document(os.path.join(LAWS_DIR, file))
                except Exception as e:
                    st.warning(f"⚠️ تعذر قراءة الملف {file}: {e}. يرجى التأكد من أنه ملف DOCX صالح.")
                    continue

                law_name = file.replace(".docx", "")
                last_article = "غير معروفة"
                current_article_paragraphs = []

                for para in doc.paragraphs:
                    txt = para.text.strip()
                    if not txt:
                        continue
                    match = re.match(r"مادة\s*[\(]?\s*(\d+)[\)]?", txt)
                    if match:
                        # عند الانتقال إلى مادة جديدة احفظ المادة السابقة
                        if current_article_paragraphs:
                            full_text = "\n".join(current_article_paragraphs)
                            add_result = False
                            # البحث حسب رقم المادة فقط
                            if search_by_article and normalize_arabic_numbers(last_article) == norm_article:
                                add_result = True
                            # البحث حسب كلمات مفتاحية فقط أو مع رقم المادة
                            elif kw_list and any(kw.lower() in full_text.lower() for kw in kw_list):
                                if search_by_article:
                                    if normalize_arabic_numbers(last_article) == norm_article:
                                        add_result = True
                                else:
                                    add_result = True

                            if add_result:
                                highlighted = highlight_keywords(full_text, kw_list) if kw_list else full_text
                                results.append({
                                    "law": law_name,
                                    "num": last_article,
                                    "text": highlighted,
                                    "plain": full_text
                                })
                            current_article_paragraphs = []
                        last_article = match.group(1)
                    current_article_paragraphs.append(txt)

                # معالجة آخر مادة في الملف
                if current_article_paragraphs:
                    full_text = "\n".join(current_article_paragraphs)
                    add_result = False
                    if search_by_article and normalize_arabic_numbers(last_article) == norm_article:
                        add_result = True
                    elif kw_list and any(kw.lower() in full_text.lower() for kw in kw_list):
                        if search_by_article:
                            if normalize_arabic_numbers(last_article) == norm_article:
                                add_result = True
                        else:
                            add_result = True

                    if add_result:
                        highlighted = highlight_keywords(full_text, kw_list) if kw_list else full_text
                        results.append({
                            "law": law_name,
                            "num": last_article,
                            "text": highlighted,
                            "plain": full_text
                        })

        st.session_state.results = results
        st.session_state.search_done = True
        if not results:
            st.info("لم يتم العثور على نتائج مطابقة للبحث.")

    # الواجهة الرئيسية لعرض النتائج وزر التصدير
    if st.session_state.get("search_done", False) and st.session_state.results:
        st.markdown("<h2 style='text-align: center; color: #388E3C;'>نتائج البحث في القوانين 📚</h2>", unsafe_allow_html=True)
        st.markdown("---")

    # عرض زر التصدير ونتائج البحث فقط إذا تم البحث بالفعل وهناك نتائج
    if st.session_state.get("search_done", False):
        results = st.session_state.results
        unique_laws = sorted(set(r["law"] for r in results))

        # ---- محاذاة يمين للـ metric ----
        st.markdown('<div class="rtl-metric">', unsafe_allow_html=True)
        st.metric(label="📊 إجمالي النتائج التي تم العثور عليها", value=f"{len(results)}", delta=f"في {len(unique_laws)} قانون/ملف")
        st.markdown('</div>', unsafe_allow_html=True)

        # ---- محاذاة يمين لزر التصدير ----
        if results:
            export_data = export_results_to_word(results)
            st.markdown('<div class="rtl-download-btn">', unsafe_allow_html=True)
            st.download_button(
                label="⬇️ تصدير النتائج إلى Word",
                data=export_data,
                file_name="نتائج_البحث_القوانين_اليمنية.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                key="download_button_word_main",
                use_container_width=False
            )
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.warning("لا توجد نتائج لتصديرها.")
            
        st.markdown("---")

        if results:
            # ------ فلترة النتائج بمحاذاة يمين ------
            st.markdown('<div style="direction: rtl; text-align: right;">فلترة النتائج حسب القانون:</div>', unsafe_allow_html=True)
            selected_law_filter = st.selectbox("", ["الكل"] + unique_laws, key="results_law_filter", label_visibility="collapsed")
            filtered = results if selected_law_filter == "الكل" else [r for r in results if r["law"] == selected_law_filter]

            for i, r in enumerate(filtered):
                # Expander داخل Streamlit يجب أن يأخذ العرض الكامل بشكل تلقائي مع layout="wide"
                with st.expander(f"📚 المادة ({r['num']}) من قانون {r['law']}", expanded=True):
                    # هذا هو الجزء الذي يحدد عرض البطاقة الخضراء، تم تعديله ليكون مثل النسخة الاحتياطية
                    st.markdown(f'''
                    <div style="background-color:#f1f8e9;padding:15px;margin-bottom:15px;border-radius:10px;
                                border:1px solid #c5e1a5;direction:rtl;text-align:right; overflow-wrap: break-word;">
                        <p style="font-weight:bold;font-size:18px;margin:0">🔷 {r["law"]} - المادة {r["num"]}</p>
                        <p style="font-size:17px;line-height:1.8;margin-top:10px">
                            {r["text"]}
                        </p>
                    </div>
                    ''', unsafe_allow_html=True)
                    # زر نسخ المادة بشكل احترافي مع التحسينات الجديدة
                    components.html(f"""
                        <style>
                        .copy-material-btn {{
                            display: inline-flex;
                            align-items: center;
                            gap: 10px;
                            background: linear-gradient(90deg, #1abc9c 0%, #2980b9 100%);
                            color: #fff;
                            border: none;
                            border-radius: 30px;
                            font-size: 18px;
                            font-family: 'Cairo', 'Tajawal', sans-serif;
                            padding: 10px 22px;
                            cursor: pointer;
                            box-shadow: 0 4px 15px rgba(41, 128, 185, 0.4);
                            transition: all 0.3s ease;
                            margin-bottom: 10px;
                            direction: rtl;
                            white-space: nowrap;
                        }}
                        .copy-material-btn:hover {{
                            background: linear-gradient(90deg, #2980b9 0%, #1abc9c 100%);
                            box-shadow: 0 6px 20px rgba(41, 128, 185, 0.6);
                            transform: translateY(-2px);
                        }}
                        .copy-material-btn .copy-icon {{
                            font-size: 20px;
                            margin-left: 8px;
                            display: block;
                        }}
                        .copy-material-btn .copied-check {{
                            font-size: 20px;
                            color: #fff;
                            margin-left: 8px;
                            display: none;
                        }}
                        .copy-material-btn.copied .copy-icon {{
                            display: none;
                        }}
                        .copy-material-btn.copied .copied-check {{
                            display: inline;
                            animation: fadein-check 0.5s ease-out;
                        }}
                        @keyframes fadein-check {{
                            0% {{ opacity: 0; transform: scale(0.7); }}
                            100% {{ opacity: 1; transform: scale(1); }}
                        }}
                        </style>
                        <button class="copy-material-btn" id="copy_btn_{i}_{r['law']}_{r['num']}" onclick="
                            navigator.clipboard.writeText(document.getElementById('plain_text_{i}_{r['law']}_{r['num']}').innerText);
                            var btn = document.getElementById('copy_btn_{i}_{r['law']}_{r['num']}');
                            btn.classList.add('copied');
                            setTimeout(function(){{
                                btn.classList.remove('copied');
                            }}, 1800);
                        ">
                            <span class="copy-icon">
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                    <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                                    <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                                </svg>
                            </span>
                            <span>نسخ</span>
                            <span class="copied-check">
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                    <polyline points="20 6 9 17 4 12"></polyline>
                                </svg>
                                تم النسخ!
                            </span>
                        </button>
                        <div id="plain_text_{i}_{r['law']}_{r['num']}" style="display:none;">{html.escape(r['plain'])}</div>
                    """, height=60)
        else:
            st.info("لا توجد نتائج لعرضها حاليًا. يرجى إجراء بحث جديد.")# ----------------------------------------------------
# الدالة الرئيسية لتشغيل التطبيق (مع شاشة التفعيل/التجربة)
# ----------------------------------------------------
def main():
    # ---------- هيدر نصي مع رمز ميزان احترافي ----------
    st.markdown(
        """
        <div style="display: flex; flex-direction: column; align-items: center; margin-top: 20px; margin-bottom: 35px;">
            <div style="width: 90px; height: 90px; border-radius: 50%; background-color: #ecf0f1; display: flex; align-items: center; justify-content: center; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <svg width="72" height="72" viewBox="0 0 72 72" fill="none">
                    <circle cx="36" cy="36" r="35" fill="#f5f7fa" stroke="#d0d7de" stroke-width="1"/>
                    <g>
                        <rect x="33.2" y="14" width="5.6" height="27" rx="2.8" fill="#2c3e50"/>
                        <ellipse cx="36" cy="53" rx="16" ry="3.5" fill="#b2bec3"/>
                        <rect x="30" y="41" width="12" height="6" rx="3" fill="#f39c12"/>
                        <path d="M18 41c0-10 36-10 36 0" stroke="#2980b9" stroke-width="3" fill="none"/>
                        <ellipse cx="22" cy="41" rx="5" ry="5" fill="#fff" stroke="#2980b9" stroke-width="2"/>
                        <ellipse cx="50" cy="41" rx="5" ry="5" fill="#fff" stroke="#2980b9" stroke-width="2"/>
                        <ellipse cx="22" cy="41" rx="2" ry="2" fill="#2980b9"/>
                        <ellipse cx="50" cy="41" rx="2" ry="2" fill="#2980b9"/>
                        <rect x="33" y="10" width="6" height="6" rx="3" fill="#f8c291"/>
                        <rect x="34.7" y="6" width="2.6" height="6" rx="1.3" fill="#f8c291"/>
                    </g>
                </svg>
            </div>
            <h1 style="color: #2c3e50; font-family: 'Cairo', sans-serif; font-size: 32px; font-weight: 800; margin-top: 20px; text-align: center;">
                القوانين اليمنية<br>بآخر تعديلاتها
            </h1>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.divider()
    # ------------------------------------------------

    if is_activated():
        run_main_app()
        return

    st.markdown("<div style='text-align:center; color:#2c3e50; font-size:22px; font-weight:bold; padding:20px;'>مرحباً بك عزيزي المستخدم، قم بالنقر على أيقونة بدء النسخة المجانية أو أدخل كود التفعيل:</div>",
        unsafe_allow_html=True
    )

    # ----------- مربع النسخة التجريبية المجانية أولاً -----------------
    with st.container(border=True):
        st.markdown("<h3 style='text-align:center; color:#2c3e50;'>⏱️ النسخة التجريبية المجانية</h3>", unsafe_allow_html=True)
        device_id = get_device_id()
        trial_start = get_trial_start(device_id)

        if trial_start is None:
            if st.button("🚀 بدء النسخة المجانية", key="start_trial_button", use_container_width=True):
                register_trial(device_id)
                st.success("✅ تم تفعيل النسخة التجريبية المجانية بنجاح.")
                # st.rerun()  # لا حاجة لـ rerun هنا، سنستدعي run_main_app مباشرة
                run_main_app()
                st.stop() # يوقف التنفيذ بعد تشغيل التطبيق في الوضع التجريبي

        if trial_start is not None:
            elapsed_time = time.time() - trial_start
            remaining_time = int(TRIAL_DURATION - elapsed_time)
            if remaining_time > 0:
                days = remaining_time // 86400
                hours = (remaining_time % 86400) // 3600
                minutes = (remaining_time % 3600) // 60
                seconds = remaining_time % 60
                st.markdown(
                    f"""
                    <div style='background-color:#e3f1fd;border-radius:15px;padding:22px;margin: 0 auto;max-width:450px;text-align:center;'>
                        <span style='font-size:32px;'>&#x23F3;</span>
                        <div style='font-size:20px;color:#2c3e50;margin-bottom:6px;'>
                            عزيزي المستخدم، أنت الآن في النسخة التجريبية المجانية.
                        </div>
                        <span style='font-size:19px;color:#185a9d;'>
                            الوقت المتبقي: <b>{days}</b> يوم / <b>{hours}</b> ساعة / <b>{minutes}</b> دقيقة / <b>{seconds}</b> ثانية
                        </span>
                    </div>
                    """, unsafe_allow_html=True
                )
                run_main_app()
            else:
                st.error("❌ انتهت مدة التجربة المجانية لهذا الجهاز. يرجى تفعيل التطبيق للاستمرار في الاستخدام.")

    st.markdown("---")

    # ------------ مربع النسخة المدفوعة بعد المجانية ---------------
    with st.container(border=True):
        st.markdown("<h3 style='text-align:center; color:#2c3e50;'>🔐 النسخة المدفوعة</h3>", unsafe_allow_html=True)
        code = st.text_input("أدخل كود التفعيل هنا:", key="activation_code_input", help="أدخل الكود الذي حصلت عليه لتفعيل النسخة الكاملة.")
        if st.button("✅ تفعيل الآن", key="activate_button", use_container_width=True):
            if code and activate_app(code.strip()):
                st.success("✅ تم التفعيل بنجاح! يرجى إعادة تشغيل التطبيق لتطبيق التغييرات.")
                st.stop() # يوقف التنفيذ بعد التفعيل بنجاح
            else:
                st.error("❌ كود التفعيل غير صحيح أو انتهت صلاحيته.")

if __name__ == "__main__":
    main()
