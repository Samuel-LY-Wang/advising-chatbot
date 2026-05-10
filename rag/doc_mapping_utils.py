import json
import os
from pathlib import Path
CUR_PATH = Path.cwd()

def load_json(mapping_path):
    try:
        return json.load(open(mapping_path, "r", encoding="utf-8"))
    except FileNotFoundError:
        print(f"File not found: {mapping_path}")
        return {}
    except json.JSONDecodeError:
        print(f"Invalid JSON in file: {mapping_path}")
        return {}

doc_mapping = load_json(os.path.join(CUR_PATH, "data/mappings/doc-chunk-mappings.json"))
url_mapping = load_json(os.path.join(CUR_PATH, "data/mappings/file-url-mappings.json"))

def get_source_url(source_filename, mapping=doc_mapping):
    # mapping is now complete index
    return url_mapping.get(mapping.get(str(source_filename), None), None)