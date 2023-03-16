import json
import base64
import qrcode
import time
import requests
from flask import Flask, jsonify, request, make_response,render_template
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
    

    
    
    # Render the index.html template with the amount value and the base64 encoded image data
    return render_template('Qrcode.html', amount=amount, qr_image=encoded_image)


# If this script is being run as the main program, start the Flask application
if __name__ == '__main__':
    app.run(port=3000, debug=True)
