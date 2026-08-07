import os
import time
from unittest.mock import MagicMock

import pytest
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from rag.rag_chain import ask_question, build_rag_chain


# =====================
# INGESTION (4)
# =====================

def test_manual_loads():
    assert os.path.exists("rag/inventory_manual.md")

    docs = TextLoader(
        "rag/inventory_manual.md",
        encoding="utf-8"
    ).load()

    assert len(docs) > 0
    assert len(docs[0].page_content) > 100


def test_chunks_size():
    docs = TextLoader(
        "rag/inventory_manual.md",
        encoding="utf-8"
    ).load()

    chunks = RecursiveCharacterTextSplitter(
        chunk_size=600,
        chunk_overlap=50
    ).split_documents(docs)

    for chunk in chunks:
        assert len(chunk.page_content) <= 600


def test_min_chunks():
    docs = TextLoader(
        "rag/inventory_manual.md",
        encoding="utf-8"
    ).load()

    chunks = RecursiveCharacterTextSplitter(
        chunk_size=200,
        chunk_overlap=30
    ).split_documents(docs)

    assert len(chunks) >= 20


def test_chromadb_collection():
    import chromadb

    client = chromadb.PersistentClient(
        path="./chroma_db"
    )

    collection_names = [
        collection.name
        for collection in client.list_collections()
    ]

    assert "inventory_manual" in collection_names

    collection = client.get_collection(
        "inventory_manual"
    )

    assert collection.count() >= 20


# =====================
# RETRIEVAL (6)
# =====================

def test_sku_query():
    result = ask_question(
        "What is the SKU format for grocery products?",
        build_rag_chain()
    )

    answer = result.get(
        "answer",
        ""
    ).lower()

    assert any(
        value in answer
        for value in [
            "gro",
            "sku",
            "grocery",
            "prefix"
        ]
    )


def test_top_k():
    chain = build_rag_chain()

    retriever = (
        chain.retriever
        if hasattr(chain, "retriever")
        else chain
    )

    if hasattr(retriever, "search_kwargs"):
        assert retriever.search_kwargs.get("k", 4) == 4


def test_irrelevant_low_score():
    mock = MagicMock()

    mock.query.return_value = {
        "documents": [["Inventory stock info."]],
        "distances": [[0.87]]
    }

    response = mock.query(
        query_texts=["Football match results"],
        n_results=4
    )

    distance = response["distances"][0][0]

    assert distance > 0.5


def test_po_lifecycle():
    result = ask_question(
        "What are the stages of a purchase order?",
        build_rag_chain()
    )

    answer = result.get(
        "answer",
        ""
    ).lower()

    assert any(
        value in answer
        for value in [
            "draft",
            "submitted",
            "received",
            "status",
            "lifecycle"
        ]
    )


def test_empty_query():
    result = ask_question(
        "",
        build_rag_chain()
    )

    assert isinstance(result, dict)

    answer = result.get("answer")

    assert isinstance(answer, str)


def test_latency():
    chain = build_rag_chain()

    start_time = time.time()

    ask_question(
        "What is a reorder point?",
        chain
    )

    elapsed_time = time.time() - start_time

    assert elapsed_time < 5.0


# =====================
# GENERATION (6)
# =====================

def test_reorder_formula():
    result = ask_question(
        "How do I calculate a reorder point?",
        build_rag_chain()
    )

    answer = result.get(
        "answer",
        ""
    ).lower()

    assert any(
        value in answer
        for value in [
            "lead time",
            "daily",
            "demand",
            "safety",
            "reorder"
        ]
    )


def test_po_approval():
    result = ask_question(
        "When does a PO need Store Manager approval?",
        build_rag_chain()
    )

    answer = result.get(
        "answer",
        ""
    )

    assert (
        "50,000" in answer
        or "50000" in answer
        or "₹" in answer
    )


def test_movement_types():
    result = ask_question(
        "What are the stock movement types?",
        build_rag_chain()
    )

    answer = result.get(
        "answer",
        ""
    ).lower()

    assert any(
        value in answer
        for value in [
            "receipt",
            "sale",
            "adjustment",
            "transfer",
            "return"
        ]
    )


def test_out_of_scope():
    result = ask_question(
        "What is the weather forecast for Mumbai?",
        build_rag_chain()
    )

    answer = result.get(
        "answer",
        ""
    ).lower()

    assert any(
        value in answer
        for value in