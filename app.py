import os
from pathlib import Path
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



    
# ================== استدعاء الداتا ==================
ONEDRIVE_URL = "https://mersalcharity-my.sharepoint.com/:x:/g/personal/omar_abdallah_mersal-ngo_org1/IQAZAIJBc3rMR4MABivs_NY4AewjiwrpDvZzAH-BdcsHcdk?download=1"

@st.cache_data
def load_data():

    r = requests.get(ONEDRIVE_URL)

    file = BytesIO(r.content)

    df = pd.read_excel(file)

    return df
 

    # ================== تنظيف النص ==================
    def normalize_text(text):

        if not isinstance(text, str):
            text = str(text)

        t = text.strip().lower()

        t = t.replace('أ','ا').replace('إ','ا').replace('آ','ا')
        t = t.replace('ة','ه').replace('ى','ي')

        return " ".join(t.split())


    # ================== بناء الفهرس ==================
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

                df.columns = [str(c).strip() for c in df.columns]

                df = df.astype(str).replace('nan','')

                for i, row in df.iterrows():

                    all_data.append({

                        "C-Code": row.get("C-Code",""),
                        "Name": row.get("Name",""),
                        "موقف الحالة": row.get("موقف الحالة",""),
                        "الرقم القومى": row.get("الرقم القومى",""),
                        "تاريخ الميلاد": row.get("تاريخ الميلاد",""),
                        "رقم كارت المفاوضية للفرد": row.get("رقم كارت المفاوضية للفرد",""),
                        "رقم ملف المفاوضية": row.get("رقم ملف المفاوضية",""),
                        "كود المفاوضية": row.get("كود المفاوضية",""),
                        "موقف اللجوء": row.get("موقف اللجوء",""),
                        "الملف": file_path.name,
                        "السطر": i + 2

                    })

            except:
                continue

        return pd.DataFrame(all_data)


    # تحميل البيانات
    index_df = build_index()


    # ================== البحث ==================
    st.sidebar.header("🔎 البحث")

    q_code = st.sidebar.text_input("الكود / رقم الملف / كارت المفوضية")

    q_name = st.sidebar.text_input("الاسم")


    if st.sidebar.button("ابدأ البحث"):

        if index_df.empty:

            st.error("⚠️ قاعدة البيانات فارغة")

        else:

            res = index_df.copy()

            # البحث بالكود
            if q_code:

                res = res[

                    (res["C-Code"].astype(str).str.strip() == q_code.strip()) |

                    (res["رقم كارت المفاوضية للفرد"].astype(str).str.strip() == q_code.strip()) |

                    (res["رقم ملف المفاوضية"].astype(str).str.strip() == q_code.strip()) |

                    (res["كود المفاوضية"].astype(str).str.strip() == q_code.strip())

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

                st.download_button(
                    "📥 تحميل النتائج CSV",
                    data=res.to_csv(index=False).encode('utf-8-sig'),
                    file_name="search_results.csv"
                )


    # ================== تسجيل الخروج ==================
    if st.sidebar.button("🔒 تسجيل الخروج"):

        st.session_state["password_correct"] = False

        st.rerun()


