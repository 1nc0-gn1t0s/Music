from flask import render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required
from werkzeug.security import check_password_hash

from api import make_cover, add_song, make_text_path
from models import app, User, Song, create_user, get_user_by_username


login_manager = LoginManager()
login_manager.init_app(app)


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
    """
    Возвращает страницу пользователя
    :param username: username
    :return: html
    """
    user_0 = User.query.filter_by(username=username).first_or_404()
    songs = Song.query.filter_by(user_id=user_0.id).order_by(Song.title).all()
    return render_template('user.html', user=user_0, songs=songs)


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    """
    Функция для регистрации пользователя; открывает html соответствующей страницы
    :return: html
    """
    if request.method == 'POST':
        info = list(dict(request.form).values())
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
    """
    Функция для входа пользователей в аккаунты; открывает html соответствующей страницы
    :return: html
    """
    if request.method == 'POST':
        info = list(dict(request.form).values())
        username, password = info[0], info[1]
        if not username or not password:
            flash('All fields must be filled in.')
            return redirect(url_for('login'))

        user_1 = get_user_by_username(username)

        if not user_1:
            flash('User is not found.')
            return redirect(url_for('login'))

        if not check_password_hash(user_1.password_hash, password):
            flash('Wrong password.', 'error')
            return redirect(url_for('login'))

        login_user(user_1)
        return redirect(url_for('user', username=username))

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    """
    Функция для выхода из аккаунта пользователя
    :return: home html
    """
    logout_user()
    return redirect('/')


@app.route('/about')
def about():
    """
    Возвращает страницу 'О нас'
    :return: html
    """
    return render_template('about.html')


@app.route('/')
def index():
    """
    Возвращает домашнюю страницу
    :return: html
    """
    return render_template('index.html')


@app.route('/upload_new/<username>', methods=['GET', 'POST'])
@login_required
def upload_new(username):
    """
    Возвращает страницу добавления нового трека
    :return: html
    """
    user_1 = get_user_by_username(username)

    if request.method == 'POST':
        info = list(dict(request.form).values())
        title, singer, filepath, text, desc = info[0], info[1], info[2], info[3], info[4]

        if not filepath:
            flash('Choose the file please.')
            return redirect(url_for('upload_new', username=username))

        if not (title and singer):
            flash('The fields "title" and "singer" must be filled in.')
            return redirect(url_for('upload_new', username=username))

        photo_path = make_cover(info, user_1)
        text_path = make_text_path(info, user_1)
        add_song(title, singer, filepath, text_path, photo_path, user_1)
        return redirect(url_for('user', username=username))
    return render_template('upload_new.html', user=user_1)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)
