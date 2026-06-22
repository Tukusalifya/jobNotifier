import os
import yaml
from typing import Dict, Optional, List
from config.settings import Settings

# Cached mappings dictionary
_mappings_cache: Optional[Dict] = None


def load_mappings() -> Dict:
    """Loads and caches category mappings from category_mappings.yaml."""
    global _mappings_cache
    if _mappings_cache is not None:
        return _mappings_cache
    
    if not os.path.exists(Settings.MAPPINGS_FILE_PATH):
        # Return empty mappings if file doesn't exist yet
        return {}
        
    with open(Settings.MAPPINGS_FILE_PATH, "r", encoding="utf-8") as f:
        try:
            data = yaml.safe_load(f)
            _mappings_cache = data.get("mappings", {})
        except Exception as e:
            print(f"Error loading category mappings: {e}")
            _mappings_cache = {}
            
    return _mappings_cache


def normalize_category(raw_category: Optional[str], source_site: str) -> str:
    """
    Normalizes a job's category.
    1. Looks up the raw_category in YAML mappings for the given source_site.
    """
        
    mappings = load_mappings()
    site_mappings = mappings.get(source_site, {})

    if raw_category in site_mappings:
        return site_mappings[raw_category]

    # TODO: Implement a fuzzy matching fallback

