from .use_model import *
from . import pay_blueprint


def generate_pay_bill(to_user_id, money, cart, quantity):
    token = int(''.join([str(randint(0, 10)) for _ in range(10)]))
    times = int(time())
    sql_insert('pay_list', 'token,user_id,to_user_id,money,cart,quantity,time,status',
               f'{token},{current_user.id},{to_user_id},{money},"{cart}","{quantity}",{times},"ok"')
    return token


def generate_refund_bill(to_user_id, money):
    user = sql_search('users', '*', 'id', f'"{to_user_id}"')
    store = sql_search('users', '*', 'username', '"store"')
    sum_money = money
    user_money = int(user[6]) + int(sum_money)
    store_money = int(store[6]) - int(sum_money)
    sql_update('users', 'money', user_money, 'id', f'"{to_user_id}"')
    sql_update('users', 'money', store_money, 'username', '"store"')


@pay_blueprint.route('/token/<token>')
@login_required
def pay(token):
    result = sql_search('users', 'money', 'id', current_user.id)
    bill = sql_search('pay_list', '*', 'token', f'"{token}"', 'one')
    if bill:
        if result >= bill[4] and bill[8] == 'ok':
            return redirect(f'/pay/check/{token}')
        elif result < bill[4] and bill[8] == 'ok':
            return redirect('/redirect/餘額不足')
    return redirect('/redirect/wrong')


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
                           f'{current_user.username},"{bill[5]}","{bill[6]}","confirm"')
                result3 = sql_search("cart", where="user_id", where_value=f'{current_user.id}', fetch="all")
                if result3:
                    if len(result3):
                        for i in result3:
                            cart = i.cart
                            quantity = i.quantity
                            hot = sql_search(ufstr.products(), ufstr.star(), ufstr.id(), cart)
                            if hot:
                                hot = hot.hot
                                hot = int(hot) + int(quantity)
                                sql_update(ufstr.products(), ufstr.hot(), hot, ufstr.id(), cart)

                sql_delete('cart', 'user_id', current_user.id)
                return redirect('/orders')
            return redirect('/redirect/餘額不足')
        else:
            return redirect('/redirect/密碼錯誤')
    bill = sql_search('pay_list', '*', 'token', int(token), 'one')
    if bill:
        return render_template('pay.html', total=bill.money, token=token)
    return redirect('/redirect/錯誤')
