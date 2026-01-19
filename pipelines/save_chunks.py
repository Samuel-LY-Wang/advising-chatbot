# from langchain.document_loaders import DirectoryLoader
from langchain_community.document_loaders import DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
# from langchain.embeddings import OpenAIEmbeddings
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
import openai 
from dotenv import load_dotenv
import os
import shutil
import nltk
import Util

import warnings
warnings.filterwarnings("ignore", message=r"libmagic is unavailable.*")


nltk.download('punkt_tab')
nltk.download('averaged_perceptron_tagger_eng')
# Load environment variables. Assumes that project contains .env file with API keys
load_dotenv()
#---- Set OpenAI API key 
# Change environment variable name from "OPENAI_API_KEY" to the name given in 
# your .env file.
openai.api_key = os.environ['OPENAI_API_KEY']

CUR_PATH = os.getcwd()
OUT_PATH = os.path.join(CUR_PATH, "data/chunks")
DATA_PATH = os.path.join(CUR_PATH, "data/raw")


def main():
    generate_data_store()


def generate_data_store(data_path=DATA_PATH, output_path=OUT_PATH):
    documents = load_documents(data_path)
    chunks = split_text(documents)
    save_text(chunks, output_path)

def save_text(chunks: list[Document], output_path=OUT_PATH):
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    for i, chunk in enumerate(chunks):
        file_path = os.path.join(output_path, f"chunk_{i}.txt")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(chunk.page_content)
    print(f"Saved {len(chunks)} chunks to {output_path}.")

def load_documents(data_path=DATA_PATH) -> list[Document]:
    loader = DirectoryLoader(data_path, glob="*.txt", recursive=True)
    ## loader = PyPDFLoader(DATA_PATH + "/the-hundred-page-language-models-book-hands-on-with-pytorch.pdf")
    documents = loader.load()
    print(f"Loaded {len(documents)} documents from {data_path}.")
    return documents


def split_text(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=100,
        length_function=len,
        add_start_index=True,
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Split {len(documents)} documents into {len(chunks)} chunks.")

    document = chunks[0]
    print(document.page_content)
    print(document.metadata)

    return chunks

if __name__ == "__main__":
    Util.time_execution(main) # ~167s (3 minutes)
