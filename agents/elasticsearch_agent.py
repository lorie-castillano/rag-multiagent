import json
import os
from dotenv import load_dotenv
from elasticsearch import Elasticsearch
from google import genai
from mcp.server.fastmcp import FastMCP

load_dotenv()

ES_HOST = "http://localhost:9200"
ES_INDEX = "rag_documents"
TOP_K = 7
MIN_SCORE = 0.6

mcp = FastMCP("elasticsearch-specialist")
es = Elasticsearch(ES_HOST)
gemini = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
EMBED_MODEL = "models/gemini-embedding-001"


@mcp.tool()
def retrieve_documents(query: str) -> str:
    """Search the RAG knowledge base and return the top relevant document chunks."""
    result = gemini.models.embed_content(model=EMBED_MODEL, contents=query)
    query_vector = result.embeddings[0].values

    response = es.search(
        index=ES_INDEX,
        body={
            "knn": {
                "field": "embedding",
                "query_vector": query_vector,
                "k": TOP_K,
                "num_candidates": 50,
            },
            "_source": ["title", "content", "source", "chunk_id"],
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
            "chunk_id": hit["_source"].get("chunk_id", 0),
        }
        for i, hit in enumerate(hits)
    ]

    return json.dumps({"results": results}, indent=2)


if __name__ == "__main__":
    mcp.run(transport="stdio")
