from flask import Flask, render_template, redirect, request
import mysql.connector
from config import db_config

app = Flask(__name__)

# Function to establish database connection
def get_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except mysql.connector.Error as e:
        print("❌ Database connection error:", e)
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        comments = request.form.get('comments')  # Ensure this matches the form input & DB field

        # Debugging: Print received values in the terminal
        print("✅ Received form data:")
        print(f"Name: {name}")
        print(f"Email: {email}")
        print(f"Comments: {comments}")

        if not comments:
            print("⚠ WARNING: Comments field is empty before insertion!")

        conn = get_db_connection()
        if conn is None:
            return "Database connection error!", 500

        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO feedback (student_name, email, comments) VALUES (%s, %s, %s)", (name, email, comments))
            conn.commit()
        except mysql.connector.Error as e:
            print("❌ Error inserting data:", e)
        finally:
            cursor.close()
            conn.close()

        return redirect('/admin')  # Redirect to admin panel after submission

    return render_template('feedback.html')

@app.route('/admin')
def admin():
    conn = get_db_connection()
    if conn is None:
        return "Database connection error!", 500  

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM feedback ORDER BY submitted_at DESC")
        feedbacks = cursor.fetchall()
    except mysql.connector.Error as e:
        print("❌ Error fetching data:", e)
        feedbacks = []
    finally:
        cursor.close()
        conn.close()

    return render_template('admin.html', feedbacks=feedbacks)

if __name__ == '__main__':
    app.run(debug=True)