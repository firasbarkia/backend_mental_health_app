from flask import Flask, request, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
import uuid
import requests

# Flask app setup
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mental_health.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database models
class User(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    responses = db.Column(db.JSON)

class Consultant(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(100))
    expertise = db.Column(db.String(200))

# Initialize the database and create sample consultants on app start
def create_sample_consultants():
    with app.app_context():
        if Consultant.query.count() == 0:
            sample_consultants = [
                Consultant(id=str(uuid.uuid4()), name="Alice", expertise="Bullying"),
                Consultant(id=str(uuid.uuid4()), name="Bob", expertise="Violence"),
                Consultant(id=str(uuid.uuid4()), name="Charlie", expertise="Harassment")
            ]
            db.session.bulk_save_objects(sample_consultants)
            db.session.commit()

# Initialize the database
with app.app_context():
    db.create_all()
    create_sample_consultants()

# Route to render the UI
@app.route('/')
def index():
    return render_template('index.html')

# Endpoint for saving health check responses
@app.route('/api/questionnaire', methods=['POST'])
def fill_questionnaire():
    data = request.json
    user_id = str(uuid.uuid4())
    responses = data.get('responses', {})

    user = User(id=user_id, responses=responses)
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "Responses recorded", "user_id": user_id}), 201

# Endpoint for getting consultants
@app.route('/api/consultants', methods=['GET'])
def get_consultants():
    consultants = Consultant.query.all()
    return jsonify([{"id": c.id, "name": c.name, "expertise": c.expertise} for c in consultants]), 200

# Endpoint for chat with consultant (AI and human)
@app.route('/api/chat', methods=['POST'])
def chat_with_consultant():
    data = request.json
    message = data.get('message')
    consultant_id = data.get('consultant_id')

    # Chat logic with a dummy response for now
    response_message = f"Consultant {consultant_id} received your message: {message}"
    
    return jsonify({"response": response_message}), 200

if __name__ == '__main__':
    app.run(debug=True)

