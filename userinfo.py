import mysql.connector
from flask import request
from flask import Flask, jsonify, request, render_template, abort, flash, session, request, redirect, url_for


app = Flask(__name__)

@app.route('/user information')
def user_information():
 conn = mysql.connector.connect(host="localhost",port="3306",user="root",password="1234",database="vending")
 cursor=conn.cursor()
 selectquery="select * from users_detail"
 cursor.execute(selectquery)
 records=cursor.fetchall()
 print (" No. of Users",cursor.rowcount)
 
 for row in records:
     print("users_detail_ID")
     print("first_name")
     print("last_name")
     print("gender")
     print("email")
     print("blood_type")
     print("age")
     print("ethnicity")
     print("weight")
     print("height")
     print("congenital_disease")
     print("drug_allergy")
     print("phone_no")
     print("provinces")
     print("districts")
     print("sub_districts")
     print("address")
     print("post_code")
     print("user_id")
     print()
     
     cursor.close()
     conn.close()
     
     if __name__ == '__main__':       
        app.run(port=3000, debug=True)
