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
    if text and submit:
        idea_id = hash_to_id(text)
        doc_ref = db.collection("ideas").document(idea_id)
        doc_ref.set({"name": name, "text": text, "voters": [name]})

# Get and display all ideas
ideas_ref = db.collection("ideas")
for doc in ideas_ref.stream():
    # idea is like {id: "b0xF0ss", "name": Austin, "text": ..., "voters": ['Austin', 'Alex']}
    idea = doc.to_dict()
    idea["id"] = doc.id

    col1, col2, col3 = st.beta_columns([2, 4, 2])
    col1.subheader(f"{len(idea['voters'])} Votes")
    if name:
        upvoted = col1.checkbox("Upvote", value=name in idea["voters"], key=idea["id"])
    col2.subheader(idea["text"])
    col3.subheader(idea["name"])

    # If upvoted: add the name to the list of voters
    if name and (name not in idea["voters"]) and upvoted:
        doc_ref = db.collection("ideas").document(idea["id"])
        doc_ref.update({"voters": idea["voters"] + [name]})
        st.experimental_rerun()

    # Or, if unvoted: remove the name
    if name and (name in idea["voters"]) and not upvoted:
        doc_ref = db.collection("ideas").document(idea["id"])
        idea["voters"].remove(name)
        doc_ref.update({"voters": idea["voters"]})
        st.experimental_rerun()

