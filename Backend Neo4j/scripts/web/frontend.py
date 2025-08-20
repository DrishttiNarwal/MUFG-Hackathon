# ============================
# Streamlit Frontend
# ============================

import streamlit as st
from scripts.recommendation.predict import predict_policies
from scripts.llm.llm_orchestrator import explain_policy

st.title("🌍 Insurance Recommendation (Federated + LLaMA 70B + RAG)")

st.sidebar.header("User Input")
name = st.sidebar.text_input("Name")
age = st.sidebar.number_input("Age", 18, 100, 30)
country = st.sidebar.selectbox("Country", ["India", "Australia"])
premium = st.sidebar.number_input("Premium you can afford", 100, 100000, 500)
insurance_type = st.sidebar.multiselect("Insurance Type", ["Health", "Life", "Travel"])

if st.sidebar.button("Get Recommendation"):
    user_input = {
        "Name": name,
        "Age": age,
        "Country": country,
        "Premium": premium,
        "InsuranceType": ",".join(insurance_type)
    }

    rec = predict_policies(user_input)

    st.subheader("🟢 Policy Options (with Probabilities)")
    for item in rec["ranked_policies"]:
        policy, prob = item["policy"], item["probability"]

        # Highlight best one
        if policy == rec["best_recommendation"]:
            st.markdown(f"**✨ {policy} (Best Choice) → {prob:.2%}**")
        else:
            st.markdown(f"- {policy}: {prob:.2%}")

        # Button to see reasoning
        if st.button(f"📑 Why {policy}?"):
            rag_context = "Fetched policy details from GraphRAG..."  # placeholder
            explanation = explain_policy(
                user_input, policy, rag_context, is_best=(policy == rec["best_recommendation"])
            )
            st.markdown(f"### {policy} Explanation")
            st.write(explanation)
