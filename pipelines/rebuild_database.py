try:
    from pipelines.bulk_sources_crawler import fetch_all
    from pipelines.save_chunks import generate_data_store
    from pipelines.save_chunks_to_db import load_chunks, save_to_chroma
    from pipelines.Util import time_execution
except ModuleNotFoundError:
    from bulk_sources_crawler import fetch_all
    from save_chunks import generate_data_store
    from save_chunks_to_db import load_chunks, save_to_chroma
    from Util import time_execution

def main():
    time_execution(fetch_all, out="Webscraping time: ")
    time_execution(generate_data_store, out="Chunk generation time: ")
    chunks = time_execution(load_chunks, out="Chunk loading time: ")
    time_execution(lambda: save_to_chroma(chunks), out="DB saving time: ")

if __name__ == "__main__":
    main()