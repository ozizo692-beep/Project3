import pandas as pd
import streamlit as st

# ================== رابط ملف OneDrive ==================
ONEDRIVE_FILE = "C:\\Users\\omar.shoman\\OneDrive - Mersal Foundation\\Nada\\data.xlsx"
import pandas as pd


# ================== تحميل ملف الخدمات ==================

df = pd.read_excel(ONEDRIVE_FILE)
# ================== BUILD INDEX ==================

@st.cache_data(show_spinner="جاري تحميل البيانات...")
def build_index():

    data = []

    try:

        xls = pd.ExcelFile(ONEDRIVE_FILE)

        for sheet in xls.sheet_names:

            try:

                df = pd.read_excel(ONEDRIVE_FILE, sheet_name=sheet)

                df.columns = df.columns.astype(str).str.strip()

            except:
                continue

            for i, row in df.iterrows():

                data.append([

                    str(row.get("C-Code","")),
                    str(row.get("Name","")),
                    str(row.get("موقف الحالة","")),
                    str(row.get("الرقم القومى","")),
                    str(row.get("تاريخ الميلاد","")),
                    str(row.get("رقم كارت المفاوضية للفرد","")),
                    str(row.get("رقم ملف المفاوضية","")),
                    str(row.get("كود المفاوضية","")),
                    str(row.get("موقف اللجوء","")),
                    "OneDrive"

                ])

    except Exception as e:

        st.error(f"خطأ في تحميل البيانات: {e}")

    df_index = pd.DataFrame(

        data,

        columns=[

            "C-Code",
            "Name",
            "موقف الحالة",
            "الرقم القومى",
            "تاريخ الميلاد",
            "رقم كارت المفاوضية للفرد",
            "رقم ملف المفاوضية",
            "كود المفاوضية",
            "موقف اللجوء",
            "Path"

        ]
    )

    return df_index


# ================== LOAD INDEX ==================

def load_index():

    return build_index()


# ================== SEARCH ==================

def search_index(index_df, code, name):

    df = index_df.copy()

    if code:

        df = df[
            (df["C-Code"].astype(str).str.strip() == code) |

            (df["رقم كارت المفاوضية للفرد"].astype(str).str.strip() == code) |

            (df["رقم ملف المفاوضية"].astype(str).str.strip() == code) |

            (df["كود المفاوضية"].astype(str).str.strip() == code)
        ]

    if name:

        df = df[
            df["Name"].str.contains(name, case=False, na=False)
        ]

    return df


# ================== واجهة Streamlit ==================

st.title("🔎 Search System")

index_df = load_index()

# تقسيم الشاشة مثل مشروعك
left_col, right_col = st.columns([1,3])

with left_col:

    st.subheader("Search")

    code = st.text_input("C-Code")

    name = st.text_input("Name")

    search_btn = st.button("Search")

    results_label = st.empty()

with right_col:

    table_placeholder = st.empty()

# تنفيذ البحث
if search_btn:

    results = search_index(index_df, code, name)

    if results.empty:

        results_label.warning("عدد النتائج: 0")

        table_placeholder.warning("لا توجد نتائج")

    else:

        results_label.success(f"عدد النتائج: {len(results)}")

        table_placeholder.dataframe(
            results,
            use_container_width=True,
            height=500
        )
