import streamlit as st
import requests


BASE_URL="https://rag-implementation-using-streamlit.onrender.com"

def main():
    st.title("PDF Collection Manager")

    # Upload PDF files
    with st.form("upload_form", clear_on_submit=True):
        collection_name = st.text_input("Collection Name")
        uploaded_files = st.file_uploader("Upload PDFs", accept_multiple_files=True, type="pdf")
        upload_button = st.form_submit_button("Upload")

        if upload_button and collection_name and uploaded_files:
            files = [("files", (file.name, file, file.type)) for file in uploaded_files]
            response = requests.post(f"{BASE_URL}/upload/?name={collection_name}", files=files)
            if response.status_code == 200:
                st.success(f"Files uploaded successfully to collection: {collection_name}")
            else:
                st.error(f"Failed to upload files: {response.json()['detail']}")

    # Display collections and deploy button
    response = requests.get(f"{BASE_URL}/collections/")
    if response.status_code == 200:
        collections = response.json()
        for collection in collections:
            col_name = collection['name']
            st.write(f"**Collection Name:** {col_name}")
            deploy_button = st.button(f"Deploy {col_name}", key=f"deploy_{col_name}")

            if deploy_button:
                response = requests.get(f"{BASE_URL}/collections/{col_name}/deploy")
                if response.status_code == 200:
                    st.session_state['current_collection'] = col_name
                    st.session_state['vector_db'] = response.json()['vector_db']
                    st.session_state['query_responses'] = []
                    st.session_state['page'] = 'query'
                    st.rerun()

def query_page():
    collection_name = st.session_state['current_collection']
    st.title(f"Query Collection: {collection_name}")

    st.write("### Previous Queries and Responses")
    for q, r in st.session_state['query_responses']:
        st.write(f"**Query:** {q}")
        st.write(f"**Response:** {r}")
        st.write("---")

    query = st.text_input("Enter your query", key="query_input")
    if st.button("Submit Query", key="submit_button"):
        # Send query to backend
        payload = {"collection": collection_name, "query": query}
        response = requests.post(f"{BASE_URL}/query/", json=payload)
        if response.status_code == 200:
            response_text = response.json().get("response", "No response from backend")
            st.session_state['query_responses'].append((query, response_text))
            st.rerun()
        else:
            st.error("Failed to get response from backend")

    if st.button("Back"):
        st.session_state['page'] = 'main'
        st.rerun()


if 'page' not in st.session_state:
    st.session_state['page'] = 'main'

if st.session_state['page'] == 'main':
    main()
else:
    query_page()