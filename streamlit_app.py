import streamlit as st
from google.cloud import firestore

name = st.text_input("Enter your name")

if name:
    db = firestore.Client.from_service_account_json(
        "melodic-star-firebase-adminsdk-pmil4-6250789447.json"
    )
    doc_ref = db.collection("users").document(name)
    doc_ref.set({"first": name, "last": "Lovelace", "born": 1815})

    # Then query for documents
    users_ref = db.collection("users")

    for doc in users_ref.stream():
        st.write("{} => {}".format(doc.id, doc.to_dict()))

