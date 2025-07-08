import streamlit as st import streamlit.components.v1 as components from docx import Document from docx.shared import Inches import re import uuid import os import time import html import csv from io import BytesIO

----------------------------------------------------

إعدادات الصفحة الأساسية

----------------------------------------------------

st.set_page_config( page_title="القوانين اليمنية بآخر تعديلاتها حتى عام 2025م", layout="wide", initial_sidebar_state="expanded" )

----------------------------------------------------

ثوابت ومتغيرات عامة

----------------------------------------------------

TRIAL_DURATION = 3 * 24 * 60 * 60  # 3 أيام TRIAL_USERS_FILE = "trial_users.txt" DEVICE_ID_FILE = "device_id.txt" ACTIVATED_FILE = "activated.txt" ACTIVATION_CODES_FILE = "activation_codes.txt" LAWS_DIR = "laws"

----------------------------------------------------

دوال المساعدة

----------------------------------------------------

def get_device_id(): if os.path.exists(DEVICE_ID_FILE): with open(DEVICE_ID_FILE, "r") as f: return f.read().strip() new_id = str(uuid.uuid4()) with open(DEVICE_ID_FILE, "w") as f: f.write(new_id) return new_id

def get_trial_start(device_id): if not os.path.exists(TRIAL_USERS_FILE): return None with open(TRIAL_USERS_FILE, "r") as f: reader = csv.reader(f) for row in reader: if row and row[0] == device_id: return float(row[1]) return None

def register_trial(device_id): if not os.path.exists(TRIAL_USERS_FILE): with open(TRIAL_USERS_FILE, "w", newline='') as f: pass with open(TRIAL_USERS_FILE, "a", newline='') as f: writer = csv.writer(f) writer.writerow([device_id, time.time()])

def is_activated(): return os.path.exists(ACTIVATED_FILE)

def activate_app(code): if not os.path.exists(ACTIVATION_CODES_FILE): return False with open(ACTIVATION_CODES_FILE, "r") as f: codes = [line.strip() for line in f.readlines()] if code in codes: codes.remove(code) with open(ACTIVATION_CODES_FILE, "w") as f: for c in codes: f.write(c + "\n") with open(ACTIVATED_FILE, "w") as f: f.write("activated") return True return False

def highlight_keywords(text, keywords): for kw in keywords: text = re.sub(f"({re.escape(kw)})", r"<mark>\1</mark>", text, flags=re.IGNORECASE) return text

def export_results_to_word(results, filename="نتائج_البحث.docx"): document = Document() document.add_heading('نتائج البحث في القوانين اليمنية', level=1)

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

def normalize_arabic_numbers(text): arabic_to_english = str.maketrans('٠١٢٣٤٥٦٧٨٩', '0123456789') return text.translate(arabic_to_english)

----------------------------------------------------

الدالة الرئيسية لتشغيل التطبيق

----------------------------------------------------

def main(): device_id = get_device_id() trial_start = get_trial_start(device_id)

if is_activated():
    st.write("تم التفعيل ✅")
    return

if trial_start is not None:
    elapsed_time = time.time() - trial_start
    remaining_time = int(TRIAL_DURATION - elapsed_time)
    if remaining_time > 0:
        st.write("التجربة المجانية فعّالة ✅")
        return
    else:
        st.error("❌ انتهت مدة التجربة المجانية لهذا الجهاز. يرجى تفعيل التطبيق.")
        return

st.markdown("""
<div style='text-align:center; color:#2c3e50; font-size:22px; font-weight:bold; padding:20px;'>
    مرحباً بك عزيزي المستخدم، قم بالنقر على أيقونة بدء النسخة المجانية أو أدخل كود التفعيل:
</div>""", unsafe_allow_html=True)

with st.container(border=True):
    st.markdown("<h3 style='text-align:center; color:#2c3e50;'>⏱️ النسخة التجريبية المجانية</h3>", unsafe_allow_html=True)
    if trial_start is None:
        if st.button("🚀 بدء النسخة المجانية", key="start_trial_button", use_container_width=True):
            register_trial(device_id)
            st.rerun()

st.markdown("---")

with st.container(border=True):
    st.markdown("<h3 style='text-align:center; color:#2c3e50;'>🔐 النسخة المدفوعة</h3>", unsafe_allow_html=True)
    code = st.text_input("أدخل كود التفعيل هنا:", key="activation_code_input")
    if st.button("✅ تفعيل الآن", key="activate_button", use_container_width=True):
        if code and activate_app(code.strip()):
            st.success("✅ تم التفعيل بنجاح! يرجى إعادة تشغيل التطبيق.")
            st.stop()
        else:
            st.error("❌ كود التفعيل غير صحيح أو انتهت صلاحيته.")

if name == "main": main()

