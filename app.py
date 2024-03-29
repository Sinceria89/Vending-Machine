from __future__ import print_function  # In python 2.7
from icon import *
from router import *
from decimal import Decimal
from Qrcode import *
import math
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import sys
from flask_paginate import Pagination, get_page_parameter
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import timedelta, datetime
import logging
import urllib.request
import os
import re
import io
import base64
import threading

class Config:
    SCHEDULER_API_ENABLED = True

USER_FOLDER = 'static/user_pic'
UPLOAD_FOLDER = 'static/upload'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['USER_PROFILE'] = USER_FOLDER
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
time = datetime.now()


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    if 'logged_in' in session:
        return redirect('/homepage')

    return render_template('index.html')


@app.route('/homepage')
def homepage():
    if 'logged_in' not in session:
        # abort(403)
        return render_template("test.html")
    else:
        try:
            user_id = session.get('user_id')
            
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            curr = conn.cursor(pymysql.cursors.DictCursor)
            cur = conn.cursor(pymysql.cursors.DictCursor)
            categories = conn.cursor(pymysql.cursors.DictCursor)
            categories.execute("SELECT * FROM categories")
            cursor.execute("SELECT * FROM products")
            curr.execute(
                "SELECT * FROM users_detail WHERE user_id=%s", (user_id,))
            cur.execute(
                "SELECT transactions.transaction_id,cart_items.cart_item_id, cart_items.cart_id, carts.user_id, products.product_id, products.image, products.product_name, cart_items.quantity, products.price, carts.total_price, carts.total_quantity FROM products LEFT JOIN cart_items ON products.product_id=cart_items.product_id  LEFT JOIN carts ON cart_items.cart_id=carts.cart_id LEFT JOIN transactions ON transactions.cart_id=carts.cart_id WHERE cart_items.quantity > 0 AND carts.user_id=%s AND transactions.status != 'success'", (user_id,))
            rows = cursor.fetchall()
            cat = categories.fetchall()
            user = curr.fetchone()
            Cart_list = cur.fetchall()
            # app.logger.info(Cart_list)
            if len(Cart_list) > 0:
                session['Shoppingcart'] = Cart_list
                session['cart_id'] = session.get('Shoppingcart')[0].get('cart_id')
            return render_template('homepage.html', user=user, Cart_list=Cart_list, user_id=user_id, products=rows, categories=cat)

        finally:
            if 'cursor' in locals() and cursor is not None:
                cursor.close()
            if 'conn' in locals() and conn is not None:
                conn.close()



@app.route('/category/<int:category_id>')
def show_items_by_category(category_id):
    try:
        user_id = session.get('user_id')
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        curr = conn.cursor(pymysql.cursors.DictCursor)
        cur = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM products LEFT JOIN categories ON products.category_id = categories.category_id WHERE categories.category_id = %s AND products.stock != 0", category_id)
        curr.execute(
        "SELECT * FROM users_detail WHERE user_id=%s", (user_id,))
        cur.execute(
        "SELECT transactions.transaction_id,cart_items.cart_item_id, cart_items.cart_id, carts.user_id, products.product_id, products.image, products.product_name, cart_items.quantity, products.price, carts.total_price, carts.total_quantity FROM products LEFT JOIN cart_items ON products.product_id=cart_items.product_id  LEFT JOIN carts ON cart_items.cart_id=carts.cart_id LEFT JOIN transactions ON transactions.cart_id=carts.cart_id WHERE cart_items.quantity > 0 AND carts.user_id=%s AND transactions.status != 'success'", (user_id,))
        products = cursor.fetchall()
        user = curr.fetchone()
        Cart_list = cur.fetchall()
        session['category_name'] = products[0]['category_name'] if len(products) > 0 else None
        if len(Cart_list) > 0:
            session['Shoppingcart'] = Cart_list
            session['cart_id'] = session.get('Shoppingcart')[0].get('cart_id')
        if not products:
            flash("ไม่พบสินค้าในหมวดหมู่ดังกล่าว", "warning")
            return redirect(request.referrer)
        return render_template('category.html', user=user, Cart_list=Cart_list, user_id=user_id, products=products)
    except Exception as e:
        print(e)
        flash("An error occurred while retrieving products. Please try again later.", "danger")
        return redirect(request.referrer)
    finally:
        cursor.close()
        conn.close()


@app.route('/cart_add', methods=['POST'])
def AddCart():
    try:
        conn = mysql.connect()
        user_id = session.get('user_id')
        product_id = int(request.form.get('product_id'))
        quantity = int(request.form.get('quantity'))
        select = conn.cursor(pymysql.cursors.DictCursor)
        price_check = conn.cursor(pymysql.cursors.DictCursor)
        carts = conn.cursor(pymysql.cursors.DictCursor)
        cart_items = conn.cursor(pymysql.cursors.DictCursor)
        transc = conn.cursor(pymysql.cursors.DictCursor)
        log = conn.cursor(pymysql.cursors.DictCursor)
        if request.method == "POST":
            DateTime = datetime.now()
            total_price = 0.0
            total_quantity = 0
            total_price += float(request.form.get('price')) * quantity
            total_quantity += quantity
            new_total_price = 0
            # Check if there is an active cart for the user
            carts.execute(
                "SELECT * FROM carts LEFT JOIN transactions ON carts.cart_id = transactions.cart_id WHERE user_id=%s AND transactions.status='pending'", (user_id,))
            cart = carts.fetchone()

            if cart:
                cart_id = cart['cart_id']
                # Check if the product is already in the cart
                cart_items.execute(
                    "SELECT * FROM cart_items WHERE cart_id=%s AND product_id=%s", (cart_id, product_id))
                cart_item = cart_items.fetchone()
                if cart_item:
                    cart_item_id = cart_item['cart_item_id']
                    price_check.execute("SELECT cart_items.cart_item_id, cart_items.cart_id, cart_items.product_id, cart_items.quantity, products.price FROM cart_items LEFT JOIN products ON cart_items.product_id = products.product_id LEFT JOIN carts ON cart_items.cart_id = carts.cart_id WHERE carts.user_id = %s AND cart_items.cart_id = %s ", (user_id, cart_id))
                    product_prices = price_check.fetchall()
                    new_total_price = 0
                    total_quantity = 0
                    for row in product_prices:
                        current_price = row['price']
                        current_quantity = row['quantity']
                        if row['cart_item_id'] == cart_item_id:
                            current_quantity = quantity
                        sub_total = current_price * current_quantity
                        print(sub_total)
                        new_total_price += sub_total
                        print(new_total_price)
                        total_quantity += current_quantity

                    cart_items.execute(
                        "UPDATE cart_items SET quantity=%s WHERE cart_item_id=%s", (quantity, cart_item_id))
                    carts.execute("UPDATE carts SET total_price=%s, total_quantity=%s WHERE cart_id=%s", (
                        new_total_price, total_quantity, cart_id))
                    cart_items.execute(
                        "UPDATE cart_items SET quantity=%s WHERE cart_item_id=%s", (quantity, cart_item_id))
                    carts.execute("UPDATE carts SET total_price=%s, total_quantity=%s WHERE cart_id=%s", (
                        new_total_price, total_quantity, cart_id))
                else:
                    cart_items.execute(
                        "INSERT INTO cart_items (cart_id, product_id, quantity) VALUES (%s, %s, %s)", (cart_id, product_id, quantity))
                    new_total_price = Decimal(
                        request.form.get('price')) * quantity
                    carts.execute("UPDATE carts SET total_price=total_price+%s, total_quantity=total_quantity+%s WHERE cart_id=%s",
                                  (new_total_price, quantity, cart_id))

                # Update total_quantity in case new item is added to the cart
                carts.execute(
                    "SELECT SUM(quantity) as total_quantity FROM cart_items WHERE cart_id=%s", (cart_id,))
                cart_items_total = carts.fetchone()['total_quantity']
                carts.execute(
                    "UPDATE carts SET total_quantity=%s WHERE cart_id=%s", (cart_items_total, cart_id))
            else:
                # Create a new cart for the user
                carts.execute("INSERT INTO carts (total_price, total_quantity, date, user_id) VALUES (%s, %s, %s, %s)",
                              (total_price, total_quantity, DateTime, user_id))
                cart_id = carts.lastrowid
                cart_items.execute(
                    "INSERT INTO cart_items (cart_id, product_id, quantity) VALUES (%s, %s, %s)", (cart_id, product_id, quantity))
                transc.execute(
                    "INSERT INTO transactions (cart_id, status, date) VALUES (%s, %s, %s)", (cart_id, 'pending', DateTime))
            flash("Item successfully added to cart.", "success")
            print(cart_id)
            conn.commit()
            select.execute(
                "SELECT transactions.transaction_id,cart_items.cart_item_id, cart_items.cart_id, carts.user_id, products.product_id, products.image, products.product_name, cart_items.quantity, products.price, carts.total_price, carts.total_quantity FROM products LEFT JOIN cart_items ON products.product_id=cart_items.product_id  LEFT JOIN carts ON cart_items.cart_id=carts.cart_id LEFT JOIN transactions ON transactions.cart_id=carts.cart_id WHERE cart_items.quantity > 0 AND carts.user_id=%s AND transactions.status != 'success'", (user_id,))
            Cart_list = select.fetchall()
            session['Shoppingcart'] = Cart_list
            log.execute("INSERT INTO activity_log (action, date, user_id) VALUES ('Shopping Cart added', %s, %s)",
                              (DateTime, user_id))
            conn.commit()
            return redirect(request.referrer)

    except Exception as e:
        print(e)
    finally:
        select.close()
        carts.close()
        cart_items.close()
        transc.close
        return redirect(request.referrer)


@app.route('/cart_empty')
def empty_cart():
    try:
        user_id = session.get('user_id')
        conn = mysql.connect()
        cart_id_query = conn.cursor(pymysql.cursors.DictCursor)
        clear_transactions = conn.cursor(pymysql.cursors.DictCursor)
        clear_cart_items = conn.cursor(pymysql.cursors.DictCursor)
        clear_carts = conn.cursor(pymysql.cursors.DictCursor)
        log = conn.cursor(pymysql.cursors.DictCursor)
        DateTime = datetime.now()
        cart_id_query.execute(
            "SELECT * FROM carts LEFT JOIN transactions ON carts.cart_id = transactions.cart_id WHERE user_id=%s AND transactions.status='pending'", (user_id,))
        cart_id = cart_id_query.fetchone()['cart_id']
        clear_transactions.execute(
            "DELETE FROM transactions WHERE cart_id=%s", (cart_id,))
        clear_cart_items.execute(
            "DELETE FROM cart_items WHERE cart_id=%s", (cart_id,))
        clear_carts.execute("DELETE FROM carts WHERE cart_id=%s", (cart_id,))
        flash("Cart has been empty.", "success")
        log.execute("INSERT INTO activity_log (action, date, user_id) VALUES ('Shopping Cart empty', %s, %s)",
                              (DateTime, user_id))
        conn.commit()
        session.pop('Shoppingcart', None)
        session.pop('cart_id', None)
        session.pop('cart_item_id', None)
        return redirect(request.referrer)
    except Exception as e:
        print(e)
        return redirect(request.referrer)
    finally:
        clear_transactions.close()
        clear_cart_items.close()
        clear_carts.close()
        cart_id_query.close()
        conn.close()


@app.route('/cart_item_delete/<int:cart_item_id>')
def delete_cart_item(cart_item_id):
    try:
        conn = mysql.connect()
        user_id = session.get('user_id')
        cart_items = conn.cursor(pymysql.cursors.DictCursor)
        transactions = conn.cursor(pymysql.cursors.DictCursor)
        cur = conn.cursor(pymysql.cursors.DictCursor)
        carts = conn.cursor(pymysql.cursors.DictCursor)
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        Cart_list = session.get('Shoppingcart')
        cart_id = session.get('Shoppingcart')[0].get('cart_id')
        log = conn.cursor(pymysql.cursors.DictCursor)
        DateTime = datetime.now()
        total_price = 0
        total_quantity = 0
        if Cart_list:
            for item in Cart_list:
                if item['cart_item_id'] == cart_item_id:
                    Cart_list.remove(item)
                    cart_items.execute(
                        "DELETE cart_items FROM cart_items WHERE cart_item_id = %s", (cart_item_id,))
                    cur.execute(
                        "SELECT transactions.transaction_id,cart_items.cart_item_id, cart_items.cart_id, carts.user_id, products.product_id, products.image, products.product_name, cart_items.quantity, products.price, carts.total_price, carts.total_quantity FROM products LEFT JOIN cart_items ON products.product_id=cart_items.product_id  LEFT JOIN carts ON cart_items.cart_id=carts.cart_id LEFT JOIN transactions ON transactions.cart_id=carts.cart_id WHERE cart_items.quantity > 0 AND carts.user_id=%s AND transactions.status != 'success'", (user_id,))
                    for row in cur:
                        current_price = row['price']
                        current_quantity = row['quantity']
                        subtotal = current_price * current_quantity
                        total_quantity += current_quantity
                        total_price += subtotal
                        print(total_quantity)
                        print(subtotal)
                        print(total_price)
                    cursor.execute(
                        "UPDATE carts SET total_price = %s, total_quantity = %s WHERE cart_id = %s", (total_price ,total_quantity ,cart_id))
                    session['Shoppingcart'] = []
                    for row in cur:
                        item = {
                            'cart_item_id': row['cart_item_id'],
                            'cart_id': row['cart_id'],
                            'user_id': row['user_id'],
                            'product_id': row['product_id'],
                            'image': row['image'],
                            'product_name': row['product_name'],
                            'quantity': row['quantity'],
                            'price': row['price'],
                            'total_price': row['total_price'],
                            'total_quantity': row['total_quantity']
                        }
                        session['Shoppingcart'].append(item)
                    session.modified = True
                    flash("Item successfully removed from cart.", "success")
                    session['Shoppingcart'] = Cart_list
                    print(Cart_list)
        if len(Cart_list) == 0:
            transactions.execute(
                "DELETE FROM transactions WHERE cart_id = %s", (cart_id,))
            carts.execute(
                "DELETE FROM carts WHERE cart_id = %s", (cart_id,))
            session.pop('Shoppingcart')
            session.pop('cart_id', None)
            session.pop('cart_item_id', None)
        log.execute("INSERT INTO activity_log (action, date, user_id) VALUES ('Shopping Cart item deleted', %s, %s)",
            (DateTime, user_id))
        conn.commit()
        return redirect(request.referrer)
    except Exception as e:
        print(e)
        flash("An error occurred while removing item from cart. Please try again later.", "danger")
        return redirect(request.referrer)
    finally:
        transactions.close()
        cart_items.close()
        carts.close()
        conn.close()


@app.route('/update_cart_item/<int:cart_item_id>', methods=['POST', 'GET'])
def update_cart_item(cart_item_id):
    if request.method == 'POST':
        try:
            user_id = session.get('user_id')
            cart_id = session.get('cart_id')
            total_price = 0
            total_quantity = 0
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cur = conn.cursor(pymysql.cursors.DictCursor)
            new_quantity = int(request.form.get('cart_quantity'))
            log = conn.cursor(pymysql.cursors.DictCursor)
            DateTime = datetime.now()
            cursor.execute(
                "UPDATE cart_items SET quantity = %s WHERE cart_item_id = %s", (new_quantity, cart_item_id))
            cur.execute(
                "SELECT transactions.transaction_id,cart_items.cart_item_id, cart_items.cart_id, carts.user_id, products.product_id, products.image, products.product_name, cart_items.quantity, products.price, carts.total_price, carts.total_quantity FROM products LEFT JOIN cart_items ON products.product_id=cart_items.product_id  LEFT JOIN carts ON cart_items.cart_id=carts.cart_id LEFT JOIN transactions ON transactions.cart_id=carts.cart_id WHERE cart_items.quantity > 0 AND carts.user_id=%s AND transactions.status != 'success'", (user_id,))
            Cart_list = cur.fetchall()
            print(Cart_list)
            for row in Cart_list:
                current_price = row['price']
                current_quantity = row['quantity']
                subtotal = current_price * current_quantity
                total_quantity += current_quantity
                total_price += subtotal
                print(total_quantity)
                print(total_price)
            cursor.execute(
                "UPDATE carts SET total_price = %s, total_quantity = %s WHERE cart_id = %s", (total_price ,total_quantity ,cart_id))
            session['Shoppingcart'] = []
            for row in cur:
                item = {
                    'cart_item_id': row['cart_item_id'],
                    'cart_id': row['cart_id'],
                    'user_id': row['user_id'],
                    'product_id': row['product_id'],
                    'image': row['image'],
                    'product_name': row['product_name'],
                    'quantity': row['quantity'],
                    'price': row['price'],
                    'total_price': row['total_price'],
                    'total_quantity': row['total_quantity']
                }
                session['Shoppingcart'].append(item)
            session.modified = True
            log.execute("INSERT INTO activity_log (action, date, user_id) VALUES ('Shopping Cart updated', %s, %s)",
                (DateTime, user_id))            
            conn.commit()
            flash("Item in cart has successfully updated.", "danger")
            return redirect(request.referrer)
        except Exception as e:
            print(e)
            flash(
                "An error occurred while updating item in cart. Please try again later.", "danger")
            return redirect(request.referrer)
        finally:
            conn.close()


@app.route('/login')
def login():
    return render_template("login.html")

    # login


@app.route('/register', methods=['GET', 'POST'])
def register():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    prov = conn.cursor(pymysql.cursors.DictCursor)
    prov.execute(
        "SELECT `id`,`code`,`name_th` FROM `provinces`")
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        first_name = request.form['first_name']
        last_name = request.form['first_name']
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        gender = request.form['gender']
        email = request.form['email']
        blood_type = request.form['blood_type']
        age = request.form['age']
        ethnicity = request.form['ethnicity']
        weight = request.form['weight']
        height = request.form['height']
        congenital_disease = request.form['congenital_disease']
        drug_allergy = request.form['drug_allergy']
        phone_no = request.form['phone_no']
        provinces = request.form['province']
        districts = request.form['amphure']
        sub_districts = request.form['district']
        post_code = request.form['post_code']
        address = request.form['address']

  # Check if account exists using MySQL
        cursor.execute(
            'SELECT * FROM users WHERE username = %s', (username))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            flash('Account already exists!')
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash('Invalid email address!')
        elif not re.match(r'[A-Za-z0-9]+', username):
            flash('Username must contain only characters and numbers!')
        elif password != confirm_password:
            flash('Password is not matcing!')
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, 'user')",
                           (username, generate_password_hash(password)))
            user_id = cursor.lastrowid
            print("Hi!")
            cursor.execute("INSERT INTO users_detail (first_name, last_name, gender, email, blood_type, age, ethnicity, weight, height, congenital_disease, drug_allergy, phone_no, provinces, districts, sub_districts, address, post_code, user_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                           (first_name, last_name, gender, email, blood_type, age, ethnicity, weight, height, congenital_disease, drug_allergy, phone_no, provinces, districts, sub_districts, address, post_code, user_id))
            conn.commit()
            flash('You have successfully registered!')
            return redirect('/login')
    elif request.method == 'POST':
        # Form is empty... (no POST data)
       flash('Please fill out the form!')
    # Show registration form with message (if any)
    return render_template('register.html', prov=prov)


@app.route('/amphure/<get_amphure>')
def amphurebyprovince(get_amphure):
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute(
        "SELECT * FROM amphures WHERE province_id = %s", [get_amphure])
    amphure = cursor.fetchall()
    amphureArray = []
    for row in amphure:
        amphureObj = {
            'id': row['id'],
            'name': row['name_th']}
        amphureArray.append(amphureObj)
    return jsonify({'amphureprovince': amphureArray})


@app.route('/district/<get_district>')
def districtbyamphure(get_district):
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute(
        "SELECT * FROM districts WHERE amphure_id = %s", [get_district])
    district = cursor.fetchall()
    districtArray = []
    for row in district:
        districtObj = {
            'id': row['id'],
            'name': row['name_th']}
        districtArray.append(districtObj)
    return jsonify({'districtamphure': districtArray})


@app.route('/submit', methods=['POST'])
def login_submit():
    _username = request.form['UsernameInput']
    _password = request.form['PasswordInput']

    if 'username' in request.cookies:
        username = request.cookies.get('username')
        password = request.cookies.get('password')
        conn = mysql.connect()
        cursor = conn.cursor()
        log = conn.cursor(pymysql.cursors.DictCursor)
        DateTime = datetime.now()
        sql = "SELECT * FROM users WHERE username=%s"
        sql_where = (username,)

        cursor.execute(sql, sql_where)
        row = cursor.fetchone()
        if row and check_password_hash(row[2], password):
            print(username + ' ' + password)
            session['username'] = row[1]
            cursor.close()
            if row[3] == 'admin':
                user_id = row[0]
                session['user_id'] = row[0]
                session['admin'] = True
                session['logged_in'] = True
                log.execute("INSERT INTO activity_log (action, date, user_id) VALUES ('User has logged in', %s, %s)",
                (DateTime, user_id))            
                conn.commit()
                return redirect('/homepage')
            elif row[3] == 'user':
                user_id = row[0]
                session['user_id'] = row[0]
                session['logged_in'] = True
                log.execute("INSERT INTO activity_log (action, date, user_id) VALUES ('User has logged in', %s, %s)",
                (DateTime, user_id))            
                conn.commit()
                return redirect('/homepage')
            else:
                return redirect('/')
        else:
            return redirect('/login')
    # Check if exist
    elif _username and _password:
        conn = mysql.connect()
        cursor = conn.cursor()
        log = conn.cursor(pymysql.cursors.DictCursor)
        DateTime = datetime.now()
        sql = "SELECT * FROM users WHERE username=%s"
        sql_where = (_username,)
        cursor.execute(sql, sql_where)
        row = cursor.fetchone()
        if row:
            if check_password_hash(row[2], _password):
                session['username'] = row[1]
                cursor.close()
                if row[3] == 'admin':
                    user_id = row[0]
                    session['user_id'] = row[0]
                    session['admin'] = True
                    session['logged_in'] = True
                    log.execute("INSERT INTO activity_log (action, date, user_id) VALUES ('User has logged in', %s, %s)",
                        (DateTime, user_id))            
                    conn.commit()
                    return redirect('/homepage')
                elif row[3] == 'user':
                    user_id = row[0]
                    session['user_id'] = row[0]
                    session['logged_in'] = True
                    log.execute("INSERT INTO activity_log (action, date, user_id) VALUES ('User has logged in', %s, %s)",
                        (DateTime, user_id))            
                    conn.commit()
                    return redirect('/homepage')
                else:
                    return redirect('/')
            else:
                flash('Invalid Password!')
                return redirect('/login')
        else:
            flash('Invalid Email Or Password!')
            return redirect('/login')
    else:
        flash('Invalid Email Or Password!')
        return redirect('/login')


@app.route('/logout')
def logout():
    if 'logged_in' in session:
        conn = mysql.connect()
        log = conn.cursor(pymysql.cursors.DictCursor)
        DateTime = datetime.now()
        user_id = session['user_id']
        log.execute("INSERT INTO activity_log (action, date, user_id) VALUES ('User has logged out', %s, %s)",
                        (DateTime, user_id))            
        conn.commit()
        session.clear()
    return redirect('/')


@app.route('/products_manage')
def products():
    if 'admin' not in session:
        # abort(403)
        return render_template("test.html")
    conn = mysql.connect()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    cur.execute(
        "SELECT * FROM `products` LEFT JOIN `categories` ON products.category_id = categories.category_id")
    cur1 = conn.cursor(pymysql.cursors.DictCursor)
    cur1.execute("SELECT * FROM `categories`")
    data = cur.fetchall()
    cate = cur1.fetchall()
    user_id = session.get('user_id')
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    curr = conn.cursor(pymysql.cursors.DictCursor)
    curr1 = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM products")
    curr.execute(
        "SELECT * FROM users_detail WHERE user_id=%s", (user_id,))
    curr1.execute(
        "SELECT transactions.transaction_id,cart_items.cart_item_id, cart_items.cart_id, carts.user_id, products.product_id, products.image, products.product_name, cart_items.quantity, products.price, carts.total_price, carts.total_quantity FROM products LEFT JOIN cart_items ON products.product_id=cart_items.product_id  LEFT JOIN carts ON cart_items.cart_id=carts.cart_id LEFT JOIN transactions ON transactions.cart_id=carts.cart_id WHERE cart_items.quantity > 0 AND carts.user_id=%s AND transactions.status != 'success'", (user_id,))
    rows = cursor.fetchall()
    user = curr.fetchone()
    Cart_list = curr1.fetchall()
    if len(Cart_list) > 0:
        session['Shoppingcart'] = Cart_list
        session['cart_id'] = session.get('Shoppingcart')[0].get('cart_id')
    cur.close()
    cur1.close()
    return render_template('products_manage.html', products=data, categories=cate, time=time, user=user, Cart_list=Cart_list, user_id=user_id, product_list=rows)


@app.route('/product_add', methods=['POST'])
def product_add():
    if request.method == 'POST':
        flash("Data Inserted Successfully")
        product_name = request.form['product_name']
        price_value = request.form['price']
        price_value = price_value.replace(',', '')
        price = float(price_value)
        stock = request.form['stock']
        image = request.files['image']
        row = request.form['row']
        category = request.form['category']
        description = request.form['description']
        conn = mysql.connect()
        cur = conn.cursor(pymysql.cursors.DictCursor)
        log = conn.cursor(pymysql.cursors.DictCursor)
        DateTime = datetime.now()
        user_id = session['user_id']
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        cur.execute("INSERT INTO products (product_name, price, stock, row, category_id, image, description) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (product_name, price, stock, row, category, filename, description))
        log.execute("INSERT INTO activity_log (action, date, user_id) VALUES ('Product added', %s, %s)",
                        (DateTime, user_id))   
        conn.commit()
        print(image)
        return redirect(url_for('products'))


@app.route('/product_edit', methods=['POST', 'GET'])
def update():
    if request.method == 'POST':
        product_id = request.form['product_id']
        product_name = request.form['product_name']
        price_value = request.form['price']
        price_value = price_value.replace(',', '')
        price = float(price_value)
        stock = request.form['stock']
        row = request.form['row']
        category = request.form['category']
        description = request.form['description']
        conn = mysql.connect()
        cur = conn.cursor(pymysql.cursors.DictCursor)
        log = conn.cursor(pymysql.cursors.DictCursor)
        DateTime = datetime.now()
        user_id = session['user_id']
        cur.execute("""
        UPDATE products SET product_name=%s, price=%s, stock=%s, row=%s, category_id=%s, description=%s
        WHERE product_id=%s
        """, (product_name, price, stock, row, category, description, product_id))
        log.execute("INSERT INTO activity_log (action, date, user_id) VALUES ('Product updated', %s, %s)",
                        (DateTime, user_id))   
        flash("Data Updated Successfully")
        conn.commit()
        return redirect(url_for('products'))


@app.route("/upload", methods=["POST", "GET"])
def upload():
    conn = mysql.connect()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    if request.method == 'POST':
        product_id = request.form['product_id_image']
        image = request.files['image']
        # print(files)
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            cur.execute("""
            UPDATE products SET image=%s
            WHERE product_id=%s
            """, (filename, product_id))
            conn.commit()
        print(filename)
        cur.close()
        flash('File(s) successfully uploaded')
    return '', 204


@app.route('/delete/<string:product_id>', methods=['POST', 'GET'])
def delete(product_id):
    flash("Record Has Been Deleted Successfully")
    conn = mysql.connect()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    log = conn.cursor(pymysql.cursors.DictCursor)
    DateTime = datetime.now()
    user_id = session['user_id']
    cur.execute("DELETE FROM products WHERE product_id=%s", (product_id))
    log.execute("INSERT INTO activity_log (action, date, user_id) VALUES ('Product deleted', %s, %s)",
        (DateTime, user_id)) 
    conn.commit()
    return redirect(url_for('products'))


@app.route('/user_profile')
def user_profile():
    user_id = session.get('user_id')
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    curr = conn.cursor(pymysql.cursors.DictCursor)
    cur = conn.cursor(pymysql.cursors.DictCursor)
    prov = conn.cursor(pymysql.cursors.DictCursor)
    dist = conn.cursor(pymysql.cursors.DictCursor)
    sub_dist = conn.cursor(pymysql.cursors.DictCursor)
    history = conn.cursor(pymysql.cursors.DictCursor)
    prov.execute(
        "SELECT `id`,`code`,`name_th` FROM `provinces`")
   
    cursor.execute("SELECT * FROM products")
    curr.execute(
        "SELECT `users_detail_Id`,`user_image`,`first_name`,`last_name`,`gender`,`email`,`blood_type`,`age`,`ethnicity`,`weight`,`height`,`congenital_disease`,`drug_allergy`,`phone_no`,`provinces`,provinces.name_th as province_name,`districts`,amphures.name_th as district_name,`sub_districts`,districts.name_th as sub_district_name,`address`,`post_code`,`user_id` FROM users_detail LEFT JOIN provinces ON provinces.id = users_detail.provinces LEFT JOIN amphures ON amphures.id = users_detail.districts LEFT JOIN districts ON districts.id = users_detail.sub_districts WHERE user_id=%s;", (user_id,))
    cur.execute(
        "SELECT transactions.transaction_id,cart_items.cart_item_id, cart_items.cart_id, carts.user_id, products.product_id, products.image, products.product_name, cart_items.quantity, products.price, carts.total_price, carts.total_quantity FROM products LEFT JOIN cart_items ON products.product_id=cart_items.product_id  LEFT JOIN carts ON cart_items.cart_id=carts.cart_id LEFT JOIN transactions ON transactions.cart_id=carts.cart_id WHERE cart_items.quantity > 0 AND carts.user_id=%s AND transactions.status != 'success'", (user_id,))
    history.execute(
        "SELECT transactions.transaction_id,cart_items.cart_item_id, cart_items.cart_id, carts.user_id, products.product_id, products.image, products.product_name, cart_items.quantity, products.price, carts.total_price, carts.total_quantity FROM products LEFT JOIN cart_items ON products.product_id=cart_items.product_id LEFT JOIN carts ON cart_items.cart_id=carts.cart_id LEFT JOIN transactions ON transactions.cart_id=carts.cart_id WHERE cart_items.quantity > 0 AND carts.user_id=%s AND transactions.status = 'success';", (user_id,))
    histo = history.fetchall()
    rows = cursor.fetchall()
    user = curr.fetchone()
    Cart_list = cur.fetchall()
    provi = prov.fetchall()
    selected_prov = int(user['provinces'])
    dist.execute(
        "SELECT `id`,`code`,`name_th` FROM `amphures` WHERE `province_id` = %s;", (selected_prov,))
    distri = dist.fetchall()
    selected_distri = int(user['districts'])
    sub_dist.execute(
        "SELECT `id`,`name_th` FROM `districts` WHERE `amphure_id` = %s;", (selected_distri,))
    sub_distri = sub_dist.fetchall()
    selected_sub_distri = int(user['sub_districts'])
    if len(Cart_list) > 0:
        session['Shoppingcart'] = Cart_list
        session['cart_id'] = session.get('Shoppingcart')[0].get('cart_id')
    page = int(request.args.get('page', 1))
    per_page = 5
    offset = (page - 1) * per_page
    
    # Paginated data
    paginated_data = histo[offset:offset+per_page]
    
    # Total number of pages
    total_pages = math.ceil(len(histo) / per_page)
    print(paginated_data)

    
    return render_template('user_profile.html', user=user,history=histo, data=paginated_data, total_pages=total_pages, current_page=page, Cart_list=Cart_list, user_id=user_id, products=rows, provi=provi,distri=distri,sub_dist=sub_distri,selected_distri=selected_distri,selected_sub_dist=selected_sub_distri,selected_prov=selected_prov)


@app.route('/user_general_edit', methods=['POST', 'GET'])
def user_general_edit():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        gender = request.form['gender']
        blood_type = request.form['blood_type']
        age = request.form['age']
        weight = request.form['weight']
        height = request.form['height']
        ethnicity = request.form['ethnicity']
        congenital_disease = request.form['congenital_disease']
        drug_allergy = request.form['drug_allergy']
        conn = mysql.connect()
        cur = conn.cursor(pymysql.cursors.DictCursor)
        log = conn.cursor(pymysql.cursors.DictCursor)
        DateTime = datetime.now()
        user_id = session['user_id']
        cur.execute("""
        UPDATE users_detail SET first_name=%s, last_name=%s, gender=%s, blood_type=%s, age=%s, weight=%s, height=%s, ethnicity=%s, congenital_disease=%s, drug_allergy =%s
        WHERE user_id=%s
        """, (first_name, last_name, gender, blood_type, age, weight, height, ethnicity, congenital_disease, drug_allergy,user_id ))
        log.execute("INSERT INTO activity_log (action, date, user_id) VALUES ('User has updated a profile', %s, %s)",
                        (DateTime, user_id))   
        flash("Profile updated")
        conn.commit()
        return redirect(request.referrer)


@app.route('/user_contact_edit', methods=['POST', 'GET'])
def user_contact_edit():
    if request.method == 'POST':
        phone_no = request.form['phone_no']
        provinces = request.form['province']
        districts = request.form['district']
        sub_districts = request.form['sub_district']
        post_code = request.form['post_code']
        address = request.form['address']
        conn = mysql.connect()
        cur = conn.cursor(pymysql.cursors.DictCursor)
        log = conn.cursor(pymysql.cursors.DictCursor)
        DateTime = datetime.now()
        user_id = session['user_id']
        cur.execute("""
        UPDATE users_detail SET phone_no=%s, provinces=%s, districts=%s, sub_districts=%s, post_code=%s, address=%s
        WHERE user_id=%s
        """, (phone_no, provinces, districts, sub_districts, post_code,address,user_id ))
        log.execute("INSERT INTO activity_log (action, date, user_id) VALUES ('User has updated a profile', %s, %s)",
                        (DateTime, user_id))   
        flash("Profile updated")
        conn.commit()
        return redirect(request.referrer)


@app.route("/profile_pic", methods=["POST", "GET"])
def profile_pic():
    conn = mysql.connect()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    log = conn.cursor(pymysql.cursors.DictCursor)
    DateTime = datetime.now()
    if request.method == 'POST':
        user_id = session['user_id']
        image = request.files['image']
        # print(files)
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['USER_PROFILE'], filename))
            cur.execute("""
            UPDATE users_detail SET user_image=%s
            WHERE user_id=%s
            """, (filename, user_id))
            log.execute("INSERT INTO activity_log (action, date, user_id) VALUES ('User has updated a profile', %s, %s)",
                        (DateTime, user_id))
            conn.commit()
        cur.close()
        flash('Profile picture updated!')
    return redirect(request.referrer)


@app.route('/admin')
def admin():
    if 'admin' not in session:
        # abort(403)
        return render_template("test.html")
    user_id = session.get('user_id')
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    curr = conn.cursor(pymysql.cursors.DictCursor)
    cur = conn.cursor(pymysql.cursors.DictCursor)
    graph = conn.cursor(pymysql.cursors.DictCursor)
    cone = conn.cursor(pymysql.cursors.DictCursor)
    

    graph.execute("SELECT product_name, stock FROM products")
    cursor.execute("SELECT * FROM products")
    curr.execute(
        "SELECT * FROM users_detail WHERE user_id=%s", (user_id,))
    cur.execute(
        "SELECT transactions.transaction_id,cart_items.cart_item_id, cart_items.cart_id, carts.user_id, products.product_id, products.image, products.product_name, cart_items.quantity, products.price, carts.total_price, carts.total_quantity FROM products LEFT JOIN cart_items ON products.product_id=cart_items.product_id  LEFT JOIN carts ON cart_items.cart_id=carts.cart_id LEFT JOIN transactions ON transactions.cart_id=carts.cart_id WHERE cart_items.quantity > 0 AND carts.user_id=%s AND transactions.status != 'success'", (user_id,))
    cone.execute("SELECT SUM(carts.total_price) as sum FROM carts LEFT JOIN transactions ON carts.cart_id = transactions.cart_id WHERE status='success'")
    result = cone.fetchone()
    combined_total_price = result['sum']
    rows = cursor.fetchall()    
    graphs = graph.fetchall()
    user = curr.fetchone()
    Cart_list = cur.fetchall()
    
    if len(Cart_list) > 0:
        session['Shoppingcart'] = Cart_list
        session['cart_id'] = session.get('Shoppingcart')[0].get('cart_id')
    

    t = threading.Thread(target=create_plot)
    t.start()
    t.join()

   

    # Close the cursor and database connection
    cone.close()
    curr.close()
    cur.close()
    cursor.close()
    conn.close()

    print("combined_total_price", combined_total_price)
    return render_template('admin.html', user=user, Cart_list=Cart_list, user_id=user_id, product=rows, products=graphs, combined_total_price=combined_total_price,)

    # ... existing code ...
def create_plot():
    conn = mysql.connect()
    new_cursor = conn.cursor(pymysql.cursors.DictCursor)
    new_cursor.execute("""
    SELECT
        p.product_name,
        SUM(ci.quantity) AS total_quantity
    FROM
        transactions AS t
        INNER JOIN carts AS c ON t.cart_id = c.cart_id
        INNER JOIN cart_items AS ci ON c.cart_id = ci.cart_id
        INNER JOIN products AS p ON ci.product_id = p.product_id
    WHERE
        t.status = 'pending'
    GROUP BY
        p.product_name
    ORDER BY
        total_quantity DESC
    LIMIT 3
    """)
    # extract data from query result
    data = new_cursor.fetchall()
    product_names = [row['product_name'] for row in data]
    sales_totals = [row['total_quantity'] for row in data]
    # create pie chart
    plt.pie(sales_totals, labels=product_names, shadow=True)
    plt.title('Top 3 Products by Total Quantity')
    chart_path = 'static/chart.png'
    plt.savefig(chart_path)


if __name__ == "__main__":
    # scheduler.add_job(id = 'Checking Stock', func=stockChecking, trigger="interval", minutes=5)
    # scheduler.start()

    app.run(debug=True)
