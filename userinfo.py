import mysql.connector
from flask import request
from flask import Flask, jsonify, request, render_template, abort, flash, session, request, redirect, url_for


app = Flask(__name__)

@app.route('/user_information')
def user_information():
  conn = mysql.connector.connect(host="localhost", port="3306", user="root", password="1234", database="vending")
  cursor = conn.cursor()
  selectquery = "select * from users_detail"
  cursor.execute(selectquery)
  users = cursor.fetchall()
  cursor.close()
  conn.close()
  return render_template('information.html', users=users)
     
if __name__ == '__main__':       
    app.run(port=3000, debug=True)
