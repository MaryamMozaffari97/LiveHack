from flask import Flask, render_template, request, make_response, redirect, url_for, flash
import db
import sqlite3
import hashlib
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

def get_username_from_session_token(session_token):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users WHERE session_token=?", (session_token,))
    result = cursor.fetchone()
    conn.close()

    if result:
        return result[0]
    else:
        return None

def create_user_table():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users(
            email TEXT PRIMARY KEY,
            username TEXT,
            password TEXT,
            session_token TEXT
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/', methods=['GET'])
def index():


    return render_template('index.html')



@app.route('/home', methods=['GET', 'POST'])
def home():
    session_token = request.cookies.get('session_token')

    # Here, you can validate the session_token against the user's record in the database
    # to ensure the session is still valid.

    if session_token:
        username = get_username_from_session_token(session_token)
        if username:
            if request.method == 'POST':
                db.add_comment(request.form['comment'])
               
               
            search_query = request.args.get('q')
            comments = db.get_comments(search_query)
            return render_template('home.html',username=username, comments=comments, search_query=search_query)
    
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        password_hash = hashlib.sha256(password.encode()).hexdigest()

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM users WHERE email=? AND password=?", (email, password_hash))
        result = cursor.fetchone()
        conn.close()

        if result:
            username = result[0]
            session_token = os.urandom(16).hex()
            response = make_response(redirect(url_for('home')))
            response.set_cookie('session_token', session_token)

            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET session_token=? WHERE email=?", (session_token, email))
            conn.commit()
            conn.close()

            flash(f"Welcome back, {username}!")  # Show success message using flash
            return response
        else:
            flash("Invalid email or password! 😟")  # Show error message using flash
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash("Passwords do not match! 😞")  # Show error message using flash
            return redirect(url_for('signup'))

        password_hash = hashlib.sha256(password.encode()).hexdigest()

        session_token = os.urandom(16).hex()
        response = make_response(redirect(url_for('home')))
        response.set_cookie('session_token', session_token)

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?)", (email, username, password_hash, session_token))
        conn.commit()
        conn.close()

        flash("Successfully registered!")  # Show success message using flash
        return response

    return render_template('signup.html')
    
@app.route('/logout')
def logout():
    session_token = request.cookies.get('session_token')

    if session_token:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET session_token='' WHERE session_token=?", (session_token,))
        conn.commit()
        conn.close()

    response = make_response(redirect(url_for('login')))
    response.delete_cookie('session_token')
    flash("You have been logged out. See you next time! 👋")  # Show logout message using flash
    return response
    
if __name__ == '__main__':
    create_user_table()  # Create the user table if it doesn't exist
    app.run(debug=True)

