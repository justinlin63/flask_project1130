from .use_model import *
from . import registers_blueprint


@registers_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        input_username = request.form['username']
        input_password = request.form['password']
        input_email = request.form['email']
        hashed_password = generate_password_hash(input_password, salt_length=10)  # 將新使用者的密碼進行哈希函式加密
        # cursor.execute('SELECT * FROM users WHERE username = %s', (input_username,))
        user = sql_search('users', '*', 'username', input_username)
        if user:
            return redirect('/redirect/使用者名稱已存在')
        string = f'"{input_username}","{hashed_password}","user","{input_email}","0",0'
        sql_insert('users', 'username, password, role, email,reset_password_token,money', string)

        return redirect('/redirect/註冊成功，請重新登入')

    return render_template('register.html')
