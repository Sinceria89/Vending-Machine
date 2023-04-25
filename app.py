from __future__ import print_function  # In python 2.7
from router import *
from test import *
import sys
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import timedelta, datetime
import logging
import urllib.request
import os
import re


class Config:
    SCHEDULER_API_ENABLED = True


UPLOAD_FOLDER = 'static/upload'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
time = datetime.now()


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def stockChecking():
    print("This test runs every 5 minutes")


@app.route('/')
def index():
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
            cursor.execute("SELECT * FROM products")
            curr.execute(
                "SELECT * FROM users_detail WHERE user_id=%s", (user_id,))
            rows = cursor.fetchall()
            user = curr.fetchone()
            TotalQuantity = 0
            TotalPrice = 0
            app.logger.info(user)
            if 'Shoppingcart' in session:
                for key, product in session['Shoppingcart'].items():
                    subtotal = 0
                    subquantity = 0
                    subquantity = int(product['quantity'])
                    TotalQuantity += subquantity
                    subtotal += float(product['price']) * \
                        int(product['quantity'])
                    TotalPrice = float(TotalPrice + subtotal)
            return render_template('homepage.html', user=user, user_id=user_id, products=rows, grandtotal=TotalPrice, TotalQuantity=TotalQuantity)
        except Exception as e:
            print(e)
            return render_template('index.html')
        finally:
            if 'cursor' in locals() and cursor is not None:
                cursor.close()
            if 'conn' in locals() and conn is not None:
                conn.close()


@app.route('/add', methods=['POST'])
def AddCart():
    DictItems = {}
    try:
        product_id = int(request.form.get('product_id'))
        quantity = int(request.form.get('quantity'))

        if request.method == "POST":
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute(
                "SELECT * FROM products WHERE product_id=%s", product_id)
            row = cursor.fetchone()
            DictItems = {str(row['product_id']): {'product_name': row['product_name'], 'price': float(row['price']),
                                                  'stock': row['stock'], 'quantity': quantity, 'image': row['image']}}
            if 'Shoppingcart' in session:
                print(session['Shoppingcart'])
                if product_id in session['Shoppingcart']:
                    for key, item in session['Shoppingcart'].items():
                        if int(key) == int(product_id):
                            session.modified = True
                            item['quantity'] += quantity
                else:
                    session['Shoppingcart'] = MagerDicts(
                        session['Shoppingcart'], DictItems)
                    return redirect(request.referrer)
            else:
                session['Shoppingcart'] = DictItems
                return redirect(request.referrer)

    except Exception as e:
        print(e)
        return redirect(request.referrer)
    finally:
        print(DictItems)
        return redirect(request.referrer)


def MagerDicts(dict1, dict2):
    if isinstance(dict1, list) and isinstance(dict2, list):
        return dict1 + dict2
    if isinstance(dict1, dict) and isinstance(dict2, dict):
        return dict(list(dict1.items()) + list(dict2.items()))


@app.route('/updatecart/<int:code>', methods=['POST'])
def updatecart(code):
    if 'Shoppingcart' not in session or len(session['Shoppingcart']) <= 0:
        return redirect(url_for('homepage'))
    if request.method == "POST":
        cart_quantity = request.form.get('cart_quantity')
        try:
            session.modified = True
            for key, item in session['Shoppingcart'].items():
                if int(key) == code:
                    item['quantity'] = cart_quantity
                    flash('Item is updated!')
                    return redirect(url_for('homepage'))
        except Exception as e:
            print(e)
            return redirect(url_for('homepage'))


@app.route('/deleteitem/<int:product_id>')
def deleteitem(product_id):
    if 'Shoppingcart' not in session or len(session['Shoppingcart']) <= 0:
        return redirect(url_for('homepage'))
    try:
        session.modified = True
        for key, item in session['Shoppingcart'].items():
            if int(key) == product_id:
                session['Shoppingcart'].pop(key, None)
                return redirect(url_for('homepage'))
    except Exception as e:
        print(e)
        return redirect(url_for('homepage'))


@app.route('/empty')
def empty_cart():
    try:
        for key, item in session['Shoppingcart'].items():
            session.pop('Shoppingcart', default=None)
            return redirect(url_for('homepage'))
    except Exception as e:
        print(e)


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
    msg = ''
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
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif password != confirm_password:
            msg = 'Password is not matcing!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, 'user')",
                           (username, generate_password_hash(password)))
            user_id = cursor.lastrowid
            cursor.execute("INSERT INTO users_detail (first_name, last_name, gender, email, blood_type, age, ethnicity, weight, height, congenital_disease, drug_allergy, phone_no, provinces, districts, sub_districts, address, post_code, user_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                           (first_name, last_name, gender, email, blood_type, age, ethnicity, weight, height, congenital_disease, drug_allergy, phone_no, provinces, districts, sub_districts, address, post_code, user_id))
            conn.commit()
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg, prov=prov)


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
        sql = "SELECT * FROM users WHERE username=%s"
        sql_where = (username,)

        cursor.execute(sql, sql_where)
        row = cursor.fetchone()
        if row and check_password_hash(row[2], password):
            print(username + ' ' + password)
            session['username'] = row[1]
            cursor.close()
            if row[3] == 'admin':
                session['user_id'] = row[0]
                session['admin'] = True
                session['logged_in'] = True
                return redirect('/admin')
            elif row[3] == 'user':
                session['user_id'] = row[0]
                session['logged_in'] = True
                return redirect('/homepage')
            else:
                return redirect('/')
        else:
            return redirect('/login')
    # Check if exist
    elif _username and _password:
        conn = mysql.connect()
        cursor = conn.cursor()
        sql = "SELECT * FROM users WHERE username=%s"
        sql_where = (_username,)
        cursor.execute(sql, sql_where)
        row = cursor.fetchone()
        if row:
            if check_password_hash(row[2], _password):
                session['username'] = row[1]
                cursor.close()
                if row[3] == 'admin':
                    session['user_id'] = row[0]
                    session['admin'] = True
                    session['logged_in'] = True
                    return redirect('/admin')
                elif row[3] == 'user':
                    session['user_id'] = row[0]
                    session['logged_in'] = True
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
        session.pop('user_id')
        session.pop('logged_in')
        if 'admin' in session:
            session.pop('admin')
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
    cur.close()
    cur1.close()
    # app.logger.info(data)
    # app.logger.info(cate)
    return render_template('products_manage.html', products=data, categories=cate, time=time)


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
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        cur.execute("INSERT INTO products (product_name, price, stock, row, category_id, image, description) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (product_name, price, stock, row, category, filename, description))
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
        cur.execute("""
        UPDATE products SET product_name=%s, price=%s, stock=%s, row=%s, category_id=%s, description=%s
        WHERE product_id=%s
        """, (product_name, price, stock, row, category, description, product_id))
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
    cur.execute("DELETE FROM products WHERE product_id=%s", (product_id))
    conn.commit()
    return redirect(url_for('products'))


@app.route('/admin')
def admin():
    if 'admin' not in session:
        # abort(403)
        return render_template("test.html")
    return render_template("admin.html")


if __name__ == "__main__":
    # scheduler.add_job(id = 'Checking Stock', func=stockChecking, trigger="interval", minutes=5)
    # scheduler.start()

    app.run(debug=True)
