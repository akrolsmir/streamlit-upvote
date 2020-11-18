import streamlit as st
from google.cloud import firestore

import hashlib
import base64


def hash_to_id(input_string):
    hasher = hashlib.sha1(input_string.encode())
    return base64.urlsafe_b64encode(hasher.digest()).decode()[:8]


db = firestore.Client.from_service_account_json(
    "melodic-star-firebase-adminsdk-pmil4-6250789447.json"
)

# DAMMIT fe0f!
ballot_icon = "https://twemoji.maxcdn.com/2/72x72/1f5f3.png"
st.set_page_config(page_title="Streamlit Upvote", page_icon=ballot_icon)

name = st.text_input("Enter your name to upvote & suggest ideas!")

# Let users create new ideas
if name:
    text = st.text_input("What do you want to see in Streamlit?")
    submit = st.button("Submit")
    idea_id = hash_to_id(text)

if name and text and submit:
    doc_ref = db.collection("ideas").document(idea_id)
    doc_ref.set({"name": name, "text": text, "votes": 1})

# Get and display all ideas
ideas_ref = db.collection("ideas")
for doc in ideas_ref.stream():
    # idea is like {id: "b0xF0ss", "name": Austin, "text": ..., "votes": 1}
    idea = doc.to_dict()
    idea["id"] = doc.id

    col1, col2, col3 = st.beta_columns([2, 4, 2])
    col1.subheader(f"{idea['votes']} Votes")
    if name:
        upvoted = col1.checkbox("Upvote", key=idea["id"])
    col2.subheader(idea["text"])
    col3.subheader(idea["name"])

    if name and upvoted:
        doc_ref = db.collection("ideas").document(idea["id"])
        doc_ref.update({"votes": idea["votes"] + 1})
        # TODO: Rerun page after an upvote?

