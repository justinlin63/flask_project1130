import requests

from .use_model import *
from . import cart_blueprint


@cart_blueprint.route('/')
@login_required
def cart():
    result = sql_search(ufstr.cart(), ufstr.star(), ufstr.user_id(), ufstr.db_string(current_user.id), ufstr.all())
    carts_list = []
    total_price = 0
    if result:
        if len(result):
            for i in result:
                cart_list = []
                cart = i.cart
                name = sql_search('products', 'name', 'id', where_value=cart)
                price = sql_search('products', 'price', 'id', where_value=cart)
                quantity = i.quantity
                subtotal = price * quantity
                add_path = "/cart/add/" + str(cart)
                minus_path = "/cart/minus/" + str(cart)
                cart_list.append(cart)
                cart_list.append(name)
                cart_list.append(price)
                cart_list.append(quantity)
                cart_list.append(subtotal)
                cart_list.append(add_path)
                cart_list.append(minus_path)
                carts_list.append(cart_list)
                total_price += subtotal
                cart_buy_bool = 1
        else:
            cart_buy_bool = 0
    else:
        cart_buy_bool = 0

    return render_template('cart.html', carts=carts_list, cart_buy_bool=cart_buy_bool, total=total_price)


@cart_blueprint.route('/join', methods=['GET', 'POST'])
@login_required
def cart_join():
    if request.method == 'POST':
        product_id = int(request.form['product_id'])
        quantity = int(request.form['quantity'])
        result = sql_search('cart', '*', 'user_id', current_user.id, 'all')
        if result:
            for i in result:
                if product_id == i.cart:
                    new_quantity = i.quantity + quantity
                    string = f'{current_user.id} AND cart = {product_id}'
                    sql_update('cart', 'quantity', new_quantity, 'user_id', string)
                    return redirect('/')
        string = f'{current_user.id},{product_id},{quantity}'
        sql_insert('cart', 'user_id,cart,quantity', string)
    return redirect('/')


@cart_blueprint.route('/add/<int:id>')
@login_required
def cart_add(id):
    string = str(current_user.id) + ' AND cart = ' + str(id)
    result = sql_search('cart', 'quantity', 'user_id', string, 'one')
    new_quantity = result + 1
    sql_update('cart', 'quantity', new_quantity, 'user_id', string)
    return redirect('/cart')


@cart_blueprint.route('/minus/<int:id>')
@login_required
def cart_minus(id):
    string = str(current_user.id) + ' AND cart = ' + str(id)
    result = sql_search('cart', 'quantity', 'user_id', string, 'one')
    if (result - 1) <= 0:
        sql_delete('cart', 'user_id', string)
    else:
        new_quantity = result - 1
        sql_update('cart', 'quantity', new_quantity, 'user_id', string)
    return redirect('/cart')


@cart_blueprint.route('/buy')
@login_required
def buy():
    result = sql_search("cart", where="user_id", where_value=f'{current_user.id}', fetch="all")
    total_price = 0
    product_id_string = ''
    quantity_string = ''
    if result:
        if len(result):
            for i in result:
                cart = i.cart
                price = sql_search('products', 'price', 'id', where_value=cart)
                quantity = i.quantity
                subtotal = price * quantity
                total_price += subtotal
                if product_id_string == '':
                    product_id_string = product_id_string + str(cart)
                    quantity_string = quantity_string + str(quantity)
                else:
                    product_id_string = product_id_string + ',' + str(cart)
                    quantity_string = quantity_string + ',' + str(quantity)

            token = generate_pay_bill(1, total_price, product_id_string, quantity_string)

            return redirect(f'/pay/token/{token}')
    return redirect('/redirect/錯誤')
