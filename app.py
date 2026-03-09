import pandas as pd
import streamlit as st
import requests
from io import BytesIO

# ================== إعداد الصفحة ==================
st.set_page_config(page_title="نظام البحث", layout="wide")

# ================== تسجيل الدخول ==================
def check_password():

    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if st.session_state["password_correct"]:
        return True

    st.title("🔐 تسجيل الدخول للنظام الخاص")

    user = st.text_input("اسم المستخدم")
    pw = st.text_input("كلمة المرور", type="password")

    if st.button("دخول"):
        if user == "admin" and pw == "12345":
            st.session_state["password_correct"] = True
            st.rerun()
        else:
            st.error("❌ اسم المستخدم أو كلمة المرور غير صحيحة")

    return False


# ================== تشغيل النظام بعد تسجيل الدخول ==================
if check_password():

    # ================== رابط OneDrive ==================
    ONEDRIVE_URL = "https://mersalcharity-my.sharepoint.com/:x:/g/personal/omar_abdallah_mersal-ngo_org1/IQAZAIJBc3rMR4MABivs_NY4AU9ZwCDrPRi6BkAVIcAzCsY?download=1"

    # ================== تحميل البيانات ==================
    @st.cache_data(show_spinner="جاري تحميل البيانات من OneDrive...")
    def load_data():

        r = requests.get(ONEDRIVE_URL)

        if r.status_code != 200:
            st.error("فشل تحميل الملف من OneDrive")
            return pd.DataFrame()

        file = BytesIO(r.content)

        try:
            df = pd.read_excel(file, engine="openpyxl", sheet_name="all التكوين")
        except Exception as e:
            st.error(f"⚠️ الملف ليس Excel صحيح: {e}")
            return pd.DataFrame()

        df.columns = [str(c).strip() for c in df.columns]
        df = df.astype(str).replace("nan", "")

        return df


    index_df = load_data()

    # ================== تنظيف النص ==================
    def normalize_text(text):

        if not isinstance(text, str):
            text = str(text)

        t = text.strip().lower()

        t = t.replace('أ','ا').replace('إ','ا').replace('آ','ا')
        t = t.replace('ة','ه').replace('ى','ي')

        return " ".join(t.split())


    # ================== البحث ==================
    st.sidebar.header("🔎 البحث")

    q_code = st.sidebar.text_input("الكود")
    q_name = st.sidebar.text_input("الاسم")
    personall_card = st.sidebar.text_input("رقم كارت المفاوضية للفرد")
    family_card = st.sidebar.text_input("رقم ملف المفاوضية")
    mof_card = st.sidebar.text_input("كود المفاوضية")

    if st.sidebar.button("ابدأ البحث"):

        if index_df.empty:

            st.error("⚠️ قاعدة البيانات فارغة")

        else:

            res = index_df.copy()

            # البحث بالكود
            if q_code:
                res = res[
                    (res["C-Code"].str.strip() == q_code.strip())
                ]

            if personall_card:
                res = res[
                    (res["رقم كارت المفاوضية للفرد"].str.strip() == personall_card.strip())
                ]

            if family_card:
                res = res[
                    (res["رقم ملف المفاوضية"].str.strip() == family_card.strip())
                ]

            if mof_card:
                res = res[
                    (res["كود المفاوضية"].str.strip() == mof_card.strip())
                ]

            # البحث بالاسم
            if q_name:
                res = res[
                    res["Name"].apply(normalize_text)
                    .str.contains(normalize_text(q_name), na=False)
                ]

            if res.empty:

                st.warning("❌ لا توجد نتائج")

            else:

                st.success(f"✅ تم العثور على {len(res)} نتيجة")

                st.dataframe(res, use_container_width=True)


    # ================== تسجيل الخروج ==================
    if st.sidebar.button("🔒 تسجيل الخروج"):

        st.session_state["password_correct"] = False
        st.rerun()
