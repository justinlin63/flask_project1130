from app.functions.admin.use_model import *
from . import admin_blueprint


@admin_blueprint.route('/')
@login_required
def admin():
    if current_user.role == 'admin':
        # 這裡是管理員專屬的功能頁面
        product_type = sql_execute("SHOW COLUMNS FROM suggest_order")
        type_list = []
        for i in product_type[1:]:
            type_list.append(i[0])
        return render_template("admin.html", types=type_list)
    return redirect('/')


@admin_blueprint.route('/product/add', methods=['get', 'post'])
@login_required
def product_add():
    if current_user.role == 'admin':
        if request.method == 'POST':
            input_name = request.form['name']
            input_price = request.form['price']
            input_product_type = request.form['type']
            sql_insert(ufstr.products(), 'name,price,hot,product_type',
                       f'{ufstr.db_string(input_name)},{input_price},0,{ufstr.db_string(input_product_type)}')
            product_id = sql_search(ufstr.products(), ufstr.id(), ufstr.name(), ufstr.db_string(input_name))
            sql_insert('media', 'id,file_name', f'{int(product_id)},{ufstr.db_string("_blank.png")}')
            return render_template('product_image.html', product_id=product_id)
        return render_template('admin.html')


@admin_blueprint.route('/product/add/image', methods=['get', 'post'])
@login_required
def product_image_add():
    if current_user.role == 'admin':
        if request.method == 'POST':
            img = request.files['file']
            product_id = request.form['product_id']
            upload_folder = path + '/static/product/' + str(img.filename)  # 指定上傳目錄
            sql_update('media', 'file_name', f'{ufstr.db_string(str(img.filename))}', ufstr.id(), int(product_id))
            img.save(upload_folder)
            return redirect('/')
        return render_template('product_image.html')


@admin_blueprint.route('/orders')
@login_required
def admin_orders():
    if current_user.role == 'admin':
        page = request.args.get('page')
        if not page:
            page = 1
        else:
            page = int(page)
        start = (page - 1) * limit_per_page
        end = page * limit_per_page
        user = sql_search(ufstr.orders(), ufstr.star(), fetch=ufstr.all())
        orders = []
        orders_edit = []
        for info in user:
            if info.status == 'confirm':
                a = {'order_id': info.id, 'products': []}
                i = info.product_id.split(',')
                total_price = 0
                for w in i:
                    index = i.index(w)
                    d = {}
                    if w != '':
                        w = int(w)
                    xx = sql_search('products', "*", 'id', w)
                    q = sql_search('orders', "*", 'id', info.id)
                    q = str(q.quantity).split(',')
                    d['product_id'] = xx.id
                    d['name'] = xx.name
                    d['price'] = xx.price
                    d['quantity'] = q[index]
                    total_price += int(d['price']) * int(d['quantity'])
                    a['products'].append(d)
                a['buyer'] = info.username
                a['total_price'] = total_price
                a['cancel_url'] = '/admin/orders/cancel/' + str(info.id)
                a['deliver_url'] = '/admin/orders/deliver/' + str(info.id)
                a['status'] = '待處理'
                orders.append(a)
                orders_edit = orders[start:end]
                next_page = page + 1
        if page - 1:
            last_page = page - 1
        else:
            last_page = 0
        if not len(orders_edit) or len(orders_edit) < limit_per_page or orders_edit[-1] == orders[-1]:
            next_page = 0
        return render_template('orders.html', orders=orders_edit, admin_bool=1, next_page=next_page,
                               last_page=last_page)
    return redirect('/')


@admin_blueprint.route('/orders/all')
@login_required
def admin_all_orders():
    if current_user.role == 'admin':
        page = request.args.get('page')
        if not page:
            page = 1
        else:
            page = int(page)
        start = (page - 1) * limit_per_page
        end = page * limit_per_page
        user = sql_search(ufstr.orders(), ufstr.star(), fetch=ufstr.all())
        orders = []
        for info in user:
            a = {'order_id': info.id, 'products': []}
            i = info.product_id.split(',')
            total_price = 0
            for w in i:
                index = i.index(w)
                d = {}
                w = int(w)
                xx = sql_search('products', "*", 'id', w)
                q = sql_search('orders', "*", 'id', info.id)
                q = str(q.quantity).split(',')
                d['quantity'] = q[index]
                d['product_id'] = xx.id
                d['name'] = xx.name
                d['price'] = xx.price
                total_price += int(d['price']) * int(d['quantity'])
                a['products'].append(d)
            a['buyer'] = info.username
            a['total_price'] = total_price
            a['cancel_url'] = '/admin/orders/cancel/' + str(info.id)
            a['deliver_url'] = '/admin/orders/deliver/' + str(info.id)
            r = ''
            status = info.status
            if status == 'deliver':
                r = '已出貨'
            elif status == 'cancel':
                r = '已取消'
            elif status == 'confirm':
                r = '處理中'
            elif status == 'canceled':
                r = '商家已取消'
            a['status'] = r
            orders.append(a)
        orders.reverse()
        orders_edit = orders[start:end]
        next_page = page + 1
        if page - 1:
            last_page = page - 1
        else:
            last_page = 0
        if not len(orders_edit) or len(orders_edit) < limit_per_page or orders_edit[-1] == orders[-1]:
            next_page = 0
        return render_template('orders.html', orders=orders_edit, all_bool=1, next_page=next_page, last_page=last_page)


@admin_blueprint.route('/orders/cancel/<int:id>')
@login_required
def admin_orders_cancel(id):
    if current_user.role == 'admin':
        sql_update(ufstr.orders(), ufstr.status(), ufstr.db_string('canceled'), ufstr.id(), id)
        cart = sql_search(ufstr.orders(), ufstr.star(), ufstr.id(), id)
        cart_split = cart.product_id.split(',')
        quantity_split = cart.quantity.split(',')
        sum_money = 0
        input_username = cart.username
        if cart.product_id:
            for i in cart_split:
                info = sql_search(ufstr.products(), ufstr.star(), ufstr.id(), int(i))
                if info:
                    sum_money += int(info.price) * int(quantity_split[cart_split.index(i)])
        user = sql_search(ufstr.users(), ufstr.star(), ufstr.username(), ufstr.db_string(input_username))
        store = sql_search(ufstr.users(), ufstr.star(), ufstr.username(), ufstr.db_string('store'))
        user_money = int(user.money) + int(sum_money)
        store_money = int(store.money) - int(sum_money)
        sql_update(ufstr.users(), ufstr.money(), user_money, ufstr.username(), ufstr.db_string(input_username))
        sql_update(ufstr.users(), ufstr.money(), store_money, ufstr.username(), ufstr.db_string('store'))
        return redirect('/admin/orders')


@admin_blueprint.route('/orders/deliver/<int:id>')
@login_required
def orders_deliver(id):
    if current_user.role == 'admin':
        sql_update(ufstr.orders(), ufstr.status(), ufstr.db_string('deliver'), ufstr.id(), id)
        return redirect('/admin/orders')


@admin_blueprint.route('/search')
@login_required
def admin_search():
    if current_user.role == 'admin':
        result = sql_execute("SHOW TABLES")
        tables = [row[0] for row in result]
        return render_template('admin_search.html', tables=tables)
    return redirect('/')


@admin_blueprint.route('/search/get_columns')
@login_required
def admin_search_get_columns():
    selected_table = request.args.get('table')
    if current_user.role == 'admin':
        result = sql_execute("SHOW COLUMNS FROM {}".format(selected_table))
        columns = [row[0] for row in result]
        return jsonify(columns)


@admin_blueprint.route('/search/get_category/<category>')
@login_required
def admin_search_get_category(category):
    if current_user.role == 'admin':
        selected_table = request.args.get('table')
        result = sql_execute("SELECT {} FROM {}".format(category, selected_table))
        category = [row[0] for row in result]
        category.sort()
        return jsonify(category)


@admin_blueprint.route('/search/result', methods=['GET', 'POST'])
@login_required
def admin_search_result():
    if request.method == 'POST':
        if current_user.role == 'admin':
            selected_table = request.form.get('table')
            selected_category = request.form.get('category')
            selected_column = request.form.get('columns')
            selected_item = request.form.get('item')
            selected_list = [selected_column, selected_item, selected_category, selected_table]
            if '' not in selected_list:
                # 使用選擇的值查詢 MySQL 數據
                results = sql_search(selected_table, selected_column,
                                     selected_category, ufstr.db_string(selected_item), fetch='all')
                id = sql_search(selected_table, ufstr.id(),
                                selected_category, ufstr.db_string(selected_item), fetch='one')
            else:
                results = 0
            return render_template('admin_search_result.html', selected_table=selected_table,
                                   selected_category=selected_category, selected_columns=selected_column,
                                   results=results, id=id)
    return redirect('/admin/search')


@admin_blueprint.route('/search/modify', methods=['GET', 'POST'])
def admin_search_modify():
    if request.method == 'POST':
        if current_user.role == 'admin':
            selected_table = request.form.get('selected_table')
            selected_category = request.form.get('selected_category')
            selected_columns = request.form.get('selected_columns')
            change_value = request.form.get('change_value')
            id = request.form.get('id')
            selected_list = [selected_table, selected_columns, change_value, selected_category]
            if '' not in selected_list:
                try:
                    int(change_value)
                except Exception:
                    change_value = ufstr.db_string(change_value)
                sql_update(selected_table, selected_columns, change_value, ufstr.id(), id)
    return redirect('/admin/search')


@admin_blueprint.route('/search/delete', methods=['GET', 'POST'])
def admin_search_delete():
    if request.method == 'POST':
        if current_user.role == 'admin':
            selected_table = request.form.get('selected_table')
            selected_category = request.form.get('selected_category')
            selected_columns = request.form.get('selected_columns')
            id = request.form.get('id')
            selected_list = [selected_table, selected_columns, selected_category, id]
            if '' not in selected_list:
                sql_delete(selected_table, ufstr.id(), id)
        return redirect('/admin/search')


@admin_blueprint.route('/money', methods=['GET', 'POST'])
@login_required
def add_money():
    if request.method == 'POST':
        username = request.form['username']
        money = request.form['money']
        result = sql_search(ufstr.users(), ufstr.star(), ufstr.username(), ufstr.db_string(username))
        if result:
            money = int(money) + int(result.money)
        else:
            return redirect('/redirect/錯誤')
        sql_update(ufstr.users(), ufstr.money(), money, ufstr.username(), ufstr.db_string(username))
        return redirect('/redirect/增加成功')
    return redirect('/redirect/錯誤')
