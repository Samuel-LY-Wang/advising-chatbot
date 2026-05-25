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

import logging

import logging
logging.basicConfig(level=logging.INFO, filename="logs/rebuild_db.log", filemode="w", format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def main(verbose=False, batch_size=100):
    if verbose:
        logger.info("Starting database rebuild...")
        time_execution(fetch_all, out="Webscraping time: ", logger=logger)
        time_execution(generate_data_store, out="Chunk generation time: ", logger=logger)
        chunks = time_execution(load_chunks, out="Chunk loading time: ", logger=logger)
        time_execution(lambda: save_to_chroma(chunks, batch_size=batch_size), out="DB saving time: ", logger=logger)
    else:
        fetch_all()
        generate_data_store()
        chunks = load_chunks()
        save_to_chroma(chunks, batch_size=batch_size)

if __name__ == "__main__":
    main(verbose=True, batch_size=100)