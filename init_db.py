import sqlite3

conn = sqlite3.connect('presidents.db')
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS presidents (
    Presidency INTEGER PRIMARY KEY,
    President TEXT,
    Wikipedia_entry TEXT,
    Took_office DATE,
    Left_office DATE,
    Party TEXT,
    Home_state TEXT,
    Occupation TEXT,
    College TEXT,
    Age_when_took_office INTEGER,
    Birth_date DATE,
    Birthplace TEXT,
    Death_date DATE,
    Location_death TEXT,
    Image TEXT
)
""")

conn.commit()
conn.close()
