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
st.set_page_config(page_title="القوانين اليمنية بآخر تعديلاتها حتى عام 2025م", layout="wide", initial_sidebar_state="expanded")
TRIAL_DURATION = 3 * 24 * 60 * 60
TRIAL_USERS_FILE = "trial_users.txt"
DEVICE_ID_FILE = "device_id.txt"
ACTIVATED_FILE = "activated.txt"
ACTIVATION_CODES_FILE = "activation_codes.txt"
LAWS_DIR = "laws"
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
    for kw in keywords:
        text = re.sub(f"({re.escape(kw)})", r"<mark>\1</mark>", text, flags=re.IGNORECASE)
    return text
def export_results_to_word(results, filename="نتائج_البحث.docx"):
    document = Document()
    document.add_heading('نتائج البحث في القوانين اليمنية', level=1)
    if not results:
        document.add_paragraph("لم يتم العثور على نتائج للكلمات المفتاحية المحددة.")
    else:
        for i, r in enumerate(results):
            document.add_heading(f"القانون: {r['law']} - المادة: {r['num']}", level=2)
            document.add_paragraph(r['plain'])
            if i < len(results) - 1:
                document.add_page_break()
    buffer = BytesIO()
    document.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()
def normalize_arabic_numbers(text):
    arabic_to_english = str.maketrans('٠١٢٣٤٥٦٧٨٩', '0123456789')
    return text.translate(arabic_to_english)
def main():
    st.markdown(
        """
        <div style="display: flex; flex-direction: column; align-items: center; margin-top: 20px; margin-bottom: 35px;">
            <div style="width: 90px; height: 90px; border-radius: 50%; background-color: #ecf0f1; display: flex; align-items: center; justify-content: center; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <svg width="55" height="55" viewBox="0 0 24 24" fill="none">
                    <path d="M12 3V15" stroke="#2c3e50" stroke-width="2"/>
                    <path d="M5 21H19" stroke="#2c3e50" stroke-width="2"/>
                    <path d="M8 15C8 13.3431 6.65685 12 5 12C3.34315 12 2 13.3431 2 15C2 16.6569 3.34315 18 5 18C6.65685 18 8 16.6569 8 15Z" stroke="#2980b9" stroke-width="2"/>
                    <path d="M22 15C22 13.3431 20.6569 12 19 12C17.3431 12 16 13.3431 16 15C16 16.6569 17.3431 18 19 18C20.6569 18 22 16.6569 22 15Z" stroke="#2980b9" stroke-width="2"/>
                    <path d="M9 6H15L13 9H11L9 6Z" fill="#f39c12"/>
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
    if is_activated():
        run_main_app()
        return
    st.markdown("<div style='text-align:center; color:#2c3e50; font-size:22px; font-weight:bold; padding:20px;'>مرحباً بك عزيزي المستخدم، قم بالنقر على أيقونة التجربة المجانية لتصفح التطبيق واستخدامه بشكل كامل قبل طلب النسخة المدفوعة.</div>", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown("<h3 style='text-align:center; color:#2c3e50;'>⏱️ النسخة التجريبية المجانية</h3>", unsafe_allow_html=True)
        device_id = get_device_id()
        trial_start = get_trial_start(device_id)
        if trial_start is None:
            if st.button("🚀 بدء النسخة المجانية", key="start_trial_button", use_container_width=True):
                register_trial(device_id)
                st.success("✅ تم تفعيل النسخة التجريبية المجانية بنجاح.")
                run_main_app()
                st.stop()
        if trial_start is not None:
            elapsed_time = time.time() - trial_start
            remaining_time = TRIAL_DURATION - elapsed_time
            if remaining_time > 0:
                days = int(remaining_time // 86400)
                hours = int((remaining_time % 86400) // 3600)
                minutes = int((remaining_time % 3600) // 60)
                seconds = int(remaining_time % 60)
                st.info(f"⏳ عزيزي المستخدم، أنت الآن في النسخة التجريبية المجانية. الوقت المتبقي: {days} يوم / {hours} ساعة / {minutes} دقيقة / {seconds} ثانية")
                run_main_app()
            else:
                st.error("❌ انتهت مدة التجربة المجانية لهذا الجهاز. يرجى تفعيل التطبيق للاستمرار في الاستخدام.")
    st.markdown("---")
    with st.container(border=True):
        st.markdown("<h3 style='text-align:center; color:#2c3e50;'>🔐 النسخة المدفوعة</h3>", unsafe_allow_html=True)
        code = st.text_input("أدخل كود التفعيل هنا:", key="activation_code_input", help="أدخل الكود الذي حصلت عليه لتفعيل النسخة الكاملة.")
        if st.button("✅ تفعيل الآن", key="activate_button", use_container_width=True):
            if code and activate_app(code.strip()):
                st.success("✅ تم التفعيل بنجاح! يرجى إعادة تشغيل التطبيق لتطبيق التغييرات.")
                st.stop()
            else:
                st.error("❌ كود التفعيل غير صحيح أو انتهت صلاحيته.")
        st.markdown("---")
if __name__ == "__main__":
    main()
