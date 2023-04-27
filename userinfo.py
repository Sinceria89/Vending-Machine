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
     
@app.route('/update_user/<int:user_id>', methods=['POST'])
def update_user(user_id):
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']

    conn = mysql.connector.connect(host="localhost", port="3306", user="root", password="1234", database="vending")
    cursor = conn.cursor()
    updatequery = "UPDATE users_detail SET username=%s, email=%s, password=%s WHERE id=%s"
    cursor.execute(updatequery, (username, email, password, user_id))
    conn.commit()
    cursor.close()
    conn.close()

    flash('User information updated successfully', 'success')
    return redirect(url_for('user_information'))

if __name__ == '__main__':       
    app.run(port=3000, debug=True)