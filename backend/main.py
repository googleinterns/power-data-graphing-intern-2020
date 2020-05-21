# Simple backend server using flask framework

from flask import Flask
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app)

@app.route("/")
def hello():
    return "Hello world, welcome to Google"

if __name__ == '__main__':
     app.run(port=5000)