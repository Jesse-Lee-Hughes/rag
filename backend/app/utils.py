import io
import requests
from llama_index.core import Document
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import pypdf
from sqlalchemy.exc import IntegrityError
import hashlib
from app.database import E5Embedding


class LlamaVectorizer:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.embed_model = HuggingFaceEmbedding(model_name="intfloat/e5-small-v2")
            cls._instance.parser = SentenceSplitter(chunk_size=510, chunk_overlap=50)
        return cls._instance

    @staticmethod
    def convert_pdf_to_text(pdf_source):
        """Extract text from a PDF file or URL."""
        if pdf_source.startswith(('http://', 'https://')):
            response = requests.get(pdf_source)
            pdf_content = io.BytesIO(response.content)
        else:
            pdf_content = open(pdf_source, 'rb')

        pdf_reader = pypdf.PdfReader(pdf_content)
        text = ' '.join(
            page.extract_text().replace('\n\n', ' ').replace('\n', ' ').lower()
            for page in pdf_reader.pages if page.extract_text()
        )

        if hasattr(pdf_content, 'close'):
            pdf_content.close()

        return text.strip()

    def process_document(self, text, db_session, source_document=None):
        """Process text: chunking, embedding, and storing in database."""
        doc = Document(text=text)
        nodes = self.parser.get_nodes_from_documents([doc])
        
        results = []
        for node in nodes:
            # Generate hash first
            text_hash = hashlib.md5(node.text.encode()).hexdigest()
            
            # Check if entry exists
            existing = db_session.query(E5Embedding).filter_by(
                text_hash=text_hash
            ).first()
            
            if existing:
                results.append(existing)
            else:
                # Only generate embedding and insert if new
                embedding = self.embed_model.get_text_embedding(node.text)
                db_entry = E5Embedding(
                    text=node.text, 
                    vector=embedding, 
                    text_hash=text_hash,
                    source_document=source_document
                )
                db_session.add(db_entry)
                db_session.commit()
                results.append(db_entry)
        
        return results


# # Example usage
# try:
#     source = "https://arxiv.org/pdf/2408.09869"  # PDF URL or path
#     v = LlamaVectorizer()
#
#     text_content = v.convert_pdf_to_text(source)  # Extract text from PDF
#     embeddings, chunks = v.process_document(text_content)  # Chunk and create embeddings
#
#     # Print results
#     for i, (embedding, chunk) in enumerate(zip(embeddings, chunks), 1):
#         print(f"Chunk {i} (length: {len(chunk)}):")
#         print(f"Embedding shape: {len(embedding)}")  # Hugging Face embeddings are usually 768-d
#         print(f"First 100 chars: {chunk[:100]}...\n")
#
# except Exception as e:
#     print(f"An error occurred: {e}")
