from flask import Flask, render_template, request, redirect
from sigh_up_login import sigh_up, login
from add_song import add_song


app = Flask(__name__)


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        info = list(request.form)
        sigh_up(info)
        return redirect('/user')
    return render_template('registration.html')


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/user')
def user():
    return render_template('user.html')


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
