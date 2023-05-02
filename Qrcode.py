import json
import base64
import qrcode
from router import *
import time
from flask import request
from flask import Flask, jsonify, request, render_template, abort, flash, session, request, redirect, url_for


@app.route('/transaction')
def transaction():
    user_id = session.get('user_id')
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    curr = conn.cursor(pymysql.cursors.DictCursor)
    cur = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM products")
    curr.execute(
        "SELECT * FROM users_detail WHERE user_id=%s", (user_id,))
    cur.execute(
        "SELECT transactions.transaction_id,cart_items.cart_item_id, cart_items.cart_id, carts.user_id, products.product_id, products.image, products.product_name, cart_items.quantity, products.price, carts.total_price, carts.total_quantity FROM products LEFT JOIN cart_items ON products.product_id=cart_items.product_id  LEFT JOIN carts ON cart_items.cart_id=carts.cart_id LEFT JOIN transactions ON transactions.cart_id=carts.cart_id WHERE cart_items.quantity > 0 AND carts.user_id=%s AND transactions.status != 'success'", (user_id,))
    rows = cursor.fetchall()
    user = curr.fetchone()
    Cart_list = cur.fetchall()
    if len(Cart_list) > 0:
        session['Shoppingcart'] = Cart_list
        session['cart_id'] = session.get('Shoppingcart')[0].get('cart_id')
    return render_template('Qrcode.html', user=user, Cart_list=Cart_list, user_id=user_id, products=rows)


