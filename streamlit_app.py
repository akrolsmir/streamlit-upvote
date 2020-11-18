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
        idea["discuss"] = ""
    return idea


# Get and display all ideas
ideas = [doc_to_idea(doc) for doc in db.collection("ideas").stream()]
ideas.sort(key=lambda idea: -len(idea["voters"]))
for idea in ideas:
    expander = st.beta_expander(
        upvotes_string(len(idea["voters"])) + " - " + idea["text"]
    )
    col1, col2 = expander.beta_columns([2, 6])
    with col1:
        if name:
            upvoted = st.checkbox(
                "Upvote 👍", value=name in idea["voters"], key=idea["id"]
            )
        st.write(f"📢 {idea['name']}")
        for voter in idea["voters"]:
            if voter != idea["name"]:
                st.write(voter)

    with col2:
        st.code(idea["discuss"] if idea["discuss"] else "*crickets* 🦗. Discuss here!")
        if name:
            discuss_text = st.text_area(f"Any thoughts, {name}?", key=idea["id"],)
            discussed = st.button("Submit", key=idea["id"])

    # Now see if we need to update our Firestore database
    doc_ref = db.collection("ideas").document(idea["id"])
    # If upvoted: add the name to the list of voters
    if name and (name not in idea["voters"]) and upvoted:
        doc_ref.update({"voters": idea["voters"] + [name]})
        st.experimental_rerun()

    # Or, if unvoted: remove the name
    if name and (name in idea["voters"]) and not upvoted:
        idea["voters"].remove(name)
        doc_ref.update({"voters": idea["voters"]})
        st.experimental_rerun()

    # If the user submitted a line, append it to the discussion
    if name and discussed:
        doc_ref.update({"discuss": f"{idea['discuss']}\n{name}: {discuss_text}"})
        st.experimental_rerun()

