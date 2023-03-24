from flask import Flask, request
from application.models import Shop, History

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello, World!"

@app.route("/get")
def get():
    return Shop.select()

@app.route('/keyword')
def newKeyword():
    args = request.args
    shop = args.get('shop')
    id = args.get('id')
    name = args.get('name')
    price = args.get('price')
    print(shop, id, name, price)
    History.insert((shop, id, name, price, ''))
    return 'done'

# @app.route('/set')
# def set():
#     try:
#         History.insert(('shop1', 'id1', 'name1', 'price1', 'target1'))
#         return 'done'
#     except Exception as e:
#         print(e)
#         return 'fail'

# @app.route('/get')
# def get():
#     try:
#         History.select('id1', 'name1')
#         return 'done'
#     except Exception as e:
#         print(e)
#         return 'fail'