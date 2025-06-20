import re
import json
import os
from functools import partial

from utils.filters import combine_filters


class SearchEngine:
    def __init__(self, data_source=None):
        if data_source is None:
            self.data_source = self._load_default_data_source()
        else:
            self.data_source = data_source
    
    def _load_default_data_source(self):
        try:
            json_path = os.path.join(os.path.dirname(__file__), "..", "dicts", "out", "merged_dict.json")
            with open(json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def search(self, query, case_sensitive=False, is_regex=False, filters=None):
        if not self.data_source:
            return {}
        
        # Start with the full data source
        results = self.data_source.copy()
        
        # Apply the search query
        if query:
            if is_regex:
                results = self._regex_search(results, query, case_sensitive)
            else:
                results = self._substring_search(results, query, case_sensitive)
        
        # Apply additional filters if provided
        if filters:
            results = combine_filters(results, *filters)
        
        return results
    
    def _substring_search(self, dictionary, substring, case_sensitive=False):
        if case_sensitive:
            return {
                term: data for term, data in dictionary.items()
                if substring in term
            }
        else:
            substring_lower = substring.lower()
            return {
                term: data for term, data in dictionary.items()
                if substring_lower in term.lower()
            }
    
    def _regex_search(self, dictionary, pattern, case_sensitive=False):
        try:
            if case_sensitive:
                regex = re.compile(pattern)
            else:
                regex = re.compile(pattern, re.IGNORECASE)
            
            return {
                term: data for term, data in dictionary.items()
                if regex.search(term)
            }
        except re.error:  # Invalid regex pattern
            return {}


# Convenience function for quick searches without instantiating the class
def search(query, data_source=None, case_sensitive=False, is_regex=False, filters=None):
    engine = SearchEngine(data_source)
    return engine.search(query, case_sensitive, is_regex, filters)


if __name__ == "__main__":
    print("Testing SearchEngine...")
    
    engine = SearchEngine()
    print(f"Loaded {len(engine.data_source)} entries from default source")
    
    cat_dict_path = os.path.join(os.path.dirname(__file__), "dicts", "out", "categorized_medical_terms.json")
    with open(cat_dict_path, 'r', encoding='utf-8') as f:
        cat_dict = json.load(f)

    results = engine.search("tosse", case_sensitive=False)
    print(f"Substring search for 'tosse': {len(results)} results")

    regex_results = engine.search(r"^comp", is_regex=True, case_sensitive=False)
    print(f"Regex search for terms starting with 'comp': {len(regex_results)} results")

    quick_results = search("bronq")
    print(f"Quick search for 'bronq': {len(quick_results)} results")
    

    from filters import (filter_with_descriptions, filter_single_terms, 
                        filter_by_translation, filter_by_first_letter, filter_by_category)
    filtered_results = engine.search("", filters=[
        filter_with_descriptions, 
        filter_single_terms,
        partial(filter_by_translation, language="en"),
        partial(filter_by_first_letter, letter="a")
    ])
    print(f"Search with filters (has descriptions + single terms + english translation + starts with 'a'): {len(filtered_results)} results")
    
    category_results = engine.search("", filters=[
        partial(filter_by_category, cat_dict=cat_dict, cat="Anatomia"),
        partial(filter_by_first_letter, letter="a")
    ])
    print(f"Search with Anatomia category + starts with 'a': {len(category_results)} results")
    
    case_results = engine.search("BRONQ", case_sensitive=True)
    print(f"Case-sensitive search for 'BRONQ': {len(case_results)} results")
    
    print("SearchEngine tests completed!")
