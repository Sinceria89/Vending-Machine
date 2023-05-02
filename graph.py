# Import the necessary libraries and modules for your backend framework
from flask import Flask, render_template
from router import *
import numpy as np
import matplotlib.pyplot as plt



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
    print(product_name)
    print(stock)
    # Define custom colors for the bars
    colors = ['blue', 'green', 'orange', 'red']

    # Create a bar chart using matplotlib with custom colors
    fig, ax = plt.subplots()
    x = np.arange(len(product_name))
    width = 0.4

    # Plot each bar with a different color
    for i in range(len(product_name)):
        ax.bar(x[i], stock[i], width, color=colors[i])

    ax.set_xticks(x)
    ax.set_xticklabels(product_name, rotation=45)
    ax.set_xlabel('Product Name')
    ax.set_ylabel('Stock')
    ax.set_title('Product Stock Quantity')
    plt.tight_layout()

    # Save the chart to a file
    chart_path = 'static/barchart.png'
    plt.savefig(chart_path)

    # Render the HTML template and pass the product information to it
    return render_template('admin.html', products=rows)


