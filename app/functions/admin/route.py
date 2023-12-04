from app.functions.admin.use_model import *
from . import admin_blueprint
import mysql.connector

db = Configs.database


@admin_blueprint.route('/')
@login_required
def admin():
    print(current_user.role)
    if current_user.role == 'admin':
        # 這裡是管理員專屬的功能頁面
        return render_template("admin.html")
    return redirect('/')


@admin_blueprint.route('/product/add', methods=['get', 'post'])
@login_required
def product_add():
    if current_user.role == 'admin':
        if request.method == 'POST':
            input_name = request.form['name']
            input_price = request.form['price']
            sql_insert(ufstr.products(), 'name,price', f'{ufstr.db_string(input_name)},{input_price}')
            product_id = sql_search(ufstr.products(), ufstr.id(), ufstr.name(), ufstr.db_string(input_name))
            print(product_id)
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
            sql_insert('media', 'id,file_name', f'{int(product_id)},{ufstr.db_string(str(img.filename))}')
            img.save(upload_folder)
            return redirect('/')
        return render_template('product_image.html')


@admin_blueprint.route('/orders')
@login_required
def admin_orders():
    if current_user.role == 'admin':
        user = sql_search(ufstr.orders(), ufstr.star(), fetch=ufstr.all())
        orders = []
        for x in user:
            if x.status == 'confirm':
                a = {'order_id': x.id, 'products': []}
                i = x.product_id.split(',')
                total_price = 0
                for w in i:
                    index = i.index(w)
                    d = {}
                    if w != '':
                        w = int(w)
                    xx = sql_search('products', "*", 'id', w)
                    q = sql_search('orders', "*", 'id', x.id)
                    q = str(q.quantity).split(',')
                    d['product_id'] = xx.id
                    d['name'] = xx.name
                    d['price'] = xx.price
                    d['quantity'] = q[index]
                    total_price += int(d['price']) * int(d['quantity'])
                    a['products'].append(d)
                a['buyer'] = x.username
                a['total_price'] = total_price
                a['cancel_url'] = '/admin/orders/cancel/' + str(x.id)
                a['deliver_url'] = '/admin/orders/deliver/' + str(x.id)
                a['status'] = '待處理'
                orders.append(a)
        return render_template('orders.html', orders=orders, admin_bool=1)
    return redirect('/')


@admin_blueprint.route('/orders/all')
@login_required
def admin_all_orders():
    if current_user.role == 'admin':
        user = sql_search(ufstr.orders(), ufstr.star(), fetch=ufstr.all())
        orders = []
        for x in user:
            a = {'order_id': x.id, 'products': []}
            i = x.product_id.split(',')
            total_price = 0
            for w in i:
                index = i.index(w)
                d = {}
                w = int(w)
                xx = sql_search('products', "*", 'id', w)
                q = sql_search('orders', "*", 'id', x.id)
                q = str(q.quantity).split(',')
                d['quantity'] = q[index]
                d['product_id'] = xx.id
                d['name'] = xx.name
                d['price'] = xx.price
                total_price += int(d['price']) * int(d['quantity'])
                a['products'].append(d)
            a['buyer'] = x.username
            a['total_price'] = total_price
            a['cancel_url'] = '/admin/orders/cancel/' + str(x.id)
            a['deliver_url'] = '/admin/orders/deliver/' + str(x.id)
            r = ''
            status = x.status
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
        return render_template('orders.html', orders=orders, all_bool=1)


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
                x = sql_search(ufstr.products(), ufstr.star(), ufstr.id(), int(i))
                if x:
                    sum_money += int(x.price) * int(quantity_split[cart_split.index(i)])
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
        conn = mysql.connector.connect(
            host='192.168.1.110',  # 主機名稱
            database=db,  # 資料庫名稱
            user='root',  # 帳號
            password='admin')  # 密碼
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        return render_template('admin_search.html', tables=tables)


@admin_blueprint.route('/search/get_columns')
@login_required
def admin_search_get_columns():
    selected_table = request.args.get('table')
    if current_user.role == 'admin':
        conn = mysql.connector.connect(
            host='192.168.1.110',  # 主機名稱
            database=db,  # 資料庫名稱
            user='root',  # 帳號
            password='admin')  # 密碼
        cursor = conn.cursor()
        cursor.execute("SHOW COLUMNS FROM {}".format(selected_table))
        columns = [row[0] for row in cursor.fetchall()]
        conn.close()
        return jsonify(columns)


@admin_blueprint.route('/search/get_category/<category>')
@login_required
def admin_search_get_category(category):
    if current_user.role == 'admin':
        conn = mysql.connector.connect(
            host='192.168.1.110',  # 主機名稱
            database=db,  # 資料庫名稱
            user='root',  # 帳號
            password='admin')  # 密碼
        cursor = conn.cursor()
        selected_table = request.args.get('table')
        cursor.execute("SELECT {} FROM {}".format(category, selected_table))
        category = [row[0] for row in cursor.fetchall()]
        category.sort()
        conn.close()
        return jsonify(category)


@admin_blueprint.route('/search/result', methods=['POST'])
@login_required
def result():
    if current_user.role == 'admin':
        conn = mysql.connector.connect(
            host='192.168.1.110',  # 主機名稱
            database=db,  # 資料庫名稱
            user='root',  # 帳號
            password='admin')  # 密碼
        cursor = conn.cursor()
        selected_table = request.form.get('table')
        selected_category = request.form.get('category')
        selected_column = request.form.get('columns')
        selected_item = request.form.get('item')
        # 使用選擇的值查詢 MySQL 數據
        query = "SELECT {} FROM {} WHERE {} = %s".format(selected_column, selected_table, selected_category)
        cursor.execute(query, (selected_item,))
        results = cursor.fetchall()
        conn.close()
        return render_template('admin_search_result.html', selected_table=selected_table,
                               selected_category=selected_category, selected_columns=selected_column,
                               results=results)


@admin_blueprint.route('/money', methods=['GET', 'POST'])
@login_required
def add_money():
    if request.method == 'POST':
        username = request.form['username']
        print(username)
        money = request.form['money']
        result = sql_search(ufstr.users(), ufstr.star(), ufstr.username(), username)
        if result:
            money = int(money) + int(result.money)
        else:
            return redirect('/redirect/錯誤')
        sql_update(ufstr.users(), ufstr.money(), money, ufstr.username(), ufstr.db_string(username))
        return redirect('/redirect/增加成功')
    return redirect('/redirect/錯誤')
