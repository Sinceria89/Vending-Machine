from flask import Flask, request, render_template, abort, flash, session, request, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import logging
from flaskext.mysql import MySQL
import pymysql
import urllib.request
import os

pymysql.install_as_MySQLdb()

    # config
app = Flask(__name__)
app.secret_key = "MedVend-2023"
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'vending'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql = MySQL(app)

UPLOAD_FOLDER = 'static/upload'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


@app.route('/')
def index():
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM products")
        rows = cursor.fetchall()
        return render_template('index.html', products=rows)
    except Exception as e:
        print(e)
    finally:
        cursor.close() 
        conn.close()
        
        
@app.route('/login')
def login():
    return render_template("login.html")

    # login


@app.route('/submit', methods=['POST'])
def login_submit():
    _username = request.form['UsernameInput']
    _password = request.form['PasswordInput']

    if 'username' in request.cookies:
        username = request.cookies.get('username')
        password = request.cookies.get('password')
        conn = mysql.connect()
        cursor = conn.cursor()
        sql = "SELECT * FROM admin WHERE username=%s"
        sql_where = (username,)
        cursor.execute(sql, sql_where)
        row = cursor.fetchone()
        if row and check_password_hash(row[2], password):
            print(username + ' ' + password)
            session['username'] = row[1]
            cursor.close()
            session['logged_in'] = True
            return redirect('/admin')
        else:
            return redirect('/login')
    #Check if exist
    elif _username and _password:
        conn = mysql.connect()
        cursor = conn.cursor()
        sql = "SELECT * FROM admin WHERE username=%s"
        sql_where = (_username,)
        cursor.execute(sql, sql_where)
        row = cursor.fetchone()
        if row:
            if check_password_hash(row[2], _password):
                session['username'] = row[1]
                cursor.close()
                session['logged_in'] = True
                return redirect('/admin')
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
        session.pop('logged_in')
    return redirect('/')


@app.route('/products_manage')
def products():
    if 'logged_in' not in session:
        #abort(403)
        return render_template("test.html")
    conn = mysql.connect()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    cur.execute("SELECT * FROM `products` LEFT JOIN `categories` ON products.category_id = categories.category_id")
    cur1 = conn.cursor(pymysql.cursors.DictCursor)
    cur1.execute("SELECT * FROM `categories`")
    data = cur.fetchall()
    cate = cur1.fetchall()
    cur.close()
    cur1.close()
    #app.logger.info(data)
    app.logger.info(cate)
    return render_template('products_manage.html', products = data, categories = cate)
    

@app.route('/product_add', methods = ['POST'])
def product_add():
    if request.method == 'POST':
        flash("Data Inserted Successfully")
        product_name = request.form['product_name']
        price = request.form['price']
        quantity = request.form['quantity']
        image = request.files['image']
        row = request.form['row']
        category = request.form['category']
        description = request.form['description']
        conn = mysql.connect()
        cur = conn.cursor(pymysql.cursors.DictCursor)
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        cur.execute("INSERT INTO products (product_name, price, quantity, row, category_id, image, description) VALUES (%s, %s, %s, %s, %s, %s, %s)", (product_name, price, quantity, row, category, filename, description))
        conn.commit()
        print(image)
        return redirect(url_for('products'))
        

@app.route('/product_edit', methods= ['POST', 'GET'])
def update():
    if request.method == 'POST':
        product_id = request.form['product_id']
        product_name = request.form['product_name']
        price_value = request.form['price']
        price_value = price_value.replace(',', '')
        price = float(price_value)
        quantity = request.form['quantity']
        row = request.form['row']
        category = request.form['category']
        description = request.form['description']
        conn = mysql.connect()
        cur = conn.cursor(pymysql.cursors.DictCursor)
        cur.execute("""
        UPDATE products SET product_name=%s, price=%s, quantity=%s, row=%s, category_id=%s, image=%s, description=%s
        WHERE product_id=%s
        """, (product_name, price, quantity, row, category, filename, description, product_id))
        flash("Data Updated Successfully")
        conn.commit()
        return redirect(url_for('products'))


@app.route('/delete/<string:product_id>', methods = ['POST','GET'])
def delete(product_id):
    flash("Record Has Been Deleted Successfully")
    conn = mysql.connect()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    cur.execute("DELETE FROM products WHERE product_id=%s", (product_id))
    conn.commit()
    return redirect(url_for('products'))    


@app.route('/admin')
def admin():
    if 'logged_in' not in session:
        #abort(403)
        return render_template("test.html")
    return render_template("admin.html")


if __name__ == "__main__":
    app.run(debug=True)
