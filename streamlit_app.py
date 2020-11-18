import streamlit as st
from google.cloud import firestore

db = firestore.Client.from_service_account_json(
    "melodic-star-firebase-adminsdk-pmil4-6250789447.json"
)

# Query for ideas
ideas_ref = db.collection("ideas")
for doc in ideas_ref.stream():
    name = doc.to_dict()["name"]
    text = doc.to_dict()["text"]
    votes = doc.to_dict()["votes"]

    col1, col2, col3 = st.beta_columns([2, 4, 2])
    col1.subheader(f"{votes} Votes")
    col1.checkbox("Upvote", key=doc.id)
    col2.subheader(text)
    col3.subheader(name)

    # st.write("{} => {}".format(doc.id, doc.to_dict()))

name = st.text_input("Enter your name")
text = st.text_input("What do you want to see in Streamlit?")
idea_id = st.text_input("idea_id")

if name and text and idea_id:
    doc_ref = db.collection("ideas").document(idea_id)
    doc_ref.set({"name": name, "text": text, "votes": 1})
    st.write("Press `r` to refresh!")

