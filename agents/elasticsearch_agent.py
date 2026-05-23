import json
from elasticsearch import Elasticsearch
from mcp.server.fastmcp import FastMCP

ES_HOST = "http://localhost:9200"
ES_INDEX = "rag_documents"
TOP_K = 7
MIN_SCORE = 1.5

mcp = FastMCP("elasticsearch-specialist")
es = Elasticsearch(ES_HOST)


@mcp.tool()
def retrieve_documents(query: str) -> str:
    """Search the RAG knowledge base and return the top relevant document chunks."""
    response = es.search(
        index=ES_INDEX,
        body={
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["title^3", "content"],
                    "type": "cross_fields",
                }
            },
            "size": TOP_K,
            "_source": ["title", "content", "source"],
        },
    )

    hits = [h for h in response["hits"]["hits"] if h["_score"] >= MIN_SCORE]
    if not hits:
        return json.dumps({"results": [], "message": "No relevant documents found."})


    results = [
        {
            "rank": i + 1,
            "score": round(hit["_score"], 4),
            "title": hit["_source"].get("title", "Untitled"),
            "content": hit["_source"].get("content", ""),
            "source": hit["_source"].get("source", ""),
        }
        for i, hit in enumerate(hits)
    ]

    return json.dumps({"results": results}, indent=2)


if __name__ == "__main__":
    mcp.run(transport="stdio")
