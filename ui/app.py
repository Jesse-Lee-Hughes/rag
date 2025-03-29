import streamlit as st
import requests
from io import BytesIO


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

# Move embeddings counter and context to sidebar
with st.sidebar:
    st.title("Document Context")

    # Embeddings counter in sidebar
    st.markdown(f"**Total Embeddings:** {st.session_state.embedding_count}")
    st.markdown("---")

    # Containers for search results (will be populated during chat)
    source_container = st.empty()
    context_container = st.empty()

# Main chat area
st.title("Contextual Insight Engine")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Chat input and response handling
if prompt := st.chat_input("Ask me anything."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display user message
    with st.chat_message("user"):
        st.write(prompt)

    try:
        response = requests.post(
            "http://backend:8000/search/text/", json={"query_text": prompt}
        )

        if response.status_code == 200:
            data = response.json()
            llm_response = data["answer"]
            search_results = data["sources"]
            context_chunks = data["context_chunks"]

            # Display LLM response in main chat
            with st.chat_message("assistant"):
                st.write(llm_response)

            # Update sidebar with sources and context
            with source_container:
                st.markdown("### Source Documents")
                unique_sources = {
                    result["source_document"]: result.get("metadata", {}).get(
                        "similarity_score", 0
                    )
                    for result in search_results
                }

                with st.expander("📚 Source Links"):
                    for source, similarity in unique_sources.items():
                        st.markdown(
                            f"🔗 [{source}]({source}) (Relevance: {similarity:.1%})"
                        )

            with context_container:
                st.markdown("### Context Chunks")
                with st.expander("📝 Retrieved Chunks"):
                    for i, result in enumerate(search_results, 1):
                        similarity = result.get("metadata", {}).get(
                            "similarity_score", 0
                        )
                        st.markdown(f"**Chunk {i} (Relevance: {similarity:.1%})**")
                        st.markdown(result["text"])
                        st.markdown("---")

            # Add only the LLM response to chat history
            st.session_state.messages.append(
                {"role": "assistant", "content": llm_response}
            )

        else:
            error_message = (
                response.text if response.text else "No error details available"
            )
            st.error(f"Backend Error (Status {response.status_code}): {error_message}")

    except requests.exceptions.RequestException as e:
        st.error(f"Connection Error: {str(e)}")
