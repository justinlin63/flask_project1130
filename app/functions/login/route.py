from .use_model import *
from . import login_blueprint


@login_blueprint.route('/login', methods=['get', 'post'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password_correct = sql_search('users', 'password', 'username', f'"{username}"', 'one')
        if check_password_hash(password_correct, password):
            user_id = sql_search('users', 'id', 'username', f'"{username}"', 'one')
            role = sql_search(ufstr.users(), ufstr.role(), ufstr.id(), user_id)
            user = User(user_id, username, role)
            login_user(user)
            next_url = request.args.get('next')
            if next_url == '/logout':
                next_url = None
            return redirect(next_url or url_for('home_blueprint.home'))
        else:
            return redirect('/redirect/密碼錯誤')
    next_url = request.args.get('next')
    return render_template('login.html', url=next_url)


@login_blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/redirect/登出成功')
