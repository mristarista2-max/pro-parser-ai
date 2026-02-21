import sqlite3

def create_tables():
    conn = sqlite3.connect('recruitment_system.db')
    c = conn.cursor()
    # Create users table
    c.execute('CREATE TABLE IF NOT EXISTS users(username TEXT, password TEXT, role TEXT)')
    # Create jobs table
    c.execute('''CREATE TABLE IF NOT EXISTS jobs(
                 job_id INTEGER PRIMARY KEY AUTOINCREMENT, 
                 role_name TEXT, min_exp INTEGER, location TEXT, required_skills TEXT)''')
    # Create applications table
    c.execute('''CREATE TABLE IF NOT EXISTS applications(
                 app_id INTEGER PRIMARY KEY AUTOINCREMENT,
                 candidate_name TEXT, job_role TEXT, match_score REAL,
                 timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

def get_db_connection():
    return sqlite3.connect('recruitment_system.db')