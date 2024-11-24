from flask import Flask
from models import db
from routes.auth import auth
from routes.forum import forum
from routes.chat import chat, socketio
from routes.hume import hume

app = Flask(__name__)
app.config.from_object('config.Config')

db.init_app(app)
app.register_blueprint(auth)
app.register_blueprint(forum)
app.register_blueprint(chat)
app.register_blueprint(hume)

if __name__ == '__main__':
    socketio.init_app(app)
    app.run(debug=True)
