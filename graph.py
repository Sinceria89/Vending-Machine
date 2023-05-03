# Import the necessary libraries and modules for your backend framework
from flask import Flask, render_template
from router import *
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import pandas as pd

# Define a route to render the HTML template and retrieve product information
@app.route('/graph')
def product_list():
    # Establish a connection to your SQL database
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    # Execute a query to fetch the product_name and stock_quantity from the products table
    cursor.execute("SELECT product_name, stock FROM products")

    # Fetch all the rows returned by the query
    rows = cursor.fetchall()
    # Close the database connection
    cursor.close()
    conn.close()

    product_name = [row[0] for row in rows]
    stock = [row[1] for row in rows]

    # Define custom colors for the bars
    colors = ['blue', 'green', 'orange', 'red']

    # Create a bar chart using matplotlib with custom colors
    fig1, ax1 = plt.subplots()  # Create a new figure for the bar chart
    x = np.arange(len(product_name))
    width = 0.4

    # Plot each bar with a different color
    for i in range(len(product_name)):
        ax1.bar(x[i], stock[i], width, color=colors[i])

    ax1.set_xticks(x)
    ax1.set_xticklabels(product_name, rotation=45)
    ax1.set_xlabel('Product Name')
    ax1.set_ylabel('Stock')
    ax1.set_title('Product Stock Quantity')
    plt.tight_layout()

    # Save the bar chart to a file
    chart_path = 'static/barchart.png'
    plt.savefig(chart_path)
    plt.close(fig1)  # Close the bar chart figure

    # Establish a connection to your SQL database
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    # Execute a query to get the top 3 best-selling items

   
    

    return render_template('admin.html', products=rows,)


