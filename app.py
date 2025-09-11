import streamlit as st
import pandas as pd
# Correct top-level import
import plotly.express as px

def some_function():
    # function code indented here
from io import BytesIO
 
# Always set this at top
st.set_page_config(page_title="Student Records Dashboard", page_icon="🎓", layout="wide")
 
def login():
    st.title("🔐 Login to Student Records Dashboard")
    username = st.text_input("Username")
    password = st.text_input("Password", type='password')
    login_button = st.button("Login")
    if login_button:
        if username == "admin" and password == "password123":
            st.session_state["logged_in"] = True
            st.success("Login successful! Redirecting...")
            st.experimental_rerun()
        else:
            st.error("Invalid username or password")
 
@st.cache_data
def generate_template():
    columns = [
        "Stu_ID","Stu_name","Stu_Gender","Stu_DOB","Stu_AGE","Stu_Email","Stu_Phone_No","Stu_Address",
        "Stud_Department","Stu_program","Stu_Year","Stu_enrollment_year","Stu_Semester",
        "Stu_Coure_code","Stu_Coure_Name","Stu_Internal_marks","Stu_external_Marks",
        "Stu_total_Classes","Stu_attended","Stu_tution_Fees","Stu_fee_paid"
    ]
    df = pd.DataFrame(columns=columns)
    output = BytesIO()
    df.to_excel(output, index=False)
    return output.getvalue()
 
def calculate_formulas(df):
    # Ensure numeric columns for calculation
    num_cols = [
        "Stu_Internal_marks", "Stu_external_Marks", "Stu_total_Classes",
        "Stu_attended", "Stu_tution_Fees", "Stu_fee_paid"
    ]
    for col in num_cols:
        if col not in df.columns:
            df[col] = 0
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
 
    df['Stu_Total_Marks'] = df['Stu_Internal_marks'] + df['Stu_external_Marks']
    df['Stu_Grade'] = df['Stu_Total_Marks'].apply(lambda x: 'A+' if x>=90 else 'A' if x>=80 else 'B' if x>=70 else 'C' if x>=60 else 'F')
    df['Stu_GPA_Sub'] = df['Stu_external_Marks'].apply(lambda x: 10 if x>=90 else 9 if x>=80 else 8 if x>=70 else 7 if x>=60 else 6 if x>=50 else 5 if x>=40 else 0)
    df['Stu_SGPA'] = df['Stu_external_Marks'].apply(lambda x: 10 if x>=90 else 9 if x>=80 else 8 if x>=70 else 7 if x>=60 else 6 if x>=50 else 5 if x>=40 else 0)
    df['Stu_attended_percentage'] = (df['Stu_attended'] / df['Stu_total_Classes'].replace(0, pd.NA)) * 100
    df['Stu_attended_percentage'] = df['Stu_attended_percentage'].fillna(0)
    df['Stu_Attendance_status'] = df['Stu_attended_percentage'].apply(lambda x: "Eligible" if x >= 75 else "Not Eligible")
    df['Stu_fee_due'] = df['Stu_tution_Fees'] - df['Stu_fee_paid']
    df['Stu_payment_status'] = df['Stu_fee_due'].apply(lambda x: "Paid" if x <= 0 else "Pending")
    return df
 
def main_app():
    # Header and logout
    col_left, col_right = st.columns([9, 1])
    with col_left:
        st.image(
            "https://images.unsplash.com/photo-1529070538774-1843cb3265df?auto=format&fit=crop&w=400&q=80",
            width=80)
        st.markdown(
            "<h1 style='color:#114b5f; display:inline-block; padding-left:10px;'>Student Academic & Financial Records Dashboard</h1>",
            unsafe_allow_html=True)
    with col_right:
        if st.button("👤 Logout", use_container_width=True):
            st.session_state["logged_in"] = False
            st.success("Logged out successfully.")
            st.experimental_rerun()
        
    st.markdown("<p style='font-size:16px; color:#5a7d7c; margin-top:-10px;'>"
        "Upload your student data Excel file below to see processed academic and financial results, "
        "with live analytics and detailed insights.</p>", unsafe_allow_html=True)
    
    # Template download
    template_data = generate_template()
    st.download_button("⬇️ Download Empty Student Data Template",
        data=template_data,
        file_name="student_data_template.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
 
    uploaded_file = st.file_uploader("Upload Student Data Excel", type=['xls', 'xlsx'])
    if uploaded_file:
        try:
            df_input = pd.read_excel(uploaded_file)
            required = ["Stu_Internal_marks", "Stu_external_Marks", "Stu_total_Classes",
                "Stu_attended", "Stu_tution_Fees", "Stu_fee_paid"]
            missing = [col for col in required if col not in df_input.columns]
            if missing:
                st.error(f"Missing columns: {missing}")
                st.stop()
            st.markdown("### Raw Input Data")
            st.dataframe(df_input, use_container_width=True)
 
            df_processed = calculate_formulas(df_input)
            st.markdown("### Processed Data")
            st.dataframe(df_processed, use_container_width=True)
 
            # Set up sidebar filters, always checks if column exists
            depts = sorted(df_processed['Stud_Department'].dropna().unique()) if 'Stud_Department' in df_processed.columns else []
            years = sorted(df_processed['Stu_Year'].dropna().unique()) if 'Stu_Year' in df_processed.columns else []
            names = sorted(df_processed['Stu_name'].dropna().unique()) if 'Stu_name' in df_processed.columns else []
            semesters = sorted(df_processed['Stu_Semester'].dropna().unique()) if 'Stu_Semester' in df_processed.columns else []
 
            st.sidebar.header("Filter Analytics")
            dept_filter = st.sidebar.multiselect("Department", depts, default=depts)
            year_filter = st.sidebar.multiselect("Academic Year", years, default=years)
            name_filter = st.sidebar.multiselect("Student", names, default=names)
            sem_filter = st.sidebar.multiselect("Semester", semesters, default=semesters)
 
            df_filtered = df_processed
            if depts: df_filtered = df_filtered[df_filtered['Stud_Department'].isin(dept_filter)]
            if years: df_filtered = df_filtered[df_filtered['Stu_Year'].isin(year_filter)]
            if names: df_filtered = df_filtered[df_filtered['Stu_name'].isin(name_filter)]
            if semesters: df_filtered = df_filtered[df_filtered['Stu_Semester'].isin(sem_filter)]
 
            st.markdown("---")
            st.markdown("## Live Analytics")
 
            if len(df_filtered) == 0:
                st.warning("Filtered data is empty. Adjust filters or check your Excel file.")
            else:
                # Grade Distribution Pie Chart
                if 'Stu_Grade' in df_filtered.columns:
                    grade_counts = df_filtered['Stu_Grade'].value_counts().reset_index()
                    grade_counts.columns = ['Grade', 'Count']
                    fig1 = px.pie(grade_counts, names='Grade', values='Count',
                        title='Grade Distribution', color_discrete_sequence=px.colors.qualitative.Pastel)
                    st.plotly_chart(fig1, use_container_width=True)
 
                # Attendance Status Bar Chart
                if 'Stu_Attendance_status' in df_filtered.columns:
                    attendance_counts = df_filtered['Stu_Attendance_status'].value_counts().reset_index()
                    attendance_counts.columns = ['Attendance Status', 'Count']
                    fig2 = px.bar(attendance_counts, x='Attendance Status', y='Count',
                        title='Attendance Status', color='Attendance Status',
                        color_discrete_map={"Eligible": "green", "Not Eligible": "red"})
                    st.plotly_chart(fig2, use_container_width=True)
 
                # Attendance Percentage Histogram
               import plotly.express as px

fig_attendance_dist = px.histogram(
    df_filtered,
    x='Stu_attended_percentage',
    nbins=20,
    title='Attendance Percentage Distribution',
    color_discrete_sequence=['#44b78b']
)
fig_attendance_dist.update_xaxes(title="Attendance Percentage (%)")
fig_attendance_dist.update_yaxes(title="Number of Students")
st.plotly_chart(fig_attendance_dist, use_container_width=True)
                # Payment Status Bar Chart
                if 'Stu_payment_status' in df_filtered.columns:
                    payment_counts = df_filtered['Stu_payment_status'].value_counts().reset_index()
                    payment_counts.columns = ['Payment Status', 'Count']
                    fig3 = px.bar(payment_counts, x='Payment Status', y='Count',
                        title='Payment Status',
                        color='Payment Status',
                        color_discrete_map={"Paid": "green", "Pending": "orange"})
                    st.plotly_chart(fig3, use_container_width=True)
 
                # Outstanding Fee Amounts per Student
                if 'Stu_fee_due' in df_filtered.columns and 'Stu_name' in df_filtered.columns:
                    fig_fees_due = px.bar(
                        df_filtered,
                        x='Stu_name',
                        y='Stu_fee_due',
                        title='Outstanding Fee Amounts per Student',
                        color='Stu_fee_due',
                        color_continuous_scale='Oranges'
                    )
                    fig_fees_due.update_xaxes(title="Student Name")
                    fig_fees_due.update_yaxes(title="Outstanding Fees (INR)")
                    st.plotly_chart(fig_fees_due, use_container_width=True)
 
                # Total Paid vs Pending Fees Pie
               fee_summary = df_filtered.groupby('Stu_payment_status')['Stu_fee_due'].sum().reset_index()

import plotly.express as px

fig_fee_summary = px.pie(
    fee_summary,
    names='Stu_payment_status',
    values='Stu_fee_due',
    title='Total Paid vs Pending Fees',
    color='Stu_payment_status',
    color_discrete_map={'Paid': 'green', 'Pending': 'orange'}
)

fig_fee_summary.update_traces(textinfo='percent+label')
fig_fee_summary.show()
 
            # Download processed file (no .save() or .close())
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df_processed.to_excel(writer, index=False, sheet_name='ProcessedData')
            processed_data = output.getvalue()
            st.download_button(
                label="⬇️ Download Processed Excel",
                data=processed_data,
                file_name="processed_student_data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
 
        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.info("Upload an Excel file to begin processing and see analytics.")
 
    st.markdown("---\n<div style='font-size:12px; color:gray; text-align:center;'>Developed by 🎓</div>", unsafe_allow_html=True)
 
# Session state initialization
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
 
if not st.session_state['logged_in']:
    login()
else:
    main_app()



