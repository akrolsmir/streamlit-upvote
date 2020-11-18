import streamlit as st
from google.cloud import firestore

import hashlib
import base64


def hash_to_id(input_string):
    hasher = hashlib.sha1(input_string.encode())
    return base64.urlsafe_b64encode(hasher.digest()).decode()[:8]


def upvotes_string(number):
    if number <= 7:
        return "👍" * number
    return f"👍 x {number}"


db = firestore.Client.from_service_account_json(
    "melodic-star-firebase-adminsdk-pmil4-6250789447.json"
)

# DAMMIT fe0f!
ballot_icon = "https://twemoji.maxcdn.com/2/72x72/1f5f3.png"
st.set_page_config(page_title="Streamlit Upvote", page_icon=ballot_icon)

st.title("What are your 🤔💭💡 for Streamlit?")
name = st.text_input("Enter your name to upvote, discuss, or suggest ideas!")

# Let users create new ideas
if name:
    text = st.text_input("What do you want to see in Streamlit?")
    submit = st.button("Submit")
    if text and submit:
        idea_id = hash_to_id(text)
        doc_ref = db.collection("ideas").document(idea_id)
        doc_ref.set({"name": name, "text": text, "voters": [name]})


def doc_to_idea(doc):
    # idea is like {id: "b0xF0ss", "name": Austin, "text": ..., "voters": ['Austin', 'Alex']}
    idea = doc.to_dict()
    idea["id"] = doc.id
    if "discuss" not in idea:
        idea["discuss"] = "Discuss here!"
    return idea


# Get and display all ideas
ideas = [doc_to_idea(doc) for doc in db.collection("ideas").stream()]
ideas.sort(key=lambda idea: -len(idea["voters"]))
for idea in ideas:
    col1, col2 = st.beta_columns([6, 2])
    discuss = col1.beta_expander(idea["text"])
    if name:
        discuss_text = discuss.text_area(
            "Any additional thoughts?",
            value=idea["discuss"],
            height=250,
            key=idea["id"],
        )
        discussed = discuss.button("Submit", key=idea["id"])
    else:
        discuss.code(idea["discuss"])

    voters = col2.beta_expander(upvotes_string(len(idea["voters"])))
    if name:
        upvoted = voters.checkbox(
            "Upvote 👍", value=name in idea["voters"], key=idea["id"]
        )
    voters.write(f"(from {idea['name']})")
    for voter in idea["voters"]:
        if voter != idea["name"]:
            voters.write(voter)

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

    # If the user submitted a discussion change
    if name and discussed:
        doc_ref = db.collection("ideas").document(idea["id"])
        doc_ref.update({"discuss": discuss_text})
        st.experimental_rerun()

