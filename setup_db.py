import sqlite3

def setup_database():
    conn = sqlite3.connect("attendance_system.db")
    cursor = conn.cursor()

    
    cursor.execute("DROP TABLE IF EXISTS admin")


    cursor.execute('''
        CREATE TABLE admin (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            email TEXT
        )
    ''')

    # Default Admin credentials.
    
    admin_email = "arifwitnes6973@gmail.com" 
    
    cursor.execute('''
        INSERT INTO admin (username, password, email)
        VALUES (?, ?, ?)
    ''', ('admin', 'admin123', admin_email))
    
    print("✅ Database updated for Email OTP feature!")
    print(f"➡️ Username: admin | Email linked: {admin_email}")
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    setup_database()