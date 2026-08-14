
import os
from typing import TypedDict

import chromadb
from sentence_transformers import SentenceTransformer
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, END
from fastapi import FastAPI

MOCK_LLM = os.getenv("MOCK_LLM", "1")

# -------------------------
# Embeddings + ChromaDB
# -------------------------

model = SentenceTransformer("all-MiniLM-L6-v2")

client = chromadb.Client()
collection = client.get_or_create_collection(
    name="zepto_policies",
    metadata={"hnsw:space": "cosine"}
)

docs_dir = os.path.join(os.path.dirname(__file__), "docs")

for filename in sorted(os.listdir(docs_dir)):
    if filename.endswith(".txt"):
        path = os.path.join(docs_dir, filename)

        with open(path, "r", encoding="utf-8") as f:
            text = f.read()

        embedding = model.encode(text).tolist()

        collection.upsert(
            ids=[filename],
            documents=[text],
            embeddings=[embedding]
        )

# -------------------------
# Structured output
# -------------------------

class Answer(BaseModel):
    answer: str
    sources: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0, le=1)

class Query(BaseModel):
    query: str

# -------------------------
# Graph state
# -------------------------

class State(TypedDict, total=False):
    query: str
    intent: str
    answer: str
    sources: list[str]
    confidence: float

# -------------------------
# Prompt template
# -------------------------

PROMPT_TEMPLATE = """
ROLE:
You are a Zepto customer-support assistant.

CONTEXT:
Answer only using the provided Zepto policy context.

TASK:
Answer the customer's question accurately.

FORMAT:
Return a structured answer with answer, sources, and confidence.

LENGTH:
Keep the answer concise.

NEGATIVE CONSTRAINT:
Do not answer using information not present in the provided context.

FEW-SHOT EXAMPLE:
Question: What is the standard delivery fee below INR 149?
Context: Orders below INR 149 incur a flat INR 25 delivery fee.
Answer: The standard delivery fee is INR 25 for orders below INR 149.
"""

# -------------------------
# Node 1
# -------------------------

KEYWORDS = [
    "delivery", "return", "refund", "membership",
    "tracking", "cancel", "gift card", "support hours"
]

def classify_intent(state: State):
    query = state["query"].lower()

    if any(keyword in query for keyword in KEYWORDS):
        intent = "policy_question"
    else:
        intent = "general_question"

    return {"intent": intent}

# -------------------------
# Node 2
# -------------------------

def retrieve_and_answer(state: State):

    query = state["query"]

    query_embedding = model.encode(query).tolist()

    result = collection.query(
        query_embeddings=[query_embedding],
        n_results=3
    )

    documents = result["documents"][0]
    ids = result["ids"][0]

    top_chunk = documents[0]
    snippet = top_chunk[:200]

    if MOCK_LLM == "1":
        answer = f"Based on the retrieved context: {snippet}"
    else:
        # Optional real LLM branch placeholder
        answer = f"Based on the retrieved context: {snippet}"

    return {
        "answer": answer,
        "sources": ids,
        "confidence": 1.0
    }

# -------------------------
# Node 3
# -------------------------

def direct_answer(state: State):

    return {
        "answer": "I can only answer questions about Zepto policies right now.",
        "sources": [],
        "confidence": 1.0
    }

# -------------------------
# Conditional routing
# -------------------------

def route(state: State):

    if state["intent"] == "policy_question":
        return "retrieve_and_answer"

    return "direct_answer"

# -------------------------
# LangGraph
# -------------------------

graph = StateGraph(State)

graph.add_node("classify_intent", classify_intent)
graph.add_node("retrieve_and_answer", retrieve_and_answer)
graph.add_node("direct_answer", direct_answer)

graph.set_entry_point("classify_intent")

graph.add_conditional_edges(
    "classify_intent",
    route,
    {
        "retrieve_and_answer": "retrieve_and_answer",
        "direct_answer": "direct_answer"
    }
)

graph.add_edge("retrieve_and_answer", END)
graph.add_edge("direct_answer", END)

app_graph = graph.compile()

# -------------------------
# FastAPI
# -------------------------

app = FastAPI(title="Zepto Support Assistant")

@app.post("/ask", response_model=Answer)
def ask(query: Query):

    result = app_graph.invoke({
        "query": query.query
    })

    return Answer(
        answer=result["answer"],
        sources=result.get("sources", []),
        confidence=result.get("confidence", 1.0)
    )
