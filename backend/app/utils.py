import io
import requests
from llama_index.core import Document
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import pypdf
import hashlib
from app.database import E5Embedding


class LlamaVectorizer:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.embed_model = HuggingFaceEmbedding(
                model_name="intfloat/e5-small-v2"
            )
            cls._instance.parser = SentenceSplitter(chunk_size=510, chunk_overlap=50)
        return cls._instance

    @staticmethod
    def convert_pdf_to_text(pdf_source):
        """Extract text from a PDF file or URL."""
        if pdf_source.startswith(("http://", "https://")):
            response = requests.get(pdf_source)
            pdf_content = io.BytesIO(response.content)
        else:
            pdf_content = open(pdf_source, "rb")

        pdf_reader = pypdf.PdfReader(pdf_content)
        text = " ".join(
            page.extract_text().replace("\n\n", " ").replace("\n", " ").lower()
            for page in pdf_reader.pages
            if page.extract_text()
        )

        if hasattr(pdf_content, "close"):
            pdf_content.close()

        return text.strip()

    def process_document(self, text, db_session, source_document=None):
        """Process text: chunking, embedding, and storing in database."""
        doc = Document(text=text)
        nodes = self.parser.get_nodes_from_documents([doc])

        # Determine document type from source
        doc_type = "unknown"
        if source_document:
            if source_document.lower().endswith(".pdf"):
                doc_type = "pdf"
            elif source_document.lower().endswith(".txt"):
                doc_type = "text"
            elif source_document.lower().endswith((".xlsx", ".xls")):
                doc_type = "excel"
            elif source_document.startswith(("http://", "https://")):
                doc_type = "web"

        results = []
        for node in nodes:
            # Generate hash first
            text_hash = hashlib.md5(node.text.encode()).hexdigest()

            # Check if entry exists
            existing = (
                db_session.query(E5Embedding).filter_by(text_hash=text_hash).first()
            )

            if existing:
                results.append(existing)
            else:
                # Only generate embedding and insert if new
                embedding = self.embed_model.get_text_embedding(node.text)
                metadata = {"type": doc_type, "source": source_document}
                db_entry = E5Embedding(
                    text=node.text,
                    vector=embedding,
                    text_hash=text_hash,
                    source_document=source_document,
                )
                db_entry.set_metadata(metadata)
                db_session.add(db_entry)
                db_session.commit()
                results.append(db_entry)

        return results
