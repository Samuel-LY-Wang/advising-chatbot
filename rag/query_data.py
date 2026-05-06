import argparse
import os, sys
from dotenv import load_dotenv
# from dataclasses import dataclass
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_core.prompts import PromptTemplate
from pathlib import Path
from sentence_transformers import CrossEncoder

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from open_config import load_config
config = load_config()

CUR_PATH = Path.cwd()
CHROMA_PATH = os.path.join(CUR_PATH, config["db_path"])

PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}
"""

rerank_model = config["rerank_model"]
reranker = CrossEncoder(rerank_model)

def prepare_DB():
    load_dotenv()
    embedding_function = OllamaEmbeddings(model=config["embed_model"], base_url="http://localhost:11434")
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)
    return db

def search_DB(db: Chroma, query_text: str, k: int = 3):
    results = db.similarity_search_with_relevance_scores(query_text, k=k)
    return results

def answer_query(query_text: str):
    db = prepare_DB()

    # Search the DB.
    results = search_DB(db, query_text, k=config["chunks_to_retrieve"])
    # print(results)
    if len(results) == 0:
        return "Unable to find matching results.", None
    reranked_results = re_ranker(query_text, results, num_to_return=config["chunks_to_keep"])

    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in reranked_results])
    prompt_template = prompt_template = PromptTemplate(
        template=PROMPT_TEMPLATE,
        input_variables=["length", "topic", "audience"]
    )
    prompt = prompt_template.format(context=context_text, question=query_text)

    llm = ChatOllama(model=config["chat_model"])
    
    response_text = llm.invoke(prompt).content

    sources = [doc.metadata.get("source", None) for doc, _score in reranked_results]
    formatted_response = f"{response_text}".strip()
    return formatted_response, sources

def re_ranker(query_text: str, results: list[tuple], num_to_return: int=5):
    # using bbjson/bge-reranker-base to rerank results (https://ollama.com/bbjson/bge-reranker-base) and return the top num
    if len(results) == 0:
        return []
    rerank_inputs = [(query_text, doc.page_content) for doc, _ in results]
    rerank_scores = reranker.predict(rerank_inputs)
    reranked_results = sorted(zip(results, rerank_scores), key=lambda x: x[1], reverse=True)
    top_results = [result for result, score in reranked_results[:num_to_return]]
    return top_results


def main():
    # Create CLI.
    parser = argparse.ArgumentParser()
    parser.add_argument("query_text", type=str, help="The query text.")
    args = parser.parse_args()
    query_text = args.query_text

    db = prepare_DB()

    # Search the DB.
    results = search_DB(db, query_text, k=3)
    if len(results) == 0 or results[0][1] < 0.7:
        print("Unable to find matching results.")
        return

    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    prompt_template = prompt_template = PromptTemplate(
        template=PROMPT_TEMPLATE,
        input_variables=["length", "topic", "audience"]
    )
    prompt = prompt_template.format(context=context_text, question=query_text)
    # print(prompt)

    llm = ChatOllama(model=config["chat_model"])
    
    response_text = llm.invoke(prompt).content.strip()

    sources = [doc.metadata.get("source", None) for doc, _score in results]
    formatted_response = f"Response: {response_text}\nSources: {sources}"
    print(formatted_response)


if __name__ == "__main__":
    main()
