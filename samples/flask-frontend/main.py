from asgiref.wsgi import WsgiToAsgi
from flask import Flask

wsgi_app = Flask(__name__)
app = WsgiToAsgi(wsgi_app)

@app.route("/")
def hello():
    return "Hello World!"
