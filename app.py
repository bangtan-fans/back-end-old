#!/usr/bin/env python
# encoding: utf-8
import json
from flask import Flask, request, jsonify
from openapi import OpenAIAPI
from database import Database
import uuid
import os


app = Flask(__name__)
database = Database()
openAIAPI= OpenAIAPI(database)



def generate_unique_id():
    """Generate a unique ID using UUID."""
    return str(uuid.uuid4())

@app.route('/get_all_ids', methods=['GET'])
def get_all_ids():
    return jsonify(database.get_all_ids())

@app.route('/get_all_messages/<chat_id>')
def get_all_messages(chat_id):
    return jsonify(database.get_all_messages(chat_id))

@app.route('/new_chat', methods = ['GET'])
def new_chat():
    new_chat_id = generate_unique_id()
    database.add_new_chat(chat_id = new_chat_id)
    return jsonify({"new_chat_id": new_chat_id})

@app.route('/add_source_document', methods = ['POST'])
def add_source_document():
    message_body = json.loads(request.data)
    # Assume it's in the format of "filename": "name", "content": "text"
    
    database.add_source_document(filename=message_body["filename"], content=message_body["content"])

    

@app.route('/submit_prompt', methods=['POST'])
def submit_prompt():
    message_body = json.loads(request.data)
    chat_id = message_body["chat_id"]
    prompt = message_body["prompt"]

    #check if source docs have been selected for this chat 
    source_docs_list = message_body["source_docs"]

    response = openAIAPI.get_completion(chat_id, prompt)
    return response


def select_source_document():
    pass 


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))