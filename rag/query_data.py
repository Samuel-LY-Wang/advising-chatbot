import argparse
import os, sys, time
from dotenv import load_dotenv
# from dataclasses import dataclass
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_core.prompts import PromptTemplate
from pathlib import Path
from sentence_transformers import CrossEncoder
try:
    from rag import reverse_map
except ModuleNotFoundError:
    import reverse_map

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from open_config import load_config
from pipelines import Util
config = load_config()

CUR_PATH = config["cwd"]
CHROMA_PATH = os.path.join(CUR_PATH, config["db_path"])

PROMPT_TEMPLATE = """
Answer the question based only on the provided context and your own reasoning. If the question cannot be answered from the given context combined with your reasoning, return an empty string as your response (do not include the quotation marks).
Always use all available information to provide the best answer. Do not make up information that is not in the context. If you use information from the provided context, please cite the source using [number] notation, where the number corresponds to the source's position in the provided context. For example, if you use information from the first and third sources in the context, you would cite them as [1] and [3] respectively in your answer.
The provided context is delimited by triple dashes (---). Each source in the context is separated by these dashes. The position of each source in the context corresponds to its citation number.
Please format the output as valid markdown.
Below is the context provided:

{context}

---

Answer the question based on the above context: {question}
If the answer does not appear in the context
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

def answer_query(query_text: str, debug=False):
    db = Util.time_execution(prepare_DB, out="DB preparation time: ")

    # Search the DB.
    if debug:
        results = Util.time_execution(lambda: search_DB(db, query_text, k=config["chunks_to_retrieve"]), out="DB search time: ")
        print(f"Initial search results (pre-rerank): {results}")
    else:
        results = search_DB(db, query_text, k=config["chunks_to_retrieve"])

    if debug:
        results = Util.time_execution(lambda: re_ranker(query_text, results, num_to_return=config["chunks_to_keep"]), out="Rerank time: ")
        print(f"Reranked results: {results}")
    else:
        results = re_ranker(query_text, results, num_to_return=config["chunks_to_keep"])
    # print(results)

    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    if debug:
        print(f"Context text for LLM:\n{context_text}")
        with open("test/context.txt", "w", encoding="utf-8") as f:
            f.write(context_text)
    # with open("test/context.txt", "w", encoding="utf-8") as f:
    #     f.write(context_text)
    prompt_template = prompt_template = PromptTemplate(
        template=PROMPT_TEMPLATE,
        input_variables=["length", "topic", "audience"]
    )
    prompt = prompt_template.format(context=context_text, question=query_text)

    llm = ChatOllama(model=config["chat_model"])
    
    response_text = Util.time_execution(lambda: llm.invoke(prompt).content.strip(), out="LLM response time: ")

    if (response_text == ""):
        return "I couldn't find any information on that", []

    sources = [reverse_map.get_url_from_chunk(doc) for doc, _score in results]
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

    res, sources = answer_query(query_text)
    print(f"Answer: {res}")
    print(f"Sources: {sources}")


if __name__ == "__main__":
    main()
