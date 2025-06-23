import csv
import os
import io
from flask import Flask, render_template, request, redirect, url_for
from mysql.connector import MySQLConnection, Error
from mySqlDbConfig import readDbConfig
from datetime import datetime
from flask import send_from_directory



app = Flask(__name__)

@app.route('/')
def index():  # put application's code here
	return render_template("index.html")

@app.route('/help')
def help():  # put application's code here
    return render_template("help.html")

@app.route('/flaskCard')
def flaskCard():  # put application's code here
    cursor = None
    conn = None
    try:
        dbconfig = readDbConfig()
        dbconfig['auth_plugin'] = 'mysql_native_password'
        conn = MySQLConnection(**dbconfig)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM presidents ORDER BY Presidency ASC")
        presidents = cursor.fetchall()
        return render_template("flaskcard.html", presidents=presidents)
    except Exception as e:
        return f"❌ Error: {e}"
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            
            
@app.route('/jinjaman')
def jinjaman():
	try:
		data = [15, 11, 'Python is good','Python, Java, php, SQL, C++','<p><strong>Hey there!</strong></p>']
		return render_template("usingJinja.html", data=data)
	except Exception as e:
		return(str(e))


@app.route('/login',methods=['post','get'])
def login():
	pwd = ""
	if request.method == 'POST':
		pwd = request.form.get('password')
		if (pwd != ''):
			pwd = int(pwd)
			return redirect(url_for('processLogin', pwd=pwd))
	return render_template("login.html", pwd=pwd)


@app.route('/processLogin/<int:pwd>', methods=['POST', 'GET'])
def processLogin(pwd):
	cursor = None
	conn = None

	if pwd == 1234:
		try:
			dbconfig = readDbConfig()
			dbconfig['auth_plugin'] = 'mysql_native_password'
			conn = MySQLConnection(**dbconfig)
			cursor = conn.cursor(dictionary=True)
			cursor.execute("SELECT * FROM presidents ORDER BY Presidency DESC")
			result = cursor.fetchall()
			return render_template("presidents.html", presidents=result)

		except Error as e:
			print("Database error:", e)
			return "Database connection failed: " + str(e)

		finally:
			if cursor:
				cursor.close()
			if conn:
				conn.close()
	else:
		return redirect(url_for('login', pwd=pwd))

UPLOAD_FOLDER = os.path.dirname(os.path.abspath(__file__))

@app.route('/upload')
def upload_form():
    return render_template('upload.html')

def convert_date_safe(value):
    try:
        return datetime.strptime(value.strip(), "%m/%d/%Y").strftime("%Y-%m-%d")
    except Exception as e:
        print("Date parse error:", e, "with value:", value)

        return None  # 返回 NULL

@app.route('/upload_presidents', methods=['POST'])
def upload_presidents():
    file = request.files.get('csv_file')
    if not file:
        return "No file uploaded!"
 
    cursor = None
    conn = None
    try:
        stream = io.StringIO(file.stream.read().decode("utf-8"))
        reader = csv.DictReader(stream)

        dbconfig = readDbConfig()
        conn = MySQLConnection(**dbconfig)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM presidents")

        for row in reader:
            cursor.execute("""
                INSERT INTO presidents (
                    Presidency, President, Wikipedia_entry, Took_office, Left_office,
                    Party, Home_state, Occupation, College, Age_when_took_office,
                    Birth_date, Birthplace, Death_date, Location_death, Image
                ) VALUES (
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s
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
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/import_presidents')
def import_presidents():
    try:
        dbconfig = readDbConfig()
        dbconfig['auth_plugin'] = 'mysql_native_password'
        conn = MySQLConnection(**dbconfig)
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
                        %s, %s, %s, STR_TO_DATE(%s, '%%m/%%d/%%Y'), STR_TO_DATE(%s, '%%m/%%d/%%Y'),
                        %s, %s, %s, %s, %s,
                        STR_TO_DATE(%s, '%%m/%%d/%%Y'), %s, STR_TO_DATE(%s, '%%m/%%d/%%Y'), %s, %s
                    )
                """, (
                    row['Presidency'], row['President'], row['Wikipedia-entry'], row['Took-office'], row['Left-office'],
                    row['Party'], row['Home-state'], row['Occupation'], row['College'], row['Age-when-took-office'],
                    row['Birth-date'], row['Birthplace'], row['Death-date'], row['Location-death'], row['Image']
                ))

        conn.commit()
        return "✅ President data successfully imported into the database!"

    except Exception as e:
        return f"❌ Import failed: {str(e)}"

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/download_template')
def download_template():
    return send_from_directory(directory='downloads', path='presidents.csv', as_attachment=True)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)