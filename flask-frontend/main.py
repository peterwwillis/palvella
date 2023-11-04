from asgiref.wsgi import WsgiToAsgi
from flask import Flask

app = Flask(__name__)
asgi_app = WsgiToAsgi(app)

@app.route("/")
def hello():
    return "Hello World!"
