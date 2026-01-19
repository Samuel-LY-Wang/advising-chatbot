import argparse
import os
from dotenv import load_dotenv
# from dataclasses import dataclass
from langchain_chroma import Chroma
from langchain_community.chat_models import ChatOllama
from langchain_ollama import OllamaEmbeddings
from langchain_core.prompts import PromptTemplate
from pathlib import Path

CUR_PATH = Path.cwd()
CHROMA_PATH = os.path.join(CUR_PATH, "data/chroma_db")

PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}
"""

def prepare_DB():
    load_dotenv()
    embedding_function = OllamaEmbeddings(model="nomic-embed-text", base_url="http://localhost:11434")
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)
    return db

def search_DB(db, query_text: str, k: int = 3):
    results = db.similarity_search_with_relevance_scores(query_text, k=k)
    return results

def answer_query(query_text: str):
    db = prepare_DB()

    # Search the DB.
    results = search_DB(db, query_text, k=3)
    print(results)
    if len(results) == 0 or results[0][1] < 0.5:
        return "Unable to find matching results."

    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    prompt_template = prompt_template = PromptTemplate(
        template=PROMPT_TEMPLATE,
        input_variables=["length", "topic", "audience"]
    )
    prompt = prompt_template.format(context=context_text, question=query_text)

    llm = ChatOllama(model="mistral")
    
    response_text = llm.invoke(prompt)

    sources = [doc.metadata.get("source", None) for doc, _score in results]
    formatted_response = f"Response: {response_text}\nSources: {sources}"
    return formatted_response


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
    print(prompt)

    llm = ChatOllama(model="ollama-mistral-7b")
    
    response_text = llm.invoke(prompt)

    sources = [doc.metadata.get("source", None) for doc, _score in results]
    formatted_response = f"Response: {response_text}\nSources: {sources}"
    print(formatted_response)


if __name__ == "__main__":
    main()
