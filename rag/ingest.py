from dotenv import load_dotenv
load_dotenv()

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings

loader = TextLoader(
    "./rag/inventory_manual.md",
    encoding="utf-8"
)

documents = loader.load()

print("Documents loaded:", len(documents))

if not documents:
    raise Exception("inventory_manual.md could not be loaded")

text = documents[0].page_content

print("Text length:", len(text))

if not text.strip():
    raise Exception("inventory_manual.md is empty")

splitter = RecursiveCharacterTextSplitter(
    chunk_size=200,
    chunk_overlap=30
)

chunks = splitter.create_documents([text])

print("Chunks created:", len(chunks))

for i, chunk in enumerate(chunks[:2]):
    print(f"\nChunk {i + 1}")
    print("-" * 50)
    print(chunk.page_content[:200])

if not chunks:
    raise Exception("No chunks were created from inventory_manual.md")

print("\nCreating Ollama embeddings...")

embeddings = OllamaEmbeddings(
    model="nomic-embed-text"
)

vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    collection_name="inventory_manual",
    persist_directory="./chroma_db"
)

print("\nChromaDB created successfully")
print(f"Total chunks stored: {len(chunks)}")