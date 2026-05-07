import streamlit as st
import pandas as pd
import requests
import os
import matplotlib.pyplot as plt


API_KEY = os.getenv("API_KEY")

st.set_page_config(page_title="💰 Personal Finance Tracker", layout="wide")


st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0b132b, #1c2541, #3a506b);
}
h1, h2, h3 {
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

st.title("💰 Personal Finance Tracker")
st.markdown("### Track Expenses • Budget Smart • Save Money")


if "expenses" not in st.session_state:
    st.session_state.expenses = pd.DataFrame(columns=["Category", "Amount"])


st.sidebar.header("➕ Add Expense")

category = st.sidebar.selectbox("Category", ["Food", "Travel", "Shopping", "Bills", "Other"])
amount = st.sidebar.number_input("Amount (₹)", min_value=0)

if st.sidebar.button("Add Expense"):
    new_data = pd.DataFrame([[category, amount]], columns=["Category", "Amount"])
    st.session_state.expenses = pd.concat([st.session_state.expenses, new_data], ignore_index=True)
    st.sidebar.success("Expense Added ✅")


st.subheader("📋 Expense History")
st.dataframe(st.session_state.expenses)


total = st.session_state.expenses["Amount"].sum()
st.metric("💸 Total Spending", f"₹{total}")


st.subheader("📊 Spending Distribution")

if not st.session_state.expenses.empty:
    chart_data = st.session_state.expenses.groupby("Category")["Amount"].sum()

    fig, ax = plt.subplots()
    ax.pie(chart_data, labels=chart_data.index, autopct="%1.1f%%")
    st.pyplot(fig)


st.subheader("🎯 Budget Control")

budget = st.number_input("Set Monthly Budget (₹)", min_value=0)

if budget > 0:
    if total > budget:
        st.error("⚠️ You exceeded your budget!")
    else:
        st.success(f"✅ Remaining Budget: ₹{budget - total}")


st.subheader("💡 Smart Saving Tips")

def saving_tips(total):
    if total > 5000:
        return "💡 Try reducing unnecessary shopping & dining expenses."
    elif total > 2000:
        return "💡 Good! But you can save more by tracking daily expenses."
    else:
        return "💡 Great job! Keep maintaining your spending habits."

st.info(saving_tips(total))


st.markdown("---")
st.subheader("💬 Finance Chatbot")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Ask about finance, budgeting, saving...")

def is_valid_query(user_input):
    allowed = ["finance","money","budget","saving","investment","expense","income","tax","emi","loan","debt","credit","debit","SIP"]
    return any(word in user_input.lower() for word in allowed)


def get_ai_response(user_input):
    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "openai/gpt-3.5-turbo",  # safer free model
        "messages": [
            {"role": "system", "content": "You are a STRICT Personal Finance Advisor. expert on what SIP finance is"},
            {"role": "user", "content": user_input}
        ]
    }

    try:
        res = requests.post(url, headers=headers, json=payload)
        data = res.json()

        print(data)  # debug (see error in terminal)

        if "choices" in data:
            return data["choices"][0]["message"]["content"]

        elif "error" in data:
            return f"❌ API Error: {data['error']['message']}"

        else:
            return "❌ Unexpected response from API"

    except Exception as e:
        return f"⚠️ Error: {str(e)}"

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    if not is_valid_query(user_input):
        reply = "❌ I only answer finance-related questions 💰"
    else:
        reply = get_ai_response(user_input)

    st.session_state.messages.append({"role": "assistant", "content": reply})

    with st.chat_message("assistant"):
        st.markdown(reply)