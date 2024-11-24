from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import uuid
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mental_health.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Hume AI API configuration
HUME_API_URL = "https://api.hume.ai/sentiment"
HUME_API_KEY = "fUb6EQCri40V5bAvmYQIXnxl1RBw3K3wJ6gTAhZGO5m6JAGA"  # Replace with your actual API key

# Database model for users
class User(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    responses = db.Column(db.JSON)

# Database model for consultants
class Consultant(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(100))
    expertise = db.Column(db.String(200))

# Create the database tables
db.create_all()

# Endpoint for health check
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

# Endpoint for filling out the mental health questionnaire
@app.route('/api/questionnaire', methods=['POST'])
def fill_questionnaire():
    data = request.json
    user_id = str(uuid.uuid4())  # Generate a unique ID
    responses = data.get('responses', {})

    # Save the user's responses to the database
    user = User(id=user_id, responses=responses)
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "Responses recorded", "user_id": user_id}), 201

# Endpoint for getting consultants
@app.route('/api/consultants', methods=['GET'])
def get_consultants():
    consultants = Consultant.query.all()
    return jsonify([{"id": c.id, "name": c.name, "expertise": c.expertise} for c in consultants]), 200

# Endpoint for chat with sentiment analysis
@app.route('/api/chat', methods=['POST'])
def chat_with_consultant():
    data = request.json
    message = data.get('message')
    consultant_id = data.get('consultant_id')

    # Prepare headers for Hume AI API request
    headers = {
        'Authorization': f'Bearer {HUME_API_KEY}',
        'Content-Type': 'application/json'
    }

    # Prepare the payload for Hume AI API
    payload = {
        "text": message
    }

    try:
        # Call the Hume AI API for sentiment analysis
        sentiment_response = requests.post(HUME_API_URL, headers=headers, json=payload)
        sentiment_response.raise_for_status()  # Raise an error for bad responses

        sentiment = sentiment_response.json()  # Parse the JSON response

        # Simulate a response from the consultant
        response_message = f"Consultant {consultant_id} has received your message."
        
        return jsonify({"response": response_message, "sentiment": sentiment}), 200

    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Error communicating with Hume AI", "details": str(e)}), 500

# Sample data for consultants (you can populate this in a more dynamic way)
@app.before_first_request
def create_sample_consultants():
    if Consultant.query.count() == 0:  # Only add sample data if the table is empty
        sample_consultants = [
            Consultant(id=str(uuid.uuid4()), name="Alice", expertise="Bullying"),
            Consultant(id=str(uuid.uuid4()), name="Bob", expertise="Violence"),
            Consultant(id=str(uuid.uuid4()), name="Charlie", expertise="Harassment")
        ]
        db.session.bulk_save_objects(sample_consultants)
        db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)