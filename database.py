import requests
import firebase_admin
from firebase_admin import credentials, db
import os
from dotenv import load_dotenv


	# cred = credentials.Certificate('llmnotebook-macathon1-firebase-adminsdk-1137j-c4ecc4a9ef.json')
	# firebase_admin.initialize_app(cred, {'databaseURL': 'https://llmnotebook-macathon1-default-rtdb.asia-southeast1.firebasedatabase.app/'})
# ref = db.reference('Books/')        
# ref.set({
# 	"Book1":
# 	{
# 		"Title": "The Fellowship of the Ring",
# 		"Author": "J.R.R. Tolkien",
# 		"Genre": "Epic fantasy",
# 		"Price": 100
# 	},
# 	"Book2":
# 	{
# 		"Title": "The Two Towers",
# 		"Author": "J.R.R. Tolkien",
# 		"Genre": "Epic fantasy",
# 		"Price": 100	
# 	},
# 	"Book3":
# 	{
# 		"Title": "The Return of the King",
# 		"Author": "J.R.R. Tolkien",
# 		"Genre": "Epic fantasy",
# 		"Price": 100
# 	},
# 	"Book4":
# 	{
# 		"Title": "Brida",
# 		"Author": "Paulo Coelho",
# 		"Genre": "Fiction",
# 		"Price": 100
# 	}
# })

		
class Database():
	def __init__(self):
		load_dotenv()
		cred = credentials.Certificate(os.environ.get("FIREBASE_SECRET_DIR"))
		firebase_admin.initialize_app(cred, {'databaseURL': 'https://llmnotebook-macathon1-default-rtdb.asia-southeast1.firebasedatabase.app/'})
		
		# All References / Directories
		self.reinitialise_reference()
			
	def reinitialise_reference(self):
		# All References / Directories
		self.llm_conversation_reference = db.reference('LLMConversation/')
		self.chat_metadata = db.reference("ChatMetadata/")
		self.source_document_reference = db.reference('SourceDocuments/')	

	def get_previous_chat(self, chat_id):

        #if chat_history doesn't exist, this is an initial prompt, so this would return an empty list and provide no context
        #elsif chat_history exists, this is an existing conversation, so load chat history and query openai API with prompt + chat history 
		self.reinitialise_reference()

		previous_chat_list = []
		reference = self.llm_conversation_reference.child(chat_id).get()

		if not reference.get("chat_history", None) is None:
			for message in reference["chat_history"]:
				previous_chat_list.append(message["body"])
		return previous_chat_list
	
	def update_chat(self,  chat_id,timestamp, user, content):
		self.reinitialise_reference()
		chat_history_ref = self.llm_conversation_reference.child(chat_id).child("chat_history")
		chat  = []

		if not chat_history_ref.get() is None:
			chat = chat_history_ref.get()

		chat.append({
			"timestamp": timestamp,
			"body":{
				"role": user,
				"content": content
			}
		})
		chat_history_ref.set(chat)


	def does_chat_id_exist(self, chat_id):
		self.reinitialise_reference()
		return not (self.llm_conversation_reference.child(chat_id).get() is None)

	def add_new_chat(self, chat_id):
		#this pushes an empty json object to set up a structure for a newchat
		self.reinitialise_reference()
		self.llm_conversation_reference.child(chat_id).set({
			"chat_id": chat_id,
			"chat_history": None,
			"source_docs": {}
		})

		self.chat_metadata.child(chat_id).set("Untitled")

	def get_all_ids(self):
		'''
		Returns all ChatIDs AND Names.
		'''
		self.reinitialise_reference()
		chat_ids_and_names = []
		chat_metadata = self.chat_metadata.get()
		if not self.chat_metadata.get() is None:
			for key in chat_metadata:
				chat_ids_and_names.append({
					"id": key,
					"name": chat_metadata[key]
				})
		return chat_ids_and_names

	def add_source_document(self, filename, content, doc_type):
		source_document_object = {
			"doc_type": doc_type,
			"content": content
		}
		self.source_document_reference.child(filename).set(source_document_object)

	def get_source_document(self, filename):
		file_reference = self.source_document_reference.child(filename)
		source_document_text = ""
		if not file_reference is None:
			source_document_text = file_reference.get()["content"]
		else:
			source_document_text = f"ERROR: File {filename} does not exist."
		return source_document_text
	
	def get_all_source_documents(self):
		files_reference = self.source_document_reference.get()
		source_documents = []
		if not files_reference is None:
			source_documents = [key for key in files_reference]
		return source_documents
	
	def update_source_document(self, filename, content):
		files_reference = self.source_document_reference.child(filename)
		files_object = files_reference.get()
		if not files_object is None:
			pass





	def get_all_messages(self, chat_id):
		# List of previous messages
		chat_id_reference = self.llm_conversation_reference.child(chat_id)
		previous_messages_list = []
		if not chat_id_reference.child("chat_history") is None:
			previous_messages_object_list = chat_id_reference.child("chat_history").get()
			if not previous_messages_object_list is None:
				previous_messages_list = [obj["body"] for obj in previous_messages_object_list]
		return previous_messages_list

	def delete_chat(self, chat_id):
		self.reinitialise_reference()
		chat_id_reference = self.llm_conversation_reference.child(chat_id)
		chat_id_reference_chat_metadata = self.chat_metadata.child(chat_id)
		success = False
		if not chat_id_reference.get() is None:
			chat_id_reference.delete()
			success = True

		if not chat_id_reference_chat_metadata is None:
			chat_id_reference_chat_metadata.delete()
			success = True
		return success

	def delete_source_document(self, document_name):
		self.reinitialise_reference()
		document_id_reference = self.source_document_reference.child(document_name)
		success = False
		if not document_id_reference.get() is None:
			document_id_reference.delete()
			success = True
		return success
	


		




# content_view_document_reference = db.reference("ContentViewDocument/")


# content_view_document_reference.set({
#     "document1": {
#         "Title": "Paper 1",
#         "Author": ["Taylor", "Johnathan"]
# 	}
# })

# print(content_view_document_reference.get())




'''

SourceDocuments = {
	"doc_name": "text",
	"doc2_name": "text"
}	




LLMConversation = {
	"chatid1": {
		"chat_history": 	[
			{	"timestamp": ____,
				"body":
					{"role": "user",
					"content": "Text here."
					},
					
			},
			{
				"timestamp": ____,
				"body":
					{
						"role": "user",
						"content": "Text here."
					
					}
			}
					
		]

	},
	...
	,
}


###### This is for central docs implementation later on!!!! ######
		"source_docs":{
			"doc_name": {
				"doc_type": 1,
				"text": "text"
			},
			"doc_name2":{ 
			
			}
		}



'''





# ref.set({
# 	"Book1":
# 	{
# 		"Title": "The Fellowship of the Ring",
# 		"Author": "J.R.R. Tolkien",
# 		"Genre": "Epic fantasy",
# 		"Price": 100
# 	},
# 	"Book2":
# 	{
# 		"Title": "The Two Towers",
# 		"Author": "J.R.R. Tolkien",
# 		"Genre": "Epic fantasy",
# 		"Price": 100	
# 	},
# 	"Book3":
# 	{
# 		"Title": "The Return of the King",
# 		"Author": "J.R.R. Tolkien",
# 		"Genre": "Epic fantasy",
# 		"Price": 100
# 	},
# 	"Book4":
# 	{
# 		"Title": "Brida",
# 		"Author": "Paulo Coelho",
# 		"Genre": "Fiction",
# 		"Price": 100
# 	}
# })


# # payload = {"prompt": "Concatenate those words together."}
# # res = requests.post('http://localhost:5000/', json=payload)

# # print("response from server:",res.text)
# # dictFromServer = res.json()
# # print("\n\n\n", dictFromServer)