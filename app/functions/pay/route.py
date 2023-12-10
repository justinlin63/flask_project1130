import json

from .use_model import *
from . import pay_blueprint


def generate_pay_bill(to_user_id, money, cart, quantity):
    token = str(uuid4())
    times = int(time())
    sql_insert('pay_list', 'token,user_id,to_user_id,money,cart,quantity,time,status',
               f'{ufstr.db_string(token)},{current_user.id},{to_user_id},{money},"{cart}","{quantity}",{times},"ok"')
    return token


def generate_refund_bill(to_user_id, money):
    user = sql_search('users', '*', 'id', f'"{to_user_id}"')
    store = sql_search('users', '*', 'username', '"store"')
    sum_money = money
    user_money = int(user[6]) + int(sum_money)
    store_money = int(store[6]) - int(sum_money)
    sql_update('users', 'money', user_money, 'id', f'"{to_user_id}"')
    sql_update('users', 'money', store_money, 'username', '"store"')


@pay_blueprint.route('/token/<token>', methods=['GET', 'POST'])
@login_required
def pay(token):
    if request.method == 'POST':
        result = sql_search('users', 'money', 'id', current_user.id)
        bill = sql_search('pay_list', '*', 'token', f'{ufstr.db_string(token)}', 'one')
        if bill:
            if result >= bill[4] and bill[8] == 'ok':
                return redirect(f'/pay/check/{token}')
            elif result < bill[4] and bill[8] == 'ok':
                return redirect('/redirect/餘額不足')
        return redirect('/redirect/wrong')
    return render_template('payment.html', token=token, ip=ip, port=port)


@pay_blueprint.route('/check/<token>', methods=['GET', 'POST'])
@login_required
def check(token):
    if request.method == 'POST':
        password = request.form['password']
        password_correct = sql_search('users', 'password', 'username', f'"{current_user.username}"', 'one')
        if check_password_hash(password_correct, password):
            result = sql_search('users', 'money', 'id', current_user.id)
            bill = sql_search('pay_list', '*', 'token', f'"{token}"', 'one')
            if result >= bill[4] and bill[8] == 'ok':
                new_money = result - bill[4]
                sql_update('users', 'money', new_money, 'id', current_user.id)
                result2 = sql_search('users', 'money', 'id', bill[3])
                new_money2 = result2 + bill[4]
                sql_update('users', 'money', new_money2, 'id', bill[3])
                sql_update('pay_list', 'status', '"used"', 'id', bill[0])
                sql_insert('orders', 'username,product_id,quantity,status',
                           f'{ufstr.db_string(current_user.username)},"{bill[5]}","{bill[6]}","confirm"')
                result3 = sql_search("cart", where="user_id", where_value=f'{current_user.id}', fetch="all")
                if result3:
                    if len(result3):
                        for i in result3:
                            cart = i.cart
                            quantity = i.quantity
                            result4 = sql_search(ufstr.products(), ufstr.star(), ufstr.id(), cart)
                            if result4:
                                hot = result4.hot
                                hot = int(hot) + int(quantity)
                                sql_update(ufstr.products(), ufstr.hot(), hot, ufstr.id(), cart)
                                sql_update(ufstr.suggest_order(), result4.product_type, f'{result4.product_type}+1',
                                           ufstr.user_id(),
                                           bill.user_id)
                sql_delete('cart', 'user_id', current_user.id)
                return redirect('/orders')
            return redirect('/redirect/餘額不足')
        else:
            return redirect('/redirect/密碼錯誤')
    bill = sql_search('pay_list', '*', 'token', ufstr.db_string(token), 'one')
    if bill:
        return render_template('pay.html', total=bill.money, token=token)
    return redirect('/redirect/錯誤')


@pay_blueprint.route('/token/fp/<token>')
@login_required
def fp(token):
    bill = sql_search('pay_list', '*', 'token', f'{ufstr.db_string(token)}', 'one')
    if bill:
        data = {'token': token, 'money': bill.money, 'uid': uid, 'key': key}
        res = requests.post(f'http://{fp_ip}:5001/api/bill', json=data)
        if res.status_code == 200:
            rel = res.json()
            rel = json.loads(rel)
            if 'error' not in rel and rel['do'] == 'add_bill' and rel['status'] == "success":
                return redirect(f'http://{fp_ip}:5001/pay/token/{token}')
            else:
                return redirect('/redirect/錯誤1')
        else:
            return redirect('/redirect/錯誤2')
    return redirect('/redirect/錯誤3')


@pay_blueprint.route('/fp/callback', methods=['POST'])
def fp_callback():
    result = request.get_json()
    token = result['token']
    user = sql_search(ufstr.pay_list(), ufstr.star(), ufstr.token(), ufstr.db_string(token))
    user_id = user.user_id
    username = sql_search(ufstr.users(), ufstr.username(), ufstr.id(), user_id)
    bill = sql_search('pay_list', '*', 'token', f'"{token}"', 'one')
    if bill.status == 'ok':
        sql_update('pay_list', 'status', '"used"', 'id', bill.id)
        sql_insert('orders', 'username,product_id,quantity,status',
                   f'{ufstr.db_string(username)},"{bill.cart}","{bill.quantity}","confirm"')
        result3 = sql_search("cart", where="user_id", where_value=f'{user_id}', fetch="all")
        if result3:
            if len(result3):
                for i in result3:
                    cart = i.cart
                    quantity = i.quantity
                    result4 = sql_search(ufstr.products(), ufstr.star(), ufstr.id(), cart)
                    if result4:
                        hot = result4.hot
                        hot = int(hot) + int(quantity)
                        sql_update(ufstr.products(), ufstr.hot(), hot, ufstr.id(), cart)
                        sql_update(ufstr.suggest_order(), result4.product_type, f'{result4.product_type}+1',
                                   ufstr.user_id(),
                                   bill.user_id)
        sql_delete('cart', 'user_id', user_id)
        return redirect('/orders')
    return 'ok'
