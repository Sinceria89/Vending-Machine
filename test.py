from router import *
from flask_apscheduler import APScheduler
from flask_mail import Mail,  Message

scheduler = APScheduler()
mail = Mail(app)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'Medvend.2023@gmail.com'
app.config['MAIL_PASSWORD'] = 'hjusaohtsifugtff'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
mail = Mail(app)


@app.route('/test', methods=['GET', 'POST'])
def test():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute(
        "SELECT product_id,product_name,stock,row FROM products WHERE stock < 5")
    rows = cursor.fetchall()
    depleted = str(rows)
    for row in rows:
        if row['stock'] < 5:
            if request.method == "POST":
                msg = Message(
                    'Products Nearly depleted!',
                    sender='Medvend.2023@gmail.com',
                    recipients=['6231501089@lamduan.mfu.ac.th']
                )
                msg.body = "Products in medicine vending machine is about to be depleted " + depleted
                mail.send(msg)
                return 'Sent'
    return render_template('test1.html',)