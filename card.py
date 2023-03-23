
import psycopg2
import requests
from flask import Flask, appcontext_popped, jsonify, request, render_template, abort, flash, session, request, redirect, url_for
# Initialize database connection
conn = psycopg2.connect(
    host="localhost",
    database="mydatabase",
    user="myusername",
    password="mypassword"
)

@appcontext_popped.route('/collect_info', methods=['POST'])
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
