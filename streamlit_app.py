import streamlit as st
from google.cloud import firestore

import hashlib
import base64


def hash_to_id(input_string):
    hasher = hashlib.sha1(input_string.encode())
    return base64.urlsafe_b64encode(hasher.digest()).decode()[:8]


# DAMMIT fe0f!
ballot_icon = "https://twemoji.maxcdn.com/2/72x72/1f5f3.png"
st.set_page_config(page_title="Streamlit Upvote", page_icon=ballot_icon)

db = firestore.Client.from_service_account_json(
    "melodic-star-firebase-adminsdk-pmil4-6250789447.json"
)

# Get and display all ideas
ideas_ref = db.collection("ideas")
for doc in ideas_ref.stream():
    idea_id = doc.id
    name = doc.to_dict()["name"]
    text = doc.to_dict()["text"]
    votes = doc.to_dict()["votes"]

    col1, col2, col3 = st.beta_columns([2, 4, 2])
    col1.subheader(f"{votes} Votes")
    upvoted = col1.checkbox("Upvote", key=idea_id)
    col2.subheader(text)
    col3.subheader(name)

    if upvoted:
        doc_ref = db.collection("ideas").document(idea_id)
        doc_ref.update({"votes": votes + 1})

# Let users create new ideas
name = st.text_input("Enter your name")
text = st.text_input("What do you want to see in Streamlit?")
idea_id = hash_to_id(text)

if name and text:
    doc_ref = db.collection("ideas").document(idea_id)
    doc_ref.set({"name": name, "text": text, "votes": 1})
    st.write("Press `r` to refresh!")

