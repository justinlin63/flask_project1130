from .use_model import *
from . import reset_password_blueprint

sender_email = "ggfewi20@gmail.com"
receiver_email = ""
password = "wsgnfncjfeuvzhbv"


@reset_password_blueprint.route('/password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        input_username = request.form['username']
        input_email = request.form['email']
        user = sql_search(ufstr.users(), ufstr.star(), ufstr.username(),
                          f'{ufstr.db_string(input_username)} AND email = {ufstr.db_string(input_email)}')
        if user:
            # 寄送密碼重設連結至使用者的電子郵件
            token = generate_password_hash(str(random.random()))
            sql_update(ufstr.users(), ufstr.reset_password_token(), ufstr.db_string(token), ufstr.username(),
                       ufstr.db_string(input_username))
            message = MIMEMultipart()
            message['Subject'] = '重設密碼'
            message['From'] = sender_email
            message['To'] = input_email
            receiver_email = input_email.split()
            reset_password_url = ip + '/reset/token/' + token

            msg_html = f'''
            <html>
            <h1>重設密碼</h1>
            <br></br>
            {reset_password_url}
            '''
            # 創建一個包含HTML內容的MIMEText對象
            msg_html = MIMEText(msg_html, 'html', 'utf8')
            message.attach(msg_html)

            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(sender_email, password)
                server.sendmail(sender_email, receiver_email[0], message.as_string())
                return redirect('/redirect/密碼重設信件已發送')
        return redirect('/redirect/使用者不存在或電子郵件錯誤')

    return render_template('reset_password.html')


@reset_password_blueprint.route('/token/<reset_token>', methods=['GET', 'POST'])
def reset_password_change(reset_token):
    user = sql_search(ufstr.users(), ufstr.star(), ufstr.reset_password_token(), ufstr.db_string(reset_token))
    if user:
        return render_template('reset_password_new_password.html', reset_token=reset_token)
    return redirect('/')


@reset_password_blueprint.route('/password/change', methods=['GET', 'POST'])
def password_change():
    if request.method == 'POST':
        new_password = request.form['new_password']
        reset_token = request.form['reset_token']
        user = sql_search(ufstr.users(), ufstr.star(), ufstr.reset_password_token(), ufstr.db_string(reset_token))
        new_password = generate_password_hash(new_password)
        sql_update(ufstr.users(), ufstr.password(), ufstr.db_string(new_password), ufstr.username(),
                   ufstr.db_string(user[1]))
        sql_update(ufstr.users(), ufstr.reset_password_token(), ufstr.db_string("0"), ufstr.username(),
                   ufstr.db_string(user[1]))
        return redirect('/redirect/密碼更改成功，請重新登入')
    return redirect('/')
