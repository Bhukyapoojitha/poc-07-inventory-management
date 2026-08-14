try:
    from langchain.chains.summarize import (
        load_summarize_chain
    )
except ImportError:
    load_summarize_chain = None


def _summarize_if_long(
    text: str
) -> str:
    if len(text) <= 2000:
        return text

    if load_summarize_chain is None:
        return text[:1000]

    try:
        chain = load_summarize_chain

        return str(
            chain.run(text)
        )

    except Exception:
        return text[:1000]