import json
import csv
from pathlib import Path
from functools import lru_cache
from typing import List, Dict, Any, Union
import logging

import yaml

# Configure logging
logger = logging.getLogger(__name__)

class ReferenceDataLoader:
    def __init__(self):
        # Draft, using external files, which is using on local host only, and afeter deployment, will use database.
        self.search_paths = [
            Path(__file__).parent / "docs" / "docs/docs - PronaFlow React&FastAPI" / "07-References"
        ]
    
    def _get_file_path(self, filename: str) -> Union[Path, None]:
        for path in self.search_paths:
            full_path = path / filename
            if full_path.exists():
                return full_path
        logger.error(f"Reference fule {filename} not foun in search paths.")
        return None
    
    @lru_cache(maxsize=32) # Catching files, to avoid reloading
    def load(self, filename: str) -> Union[List[Dict], Dict, None]:
        file_path = self._get_file_path(filename)
        if not file_path:
            return None

        try:
            ext = file_path.suffix.lower()
            with open(file_path, 'r', encoding='utf-8') as f:
                if ext == '.json':
                    return json.load(f)
                elif ext == '.csv':
                    return list(csv.DictReader(f))
                elif ext in ['.yaml', '.yml']: return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Error reading {filename}: {e}")
            return None
        return None
    
    # Wrapper functions sử dụng cached load
    def get_project_priorities(self) -> List[Dict]:
        return self.load("project-priorities.json") or []

    def get_project_statuses(self) -> List[Dict]:
        return self.load("project-statuses.json") or []

reference_loader = ReferenceDataLoader()
