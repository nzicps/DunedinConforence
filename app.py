import streamlit as st
import pandas as pd
from api_pipeline import run_pipeline

st.set_page_config(
    page_title="Conference Outreach Pipeline",
    layout="centered"
)

st.title("🎯 Conference Outreach Pipeline")

st.write(
    "Upload a CSV of organisations and generate LinkedIn lead lists."
)

uploaded_file = st.file_uploader(
    "Upload CSV",
    type=["csv"]
)

if uploaded_file:

    with open("temp.csv", "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.success("CSV uploaded successfully")

    if st.button("Run Pipeline"):

        with st.spinner("Searching LinkedIn profiles..."):

            output = run_pipeline("temp.csv")

        st.success("Pipeline completed!")

        df = pd.read_csv(output)

        st.dataframe(df)

        with open(output, "rb") as file:
            st.download_button(
                label="Download Results CSV",
                data=file,
                file_name="conference_leads.csv",
                mime="text/csv"
            )