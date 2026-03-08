import pandas as pd
import streamlit as st

# إعداد الصفحة
st.set_page_config(page_title="نظام البحث ", layout="wide")

# ================== رابط ملف OneDrive ==================
ONEDRIVE_FILE = "https://mersalcharity-my.sharepoint.com/:x:/g/personal/omar_abdallah_mersal-ngo_org1/IQAZAIJBc3rMR4MABivs_NY4AU9ZwCDrPRi6BkAVIcAzCsY?e=NA7XBf"


# ================== 1. نظام تسجيل الدخول ==================
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if st.session_state["password_correct"]:
        return True

    st.title("🔐 تسجيل الدخول للنظام الخاص")
    user = st.text_input("اسم المستخدم (Username)")
    pw = st.text_input("كلمة المرور (Password)", type="password")
    
    if st.button("دخول"):
        if user == "admin" and pw == "12345":
            st.session_state["password_correct"] = True
            st.rerun()
        else:
            st.error("❌ اسم المستخدم أو كلمة المرور غير صحيحة")
    return False


# تشغيل التطبيق فقط في حالة تسجيل الدخول
if check_password():

    # ================== تنظيف النصوص ==================
    def normalize_text(text):
        if not isinstance(text, str):
            text = str(text)

        t = text.strip().lower()
        t = t.replace('أ','ا').replace('إ','ا').replace('آ','ا').replace('ة','ه').replace('ى','ي')

        return " ".join(t.split())


    # ================== تحميل البيانات من OneDrive ==================
    @st.cache_data(show_spinner="جاري تحميل البيانات من OneDrive...")
    def build_index():

        all_data = []

        try:

            df = pd.read_excel(ONEDRIVE_FILE, engine="openpyxl")

            df.columns = [normalize_text(str(c)) for c in df.columns]

            df = df.astype(str).replace('nan','')

            for i,row in df.iterrows():

                def get_flexible_val(keywords):

                    for kw in keywords:

                        norm_kw = normalize_text(kw)

                        for col in df.columns:

                            if norm_kw in col:

                                return row[col].strip()

                    return ""

                all_data.append({

                  str(row.get("C-Code","")),
                                str(row.get("Name","")),
                                str(row.get("موقف الحالة","")),
                                str(row.get("الرقم القومى","")),
                                str(row.get("تاريخ الميلاد","")),
                                str(row.get("رقم كارت المفاوضية للفرد","")),
                                str(row.get("رقم ملف المفاوضية","")),
                                str(row.get("كود المفاوضية","")),
                                str(row.get("موقف اللجوء","")),

               
                })

        except Exception as e:

            st.error(f"خطأ في تحميل البيانات: {e}")

        return pd.DataFrame(all_data)


    # تحميل البيانات
    index_df = build_index()


    # ================== البحث ==================
    q_name = st.sidebar.text_input("اسم الحالة")

    q_code = st.sidebar.text_input("الكود")

 


    if st.sidebar.button("ابدأ البحث"):

        if index_df.empty:

            st.error("⚠️ قاعدة البيانات فارغة.")

        else:

            res = index_df.copy()

            if q_name:
                res = res[
                    res["اName"]
                    .apply(normalize_text)
                    .str.contains(normalize_text(q_name), na=False)
                ]

            if q_code:
                res = res[
                    res["C-Code"].str.strip() == q_code.strip()
                ]


            if res.empty:

                st.warning("❌ لا توجد نتائج مطابقة.")

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



