from router import * 


@app.route('/test11')
def test11():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT product_name,stock FROM products")
    rows = cursor.fetchall()
    conn.close()
    cursor.close()
    return render_template('test1.html',products=rows)
