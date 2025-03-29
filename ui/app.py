import streamlit as st
import requests
from io import BytesIO

# Configure the page
st.set_page_config(page_title="Chat Interface", layout="wide")

# Add custom CSS at the app level
st.markdown(
    """
    <style>
        .search-result {
            font-size: 14px;
            margin-bottom: 10px;
        }
        .source {
            color: #666;
            margin-bottom: 5px;
        }
        .match-text {
            background-color: #f0f2f6;
            padding: 8px;
            border-radius: 4px;
            margin-bottom: 10px;
        }
    </style>
""",
    unsafe_allow_html=True,
)

# Initialize session state for chat history and embedding count
if "messages" not in st.session_state:
    st.session_state.messages = []
if "embedding_count" not in st.session_state:
    st.session_state.embedding_count = 0


# Function to fetch embedding count
def get_embedding_count():
    try:
        response = requests.get("http://backend:8000/admin/table-counts")
        if response.status_code == 200:
            data = response.json()
            # Find the embeddings table count
            for table_info in data["table_counts"]:
                if table_info["table"] == "embeddings":
                    return table_info["count"]
            return 0  # Return 0 if embeddings table not found
    except requests.exceptions.RequestException:
        return 0
    return 0


# Update embedding count
st.session_state.embedding_count = get_embedding_count()

# Create a container for the counter in the top left
counter_container = st.container()
with counter_container:
    st.markdown(f"**Total Embeddings:** {st.session_state.embedding_count}")

# Display chat title
st.title("Chat Interface")

# # Add file upload section
# with st.sidebar:
#     st.header("Document Upload")

#     # URL input
#     url = st.text_input("Enter PDF URL")
#     if url and st.button("Upload from URL"):
#         try:
#             # Fixed: match the backend expectation exactly
#             response = requests.post(
#                 "http://backend:8000/ingest/pdf",
#                 json={"url": url}  # Changed back to json with correct parameter name
#             )
#             if response.status_code == 200:
#                 st.success(f"Successfully processed PDF from URL")
#                 # Refresh embedding count
#                 st.session_state.embedding_count = get_embedding_count()
#             else:
#                 error_message = response.json() if response.text else "Unknown error"
#                 st.error(f"Error processing URL: {error_message}")
#         except Exception as e:
#             st.error(f"Error: {str(e)}")

#     # File upload
#     uploaded_file = st.file_uploader("Or upload PDF file", type=['pdf'])
#     if uploaded_file:
#         try:
#             # Create file object for upload
#             files = {"file": (uploaded_file.name, uploaded_file, "application/pdf")}

#             response = requests.post(
#                 "http://backend:8000/ingest/file",
#                 files=files
#             )

#             if response.status_code == 200:
#                 st.success(f"Successfully processed {uploaded_file.name}")
#             else:
#                 st.error(f"Error processing file: {response.text}")
#         except Exception as e:
#             st.error(f"Error: {str(e)}")

#     # Show current embedding count
#     st.markdown("---")
#     st.markdown(f"**Total Embeddings:** {st.session_state.embedding_count}")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Chat input
if prompt := st.chat_input("What's on your mind?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display user message
    with st.chat_message("user"):
        st.write(prompt)

    try:
        # Replace this URL with your actual backend API endpoint
        API_URL = "http://backend:8000/search/text/"

        # Send request to backend
        response = requests.post(API_URL, json={"query_text": prompt})

        if response.status_code == 200:
            data = response.json()
            search_results = data["sources"]
            llm_response = data["answer"]
            context_chunks = data["context_chunks"]

            # Format each result
            with st.chat_message("assistant"):
                # Display LLM response first
                st.markdown("### LLM Response:")
                st.markdown(llm_response)
                st.markdown("---")

                # Display context chunks
                st.markdown("### Context Chunks Used:")
                for i, chunk in enumerate(context_chunks, 1):
                    with st.expander(f"Context Chunk {i}"):
                        st.markdown(chunk)
                st.markdown("---")

                # Display source documents
                st.markdown("### Source Documents:")
                if not search_results:
                    st.markdown("No relevant matches found.")
                else:
                    for result in search_results:
                        text = result["text"]
                        source = result["source_document"] or "Unknown source"
                        similarity = result.get("metadata", {}).get(
                            "similarity_score", 0
                        )
                        similarity_pct = f"{similarity:.1%}" if similarity else "N/A"

                        st.markdown(
                            f'🔍 Source: "{source}" (Relevance: {similarity_pct})'
                        )
                        with st.expander(f'💡 Text: "{text[:100]}..."'):
                            st.markdown(f'"{text}"')
                        st.markdown("---")

            assistant_response = ""
        else:
            # More detailed error handling
            error_message = (
                response.text if response.text else "No error details available"
            )
            st.error(f"Backend Error (Status {response.status_code}): {error_message}")
            assistant_response = f"Sorry, there was an error searching the database. Status code: {response.status_code}"

    except requests.exceptions.RequestException as e:
        st.error(f"Connection Error: {str(e)}")
        assistant_response = "Error: Could not connect to the backend service. Please check if the backend is running."

    # Add assistant response to chat history
    st.session_state.messages.append(
        {"role": "assistant", "content": assistant_response}
    )

    # Display assistant response
    with st.chat_message("assistant"):
        st.write(assistant_response)
