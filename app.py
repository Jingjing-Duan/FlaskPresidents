import csv
import os
import io
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/help')
def help():
    return render_template("help.html")

@app.route('/flaskCard')
def flaskCard():
    try:
        conn = sqlite3.connect("presidents.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM presidents ORDER BY Presidency ASC")
        rows = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        presidents = [dict(zip(columns, row)) for row in rows]
        return render_template("flaskCard.html", presidents=presidents)
    except Exception as e:
        return f"❌ Error: {e}"
    finally:
        conn.close()

@app.route('/jinjaman')
def jinjaman():
    try:
        data = [15, 11, 'Python is good','Python, Java, php, SQL, C++','<p><strong>Hey there!</strong></p>']
        return render_template("usingJinja.html", data=data)
    except Exception as e:
        return str(e)

@app.route('/login', methods=['POST', 'GET'])
def login():
    pwd = ""
    if request.method == 'POST':
        pwd = request.form.get('password')
        if pwd:
            pwd = int(pwd)
            return redirect(url_for('processLogin', pwd=pwd))
    return render_template("login.html", pwd=pwd)

@app.route('/processLogin/<int:pwd>', methods=['POST', 'GET'])
def processLogin(pwd):
    if pwd == 1234:
        try:
            conn = sqlite3.connect("presidents.db")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM presidents ORDER BY Presidency DESC")
            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            result = [dict(zip(columns, row)) for row in rows]
            return render_template("presidents.html", presidents=result)
        except Exception as e:
            return "Database connection failed: " + str(e)
        finally:
            conn.close()
    else:
        return redirect(url_for('login', pwd=pwd))

@app.route('/upload')
def upload_form():
    return render_template('upload.html')

def convert_date_safe(value):
    try:
        return datetime.strptime(value.strip(), "%m/%d/%Y").strftime("%Y-%m-%d")
    except Exception as e:
        print("Date parse error:", e, "with value:", value)
        return None

@app.route('/upload_presidents', methods=['POST'])
def upload_presidents():
    file = request.files.get('csv_file')
    if not file:
        return "No file uploaded!"

    try:
        stream = io.StringIO(file.stream.read().decode("utf-8"))
        reader = csv.DictReader(stream)

        conn = sqlite3.connect("presidents.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM presidents")

        for row in reader:
            cursor.execute("""
                INSERT INTO presidents (
                    Presidency, President, Wikipedia_entry, Took_office, Left_office,
                    Party, Home_state, Occupation, College, Age_when_took_office,
                    Birth_date, Birthplace, Death_date, Location_death, Image
                ) VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
            """, (
                int(row['Presidency']),
                row['President'],
                row['Wikipedia-entry'],
                convert_date_safe(row['Took-office']),
                convert_date_safe(row['Left-office']),
                row['Party'],
                row['Home-state'],
                row['Occupation'],
                row['College'],
                int(row['Age-when-took-office']) if row['Age-when-took-office'] else None,
                convert_date_safe(row['Birth-date']),
                row['Birthplace'],
                convert_date_safe(row['Death-date']),
                row['Location-death'],
                row['Image']
            ))

        conn.commit()
        return '''
            <script>
                alert("Presidents data uploaded successfully. Please log in to view the full details.");
                window.location.href = "/login";
            </script>
        '''

    except Exception as e:
        return f"❌ Upload failed: {e}"

    finally:
        conn.close()

@app.route('/import_presidents')
def import_presidents():
    try:
        conn = sqlite3.connect("presidents.db")
        cursor = conn.cursor()

        with open('presidents.csv', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                cursor.execute("""
                    INSERT INTO presidents (
                        Presidency, President, Wikipedia_entry, Took_office, Left_office,
                        Party, Home_state, Occupation, College, Age_when_took_office,
                        Birth_date, Birthplace, Death_date, Location_death, Image
                    ) VALUES (
                        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                    )
                """, (
                    int(row['Presidency']), row['President'], row['Wikipedia-entry'],
                    convert_date_safe(row['Took-office']), convert_date_safe(row['Left-office']),
                    row['Party'], row['Home-state'], row['Occupation'], row['College'],
                    int(row['Age-when-took-office']) if row['Age-when-took-office'] else None,
                    convert_date_safe(row['Birth-date']), row['Birthplace'],
                    convert_date_safe(row['Death-date']), row['Location-death'], row['Image']
                ))

        conn.commit()
        return "✅ President data successfully imported into the database!"

    except Exception as e:
        return f"❌ Import failed: {str(e)}"

    finally:
        conn.close()

@app.route('/download_template')
def download_template():
    return send_from_directory(directory='downloads', path='presidents.csv', as_attachment=True)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
#    app.run(host='127.0.0.1', port=5001, debug=True)

    