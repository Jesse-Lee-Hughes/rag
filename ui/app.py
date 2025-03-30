import streamlit as st
import requests
from io import BytesIO
from datetime import datetime
import pandas as pd


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
        .conversation-item {
            padding: 8px;
            border-radius: 4px;
            margin-bottom: 4px;
            background-color: #f0f2f6;
        }
    </style>
""",
    unsafe_allow_html=True,
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "embedding_count" not in st.session_state:
    st.session_state.embedding_count = 0
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None
if "conversation_count" not in st.session_state:
    st.session_state.conversation_count = 0


# Function to fetch embedding count
def get_embedding_count():
    try:
        response = requests.get("http://backend:8000/admin/table-counts")
        if response.status_code == 200:
            data = response.json()
            for table_info in data["table_counts"]:
                if table_info["table"] == "embeddings":
                    return table_info["count"]
            return 0
    except requests.exceptions.RequestException:
        return 0
    return 0


# Function to fetch conversation count
def get_conversation_count():
    try:
        response = requests.get("http://backend:8000/conversations")
        if response.status_code == 200:
            data = response.json()
            return len(data["conversations"])
    except requests.exceptions.RequestException:
        return 0
    return 0


# Function to clear conversation memory
def clear_conversation_memory():
    try:
        if st.session_state.conversation_id:
            response = requests.delete(
                f"http://backend:8000/conversations/{st.session_state.conversation_id}"
            )
            if response.status_code == 200:
                st.session_state.messages = []
                st.session_state.conversation_id = None
                st.session_state.conversation_count = get_conversation_count()
                st.success("Conversation memory cleared!")
    except requests.exceptions.RequestException as e:
        st.error(f"Error clearing memory: {str(e)}")


# Update counts
st.session_state.embedding_count = get_embedding_count()
st.session_state.conversation_count = get_conversation_count()

# Sidebar
with st.sidebar:

    # Document statistics
    st.markdown("### Statistics")

    # Create DataFrame with statistics
    stats_data = {
        "Metric": ["Total Embeddings", "Total Conversations"],
        "Value": [
            st.session_state.embedding_count,
            st.session_state.conversation_count,
        ],
    }
    stats_df = pd.DataFrame(stats_data)
    st.dataframe(stats_df, hide_index=True)

    # Search results containers
    st.markdown("### Search Results")
    source_container = st.empty()
    context_container = st.empty()

    st.markdown("### Conversation History")
    if st.session_state.conversation_id:
        try:
            response = requests.get(
                f"http://backend:8000/conversations/{st.session_state.conversation_id}"
            )
            if response.status_code == 200:
                history = response.json()
                for turn in history["turns"]:
                    with st.expander(f"Q: {turn['query'][:50]}...", expanded=False):
                        st.markdown(f"**Query:** {turn['query']}")
                        st.markdown(f"**Response:** {turn['response']}")
                        st.markdown(f"**Time:** {turn['timestamp']}")
        except requests.exceptions.RequestException:
            st.error("Error fetching conversation history")
    else:
        st.info("No active conversation")
    if st.button("🗑️ Clear Conversation Memory"):
        clear_conversation_memory()


# Main chat area
st.title("Ask Mook")

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
        # Prepare request with conversation context
        request_data = {
            "query_text": prompt,
            "conversation_id": st.session_state.conversation_id,
            "memory_window": 5,
        }

        response = requests.post("http://backend:8000/search/text/", json=request_data)

        if response.status_code == 200:
            data = response.json()
            llm_response = data["answer"]
            search_results = data["sources"]
            context_chunks = data["context_chunks"]

            # Update conversation ID if this is a new conversation
            if not st.session_state.conversation_id and data.get("conversation_id"):
                st.session_state.conversation_id = data["conversation_id"]
                st.session_state.conversation_count = get_conversation_count()

            # Display LLM response in main chat
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(f"**Mook**: {llm_response}")
                if data.get("provider"):
                    st.markdown(f"*Source: {data['provider']}*")

            # Update sidebar with sources and context
            with source_container:
                st.markdown("### Source Information")
                if data.get("source_links"):
                    with st.expander("🔗 Source Links"):
                        # Create a set to track unique links
                        unique_links = set()
                        for link in data["source_links"]:
                            # Only process if this link hasn't been seen
                            if link["link"] not in unique_links:
                                unique_links.add(link["link"])
                                metadata_str = ""
                                if link.get("metadata"):
                                    metadata_items = [
                                        f"{k}: {v}" for k, v in link["metadata"].items()
                                    ]
                                    metadata_str = f" ({', '.join(metadata_items)})"
                                st.markdown(
                                    f"**Provider: {link['provider']}** \n\n  **Source: [{link['link']}]** \n\n **Metadata:** {metadata_str}\n\n---\n\n"
                                    
                                )
                else:
                    st.info("No source links available")

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
