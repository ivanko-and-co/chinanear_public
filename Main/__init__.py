import ast
import base64
import datetime
import io
import json
import math
import os
import uuid
from random import randint

import requests
from flask import (Flask, jsonify, make_response, redirect, render_template,
                   request, send_file, send_from_directory, session, url_for)
from flask_mail import Mail, Message
from flask_socketio import SocketIO, emit, send
from PIL import Image
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from SQL import SQL

app = Flask(__name__)
app.config['SECRET_KEY'] = ''
app.permanent_session_lifetime = datetime.timedelta(days=10)

#   Администратор сайта
ADMIN_UID = ''
ADMIN_ROLE_UID = ''

#   Настройки почтового сервера
app.config['MAIL_SERVER']=''
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = ''
app.config['MAIL_PASSWORD'] = ''
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)

socketio = SocketIO(app)

sql = SQL()

@app.route('/')
@app.route('/<string:l1_category>')
@app.route('/<string:l1_category>/<string:l2_category>')
def home(l1_category = '', l2_category = ''):
    check_auth()

    if l1_category == '':
        category= sql.get_uppercategory(session['localization'])
    elif l2_category == '':
        category = sql.get_subcategory(session['localization'], l1_category, 1)
    else:
        category = sql.get_subcategory(session['localization'], l2_category, 2)

    return render_template('main/index.html', category=category, l1_category=l1_category, l2_category=l2_category, ses=session['auth'], conf=open_config()[session['localization']])

@app.route('/catalog/<string:l1_category>/<string:l2_category>/<string:l3_category>')
def catalog(l1_category, l2_category, l3_category):
    check_auth()

    page = request.args.get('page', 1, int)
    per_page = int(request.cookies.get('perpage', 15))
    offset = (page - 1) * per_page

    currency_rate = 1
    if session['currency'] == '₽':
        currency_rate = sql.get_currency()[0][1]

    if session['localization'] == 'Ru':
        leng = 'Ru'
    elif session['localization'] == 'En':
        leng = 'EnUs'
    
    l3_category_uid = str(sql.get_category_uid(l3_category, 3)[0][0]).upper()
    products_sql = sql.get_products(leng, l3_category_uid, offset, per_page)
    category_sql = sql.get_category_name(session['localization'], [l1_category, l2_category, l3_category])
    category_tree = [category_sql.pop(0)]
    for i in category_sql:
        if i != category_tree[-1] or len(category_sql) == 2:
            category_tree.append(i)

    pages_count = math.ceil(sql.get_count_product(l3_category_uid)[0][0] / per_page)
    pages_count_list = range(1, pages_count + 1)

    categoryes = sql.get_subcategory(session['localization'], l2_category, 2)

    products = []
    for i in products_sql:
        uid = str(i[0]).upper()
        name = i[1]
        shortDescription = i[2]
        photo = json.loads(i[3])['photo-url']
        if photo.find('tatic/img') == 1:
            photo = '../../../'+photo
        
        maxprice = 0
        minprice = 9999999
        for dict in ast.literal_eval(i[4]):
            if int(dict['price']) > maxprice:
                maxprice = int(dict['price'])
            if int(dict['price']) < minprice:
                minprice = int(dict['price'])

        if minprice == maxprice:
            prices = int(maxprice * int(currency_rate))
        else:
            prices = f"{int(minprice * int(currency_rate))} - {int(maxprice * int(currency_rate))}"

        seller_name = i[6]
        if i[7] == None:
            stock = 0
        else:
            stock = i[7]

        products.append({
            "uid": uid,
            "name": name,
            "shortDescription":shortDescription,
            "photo": photo,
            "prices": prices,
            "seller_name": seller_name,
            "stock": stock
        })


    return render_template('main/main.html', products=products, tree=category_tree, categoryes=categoryes, ses=session['auth'], page=page,
                           pages_count=pages_count, pages_count_list=pages_count_list, conf=open_config()[session['localization']])

@app.route('/product/<string:l1_category>/<string:l2_category>/<string:l3_category>/<path:article>')
def product(l1_category, l2_category, l3_category, article):
    check_auth()

    product_sql = sql.get_product(article)[0]
    currency_rate = 1
    if session['currency'] == '₽':
        currency_rate = sql.get_currency()[0][1]
    tree_sql = sql.get_category_name(session['localization'], [l1_category, l2_category, l3_category])
    tree = [tree_sql.pop(0)]
    for i in tree_sql:
        if i != tree[-1] or len(tree_sql) == 2:
            tree.append(i)
    
    def pars(product_sql, leng, currency_rate):
        name = json.loads(product_sql[0])[leng]
        description = json.loads(product_sql[1])[leng]
        shortdescription = json.loads(product_sql[2])[leng]
        photo = []
        for i in zip(json.loads(product_sql[3]), range(1, len(json.loads(product_sql[3])) + 1)):
            if i[0]['photo-url'].find('tatic/') == 1:
                photo.append(['../../../../'+i[0]['photo-url'], str(i[1])])
            else:
                photo.append([i[0]['photo-url'], str(i[1])])
        price = []
        count = []
        for i in json.loads(product_sql[4]):
            price.append(int(int(i['price']) * currency_rate))
            count.append(f"{i['quantity-min']} - {i['quantity-max']}")
        unit = json.loads(product_sql[6])[leng]
        s_uid = product_sql[7]
        return name, description, shortdescription, photo, price, count, unit, s_uid
    
    if session['localization'] == 'Ru':
        name, description, shortdescription, photo, price, count, unit, s_uid = pars(product_sql, 'ru', int(currency_rate))
    elif session['localization'] == 'En':
        name, description, shortdescription, photo, price, count, unit, s_uid = pars(product_sql, 'en-us', int(currency_rate))
    else:
        name, description, shortdescription, photo, price, count, unit, s_uid = pars(product_sql, 'zh-cn', int(currency_rate))

    return render_template('main/product.html', tree=tree, name=name, description=description,
                           short_description=shortdescription, photo=photo, price=price,
                           count=count, unit=unit, s_uid=s_uid, p_uid=article, ses=session['auth'], conf=open_config()[session['localization']])

@app.route('/get_product_url_by_uid/<string:uid>')
def get_product_url_by_uid(uid: str):
    url_sql = sql.get_product_url_by_uid(uid)[0]
    return redirect(url_for('product', l1_category=url_sql[0], l2_category=url_sql[1], l3_category=url_sql[2], article=url_sql[3]))


#Cart
@app.route('/cart')
def cart():
    check_auth()
    if session['auth'][-1] != 'buyer':
        return redirect(url_for('home'))
    
    addres_sql = json.loads(sql.get_buyer_address(session['auth'][0])[0][0])['local']
    addres = addres_sql['postcode'] + ', ' + addres_sql['country'] + ', ' + addres_sql['city'] + ', ' + addres_sql['street']+ ', ' + addres_sql['house-number']

    cart_sql = json.loads(sql.get_cart(session['auth'][0])[0][0])
    if len(cart_sql) != 0:
        products_list_uid = []
        for i in cart_sql:
            products_list_uid.append(i['product-card-uid'])


        if session['localization'] == 'Ru':
            leng = 'Ru'
        elif session['localization'] == 'En':
            leng = 'EnUs'

        if len(products_list_uid) == 0:
            products_list_sql = 'none'

        elif len(products_list_uid) == 1:
            products_list_sql = sql.get_product_cart(f"('{products_list_uid[0]}')", leng)
        else:
            products_list_sql = sql.get_product_cart(tuple(products_list_uid), leng)

        for product in zip(products_list_sql, range(len(products_list_sql))):
            products_list_sql[product[1]] = list(products_list_sql[product[1]])
            for i in zip(product[0], range(len(product[0]))):
                try:
                    products_list_sql[product[1]][i[1]] = json.loads(i[0])
                except Exception as e:
                    i = i

        dict_products = {}
        for product in zip(products_list_sql, cart_sql):
            if product[0][5] not in dict_products:
                product[0].append(product[1]['product-quantity'])
                dict_products.update({product[0][5]:[product[0]]})
            else:
                product[0].append(product[1]['product-quantity'])
                dict_products[product[0][5]].append(product[0])

        script_dict = {}
        if session['currency'] == '₽':
            currency_rate = sql.get_currency()[0][1]
        else:
            currency_rate = 1

        for i in products_list_sql:
            for pr in i[3]:
                pr['price'] = int(pr['price'] * int(currency_rate))
            script_dict.update({str(i[0]).upper():i[3]})

        script = "<script> var cart = " + json.dumps(script_dict) + "</script>"

        return render_template('main/cart.html', ses=session['auth'],script=script, cart = 1, address=addres, dict=dict_products, conf=open_config()[session['localization']])
    else:
        return render_template('main/cart.html', ses=session['auth'], address=addres, cart = 0, conf=open_config()[session['localization']])


def clear_cart():
    sql.update_cart(json.dumps([]), session['auth'][0])

@app.route('/cart/delete/<path:product_uid>')
def del_cart(product_uid):
    check_auth()
    if 'auth' not in session or session['auth'][-1] == 'none':
        return '404'
    
    cart_sql = json.loads(sql.get_cart(session['auth'][0])[0][0])
    for i in zip(cart_sql.copy(), range(len(cart_sql))):
        if i[0]['product-card-uid'] == product_uid:
            del cart_sql[i[1]]
            break

    sql.update_cart(json.dumps(cart_sql), session['auth'][0])

    return '200'

@app.route('/cart/add/<path:product_uid>')
def add_cart(product_uid):
    check_auth()
    if 'auth' not in session or session['auth'][-1] == 'none':
        return '404'
    
    cart = json.loads(sql.get_cart(session['auth'][0])[0][0])
    bool = False
    for i in cart:
        if i['product-card-uid'] == product_uid:
            i['product-quantity']+=1
            bool = True
            break
    if bool == False:
        cart.append({"product-card-uid":product_uid,"product-quantity":1,"product-seller-uid":None})

    sql.update_cart(json.dumps(cart), session['auth'][0])

    return '200'

#Order
@app.route('/order/add', methods=['POST'])
def order():
    orders = json.loads(request.get_data())
    offer_uid = uuid.uuid4()
    order_uid = uuid.uuid4()
    offer_details = {}
    price = 0

    current_rate = sql.get_currency()
    def curr_convert(price):
        if session['currency'] == '₽':
            return int(price / float(current_rate[0][1]))
        return price

    def order_convert(detail):
        if session['currency'] == '₽':
            detail['itemPrice'] = int(int(detail['itemPrice']) / float(current_rate[0][1]))
            detail['totalPrice'] = int(int(detail['totalPrice']) / float(current_rate[0][1]))

        return detail
            

    for order in orders['orders']:
        uid = order.pop('uid')
        offer_details.update({uid:order_convert(order)})
        price += curr_convert(order['totalPrice'])
    time = datetime.datetime.utcnow()
    status = 'New'
    s_uid = orders['seller_uid']
    b_uid = sql.get_actor_uid(session['auth'][0], session['auth'][-1])
    b_note = orders['comment']
    address = orders['address']

    sql.insert_offer(offer_uid, order_uid, json.dumps(offer_details),
                     price, time, session['auth'][0], status)
    sql.insert_order(order_uid, s_uid, b_uid, b_note, address,
                     offer_uid, time, status)
    clear_cart()
    return jsonify(success=True)

@app.route('/order/change_status')
def change_order():
    data = request.get_data()
    sql.update_order_state(data['state'], datetime.datetime.utcnow(), data['order_number'], session['auth'][0])
    return '200'

@app.route('/order/custom_add')
def custom_add():
    data = request.args.to_dict()
    offer_uid = uuid.uuid4()
    order_uid = uuid.uuid4()
    current_rate = sql.get_currency()
    def convert(price):
        if session['currency'] != '$':
            return int(float(price) / float(current_rate[0][1]))
        return int(price)
    offer_details = {data['productUid']:{"amount":int(data['quantity']), "itemPrice":convert(data['price']), "totalPrice":int(data['quantity'])*convert(data['price'])}}
    price = int(data['quantity']) * convert(data['price'])
    time = datetime.datetime.utcnow()
    status = 'New'
    s_uid = data['sellerUid']
    b_uid = sql.get_actor_uid(session['auth'][0], session['auth'][-1])
    b_note = ''
    addres_sql = json.loads(sql.get_buyer_address(session['auth'][0])[0][0])['local']
    address = addres_sql['postcode'] + ', ' + addres_sql['country'] + ', ' + addres_sql['city'] + ', ' + addres_sql['street']+ ', ' + addres_sql['house-number']

    sql.insert_offer(offer_uid, order_uid, json.dumps(offer_details),
                     price, time, session['auth'][0], status)
    sql.insert_order(order_uid, s_uid, b_uid, b_note, address,
                     offer_uid, time, status)

    return jsonify(success=True)

#Localization
@app.route('/change_localization/<path:lang>')
def change_localization(lang):
    session['localization'] = lang
    return redirect(request.referrer)

#Currency
@app.route('/change_currency/<path:cur>')
def change_currency(cur):
    session['currency'] = cur
    return redirect(request.referrer)

#Login
@app.route('/auth', methods=['GET', 'POST'])
def auth():
    check_auth()
    form = request.form.to_dict()
    login = form['login']
    password = form['password']
    check = list(sql.login(login)) # Uid, Email, Type, PasswordHash
    if len(check) != 0 and check_password_hash(check[0][3], password):
        session['auth'] = [check[0][0],check[0][1],check[0][2]]
        if session['auth'][2] == 'administrator':
            return redirect(url_for('currency'))
        else:
            return jsonify(success=True)
    else:
        return jsonify(success=False)

def check_auth():
    if 'auth' not in session:
        session['auth'] = ['none']

    if 'localization' not in session:
        session['localization'] = 'Ru'

    if 'currency' not in session:
        session['currency'] = '₽'


#Logout
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session['auth'] = ['none']
    return redirect(url_for('home'))


#Register
@app.route("/register", methods=['POST'])
def reg():
    form = request.form.to_dict()
    email = form['email']
    phone = form['phone']
    fname = form['fname']
    lname = form['lname']
    company_name = form['company_name']
    market_name_ru = form['market_name_ru']
    market_name_en = form['market_name_en']
    index = form['index']
    country = form['country']
    city = form['city']
    street = form['street']
    house = form['house']
    building = form['building']
    password = generate_password_hash(form['password'])
    uid = uuid.uuid4()
    create_time = datetime.datetime.utcnow()
    _type = 'buyer'
    b_uid = uuid.uuid4()

    market_json = json.dumps({"ru":market_name_ru,"en-us":market_name_en,"zh-cn":market_name_en})
    company_json = json.dumps({"ru":company_name,"en-us":company_name,"zh-cn":company_name})
    address = json.dumps({
        "local": {
            "country": country,
            "region": country,
            "city": city,
            "postcode": index,
            "street": street,
            "house-number": house,
            "building": building,
            "how-to-find": "string"
        },
        "global": {
            "country": country,
            "region": country,
            "city": city,
            "postcode": index,
            "street": street,
            "house-number": house,
            "building": building,
            "how-to-find": "string"
        },
    })
    sql.insert_user(uid, password, email, country, _type, create_time)
    sql.insert_profile(uuid.uuid4(), fname, lname, phone, uid, create_time)
    sql.insert_buyer(b_uid, address, company_json, market_json, create_time, uid)
    sql.insert_buyer_uid(b_uid, uid)
    sql.insert_chat_user(uid, b_uid, create_time)
    sql.insert_user_cart(uuid.uuid4(), '[]', b_uid, create_time, uid)

    session['auth'] = [uid, email, _type]
    return jsonify(success=True)

@app.route('/recovery', methods=['POST'])
def recovery():
    if not ('email' in request.form):
        return '404'
    email = request.form['email']
    
    cur_reset = sql.get_current_password_reset(email)

    if (not cur_reset):
        return jsonify(success=True) # Такого емейла нет в базе
    
    if (cur_reset[0][1] is not None and cur_reset[0][1] == False):
        return jsonify(success=True) # Недавний запрос на сброс пароля уже есть
        
    user_uid = cur_reset[0][0]
    reset_uid = uuid.uuid4()
    sql.create_password_reset(user_uid, reset_uid, datetime.datetime.utcnow(), datetime.datetime.utcnow() + datetime.timedelta(hours=1))
    reset_url = url_for('password_reset', token=reset_uid, _external=True)
    send_email(email, 'Сброс пароля', html = f'<p>Для того, чтобы сбросить пароль необходимо перейти по ссылке: <a href="{reset_url}">{reset_url}</a></p>')

    return jsonify(success=True)

@app.route('/password_reset')
@app.route('/password_reset/<string:token>')
def password_reset(token: str = ''):
    check_auth()

    if session['auth'][0] != 'none' or token == '':
        return redirect(url_for('home'))
    
    return render_template('main/Base/base.html', ses=session['auth'], conf=open_config()[session['localization']], token=token)

@app.route('/change_password', methods=['POST'])
def change_password():
    if not ('token' in request.form and 'password' in request.form):
        return jsonify(success=False)
    
    user_uid = sql.verify_password_reset(request.form['token'])
    if not user_uid: # Ссылка для смены пароля могла устареть
        return jsonify(success=False)
    user_uid = user_uid[0][0]
    
    # Смена пароля
    sql.finish_password_reset(request.form['token'])
    sql.change_password(user_uid, generate_password_hash(request.form['password']))

    return jsonify(success=True)

#LK
@app.route('/profile/orders')
def orders():
    check_auth()

    if session['auth'][-1] == 'administrator':
        return redirect(url_for('admin_orders'))
    else:
        offers, page, pages_count, pages_count_list = offers_list(session['auth'])

        return render_template('user_lk/buyer_order_list.html', ses=session['auth'][-1], offers=offers, 
                               conf=open_config()[session['localization']], page=page, pages_count=pages_count, pages_count_list=pages_count_list)

def offers_list(ses):
    page = request.args.get('page', 1, int)
    offset = 15 * (page-1)

    # Фильтрация
    f_status = request.args.get('status', '%', str)
    min_date = request.args.get('min_date', '2000-01-01', str)
    max_date = request.args.get('max_date', '2200-01-01', str)
    
    if session['localization'] == 'Ru':
        leng = 'Ru'
    elif session['localization'] == 'En':
        leng = 'EnUs'
    results = sql.get_orders_buyer(ses[0], leng, offset, f_status, min_date, max_date)
    offers = []
    if not results:
        return offers, page
    for result in results:
        order_number = result[0]
        status = result[1]
        create_time = result[2].strftime('%Y-%m-%d %H:%M')
        try:
            change_time = result[3].strftime('%Y-%m-%d %H:%M')
        except:
            change_time = '-'
        seller_name = result[4]
        name_count = len(json.loads(result[5]))
        product_count = 0
        price = 0
        for product in json.loads(result[5]).items():
            product_count += product[1]['amount']
            current_rate = sql.get_currency()
            if session['currency'] != '$':
                price += float(product[1]['totalPrice']) * float(current_rate[0][1])
            price += product[1]['totalPrice']
        offers.append([order_number, status, create_time, change_time, name_count, product_count, seller_name, int(price)])
    
    pages_count = math.ceil(sql.get_orders_count(ses[0])[0][0] / 15)

    return offers, page, pages_count, range(1, pages_count + 1)

@app.route('/profile/order/<int:order_number>')
def order_detal(order_number):
    check_auth()
    if session['auth'][-1] == 'administrator':
        return redirect(url_for('admin_orders'))
    else:
        if session['localization'] == 'Ru':
            local = 'RU'
        elif session['localization'] == 'En':
            local = 'EnUs'
        order = sql.get_order(order_number, local)[0]
        seller_name = order[0]
        address = order[1]

        current_rate = sql.get_currency()

        def convert(x):
            if session['currency'] != '$':
                return int(float(x) * float(current_rate[0][1]))
            return x
        total_price = convert(order[3])
        status = order[4]
        products = {}
        for product in json.loads(order[2]).items():
            products.update({product[0]:[product[1]['amount'], convert(product[1]['itemPrice']), convert(product[1]['amount'] * product[1]['itemPrice'])]})
        
        product_uid = tuple(products.keys())
        if len(product_uid) == 1:
            product_uid = f"('{product_uid[0]}')"
        product = sql.get_order_product(product_uid, local)
        for prod in product:
            products[str(prod[0]).upper()].append(json.loads(prod[1])['photo-url'])
            products[str(prod[0]).upper()].append(prod[2])



    return render_template('user_lk/buyer_order_detail.html', ses=session['auth'][-1], seller_name=seller_name,
                           address=address, products=products, total_price=total_price, order_number=order_number, status=status, conf=open_config()[session['localization']])

@app.route('/profile/order_change_status', methods=['POST'])
def change_order_status():
    check_auth()

    time = datetime.datetime.utcnow()
    for order_number,status in json.loads(request.data).items():
        sql.update_offer(time, session['auth'][0], status, order_number)
        sql.update_order(time, session['auth'][0], status, order_number)

    return redirect(request.referrer)

@app.route('/profile/product_list')
def product_list():
    check_auth()

    category = sql.get_uppercategory(session['localization'])
    products, page, pages_count, pages_count_list = product_list_lk_pars(session['auth'][0])

    return render_template('user_lk/seller_product_list.html', ses=session['auth'][-1], conf=open_config()[session['localization']],
                           category=category, page=page, products=products, pages_count=pages_count, pages_count_list=pages_count_list)

def product_list_lk_pars(uid):
    page = request.args.get('page', 1, int)
    offset = 15 * (page -1) #TODO прицепить ограничение на sql запрос по количеству товаров

    f_status = request.args.get('status', '%', str)
    category_1 = request.args.get('category_1', '%', str)
    category_2 = request.args.get('category_2', '%', str)
    category_3 = request.args.get('category_3', '%', str)

    if session['localization'] == 'En':
        local = 'EnUs'
    else:
        local = session['localization']
    products_list = sql.get_product_lk(uid, category_1, category_2, category_3, local)
    products = []
    for product in products_list:
        uid_product = product[0]
        try:
            photo = json.loads(product[1])['photo-url']
            if photo.find('tatic/i') == 1:
                photo = '../../' + photo
        except:
            photo = ''
        
        short_description = product[2]
        stock = product[3]
        if product[4] != None:
            category = sql.get_category(session['localization'], product[4])[0][0]
        else:
            category = ''
        time = product[5].strftime('%Y-%m-%d %H:%M:%S')
        is_active = product[6]

        currency_ = sql.get_currency()
        if session['currency'] == '₽':
            minprice = int(float(min([i['price'] for i in json.loads(product[7])])) * float(currency_[0][1]))
        else:
            minprice = min([i['price'] for i in json.loads(product[7])])

        products.append([uid_product, photo, short_description, stock, category, time, is_active, minprice])

    pages_count = math.ceil(sql.get_count_product(uid)[0][0] / 15)

    return products, page, pages_count, range(1, pages_count + 1)

@app.route('/profile/product_add')
@app.route('/profile/product_add/<path:id>')
def product_add(id = ''):
    check_auth()
    categories = sql.get_uppercategory(session['localization'])
    units_sql = sql.get_product_units()
    units = []
    for i in units_sql:
        units.append((i[0], json.loads(i[1])))
    if session['localization'] == 'Ru':
        local = 'ru'
    elif session['localization'] == 'En':
        local = 'en-us'
    return render_template('user_lk/seller_product_add.html', ses=session['auth'][-1], local=local, conf=open_config()[session['localization']],
                           units=units, category=categories, uid=id)

@app.route('/profile/product_add_save', methods=['POST'])
def product_add_save():
    form = request.form.to_dict()
    files = request.files.to_dict()

    product_uid = gen_uuid()
    is_active = int(form['is_active'])
    stock = int(form['stock'])
    time = datetime.datetime.utcnow()
    name = form['product_name']
    description = json.loads(form['description'])
    short_description = form['short_description']
    product_category_uid = sql.get_category_uid(form['category'], 3)[0]
    cost_range = form['price']
    quantity_sysname = form['units']
    seller_uid = sql.get_actor_uid(session['auth'][0], 'seller')

    product_path = os.path.join("Main/static/img/products/" + product_uid)
    os.mkdir(product_path)

    def img_safe(file, filename, extension):
        file.save(product_path + '/' + filename + extension)
    
    preview_photo = files.pop('preview_img')
    filename = gen_uuid()
    extension = os.path.splitext(preview_photo.filename)[1]
    img_safe(preview_photo, filename, extension)
    preview_photo = '{"photo-uid":null,"photo-url":"' + f'static/img/products/{product_uid}/{filename + extension}' + '"}'

    def photo_template(filename, extension):
        _photo_template = '{"photo-uid":null,"photo-url":"' + f'static/img/products/{product_uid}/{filename + extension}' + '"}'
        return json.loads(_photo_template)
    
    photos = []
    for file in files:
        photo = files[file]
        filename = gen_uuid()
        extension = os.path.splitext(photo.filename)[1]
        img_safe(photo, filename, extension)
        photos.append(photo_template(filename, extension))

    description_img = json.loads(form['description_img'])
    for element in description_img:
        for data in description_img[element]:
            img = Image.open(io.BytesIO(base64.decodebytes(bytes(description_img[element][data].split(',')[1], "utf-8"))))
            filename = gen_uuid()
            img.save(product_path + '/' + filename + '.' + description_img[element][data].split(';')[0].split('/')[1])
            description.update({element:description[element].replace(data, '../../../../static/img/products/' + product_uid + '/' + filename + '.' + description_img[element][data].split(';')[0].split('/')[1])})

    sql.insert_product(product_uid, is_active, stock, time, name, json.dumps(description), short_description, json.dumps(photos), preview_photo,
                       product_category_uid, cost_range, quantity_sysname, seller_uid, session['auth'][0])
    return jsonify(success=True, redirect=url_for('product_list'))

#Admin

#Currency
@app.route('/admin')
@app.route('/admin/currency')
def currency():
    check_auth()
    #if session['auth'][-1] != 'Admin':
#        return redirect(url_for('home'))
    currency_rate = sql.get_currency()
    
    return render_template('admin/admin_currency.html', ses=session['auth'][-1], currencyru=float(currency_rate[0][1]), currencycn=float(currency_rate[1][1]),
                            conf=open_config()[session['localization']])

@app.route('/admin/currency_change', methods=['GET', 'POST'])
def currency_change():
    check_auth()
    sql.update_currency(request.form['currency'], request.form['value'], datetime.datetime.utcnow())
    return redirect(request.referrer)

@app.route('/admin/product')
@app.route('/admin/product/<path:seller>')
@app.route('/admin/product/<path:seller>/<path:id>')
def admin_user(seller = '', id = ''):
    #if session['auth'][-1] != 'Admin':
#        return redirect(url_for('home'))

    page = request.args.get('page', 1, int)
    offset = page * 15

    if seller == '':
        return render_template('admin/admin_product_list_start.html', ses=session['auth'][-1], conf=open_config()[session['localization']], page=page)
    elif seller != '' and id == '':
        category = sql.get_uppercategory(session['localization'])
        products = product_list_lk_pars(seller)
        return render_template('admin/admin_product_list.html', ses=session['auth'][-1], conf=open_config()[session['localization']], 
                               category=category, page=page, seller=seller, products=products)
    elif id != '':
        return render_template('admin/admin_product_add.html', ses=session['auth'][-1], conf=open_config()[session['localization']], page=page)

@app.route('/admin/orders')
@app.route('/admin/orders/<path:user>')
@app.route('/admin/orders/<path:user>/<path:id>')
def admin_orders(user = '', id = ''):
    #if session['auth'][-1] != 'Admin':
#        return redirect(url_for('home'))

    if user == '':
        return render_template('admin/admin_product_list_start.html', ses=session['auth'][-1], str='1', conf=open_config()[session['localization']], page=page)
    elif user != '' and id == '':
        offers, page = offers_list(user)
        return render_template('admin/admin_order_list.html', ses=session['auth'][-1], offers=offers, conf=open_config()[session['localization']], page=page)
    elif id != '':
        return render_template('admin/admin_order_detail.html', ses=session['auth'][-1], conf=open_config()[session['localization']], page=page)

@app.route('/admin/change_user_status/<path:buyer_uid>/<string:type>')
def change_user_status(buyer_uid, type):
    #if session['auth'][-1] != 'Admin':
#        return redirect(url_for('home'))

    buyer_info = list(sql.get_buyer_info(buyer_uid)[0])
    b_uid = buyer_info[0]
    s_uid = gen_uuid()
    u_uid = sql.get_user_uid(b_uid, 'buyer')
    buyer_info[0] = s_uid
    time = datetime.datetime.utcnow()
    buyer_info.append(time)
    buyer_info.append(session['auth'][0])
    try:
        sql.insert_seller_user(buyer_info)
        sql.insert_seller_user_link(u_uid, s_uid)
        sql.update_user_status(type, time, u_uid)
    except:
        return '404'

    return '200'

#Chat
def gen_uuid() -> str:
    return str(uuid.uuid4()).upper()

dialogues = {}

@app.route('/start_chat/<string:trader>')
def start_chat(trader: str = ''):
    check_auth()
    if session['auth'][-1] == 'none':
        return redirect(url_for('home'))

    if (trader == ''):
        return '404'

    # Переход через связь с продавцом
    uid = session['auth'][0]
    act_uid = sql.get_actor_uid(uid, session['auth'][2])
    act_trader = sql.get_actor_uid(trader, 'seller')
    if act_trader == '':
        return '404'
    # Создание чата если его ещё нет
    sql.init_chat_room(uid, act_uid, trader, act_trader, datetime.datetime.utcnow(), uuid.uuid4())

    return redirect(url_for('chat'))

@app.route('/chat')
def chat():
    check_auth()
    if session['auth'][-1] == 'none':
        return redirect(url_for('home'))

    # Создание чата с администратором если его ещё нет
    uid = session['auth'][0]
    act_uid = sql.get_actor_uid(uid, session['auth'][2])
    sql.init_chat_room(uid, act_uid, ADMIN_UID, ADMIN_ROLE_UID, datetime.datetime.utcnow(), uuid.uuid4())

    return render_template('chat.html', ses=session['auth'][-1], conf=open_config()[session['localization']])

admin_sid = 0
NOTIFICATION_UID = '00000000-0000-0000-0000-000000000000'

@socketio.on('connect')
def on_connect():
    # Получение списка диалогов
    rows = sql.query("""SELECT room.Uid, CONCAT(prof.FirstName, ' ', prof.LastName) AS Name FROM service_chat.main.ChatRoom AS room
                    LEFT JOIN service_chat.main.ChatRoomUser AS rUser ON rUser.ChatRoomUid = room.Uid
                    LEFT JOIN service_profile.main.Profile AS prof ON prof.LinkedUserUid = rUser.UserUid
                    WHERE room.Uid IN 
                    (SELECT ChatRoomUid FROM service_chat.main.ChatRoomUser WHERE UserUid = %s)
                    AND rUser.UserUid != %s
                    AND rUser.UserUid != %s
                    ORDER BY room.LastMessageSentUtc DESC, room.MomentCreatedUtc DESC
                    """, (session['auth'][0], session['auth'][0], ADMIN_UID))

    if session['auth'][0] == ADMIN_UID:
        admin_sid = request.sid
    else:
        # Добавление диалога с админом в самый верх
        admin_chat = sql.get_chat_uid(session['auth'][0], ADMIN_UID)
        rows.insert(0, (admin_chat[0][0], ''))

    for i, row in enumerate(rows):
        row = list(row)
        row[0] = str(row[0]) # Uid to str
        d_id = row[0]
        if d_id in dialogues:
            dialogues[d_id].append((request.sid, session['auth'][0]))
        else:
            dialogues[d_id] = [(request.sid, session['auth'][0])]
        rows[i] = row

    # Отправка списка клиенту
    emit('connect', rows)

@socketio.on('disconnect')
def on_disconnect():
    # Получение списка диалогов
    rows = sql.query('SELECT ChatRoomUid FROM service_chat.main.ChatRoomUser WHERE UserUid = %s', (session['auth'][0],))

    if session['auth'][0] == ADMIN_UID:
        admin_sid = 0

    for row in rows:
        d_id = str(row[0])
        dialogues[d_id].remove((request.sid, session['auth'][0]))
        if len(dialogues[d_id]) == 0:
            del dialogues[d_id]

@socketio.event
def load_dialogue(d_id):
    #   TODO: Здесь также нужно убедиться в том, что юзер пытается получить сообщения из диалога который ему принадлежит
    rows = sql.load_chat(d_id)

    admin_invited = False

    response = []
    for row in rows:
        sender = str(row[0]).upper()
        is_notify = str(row[2]) == NOTIFICATION_UID
        message = row[1]
        name = row[3]
        if is_notify:
            response.append(['notification', message])
            admin_invited = True
        elif sender == str(session['auth'][0]).upper():
            response.append(['me', message])
        elif sender == ADMIN_UID:
            response.append(['you admin', message])
            admin_invited = True
        else:
            response.append(['you', message, name])

    emit('load_dialogue', {'id': d_id, 'messages': response, 'adminInvited': admin_invited})

@socketio.event
def send_message(data):
    # Получение ActorUid
    actorUid = sql.query('SELECT ActorUid FROM service_chat.main."User" WHERE Uid = %s', (session['auth'][0],))[0][0]

    # Получение имени отправителя
    sender_name = sql.get_full_name(session['auth'][0])[0][0]

    # Сохранение сообщения в БД
    sql.query("INSERT INTO service_chat.main.ChatRoomMessage (Id, Uid, ChatRoomUid, SenderUid, ActorUid, Payload, Type, MomentCreatedUtc) VALUES (%s, %s, %s, %s, %s, %s, 'plain-text', %s);",
                    (randint(1,127), gen_uuid(), data['id'], session['auth'][0], actorUid, data['message'], datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')))
    # Обновление даты последнего сообщения в диалоге
    sql.query("UPDATE service_chat.main.ChatRoom SET LastMessageSentUtc = %s WHERE Uid = %s", (datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'), data['id']))
    sql.connection.commit()

    # Отправка сообщения всем участникам диалога в сети
    for receiver in dialogues[data['id']]:
        sid = receiver[0] # Id сессии
        uid = receiver[1] # Id пользователя
        if uid == session['auth'][0]:
            emit('message_received', {'id': data['id'], 'message': ['me', data['message']]}, room=sid)
        elif uid == ADMIN_UID:
            emit('message_received', {'id': data['id'], 'message': ['you admin', data['message']]}, room=sid)
        else:
            emit('message_received', {'id': data['id'], 'message': ['you', data['message'], sender_name]}, room=sid)

@socketio.event
def invite_admin(d_id):
    #   TODO: Здесь также нужно убедиться в том, что юзер пытается пригласить админа в свой диалог
    sql.add_admin_to_chat(d_id, ADMIN_UID)

    # Если администратор в сети - показываем ему диалог
    if (admin_sid != 0):
        if d_id in dialogues:
            dialogues[d_id].append((admin_sid, ADMIN_UID))
        else:
            dialogues[d_id] = [(admin_sid, ADMIN_UID)]

    # Уведомление о приглашении администратора
    # Сохранение уведомления в БД
    sql.query("INSERT INTO service_chat.main.ChatRoomMessage (Id, Uid, ChatRoomUid, SenderUid, ActorUid, Payload, Type, MomentCreatedUtc) VALUES (%s, %s, %s, %s, %s, %s, 'plain-text', %s);",
                    (randint(1,127), gen_uuid(), d_id, ADMIN_UID, NOTIFICATION_UID, 'Administrator was invited to chat', datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')))
    # Рассылка уведомления тем кто в сети
    for receiver in dialogues[d_id]:
        sid = receiver[0] # Id сессии
        emit('message_received', {'id': d_id, 'message': ['notification', 'Administrator was invited to chat']}, room=sid)


def open_config() -> dict:
    with open('config.json', encoding='utf-8') as f:
        config = json.load(f)

    return config


@app.route('/search_seller', methods=['POST'])
def search_seller():
    if session['localization'] == 'Ru':
        leng = 'Ru'
    elif session['localization'] == 'En':
        leng = 'EnUs'

    response = sql.search_seller(request.form['search'], leng)
    if not response:
        response = []
    return jsonify(response)

@app.route('/search_product_and_img', methods=['POST'])
def search_product_and_img():
    if session['localization'] == 'Ru':
        leng = 'Ru'
    elif session['localization'] == 'En':
        leng = 'EnUs'

    response = sql.search_product_and_img(request.form['search'], leng)
    if not response:
        response = []
    return jsonify(response)


def send_email(receiver:str, subject:str, text = None, html = None) -> bool:
    try:
        msg = Message(subject, sender=app.config['MAIL_USERNAME'], recipients=[receiver])
        msg.body = text
        msg.html = html
        mail.send(msg)
        return True
    except Exception as e:
        print(e)
        return False
    
@app.route('/get_subcategory/<int:level>/<string:category>')
def get_subcategory(level: int, category:str):
    subcategory = sql.get_subcategory(session['localization'], category, level)
    return jsonify(subcategory)

@app.route('/get_notify_count')
def get_notify_count():
    cart = len(json.loads(sql.get_cart(session['auth'][0])[0][0]))
    order = sql.get_orders_count(session['auth'][0])[0][0]
    return jsonify(cart=cart, order=order)