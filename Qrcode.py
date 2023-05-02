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


'''
import json
import base64
import qrcode
import time
import requests
from flask import Flask, jsonify, request, render_template, abort, flash, session, request, redirect, url_for
from promptpay import qrcode as ppqrcode

# Line Notify API token
LINE_NOTIFY_API_TOKEN = 'CcfWKEtHHrNHDwM3W8xtQbhzwy1CWsCF1y8unqU23gP'

# Create a Flask application object
app = Flask(__name__)

# Load the data from the JSON file
with open('package.json', 'r') as f:
    data = json.load(f)

# Define a route for the endpoint that generates the QR code
@app.route("/")
# Define a route for the endpoint that generates the QR code
@app.route('/generateQR', methods=['POST', 'GET'])
def generateQR():
    # Check if the request method is POST
    if request.method == 'POST':
        # Get the amount from the form data
        amount = float(request.form.get("amount", 0))
    # Check if the request method is GET
    elif request.method == 'GET':
        # Get the amount from the query parameters
        amount = float(request.args.get('amount', 0))
    # If the request method is not supported, return a bad request error
    else:
        return jsonify({
            "RespCode": 400,
            "RespMessage": "Bad Request",
            "Result": "HTTP method not supported"
        }), 400

    # Set the mobile number for the payment
    mobileNumber = '0982959552'
    # Generate the QR code payload with the mobile number and amount
    payload = ppqrcode.generate_payload(mobileNumber, amount=amount)
    # Create the QR code image from the payload
    img = ppqrcode.to_image(payload)
    # Get the current timestamp as a string
    timestamp = str(int(time.time()))
    # Create a unique filename for the QR code image
    filename = f'qrcode_{timestamp}.png'
    # Save the QR code image to a file
    img.save(filename)
    # Open the QR code image file
    with open(filename, 'rb') as f:
        # Read the image data from the file
        image_data = f.read()
    # Encode the image data as a base64 string
    encoded_image = base64.b64encode(image_data).decode('utf-8')
    
    return redirect(url_for('showQR', amount=amount, qr_image=encoded_image))

@app.route('/showQR')
def showQR():
    # Get the amount and QR code image data from the URL parameters
    amount = float(request.args.get('amount', 0))
    qr_image = request.args.get('qr_image', '')

    # Render the Qrcode.html template with the amount and QR code image data
    return render_template('Qrcode.html', amount=amount, qr_image=qr_image)



@app.route("/thx")
def thx():
    return render_template('thanks.html')

# If this script is being run as the main program, start the Flask application
if __name__ == '__main__':
    app.run(port=3000, debug=True)


'''