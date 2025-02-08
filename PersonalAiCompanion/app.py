import os
import logging
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import declarative_base

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Initialize SQLAlchemy with a base class
Base = declarative_base()

db = SQLAlchemy(model_class=Base)

# Create the Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "a-very-secret-key")

# Configure database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize the database
db.init_app(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        from models import Conversation, Message

        message_content = request.json.get('message', '')
        if not message_content:
            return jsonify({'error': 'Message is required'}), 400

        # Get or create conversation
        conversation_id = request.json.get('conversation_id')
        if conversation_id:
            conversation = Conversation.query.get(conversation_id)
        else:
            conversation = Conversation()
            db.session.add(conversation)
            db.session.commit()

        # Save user message
        user_message = Message(
            content=message_content,
            is_user=True,
            conversation_id=conversation.id
        )
        db.session.add(user_message)

        # Get AI response
        ai_response = get_ai_response(message_content)

        # Save AI response
        ai_message = Message(
            content=ai_response,
            is_user=False,
            conversation_id=conversation.id
        )
        db.session.add(ai_message)
        db.session.commit()

        return jsonify({
            'response': ai_response,
            'conversation_id': conversation.id
        })

    except Exception as e:
        logging.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({'error': 'An error occurred processing your request'}), 500

# Create database tables within app context
with app.app_context():
    db.create_all()