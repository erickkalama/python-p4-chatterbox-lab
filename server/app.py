from flask import Flask, request, make_response, jsonify, abort
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

# GET /messages - Retrieve all messages
@app.route('/messages', methods=['GET'])
def get_messages():
    messages = Message.query.order_by(Message.created_at.asc()).all()
    message_list = [message.to_dict() for message in messages]
    return jsonify(message_list), 200

# POST /messages - Create a new message
@app.route('/messages', methods=['POST'])
def create_message():
    data = request.get_json()
    
    # Validate required fields
    if not data.get('body') or not data.get('username'):
        return make_response(jsonify({"error": "Both body and username are required"}), 400)
    
    new_message = Message(
        body=data.get('body'),
        username=data.get('username'),
    )
    
    db.session.add(new_message)
    db.session.commit()
    
    return jsonify(new_message.to_dict()), 201

# GET /messages/<int:id> - Retrieve a specific message by id
@app.route('/messages/<int:id>', methods=['GET'])
def get_message_by_id(id):
    message = db.session.get(Message, id)
    if not message:
        abort(404, description="Message not found")
    
    return jsonify(message.to_dict()), 200

# PATCH /messages/<int:id> - Update an existing message
@app.route('/messages/<int:id>', methods=['PATCH'])
def update_message(id):
    message = db.session.get(Message, id)
    if not message:
        abort(404, description="Message not found")

    data = request.get_json()

    # Validate if body is empty
    if 'body' in data and not data['body']:
        return make_response(jsonify({"error": "Message body cannot be empty"}), 400)

    message.body = data.get('body', message.body)
    db.session.commit()
    
    return jsonify(message.to_dict()), 200

# DELETE /messages/<int:id> - Delete a message@app.route('/messages/<int:id>', methods=['DELETE'])
def delete_message(id):
    message = Message.query.get(id)
    if message:
        db.session.delete(message)
        db.session.commit()
        return '', 204  # No Content
    return '', 404  # Not Found

if __name__ == '__main__':
    app.run(port=5555)
