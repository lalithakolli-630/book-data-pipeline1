
# Zepto Support Assistant

## Architecture

Ingestion → Embedding → Retrieval → Generation

1. Ingestion:
   The eight policy documents are stored in `docs/`.

2. Embedding:
   `SentenceTransformer` with `all-MiniLM-L6-v2` creates local embeddings.

3. Retrieval:
   ChromaDB stores the vectors. The `retrieve_and_answer` LangGraph node retrieves the top 3 chunks using cosine similarity.

4. Generation:
   `retrieve_and_answer` produces the grounded mock answer. `direct_answer` handles general questions.

## LangGraph

The graph contains:
- classify_intent
- retrieve_and_answer
- direct_answer

A conditional edge routes policy questions to retrieval and general questions to the direct-answer node.

## MOCK_LLM

The default `MOCK_LLM=1` mode is fully offline and deterministic.

Policy classification uses the required keyword heuristic.

The mock retrieval response uses:

"Based on the retrieved context: ..."

General questions return:

"I can only answer questions about Zepto policies right now."

## Example Calls

### Policy question

Query:

What is the delivery fee below INR 149?

Response:

The query is classified as `policy_question`, retrieves the relevant delivery-policy document, and returns a grounded response with its source ID.

### General question

Query:

What is the capital of India?

Response:

I can only answer questions about Zepto policies right now.

## Docker

Build:

docker build -t zepto-support .

Run:

docker run -p 7860:7860 zepto-support

The API exposes POST `/ask`.

## Prompt Template

The prompt follows:
Role → Context → Task → Format → Length

It also contains a negative constraint and a few-shot example.
