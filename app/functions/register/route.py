from .use_model import *
from . import registers_blueprint


@registers_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        input_username = request.form['username']
        input_password = request.form['password']
        input_email = request.form['email']
        hashed_password = generate_password_hash(input_password, salt_length=10)  # 將新使用者的密碼進行哈希函式加密
        user = sql_search('users', '*', 'username', ufstr.db_string(input_username))
        if user:
            return redirect('/redirect/使用者名稱已存在')
        string = f'"{input_username}","{hashed_password}","user","{input_email}","0",0'
        sql_insert('users', 'username, password, role, email,reset_password_token,money', string)
        user_id = sql_search(ufstr.users(), ufstr.id(), ufstr.username(), ufstr.db_string(input_username))
        if user_id:
            sql_insert('suggest_order', 'user_id,electronic,food,home_appliances,clothing,other', f'{user_id},0,0,0,0,0')

        return redirect('/redirect/註冊成功，請重新登入')

    return render_template('register.html')
