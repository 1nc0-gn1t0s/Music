from flask import Flask
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash


app = Flask(__name__)
app.secret_key = 'just a really secret sentence'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)


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


def create_user(nickname, username, password):
    """
    Функция для добавления пользователя в базу данных
    :param nickname: nickname
    :param username: username
    :param password: password
    :return: None
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
