from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shoeland.db'
db = SQLAlchemy(app)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    contact = db.Column(db.String(10))
    address = db.Column(db.String(200))
    order = db.Column(db.Integer)
    quantity = db.Column(db.Integer)
    amount_due = db.Column(db.Integer)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    delivery_date = db.Column(db.String(10))
    category = db.Column(db.Integer)

    def __repr__(self):
        return '<Order %r>' % self.id

class Products(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item = db.Column(db.String(50))
    price = db.Column(db.Integer)   

    def __repr__(self):
        return self.item



@app.route('/',methods=['GET','POST'])
def index():
    if request.method == 'POST':
        curr_order_json = request.get_json()
        name = curr_order_json['name']
        contact = curr_order_json['contact']
        address = curr_order_json['address']
        orderid = curr_order_json['order']
        quantity = curr_order_json['quantity']
        delivery_date = curr_order_json['delivery_date']

        orderitem = str(Products.query.get(orderid))
        
        curr_order = Order(name=name,contact=contact,address=address,order=orderitem,quantity=quantity,delivery_date=delivery_date,amount_due=0,category=1)

        try:
            db.session.add(curr_order)
            db.session.commit()
        except:
            print(curr_order)
            print('Check your order and try again.')    
            
        return('ok')
            
    elif request.args.get('view') == 'fulfilled':
        orders  = Order.query.filter_by(category=2).all()
        return render_template('index.html',orders=orders)
    elif request.args.get('view') == 'pending':
        orders  = Order.query.filter_by(category=1).all()
        return render_template('index.html',orders=orders)
    elif request.args.get('view') == 'cancelled':
        orders  = Order.query.filter_by(category=3).all()
        return render_template('index.html',orders=orders)
    else:
        return redirect('/?view=pending')

@app.route('/accept/<int:id>',methods=['GET'])
def accept(id):
    order_a = Order.query.get_or_404(id)
    order_a.category = 2
    try:
        db.session.commit()
        return redirect('/')
    except:
        return "Couldn't change status"     

@app.route('/cancel/<int:id>',methods=['GET'])
def cancel(id):
    order_a = Order.query.get_or_404(id)
    order_a.category = 3
    try:
        db.session.commit()
        return redirect('/')
    except:
        return "Couldn't change status"        

@app.route('/api',methods=['POST'])
def poll():
    price = Products.query.filter_by(id=request.get_json()['id']).first()
    try:
        return {'price':price.price}
    except:
        return 'I have no clue what you are trying to do'
if __name__ == "__main__":
    app.run(debug=True)    