from flask import Flask, request, render_template, abort, flash, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import timedelta, datetime
import logging
from flaskext.mysql import MySQL
import pymysql
import urllib.request
import os
import json


pymysql.install_as_MySQLdb()

# config
app = Flask(__name__)
app.secret_key = "MedVend-2023"

mysql = MySQL()

app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'vending'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)


UPLOAD_FOLDER = 'static/upload'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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
        return "Error: {}".format(str(e))
    finally:
        if 'cursor' in locals() and cursor is not None:
            cursor.close()
        if 'conn' in locals() and conn is not None:
            conn.close()


@app.route('/add', methods=['POST'])
def add_product_to_cart():
    cursor = None
    try:
        stock = int(request.form['stock'])
        product_id = request.form['product_id']
        # validate the received values
        if stock and product_id and request.method == 'POST':
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute("SELECT * FROM products WHERE product_id=%s", product_id)
            row = cursor.fetchone()

            itemArray = {row['product_id']: {'product_name': row['product_name'], 'quantity': stock, 'price': row['price'],
                                             'image': row['image'], 'total_price': stock * row['price'], 'total_quantity': stock + stock}}

            all_total_price = 0
            all_total_quantity = 0

            session.modified = True
            if 'cart_item' in session:
                if row['product_id'] in session['cart_item']:
                    for key, value in session['cart_item'].items():
                        if row['product_id'] == key:
                            old_quantity = session['cart_item'][key]['quantity']
                            total_quantity = old_quantity + stock
                            session['cart_item'][key]['quantity'] = total_quantity
                            session['cart_item'][key]['total_price'] = total_quantity * row['price']
                else:
                    session['cart_item'] = array_merge(
                        session['cart_item'], itemArray)

                for key, value in session['cart_item'].items():
                    individual_quantity = int(
                        session['cart_item'][key]['quantity'])
                    individual_price = float(
                        session['cart_item'][key]['total_price'])
                    all_total_quantity = all_total_quantity + individual_quantity
                    all_total_price = all_total_price + individual_price
            else:
                session['cart_item'] = itemArray
                all_total_quantity = all_total_quantity + stock
                all_total_price = all_total_price + stock * row['price']

            session['all_total_quantity'] = all_total_quantity
            session['all_total_price'] = all_total_price

            return redirect(url_for('/'))
        else:
            return 'Error while adding item to cart'
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    app.run(debug=True)


@app.route('/empty')
def empty_cart():
 try:
  session.clear()
  return redirect(url_for('/'))
 except Exception as e:
  print(e)
 
@app.route('/delete/<string:product_id>')
def delete_product(product_id):
 try:
  all_total_price = 0
  all_total_quantity = 0
  session.modified = True
   
  for item in session['cart_item'].items():
   if item[0] == product_id:    
    session['cart_item'].pop(item[0], None)
    if 'cart_item' in session:
     for key, value in session['cart_item'].items():
      individual_quantity = int(session['cart_item'][key]['stock'])
      individual_price = float(session['cart_item'][key]['total_price'])
      all_total_quantity = all_total_quantity + individual_quantity
      all_total_price = all_total_price + individual_price
    break
   
  if all_total_quantity == 0:
   session.clear()
  else:
   session['all_total_quantity'] = all_total_quantity
   session['all_total_price'] = all_total_price
   
  return redirect(url_for('.products'))
 except Exception as e:
  print(e)
   
def array_merge( first_array , second_array ):
 if isinstance( first_array , list ) and isinstance( second_array , list ):
  return first_array + second_array
 elif isinstance( first_array , dict ) and isinstance( second_array , dict ):
  return dict( list( first_array.items() ) + list( second_array.items() ) )
 elif isinstance( first_array , set ) and isinstance( second_array , set ):
  return first_array.union( second_array )
 return False
  




@app.route('/test')
def test():
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM products")
        rows = cursor.fetchall()
        return render_template('test1.html', products=rows)
    except Exception as e:
        print(e)
        return "Error: {}".format(str(e))
    finally:
        if 'cursor' in locals() and cursor is not None:
            cursor.close()
        if 'conn' in locals() and conn is not None:
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
    # Check if exist
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
    app.logger.info(cate)
    return render_template('products_manage.html', products=data, categories=cate)


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
        image = request.files['image']
        row = request.form['row']
        category = request.form['category']
        description = request.form['description']
        conn = mysql.connect()
        cur = conn.cursor(pymysql.cursors.DictCursor)
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        cur.execute("""
        UPDATE products SET product_name=%s, price=%s, stock=%s, row=%s, category_id=%s, image=%s, description=%s
        WHERE product_id=%s
        """, (product_name, price, stock, row, category, filename, description, product_id))
        flash("Data Updated Successfully")
        conn.commit()
        return redirect(url_for('products'))


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
    if 'logged_in' not in session:
        # abort(403)
        return render_template("test.html")
    return render_template("admin.html")


if __name__ == "__main__":
    app.run(debug=True)
