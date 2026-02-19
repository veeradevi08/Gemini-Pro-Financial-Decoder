import streamlit as st
import pandas as pd
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
import google.generativeai as genai
from dotenv import load_dotenv
load_dotenv()

# ----------------------------
# PAGE CONFIG
# ----------------------------
st.set_page_config(page_title="Gemini Pro Financial Decoder", layout="wide")

# ----------------------------
# CUSTOM CSS
# ----------------------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #E6E6FA, #FFC0CB);
}

.upload-card {
    background: white;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.08);
    text-align: center;
}

div.stButton > button {
    background-color: #1f77ff;
    color: white;
    font-size: 18px;
    padding: 10px 25px;
    border-radius: 10px;
    border: none;
}
</style>
""", unsafe_allow_html=True)

# ----------------------------
# HEADING
# ----------------------------
st.markdown("<h1 style='text-align:center;'>💎 Gemini Pro Financial Decoder</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align:center;'>Upload Financial Sheets & Get Smart Insights</h4>", unsafe_allow_html=True)
st.write("")

# ----------------------------
# FILE UPLOAD SECTION
# ----------------------------
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown('<div class="upload-card">', unsafe_allow_html=True)
    balance_file = st.file_uploader("📊 Upload Balance Sheet", type=["csv", "xlsx"])
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="upload-card">', unsafe_allow_html=True)
    profit_file = st.file_uploader("📈 Upload Profit & Loss", type=["csv", "xlsx"])
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="upload-card">', unsafe_allow_html=True)
    cash_file = st.file_uploader("💵 Upload Cash Flow", type=["csv", "xlsx"])
    st.markdown('</div>', unsafe_allow_html=True)

st.write("")

# ----------------------------
# GEMINI CONFIGURATION
# ----------------------------
import os

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)


# ----------------------------
# FILE LOADER FUNCTION
# ----------------------------
def load_file(file):
    if file.name.endswith(".csv"):
        return pd.read_csv(file)
    else:
        return pd.read_excel(file)

# ----------------------------
# GEMINI SUMMARY FUNCTION
# ----------------------------
def generate_summary(balance_data, profit_data, cash_data):

    combined_text = ""

    if balance_data is not None:
        combined_text += "\nBalance Sheet:\n" + balance_data.head(15).to_string()

    if profit_data is not None:
        combined_text += "\nProfit & Loss:\n" + profit_data.head(15).to_string()

    if cash_data is not None:
        combined_text += "\nCash Flow:\n" + cash_data.head(15).to_string()

    prompt = f"""
    You are a professional financial analyst.
    Analyze the financial statements and provide:
    - Summary
    - Key Metrics
    - Trends
    - Overall Financial Health

    {combined_text}
    """

    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content(prompt)

    return response.text

# ----------------------------
# PDF CREATION FUNCTION
# ----------------------------
def create_pdf(text):
    filename = "Financial_Report.pdf"
    doc = SimpleDocTemplate(filename, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    for line in text.split("\n"):
        elements.append(Paragraph(line, styles["Normal"]))
        elements.append(Spacer(1, 0.2 * inch))

    doc.build(elements)
    return filename

# ----------------------------
# VISUALIZATION FUNCTION (Milestone Requirement)
# ----------------------------
def create_visuals(data, title):
    if data is not None:
        st.subheader(title)
        st.write(data)

        numeric_data = data.select_dtypes(include=['number'])

        if not numeric_data.empty:
            col1, col2, col3 = st.columns([1, 2, 1])  # center medium width

            with col2:
                st.line_chart(numeric_data)

# ----------------------------
# ANALYZE BUTTON
# ----------------------------
if st.button("🔍 Analyze Financial Data"):

    if not balance_file and not profit_file and not cash_file:
        st.warning("Please upload at least one file.")
    else:
        with st.spinner("Analyzing... Please wait..."):

            balance_data = load_file(balance_file) if balance_file else None
            profit_data = load_file(profit_file) if profit_file else None
            cash_data = load_file(cash_file) if cash_file else None

            summary = generate_summary(balance_data, profit_data, cash_data)

            # Display Summary
            st.subheader("📊 Financial Analysis Report")
            st.write(summary)

            # Visualizations
            st.subheader("📈 Financial Visualizations")

            create_visuals(balance_data, "Balance Sheet")
            create_visuals(profit_data, "Profit & Loss Statement")
            create_visuals(cash_data, "Cash Flow Statement")

            # PDF Download
            pdf_file = create_pdf(summary)

            with open(pdf_file, "rb") as f:
                st.download_button(
                    "📥 Download Report as PDF",
                    f,
                    file_name="Financial_Report.pdf",
                    mime="application/pdf"
                )
