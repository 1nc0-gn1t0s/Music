from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, current_user, UserMixin, login_required
from werkzeug.security import check_password_hash, generate_password_hash


app = Flask(__name__)
app.secret_key = 'just a really secret sentence'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)


class User(db.Model, UserMixin):
    """
    Класс пользователя
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(300), nullable=False)
    nickname = db.Column(db.Text, nullable=False)
    password_hash = db.Column(db.String(300), nullable=False)

    def __init__(self, nickname, username, password_hash):
        self.nickname = nickname
        self.username = username
        self.password_hash = password_hash

    def __repr__(self):
        return '<User {}>'.format(self.username)


class Song(db.Model):
    """
    Класс трека
    """
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    singer = db.Column(db.String(300), nullable=False)
    text_path = db.Column(db.String(300), nullable=False)
    song_path = db.Column(db.String(300), nullable=False)
    photo_path = db.Column(db.String(300), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, singer, text_path, song_path, photo_path, user_id):
        self.title = title
        self.singer = singer
        self.text_path = text_path
        self.song_path = song_path
        self.photo_path = photo_path
        self.user_id = user_id

    def __repr__(self):
        return '<Song {}>'.format(self.title)


@login_manager.user_loader
def load_user(user_id):
    """
    Функция для поиска пользователя по id
    :param user_id: id
    :return: User
    """
    return User.query.get(int(user_id))


@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    songs = Song.query.filter_by(user_id=user.id).order_by(Song.title).all()
    return render_template('user.html', user=user, songs=songs)


def create_user(nickname, username, password):
    """
    Функция для добавления пользователя в базу данных
    :param nickname: nickname
    :param username: username
    :param password: password
    :return:
    """
    new_user = User(nickname=nickname, username=username, password_hash=generate_password_hash(password))
    db.session.add(new_user)
    db.session.commit()


def get_user_by_username(username):
    """
    Функция для получения пользователя по username
    :param username: username
    :return: None
    """
    return User.query.filter_by(username=username).first()


def check_password(user, password):
    """
    Функция для проверки пароля
    :param user: user
    :param password: password
    :return: Bool
    """
    return check_password_hash(user.password_hash, password)


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        info = list(dict(request.form).values())
        print(info)
        nickname, username, password, repeat_password = info[0], info[1], info[2], info[3]
        if not (nickname and username and password and repeat_password):
            flash('All fields must be filled in.')
            return redirect(url_for('registration'))

        if password != repeat_password:
            flash('You repeated the password incorrectly.')
            return redirect(url_for('registration'))

        if get_user_by_username(username):
            flash('The name is occupied.')
            return redirect(url_for('registration'))

        create_user(nickname, username, password)

        flash("You're successfully sighed up. Please log in.")
        return redirect(url_for('login'))

    return render_template('registration.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        info = list(dict(request.form).values())
        username, password = info[0], info[1]
        print(info)
        if not username or not password:
            flash('All fields must be filled in.')
            return redirect(url_for('login'))

        user = get_user_by_username(username)
        print(user)

        if not user:
            flash('User is not found.')
            return redirect(url_for('login'))

        if not check_password_hash(user.password_hash, password):
            flash('Wrong password.', 'error')
            return redirect(url_for('login'))

        login_user(user)
        return redirect(url_for('user', username=username))

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload_new')
@login_required
def upload_new():
    return render_template('upload_new.html')


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)
