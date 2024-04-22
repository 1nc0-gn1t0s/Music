from flask import Flask, render_template


app = Flask(__name__)


@app.route('/registration')
def registration():
    return render_template('registration.html')


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/upload_new')
def upload_new():
    return render_template('upload_new.html')


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)
