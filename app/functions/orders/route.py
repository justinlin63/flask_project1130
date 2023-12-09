from .use_model import *
from . import orders_blueprint


@orders_blueprint.route('/')
@login_required
def orders():
    page = request.args.get('page')
    if not page:
        page = 1
    else:
        page = int(page)
    start = (page - 1) * limit_per_page
    end = page * limit_per_page
    input_username = current_user.username
    user = sql_search('orders', "*", 'username', f"'{input_username}'", fetch='all')
    orders = []
    for result in user:
        order = {'order_id': result.id, 'products': []}
        product_list = result.product_id.split(',')
        total_price = 0
        for product_info in product_list:
            index = product_list.index(product_info)
            d = {}
            if product_info != '':
                product_info = int(product_info)
            xx = sql_search('products', "*", 'id', product_info)
            q = sql_search('orders', "*", 'id', result[0])
            q = str(q.quantity).split(',')
            d['product_id'] = xx.id
            d['name'] = xx.name
            d['price'] = xx.price
            d['quantity'] = q[index]
            total_price += int(d['price']) * int(d['quantity'])
            order['products'].append(d)
        order['buyer'] = result.username
        order['total_price'] = total_price
        order['cancel_url'] = '/orders/cancel/' + str(result.id)
        r = ''
        status = result.status
        if status == 'deliver':
            r = '已出貨'
        elif status == 'cancel':
            r = '已取消'
        elif status == 'confirm':
            r = '處理中'
        elif status == 'canceled':
            r = '商家已取消'
        order['status'] = r
        orders.append(order)
    orders.reverse()
    orders_edit = orders[start:end]
    next_page = page + 1
    if page - 1:
        last_page = page - 1
    else:
        last_page = 0
    if not len(orders_edit) or len(orders_edit) < limit_per_page or orders_edit[-1] == orders[-1]:
        next_page = 0
    return render_template('orders.html', orders=orders_edit, next_page=next_page, last_page=last_page)


@orders_blueprint.route('/cancel/<int:id>')
@login_required
def orders_cancel(id):
    sql_update('orders', 'status', '"cancel"', 'id', id)
    cart = sql_search('orders', "*", 'id', id)
    cart_split = cart.product_id.split(',')
    quantity_split = cart.quantity.split(',')
    sum_money = 0
    if cart.product_id:
        for i in cart_split:
            x = sql_search('products', '*', 'id', int(i))
            if x:
                sum_money += int(x.price) * int(quantity_split[cart_split.index(i)])
    generate_refund_bill(current_user.id, sum_money)
    return redirect('/orders')
