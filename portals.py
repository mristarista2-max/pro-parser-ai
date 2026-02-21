import streamlit as st
import re
from database import get_db_connection
from utils import extract_text_from_pdf, send_shortlist_email

def admin_portal():
    st.header("👑 Admin Dashboard")
    conn = get_db_connection()
    
    # --- 1. POST NEW JOB ---
    with st.expander("➕ Post a New Job Vacancy"):
        with st.form(key='job_form', clear_on_submit=True):
            r = st.text_input("Job Role (e.g., Python Developer)")
            e = st.number_input("Minimum Experience Required (Years)", min_value=0)
            s = st.text_area("Required Skills (Comma separated: e.g., Python, SQL, Git)")
            if st.form_submit_button("Post Vacancy"):
                if r and s:
                    conn.execute('INSERT INTO jobs(role_name, min_exp, required_skills) VALUES (?,?,?)', 
                                 (r, e, s.lower()))
                    conn.commit()
                    st.success(f"Successfully posted vacancy for {r}")
                    st.rerun()
                else:
                    st.error("Please fill in both Job Role and Skills.")

    # --- 2. VIEW APPLICANTS ---
    st.subheader("👥 Applicant Tracking System")
    apps = conn.execute("""
        SELECT candidate_name, job_role, match_score, timestamp 
        FROM applications 
        ORDER BY timestamp DESC
    """).fetchall()

    if apps:
        # Transforming data for a professional table view
        app_display = []
        for a in apps:
            status = "✅ Shortlisted" if a[2] >= 60 else "❌ Rejected"
            app_display.append({
                "Candidate Name": a[0],
                "Applied Role": a[1],
                "Match Score": f"{a[2]}%",
                "Status": status,
                "Applied Date": a[3]
            })
        st.dataframe(app_display, use_container_width=True)
    else:
        st.info("No applications received yet.")
    
    conn.close()

def candidate_portal():
    st.header("🎓 Candidate Dashboard")
    conn = get_db_connection()
    
    # Fetch active jobs for the dropdown
    jobs = conn.execute("SELECT role_name, required_skills, min_exp FROM jobs").fetchall()
    
    if jobs:
        st.subheader("Apply for a Position")
        selected_role = st.selectbox("Select Job Role", [j[0] for j in jobs])
        
        # Candidate Email for Notification
        candidate_email = st.text_input("Enter your Email Address (to receive status updates)")
        
        file = st.file_uploader("Upload your Resume (PDF format only)", type=["pdf"])
        
        if file and st.button("Submit Application"):
            if not candidate_email:
                st.warning("Please provide your email address to proceed.")
                return

            with st.spinner("Our AI is analyzing your profile..."):
                # 1. Extract Text
                text = extract_text_from_pdf(file)
                
                # 2. Get Job Details
                job_data = next(j for j in jobs if j[0] == selected_role)
                req_skills = [skill.strip() for skill in job_data[1].split(",")]
                req_exp = job_data[2]

                # 3. Experience Matching (Regex)
                exp_match = re.search(r"(\d+)\s*(?:years?|yrs?)", text)
                found_exp = int(exp_match.group(1)) if exp_match else 0
                
                # 4. Skill Matching
                found_skills = [s for s in req_skills if s in text]
                score = round((len(found_skills) / len(req_skills)) * 100, 2) if req_skills else 0

                # 5. Qualification Logic
                is_qualified = (score >= 60) and (found_exp >= req_exp)

                if is_qualified:
                    st.balloons()
                    st.success(f"Great News! You are shortlisted with a match score of {score}%")
                    
                    # --- TRIGGER PROFESSIONAL EMAIL ---
                    with st.spinner("Sending your official confirmation email..."):
                        email_sent = send_shortlist_email(candidate_email, st.session_state['username'], selected_role, score)
                        if email_sent:
                            st.info(f"A confirmation email has been sent to {candidate_email}")
                        else:
                            st.warning("Application saved, but email notification failed. Please check system settings.")
                else:
                    st.error(f"Application Status: Not Shortlisted. (Match Score: {score}%)")

                # 6. Save results to Database
                conn.execute('INSERT INTO applications(candidate_name, job_role, match_score) VALUES (?,?,?)', 
                             (st.session_state['username'], selected_role, score))
                conn.commit()
    else:
        st.warning("There are currently no active job vacancies. Please check back later.")
    
    conn.close()