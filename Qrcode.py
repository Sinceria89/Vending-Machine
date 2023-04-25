import json
import base64
import qrcode
import time
from flask import request
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
        amount = float(request.form.get("grandtotal", 0))
    # Check if the request method is GET
    elif request.method == 'GET':
        # Get the amount from the query parameters
        amount = float(request.args.get('grandtotal', 0))
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
    amount = float(request.args.get('grandtotal', 0))
    qr_image = request.args.get('qr_image', '')

    # Render the Qrcode.html template with the amount and QR code image data
    return render_template('Qrcode.html', amount=amount, qr_image=qr_image)



@app.route("/thx")
def thx():
    return render_template('thanks.html')

# If this script is being run as the main program, start the Flask application
if __name__ == '__main__':       
    app.run(port=3000, debug=True)

#code for electric lock waiting for more information
''' 
from flask import Flask, request, jsonify
S
app = Flask(__name__)

@app.route('/collect_info', methods=['POST'])
def collect_info():
    data = request.get_json()
    name = data['name']
    address = data['address']
    date_of_birth = data['date_of_birth']
    id_number = data['id_number']
    # Additional data fields can be added here as needed
    
    # Validate the data (e.g. ensure that the ID number is valid)
    
    # Store the data in a database
    
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run()




with sql
import psycopg2

# Initialize database connection
conn = psycopg2.connect(
    host="localhost",
    database="mydatabase",
    user="myusername",
    password="mypassword"
)

@app.route('/collect_info', methods=['POST'])
def collect_info():
    data = request.get_json()
    name = data['name']
    address = data['address']
    date_of_birth = data['date_of_birth']
    id_number = data['id_number']
    # Additional data fields can be added here as needed
    
    # Validate the data (e.g. ensure that the ID number is valid)
    
    # Store the data in the database
    cur = conn.cursor()
    cur.execute("INSERT INTO mytable (name, address, date_of_birth, id_number) VALUES (%s, %s, %s, %s)", (name, address, date_of_birth, id_number))
    conn.commit()
    
    return jsonify({'success': True})

'''