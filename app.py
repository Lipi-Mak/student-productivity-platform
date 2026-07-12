from flask import Flask, render_template, redirect, url_for

app = Flask(__name__)

# Route for the Login Page
@app.route('/')
@app.route('/login')
def login():
    return render_template('login.html')

# Route for the Registration Page
@app.route('/register')
def register():
    return render_template('register.html')

# Route for the main StudentOS Dashboard
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)