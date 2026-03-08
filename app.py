import pandas as pd
import streamlit as st
import requests
from io import BytesIO

# إعداد الصفحة
st.set_page_config(page_title="نظام البحث", layout="wide")

# ================== رابط ملف OneDrive ==================
ONEDRIVE_FILE = "https://mersalcharity-my.sharepoint.com/:x:/g/personal/omar_abdallah_mersal-ngo_org1/IQAZAIJBc3rMR4MABivs_NY4AU9ZwCDrPRi6BkAVIcAzCsY?download=1&web=0"

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


# ================== تشغيل التطبيق ==================
if check_password():

    # ================== تحميل البيانات ==================
    @st.cache_data(show_spinner="جاري تحميل البيانات من OneDrive...")
    def load_data():
        try:
            response = requests.get(ONEDRIVE_FILE)

             df = pd.read_excel(
               BytesIO(response.content),
               engine="openpyxl",
                header=0
           )

               df.columns = df.columns.str.strip()

            # تحويل القيم إلى نص
            df = df.astype(str).replace("nan", "")

            return df

        except Exception as e:
            st.error(f"خطأ في تحميل البيانات: {e}")
            return pd.DataFrame()


    # تحميل البيانات
    index_df = load_data()
st.write(df.head())
st.write(df.columns)
# ================== البحث ==================
    st.sidebar.title("البحث")

    q_name = st.sidebar.text_input("اسم الحالة")
    q_code = st.sidebar.text_input("الكود")

    if st.sidebar.button("ابدأ البحث"):

        if index_df.empty:
            st.error("⚠️ قاعدة البيانات فارغة")

        else:

            res = index_df.copy()

            if q_name:
                res = res[
                    res["Name"].str.contains(q_name, case=False, na=False)
                ]

            if q_code:
                res = res[
                    res["C-Code"].astype(str).str.contains(q_code.strip(), na=False)
                ]

            if res.empty:
                st.warning("❌ لا توجد نتائج مطابقة")

            else:
                st.success(f"✅ تم العثور على {len(res)} نتيجة")

                st.dataframe(res, use_container_width=True)

                st.download_button(
                    "📥 تحميل النتائج CSV",
                    data=res.to_csv(index=False).encode("utf-8-sig"),
                    file_name="search_results.csv"
                )


    # ================== تسجيل الخروج ==================
    if st.sidebar.button("🔒 تسجيل الخروج"):
        st.session_state["password_correct"] = False
        st.rerun()


