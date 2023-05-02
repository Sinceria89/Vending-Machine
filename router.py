from flask import Flask, request, render_template, abort, flash, session, redirect, url_for, json, jsonify
from flaskext.mysql import MySQL
import pymysql

pymysql.install_as_MySQLdb()

app = Flask(__name__)
app.secret_key = "MedVend-2023"
mysql = MySQL()

# config
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'vending'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'

mysql.init_app(app)