import hashlib
import fitz
import re
import smtplib
from email.message import EmailMessage

# --- EXISTING FUNCTIONS ---
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def extract_text_from_pdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    return "".join([page.get_text() for page in doc]).lower()

# --- NEW EMAIL FUNCTION ---
def send_shortlist_email(candidate_email, candidate_name, job_role, score):
    # IMPORTANT: Use your actual Gmail and App Password here
    SENDER_EMAIL = "accitrack03@gmail.com"
    SENDER_PASSWORD = "gzpg oppa zdko luit" 
    
    try:
        msg = EmailMessage()
        msg.set_content(f"Dear {candidate_name},\n\nCongratulations! You have been shortlisted for the position of {job_role}. Your profile match score is {score}%.\n\nOur team will contact you soon for the next steps.\n\nBest Regards,\nRecruitment Team")
        
        msg['Subject'] = f"Shortlisted for {job_role} - Pro-Parser AI"
        msg['From'] = SENDER_EMAIL
        msg['To'] = candidate_email

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(SENDER_EMAIL, SENDER_PASSWORD)
            smtp.send_message(msg)
        return True
    except Exception as e:
        print(f"Email Error: {e}")
        return False