import os
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from rag.rag_chain import build_rag_chain, ask_question


# ======================
# INGESTION TESTS
# ======================

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

    for c in chunks:
        assert len(c.page_content) <= 600


def test_min_chunks():
    from langchain_community.document_loaders import TextLoader
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    docs = TextLoader(
        "rag/inventory_manual.md",
        encoding="utf-8"
    ).load()

    chunks = RecursiveCharacterTextSplitter(
        chunk_size=200,
        chunk_overlap=30
    ).split_documents(docs)

    assert len(chunks) >= 20


# ======================
# RETRIEVAL TESTS
# ======================

def test_sku_query():
    result = ask_question(
        "What is the SKU format for grocery products?",
        build_rag_chain()
    )

    answer = result.get("answer", "").lower()

    assert any(
        x in answer
        for x in ["gro", "sku", "grocery", "prefix"]
    )


def test_top_k():
    chain = build_rag_chain()

    retriever = (
        chain.retriever
        if hasattr(chain, "retriever")
        else chain
    )

    assert retriever.search_kwargs.get("k", 4) == 4


def test_po_lifecycle():
    result = ask_question(
        "What are the stages of a purchase order?",
        build_rag_chain()
    )

    answer = result.get("answer", "").lower()

    assert any(
        x in answer
        for x in [
            "draft",
            "submitted",
            "received",
            "lifecycle"
        ]
    )


def test_empty_query():
    result = ask_question(
        "",
        build_rag_chain()
    )

    assert isinstance(result, dict)


# ======================
# GENERATION TESTS
# ======================

def test_reorder_formula():
    result = ask_question(
        "How do I calculate a reorder point?",
        build_rag_chain()
    )

    answer = result.get("answer", "").lower()

    assert any(
        x in answer
        for x in [
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

    answer = result.get("answer", "")

    assert (
        "50,000" in answer
        or "50000" in answer
        or "₹" in answer
    )


def test_stock_movement_types():
    result = ask_question(
        "What are the stock movement types?",
        build_rag_chain()
    )

    answer = result.get("answer", "").lower()

    assert any(
        x in answer
        for x in [
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

    answer = result.get("answer", "").lower()

    assert any(
        x in answer
        for x in [
            "don't have",
            "not in",
            "no information",
            "cannot"
        ]
    )


def test_non_empty():
    questions = [
        "What is SKU?",
        "What is FIFO?",
        "What is a stockout?"
    ]

    for q in questions:
        result = ask_question(
            q,
            build_rag_chain()
        )

        assert len(
            result.get("answer", "")
        ) > 10


def test_category_management():
    result = ask_question(
        "How do grocery products differ from electronics in inventory management?",
        build_rag_chain()
    )

    answer = result.get("answer", "").lower()

    assert any(
        x in answer
        for x in [
            "grocery",
            "electronic",
            "shelf life",
            "cost"
        ]
    )


# ======================
# OBSERVABILITY TESTS
# ======================

def test_sources():
    result = ask_question(
        "How does PO receiving update stock?",
        build_rag_chain()
    )

    assert isinstance(result, dict)
    assert "answer" in result