import streamlit as st
from recipe_bot import RecipeBot

st.set_page_config(
    page_title="Recipe Assistant",
    page_icon="🍳",
    layout="centered"
)

st.title("Recipe Assistant")

if "bot" not in st.session_state:
    st.session_state.bot = RecipeBot()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if st.button("Start New Recipe"):
    st.session_state.bot = RecipeBot()
    st.session_state.chat_history = []
    st.rerun()

for role, content in st.session_state.chat_history:
    with st.chat_message(role):
        if isinstance(content, dict):
            st.markdown(f"### {content['recipe_name']}")
            for step in content["steps"]:
                st.markdown(f"- {step}")
        else:
            st.markdown(content)

user_input = st.chat_input("Type ingredients...")

if user_input:
    st.session_state.chat_history.append(("user", user_input))

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.spinner("Cooking something delicious..."):
        response = st.session_state.bot.answer_question(user_input)

    st.session_state.chat_history.append(("assistant", response))

    with st.chat_message("assistant"):
        if isinstance(response, dict):
            st.markdown(f"### {response['recipe_name']}")
            for step in response["steps"]:
                st.markdown(f"- {step}")
        else:
            st.markdown(response)
