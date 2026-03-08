import os
from pathlib import Path
import pandas as pd
import streamlit as st

# إعداد الصفحة يجب أن يكون أول أمر من أوامر streamlit
st.set_page_config(page_title="نظام البحث ", layout="wide")

# ================== 1. نظام تسجيل الدخول ==================
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if st.session_state["password_correct"]:
        return True

    # واجهة تسجيل الدخول
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


# تشغيل التطبيق فقط في حالة تسجيل الدخول بنجاح
if check_password():
    
    # ================== 2. إعدادات المسارات والبيانات ==================
    BASE_DIR = Path(__file__).parent if "__file__" in locals() else Path.cwd()
    DATA_FOLDER = BASE_DIR / "data"

    if not DATA_FOLDER.exists():
        DATA_FOLDER.mkdir(parents=True, exist_ok=True)

    # دالة تنظيف النصوص
    def normalize_text(text):
        if not isinstance(text, str): 
            text = str(text)
        t = text.strip().lower()
        t = t.replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا').replace('ة', 'ه').replace('ى', 'ي')
        return " ".join(t.split())

    # ================== 3. بناء الفهرس ==================
    @st.cache_data(show_spinner="جاري معالجة الملفات...")
    def build_index():
        all_data = []
        files = list(DATA_FOLDER.glob("*.xls*"))
        
        for file_path in files:
            if file_path.name.startswith("~$"): 
                continue
            try:
                engine = 'openpyxl' if file_path.suffix != '.xls' else 'xlrd'
                df = pd.read_excel(file_path, engine=engine)

                df.columns = [normalize_text(str(c)) for c in df.columns]
                df = df.astype(str).replace('nan', '')

                for i, row in df.iterrows():
                    def get_flexible_val(keywords):
                        for kw in keywords:
                            norm_kw = normalize_text(kw)
                            for col in df.columns:
                                if norm_kw in col:
                                    return row[col].strip()
                        return ""

                    all_data.append({
                        "الكود": row["الكود"].strip() if "الكود" in df.columns else (
                              row["كود"].strip() if "كود" in df.columns else ""),
                        "اسم الفرد": get_flexible_val(["اسم الفرد", "الاسم", "مريض"]),
                        "الخدمة": get_flexible_val(["الخدمة", "الاجراء", "نوع الخدمة", "خدمه"]),
                        "التاريخ": get_flexible_val(["التاريخ", "تاريخ"]),
                        "الملف": file_path.name,
                        "السطر": i + 2
                    })
            except:
                continue
        return pd.DataFrame(all_data)

    # تحميل البيانات مباشرة
    index_df = build_index()
    # ================== 4. البحث ==================
    q_name = st.sidebar.text_input(" اسم الحالة")
    q_code = st.sidebar.text_input(" الكود")
    q_serv = st.sidebar.text_input("الخدمة ")
    q_date = st.sidebar.text_input("التاريخ ")

    if st.sidebar.button("ابدأ البحث"):
        if index_df.empty:
            st.error("⚠️ قاعدة البيانات فارغة.")
        else:
            res = index_df.copy()

            if q_name:
                res = res[res["اسم الفرد"].apply(normalize_text).str.contains(normalize_text(q_name), na=False)]
            if q_code:
                 res = res[res["الكود"].str.strip() == q_code.strip()]
            if q_serv:
                res = res[res["الخدمة"].apply(normalize_text).str.contains(normalize_text(q_serv), na=False)]
            if q_date:
                res = res[res["التاريخ"].str.contains(q_date, na=False)]

            if res.empty:
                st.warning("❌ لا توجد نتائج مطابقة.")
            else:
                st.success(f"✅ تم العثور على {len(res)} نتيجة")
                st.dataframe(res, use_container_width=True)
                st.download_button(
                    "📥 تحميل النتائج CSV",
                    data=res.to_csv(index=False).encode('utf-8-sig'),
                    file_name="search_results.csv"
                )

    # زر خروج
    if st.sidebar.button("🔒 تسجيل الخروج"):
        st.session_state["password_correct"] = False
        st.rerun()
