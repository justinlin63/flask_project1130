from .use_model import *
from . import home_blueprint


@home_blueprint.route('/')
def home():
    new = request.args.get('new')
    all_ = request.args.get('all')
    order_by = ufstr.hot()
    order_method = "DESC"
    if new:
        order_by = ufstr.id()
        order_method = 'DESC'
    if all_:
        order_by = ufstr.id()
        order_method = 'ASC'
    result = sql_search("products", ufstr.star(), order_by=order_by, order_method=order_method, fetch="all")
    product_list = []
    for i in result:
        product = []
        img_path = sql_search("media", 'file_name', "id", str(i[0]))
        img_path = 'product\\' + img_path  # 商品圖片網址
        product_name = i[1]  # 商品名稱
        product_price = i[2]  # 商品價格
        product_id = i[0]

        product.append(img_path)
        product.append(product_name)
        product.append(product_price)
        product.append(product_id)

        product_list.append(product)
    cart_num = ''
    admin = 0
    login = 0
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            admin = 1
        cart_num = len(sql_search('cart', "*", 'user_id', current_user.id, fetch='all'))
        login = 1
    return render_template('home.html', product_list=product_list, cart_num=cart_num, admin=admin, login=login)


@home_blueprint.route('/profile')
@login_required
def profile():
    user = sql_search(ufstr.users(), ufstr.star(), ufstr.id(), current_user.id)
    return render_template('profile.html', username=user.username, email=user.email, money=user.money)
