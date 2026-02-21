import streamlit as st
import time
from database import create_tables, get_db_connection
from utils import make_hashes
from portals import admin_portal, candidate_portal

def main():
    # 1. Page Configuration
    st.set_page_config(page_title="Pro-Parser AI", layout="wide", page_icon="📄")
    create_tables()

    # --- 2. PROFESSIONAL CENTERED SPLASH SCREEN ---
    if 'splash_done' not in st.session_state:
        st.session_state.splash_done = False

    if not st.session_state.splash_done:
        placeholder = st.empty()
        with placeholder.container():
            # CSS for exact centering and clean background
            st.markdown("""
                <style>
                header {visibility: hidden;}
                footer {visibility: hidden;}
                [data-testid="stSidebar"] {visibility: hidden;}
                .splash-box {
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    align-items: center;
                    height: 80vh;
                    text-align: center;
                }
                </style>
                """, unsafe_allow_html=True)
            
            st.markdown('<div class="splash-box">', unsafe_allow_html=True)
            
            # Logo Placement
            try:
                # Looks for logo.png in the same directory
                st.image("logo.png", width=500) 
            except:
                # Fallback if image is missing
                st.markdown("<h1 style='font-size: 60px;'>📄 PRO-PARSER AI</h1>", unsafe_allow_html=True)
            
            st.markdown("<h3>Initializing AI Engine...</h3>", unsafe_allow_html=True)
            
            # Progress bar simulation
            bar = st.progress(0)
            for p in range(100):
                time.sleep(0.02)
                bar.progress(p + 1)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
        time.sleep(0.5)
        placeholder.empty()
        st.session_state.splash_done = True
        st.rerun() # Refresh to main app

    # --- 3. AUTHENTICATION STATE ---
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    # --- 4. PRE-LOGIN NAVIGATION ---
    if not st.session_state['logged_in']:
        page = st.sidebar.selectbox("Navigation", ["Home", "Login", "SignUp"])

        if page == "Home":
            st.title("📄 Pro-Parser AI")
            col_left, col_right = st.columns([2, 1])
            with col_left:
                st.markdown("### The Future of Smart Recruitment")
                st.write("""
                Automate your hiring workflow with AI-driven resume parsing. 
                Our system extracts candidate skills and experience to match them 
                against your requirements instantly.
                """)
                st.info("Please Login or Sign Up from the sidebar to continue.")
            with col_right:
                try: st.image("logo.png", use_container_width=True)
                except: pass

        elif page == "Login":
            st.sidebar.subheader("Login")
            u = st.sidebar.text_input("Username")
            p = st.sidebar.text_input("Password", type='password')
            r = st.sidebar.selectbox("Role", ["Admin", "Candidate"])
            if st.sidebar.button("Login"):
                conn = get_db_connection()
                res = conn.execute('SELECT * FROM users WHERE username=? AND password=? AND role=?', 
                                 (u, make_hashes(p), r)).fetchone()
                if res:
                    st.session_state.update({'logged_in': True, 'user_role': r, 'username': u})
                    st.rerun()
                else:
                    st.sidebar.error("Invalid Username or Password")

        elif page == "SignUp":
            st.subheader("Create a New Account")
            nu = st.text_input("Username")
            np = st.text_input("Password", type='password')
            nr = st.selectbox("Register as:", ["Admin", "Candidate"])
            if st.button("Register"):
                conn = get_db_connection()
                conn.execute('INSERT INTO users VALUES (?,?,?)', (nu, make_hashes(np), nr))
                conn.commit()
                st.success("Account created successfully! Please proceed to Login.")
                
    # --- 5. LOGGED-IN NAVIGATION ---
    else:
        st.sidebar.write(f"Logged in as: **{st.session_state['username']}**")
        if st.sidebar.button("Logout"):
            st.session_state['logged_in'] = False
            st.rerun()
            
        if st.session_state['user_role'] == "Admin":
            admin_portal()
        else:
            candidate_portal()

if __name__ == '__main__':
    main()