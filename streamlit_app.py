import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from fpdf import FPDF
import tempfile
import os
from streamlit_option_menu import option_menu
import matplotlib as mpl

st.set_page_config(page_title="Churnlytics", layout="wide")

# a toggle Button on the top-right
left, right = st.columns([10, 2])
with right:
    dark_mode = st.toggle("🌙 Dark Mode")

css = """
        <style>
        body {
            background-color: #1e1e1e;
            color: #ffffff;
        }
        .stApp {
            background-color: #1e1e1e;
            color: white;
        }
        .stDataFrame, .stTable, .stMarkdown {
            background-color: #2c2c2c !important;
            color: white !important;
        }
        .stTextInput>div>div>input,
        .stSelectbox>div>div>div>input {
            background-color: #2c2c2c;
            color: white;
        }
        .stDownloadButton>button {
            background-color: #444;
            color: white;
        }
        .stButton>button {
            background-color: #444;
            color: white;
        }
        .css-1offfwp {
            background-color: #2c2c2c;
            color: white;
        }
        </style>
        """

if dark_mode:
    st.markdown(css,unsafe_allow_html=True)

if dark_mode:
    # Dark theme for plots
    mpl.rcParams.update({
        "axes.facecolor": "#2c2c2c",
        "figure.facecolor": "#2c2c2c",
        "axes.edgecolor": "white",
        "axes.labelcolor": "white",
        "xtick.color": "white",
        "ytick.color": "white",
        "text.color": "white",
        "axes.titlecolor": "white",
    })
    sns.set_theme(style="darkgrid")
else:
    # Reset to default light mode
    mpl.rcParams.update(mpl.rcParamsDefault)
    sns.set_theme(style="whitegrid")

if "generated_figures" not in st.session_state:
    st.session_state.generated_figures = []

# === Sidebar Navigation ===
# st.sidebar.title("Mainmanu")
# section = st.sidebar.radio("Go to", ["Upload & Preview", "Summary & Filter", "Visualizations", "Export Report"])

with st.sidebar:
    section = option_menu(
        "MainManu", 
        ["Upload & Preview", "Summary & Filter", "Visualizations", "Export Report"],
        icons=["cloud-upload", "funnel", "bar-chart", "file-earmark-pdf"], 
        menu_icon="cast", 
        default_index=0,
        styles={
            "container": {
                "padding": "10px",
                "background-color": "#f8f9fa",
                "border-radius": "8px"
            },
            "icon": {
                "color": "#0d6efd",
                "font-size": "18px"
            },
            "nav-link": {
                "font-size": "16px",
                "text-align": "left",
                "margin": "5px 0",
                "padding": "10px",
                "border-radius": "6px",
                "color": "#212529"
            },
            "nav-link-hover": {
                "background-color": "#e9ecef",
                "color": "white"
            },
            "nav-link-selected": {
                "background-color": "#0d6efd",
                "color": "white",
                "font-weight": "bold"
            }
        }
    )

# === Page Title ===
# st.title("Churnlytics Churn-focused analytics for any domain.")
st.markdown("""
<h2>📊 <b>Churnlytics</b><br>
<span style='font-size:16px; font-style:italic;'>Churn-focused analytics visuals</span>
</h2>
""", unsafe_allow_html=True)

# === File Upload ===
uploaded_file = st.sidebar.file_uploader("📂 Upload File", type=["csv", "xlsx", "json", "txt"])

# === Load Data ===
df = None
file_name = None
if uploaded_file:
    file_name = uploaded_file.name.lower()
    try:
        if file_name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        elif file_name.endswith((".xls", ".xlsx")):
            df = pd.read_excel(uploaded_file)
        elif file_name.endswith(".json"):
            df = pd.read_json(uploaded_file)
        elif file_name.endswith(".txt"):
            df = pd.read_csv(uploaded_file, delimiter="\t")
    except Exception as e:
        st.error(f"❌ Failed to load data: {e}")

# === Section 1: Upload & Preview ===
if section == "Upload & Preview":
    if df is not None:
        st.success(f"📄 File uploaded: `{file_name}`")
        st.subheader("📊 Data Preview")
        st.dataframe(df)
    else:
        st.info("⬆️ Upload a file to begin.")

# === Section 2: Summary & Filter ===
elif section == "Summary & Filter":
    if df is not None:
        st.subheader("📈 Data Summary")
        st.write(df.describe())

        st.markdown("### 🔍 Filter Data")
        filters = {}
        for col in df.select_dtypes(include='object').columns:
            options = df[col].unique().tolist()
            selected = st.multiselect(f"Filter by {col}", options, default=options)
            df = df[df[col].isin(selected)]

        st.markdown("### 📤 Download Filtered Data")
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download CSV", csv, "filtered_data.csv", "text/csv")
    else:
        st.warning("Please upload a file first.")

# === Section 3: Visualizations ===
elif section == "Visualizations":
    if df is not None:
        st.subheader("📊 Custom Visualizations")

        numeric_cols = df.select_dtypes(include='number').columns.tolist()
        cat_cols = df.select_dtypes(include='object').columns.tolist()

        num_charts = st.number_input("➕ Number of charts to add", 1, 10, 1, 1)
        chart_options = ["Bar Chart", "Line Chart", "Histogram", "Box Plot", "Scatter Plot", "Pie Chart", "Correlation Heatmap"]

        st.session_state.generated_figures = [] 

        for i in range(num_charts):
            with st.expander(f"📌 Chart {i+1}"):
                chart_type = st.selectbox(f"Chart Type {i+1}", chart_options, key=f"type_{i}")
                caption = st.text_input("📝 Chart Caption", f"My {chart_type}", key=f"caption_{i}")
                col1, col2 = st.columns(2)

                if chart_type == "Bar Chart":
                    with col1:
                        col = st.selectbox("Column", cat_cols, key=f"bar_{i}")
                    with col2:
                        fig, ax = plt.subplots()
                        df[col].value_counts().plot(kind="bar", ax=ax)
                        ax.set_title(caption)
                        st.pyplot(fig)
                        st.session_state.generated_figures.append((fig, caption))

                elif chart_type == "Line Chart":
                    with col1:
                        col = st.selectbox("Numeric Column", numeric_cols, key=f"line_{i}")
                    with col2:
                        fig, ax = plt.subplots()
                        df[col].plot(kind="line", ax=ax)
                        ax.set_title(caption)
                        st.pyplot(fig)
                        st.session_state.generated_figures.append((fig, caption))

                elif chart_type == "Histogram":
                    with col1:
                        col = st.selectbox("Numeric Column", numeric_cols, key=f"hist_{i}")
                    with col2:
                        fig, ax = plt.subplots()
                        sns.histplot(df[col], kde=True, ax=ax)
                        ax.set_title(caption)
                        st.pyplot(fig)
                        st.session_state.generated_figures.append((fig, caption))

                elif chart_type == "Box Plot":
                    with col1:
                        y_col = st.selectbox("Y-axis (numeric)", numeric_cols, key=f"box_y_{i}")
                        x_col = st.selectbox("X-axis (categorical)", cat_cols, key=f"box_x_{i}")
                    with col2:
                        fig, ax = plt.subplots()
                        sns.boxplot(x=df[x_col], y=df[y_col], ax=ax)
                        ax.set_title(caption)
                        st.pyplot(fig)
                        st.session_state.generated_figures.append((fig, caption))

                elif chart_type == "Scatter Plot":
                    with col1:
                        x = st.selectbox("X-axis", numeric_cols, key=f"sc_x_{i}")
                        y = st.selectbox("Y-axis", numeric_cols, key=f"sc_y_{i}")
                    with col2:
                        fig, ax = plt.subplots()
                        sns.scatterplot(x=df[x], y=df[y], ax=ax)
                        ax.set_title(caption)
                        st.pyplot(fig)
                        st.session_state.generated_figures.append((fig, caption))

                elif chart_type == "Pie Chart":
                    with col1:
                        cat_col = st.selectbox("Categorical Column", cat_cols, key=f"pie_{i}")
                    with col2:
                        data = df[cat_col].value_counts()
                        fig, ax = plt.subplots()
                        ax.pie(data, labels=data.index, autopct='%1.1f%%', startangle=90)
                        ax.set_title(caption)
                        ax.axis('equal')
                        st.pyplot(fig)
                        st.session_state.generated_figures.append((fig, caption))

                elif chart_type == "Correlation Heatmap":
                    with col2:
                        corr = df[numeric_cols].corr()
                        fig, ax = plt.subplots(figsize=(8, 5))
                        sns.heatmap(corr, annot=True, cmap='coolwarm', ax=ax)
                        ax.set_title(caption)
                        st.pyplot(fig)
                        st.session_state.generated_figures.append((fig, caption))

    else:
        st.warning("Please upload data to visualize.")

# === Section 4: Export Report ===
elif section == "Export Report":
    if df is not None:
        st.subheader("🧾 Generate PDF Report of Visuals")

        def generate_pdf(figures_captions):
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            temp_files = []

            for fig, caption in figures_captions:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
                    fig.savefig(tmpfile.name, format="png", bbox_inches='tight')
                    temp_files.append(tmpfile.name)
                    pdf.add_page()
                    pdf.set_font("Arial", size=12)
                    pdf.multi_cell(0, 10, caption)
                    pdf.image(tmpfile.name, x=10, y=30, w=180)

            pdf_output = pdf.output(dest='S').encode('latin-1')

            for temp_file in temp_files:
                try:
                    os.remove(temp_file)
                except Exception:
                    pass

            return pdf_output
        
        if st.session_state.generated_figures:
            pdf_bytes = generate_pdf(st.session_state.generated_figures)
            st.download_button(
                label="📄 Download Full Report (PDF)",
                data=pdf_bytes,
                file_name="employee_attrition_report.pdf",
                mime="application/pdf"
            )
        else:
            st.info("⚠️ You must first generate charts in the Visualizations tab.")
    else:
        st.warning("Upload your data first.")