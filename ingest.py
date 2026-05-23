import os
from elasticsearch import Elasticsearch, helpers

ES_HOST = "http://localhost:9200"
ES_INDEX = "rag_documents"
CHUNK_SIZE = 400
CHUNK_OVERLAP = 80

DOCS_DIR = "/Users/loriecastillano/CascadeProjects/agent-loria"
ALLOWED_EXTENSIONS = {".md", ".txt"}

es = Elasticsearch(ES_HOST)


def chunk_text(text, size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        chunk = " ".join(words[start : start + size])
        chunks.append(chunk)
        start += size - overlap
    return chunks


def create_index():
    if es.indices.exists(index=ES_INDEX):
        es.indices.delete(index=ES_INDEX)
        print(f"Deleted existing index: {ES_INDEX}")

    es.indices.create(
        index=ES_INDEX,
        body={
            "mappings": {
                "properties": {
                    "title": {"type": "text"},
                    "content": {"type": "text"},
                    "source": {"type": "keyword"},
                    "chunk_id": {"type": "integer"},
                }
            }
        },
    )
    print(f"Created index: {ES_INDEX}")


def load_documents():
    docs = []
    for filename in os.listdir(DOCS_DIR):
        ext = os.path.splitext(filename)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            continue
        filepath = os.path.join(DOCS_DIR, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()
        title = os.path.splitext(filename)[0].replace("_", " ").replace("-", " ").title()
        chunks = chunk_text(text)
        for i, chunk in enumerate(chunks):
            docs.append(
                {
                    "_index": ES_INDEX,
                    "_source": {
                        "title": title,
                        "content": chunk,
                        "source": filename,
                        "chunk_id": i,
                    },
                }
            )
        print(f"  Loaded '{filename}' → {len(chunks)} chunks")
    return docs


def main():
    create_index()
    print("\nLoading documents...")
    docs = load_documents()
    helpers.bulk(es, docs)
    es.indices.refresh(index=ES_INDEX)
    count = es.count(index=ES_INDEX)["count"]
    print(f"\nDone. {count} chunks indexed into '{ES_INDEX}'.")


if __name__ == "__main__":
    main()
