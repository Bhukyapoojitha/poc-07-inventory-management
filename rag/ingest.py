from dotenv import load_dotenv

from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

MANUAL_PATH = "./rag/inventory_manual.md"
COLLECTION_NAME = "inventory_manual"
CHROMA_PATH = "./chroma_db"
EMBEDDING_MODEL = "nomic-embed-text"


loader = TextLoader(
    MANUAL_PATH,
    encoding="utf-8"
)

documents = loader.load()

print("Documents loaded:", len(documents))

if not documents:
    raise FileNotFoundError(
        f"Unable to load manual from '{MANUAL_PATH}'"
    )

text = documents[0].page_content

print("Text length:", len(text))

if not text.strip():
    raise ValueError(
        "inventory_manual.md is empty"
    )

splitter = RecursiveCharacterTextSplitter(
    chunk_size=200,
    chunk_overlap=30
)

chunks = splitter.create_documents([text])

print("Chunks created:", len(chunks))

for index, chunk in enumerate(chunks[:2], start=1):
    print(f"\nChunk {index}")
    print("-" * 50)
    print(chunk.page_content[:200])

if not chunks:
    raise RuntimeError(
        "No chunks were created from inventory_manual.md"
    )

print("\nCreating Ollama embeddings...")

embeddings = OllamaEmbeddings(
    model=EMBEDDING_MODEL
)

vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    collection_name=COLLECTION_NAME,
    persist_directory=CHROMA_PATH
)

print("\nChromaDB created successfully")
print(f"Total chunks stored: {len(chunks)}")