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
# دالة عرض الهيدر من ملف خارجي
# ----------------------------------------------------
def render_header():
    if os.path.exists("header.html"):
        with open("header.html", "r", encoding="utf-8") as f:
            header_html = f.read()
        st.markdown(header_html, unsafe_allow_html=True)
    else:
        st.error("⚠️ ملف 'header.html' غير موجود في مجلد المشروع.")

# ----------------------------------------------------
# إعدادات الصفحة الأساسية
# ----------------------------------------------------
st.set_page_config(
    page_title="القوانين اليمنية بآخر تعديلاتها حتى عام 2025م",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------------------------------------
# ثوابت ومتغيرات عامة
# ----------------------------------------------------
TRIAL_DURATION = 3 * 24 * 60 * 60  # 3 أيام
TRIAL_USERS_FILE = "trial_users.txt"
DEVICE_ID_FILE = "device_id.txt"
ACTIVATED_FILE = "activated.txt"
ACTIVATION_CODES_FILE = "activation_codes.txt"
LAWS_DIR = "laws"

# ... (جميع الدوال المساعدة الأخرى مثل get_device_id, activate_app, highlight_keywords,...)

# ----------------------------------------------------
# الدالة الرئيسية لتشغيل التطبيق
# ----------------------------------------------------
def main():
    render_header()  # ← استدعاء الهيدر من ملف خارجي بدل إدراجه كنص مباشر
    st.divider()

    if is_activated():
        run_main_app()
        return

    st.markdown("<div style='text-align:center; color:#2c3e50; font-size:22px; font-weight:bold; padding:20px;'>مرحباً بك عزيزي المستخدم، قم بالنقر على أيقونة بدء النسخة المجانية أو أدخل كود التفعيل:</div>", unsafe_allow_html=True)

    # النسخة التجريبية المجانية
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

    # النسخة المدفوعة
    with st.container(border=True):
        st.markdown("<h3 style='text-align:center; color:#2c3e50;'>🔐 النسخة المدفوعة</h3>", unsafe_allow_html=True)
        code = st.text_input("أدخل كود التفعيل هنا:", key="activation_code_input", help="أدخل الكود الذي حصلت عليه لتفعيل النسخة الكاملة.")
        if st.button("✅ تفعيل الآن", key="activate_button", use_container_width=True):
            if code and activate_app(code.strip()):
                st.success("✅ تم التفعيل بنجاح! يرجى إعادة تشغيل التطبيق لتطبيق التغييرات.")
                st.stop()
            else:
                st.error("❌ كود التفعيل غير صحيح أو انتهت صلاحيته.")

# ----------------------------------------------------
# نقطة البداية
# ----------------------------------------------------
if __name__ == "__main__":
    main()
