import streamlit as st
import pandas as pd
from io import BytesIO
import plotly.express as px

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

def main_app():
    st.set_page_config(page_title="Student Records Dashboard", page_icon="🎓", layout="wide")

    col_left, col_right = st.columns([9, 1])
    with col_left:
        st.image(
            "https://images.unsplash.com/photo-1529070538774-1843cb3265df?auto=format&fit=crop&w=400&q=80",
            width=80, caption=None)
        st.markdown(
            "<h1 style='color:#114b5f; display:inline-block; padding-left:10px;'>Student Academic & Financial Records Dashboard</h1>",
            unsafe_allow_html=True)
    with col_right:
        logout_clicked = st.button("👤 Logout", use_container_width=True)
        if logout_clicked:
            st.session_state["logged_in"] = False
            st.success("Logged out successfully.")
            st.experimental_rerun()

    st.markdown("""
    <p style='font-size:16px; color:#5a7d7c; margin-top:-10px;'>
        Upload your student data Excel file below to see processed academic and financial results, 
        with live analytics and detailed insights.
    </p>
    """, unsafe_allow_html=True)

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

    template_data = generate_template()
    st.download_button(
        label="⬇️ Download Empty Student Data Template",
        data=template_data,
        file_name="student_data_template.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    uploaded_file = st.file_uploader("Upload Student Data Excel", type=['xls', 'xlsx'])

    def calculate_formulas(df):
        df['Stu_Total_Marks'] = df['Stu_Internal_marks'] + df['Stu_external_Marks']
        def grade(total):
            if total >= 90: return "A+"
            elif total >= 80: return "A"
            elif total >= 70: return "B"
            elif total >= 60: return "C"
            else: return "F"
        df['Stu_Grade'] = df['Stu_Total_Marks'].apply(grade)
        def gpa_sub(marks):
            if marks >= 90: return 10
            elif marks >= 80: return 9
            elif marks >= 70: return 8
            elif marks >= 60: return 7
            elif marks >= 50: return 6
            elif marks >= 40: return 5
            else: return 0
        df['Stu_GPA_Sub'] = df['Stu_external_Marks'].apply(gpa_sub)
        df['Stu_SGPA'] = df['Stu_external_Marks'].apply(gpa_sub)
        df['Stu_attended_percentage'] = (df['Stu_attended'] / df['Stu_total_Classes']) * 100
        df['Stu_Attendance_status'] = df['Stu_attended_percentage'].apply(lambda x: "Eligible" if x >= 75 else "Not Eligible")
        df['Stu_fee_due'] = df['Stu_tution_Fees'] - df['Stu_fee_paid']
        df['Stu_payment_status'] = df['Stu_fee_due'].apply(lambda x: "Paid" if x <= 0 else "Pending")
        return df

    if uploaded_file:
        try:
            df_input = pd.read_excel(uploaded_file)
            required = ["Stu_Internal_marks", "Stu_external_Marks", "Stu_total_Classes", "Stu_attended", "Stu_tution_Fees", "Stu_fee_paid"]
            missing = [col for col in required if col not in df_input.columns]
            if missing:
                st.error(f"Missing columns: {missing}")
            else:
                st.markdown("### Raw Input Data")
                st.dataframe(df_input, use_container_width=True)
                df_processed = calculate_formulas(df_input)
                st.markdown("### Processed Data")
                st.dataframe(df_processed, use_container_width=True)

                depts = sorted(df_processed['Stud_Department'].dropna().unique())
                years = sorted(df_processed['Stu_Year'].dropna().unique())
                names = sorted(df_processed['Stu_name'].dropna().unique())
                semesters = sorted(df_processed['Stu_Semester'].dropna().unique())

                st.sidebar.header("Filter Analytics")
                dept_filter = st.sidebar.multiselect("Department", depts, default=depts)
                year_filter = st.sidebar.multiselect("Academic Year", years, default=years)
                name_filter = st.sidebar.multiselect("Student", names, default=names)
                sem_filter = st.sidebar.multiselect("Semester", semesters, default=semesters)

                df_filtered = df_processed[
                    (df_processed['Stud_Department'].isin(dept_filter)) &
                    (df_processed['Stu_Year'].isin(year_filter)) &
                    (df_processed['Stu_name'].isin(name_filter)) &
                    (df_processed['Stu_Semester'].isin(sem_filter))
                ]

                st.markdown("---")
                st.markdown("## Live Analytics")

                # Grade Distribution Pie Chart
                grade_counts = df_filtered['Stu_Grade'].value_counts().reset_index()
                grade_counts.columns = ['Grade', 'Count']
                fig1 = px.pie(grade_counts, names='Grade', values='Count',
                              title='Grade Distribution',
                              color_discrete_sequence=px.colors.qualitative.Pastel)
                st.plotly_chart(fig1, use_container_width=True)

                # Attendance Status Bar Chart
                attendance_counts = df_filtered['Stu_Attendance_status'].value_counts().reset_index()
                attendance_counts.columns = ['Attendance Status', 'Count']
                fig2 = px.bar(attendance_counts, x='Attendance Status', y='Count',
                              title='Attendance Status',
                              color='Attendance Status',
                              color_discrete_map={"Eligible": "green", "Not Eligible": "red"})
                st.plotly_chart(fig2, use_container_width=True)

                # ----------- Attendance Analysis Graph -----------
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
                # -----------------------------------------------

                # Payment Status Bar Chart
                payment_counts = df_filtered['Stu_payment_status'].value_counts().reset_index()
                payment_counts.columns = ['Payment Status', 'Count']
                fig3 = px.bar(payment_counts, x='Payment Status', y='Count',
                              title='Payment Status',
                              color='Payment Status',
                              color_discrete_map={"Paid": "green", "Pending": "orange"})
                st.plotly_chart(fig3, use_container_width=True)

                # ----------- Fees Related Graphs ----------------
                # Outstanding Fee Amounts per Student
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

                # Total amount pending vs paid pie chart
                fee_summary = df_filtered.groupby('Stu_payment_status')['Stu_fee_due'].sum().reset_index()
                fig_fee_summary = px.pie(
                    fee_summary,
                    names='Stu_payment_status',
                    values='Stu_fee_due',
                    title='Total Paid vs Pending Fees',
                    color='Stu_payment_status',
                    color_discrete_map={'Paid': 'green', 'Pending': 'orange'}
                )
                st.plotly_chart(fig_fee_summary, use_container_width=True)
                # -----------------------------------------------

                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df_processed.to_excel(writer, index=False, sheet_name='ProcessedData')
                    writer.save()
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

    st.markdown("""
    ---
    <div style='font-size:12px; color:gray; text-align:center;'>
        Developed by  🎓
    </div>
    """, unsafe_allow_html=True)

# Session state initialization
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    login()
else:
    main_app()
