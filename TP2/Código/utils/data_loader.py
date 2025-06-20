import json
from utils.search_engine import SearchEngine


class DataManager:
    def __init__(self):
        self._db = None
        self._categorized_terms = None
        self._search_engine = None
        self.load_data()
    
    def load_data(self):
        try:
            with open('./dicts/out/merged_dict.json', 'r', encoding='utf-8') as file:
                self._db = json.load(file)
            
            with open('./dicts/out/categorized_medical_terms.json', 'r', encoding='utf-8') as file:
                self._categorized_terms = json.load(file)
            
            self._search_engine = SearchEngine(self._db)
            
        except FileNotFoundError as e:
            print(f"Erro a carregar os ficheiros: {e}")
            self._db = {}
            self._categorized_terms = {}
            self._search_engine = SearchEngine({})
        except json.JSONDecodeError as e:
            print(f"Erro ao analizar os ficheiros: {e}")
            self._db = {}
            self._categorized_terms = {}
            self._search_engine = SearchEngine({})
    
    @property
    def db(self):
        return self._db
    
    @property
    def categorized_terms(self):
        return self._categorized_terms
    
    @property
    def search_engine(self):
        return self._search_engine
    
    def save_data(self):
        try:
            with open('./dicts/out/merged_dict.json', 'w', encoding='utf-8') as f:
                json.dump(self._db, f, ensure_ascii=False, indent=4)
            
            with open('./dicts/out/categorized_medical_terms.json', 'w', encoding='utf-8') as f:
                json.dump(self._categorized_terms, f, ensure_ascii=False, indent=4)
            
            return True
        except Exception as e:
            print(f"Error saving data: {e}")
            return False
    
    def save_partial(self, db=True, categorized=True):
        """Save specific files based on parameters"""
        try:
            if db:
                with open('./dicts/out/merged_dict.json', 'w', encoding='utf-8') as f:
                    json.dump(self._db, f, ensure_ascii=False, indent=4)
            
            if categorized:
                with open('./dicts/out/categorized_medical_terms.json', 'w', encoding='utf-8') as f:
                    json.dump(self._categorized_terms, f, ensure_ascii=False, indent=4)
            
            return True
        except Exception as e:
            print(f"Error saving data: {e}")
            return False
    
    def reload_search_engine(self):
        self._search_engine = SearchEngine(self._db)


# Para acesso rápido ao DataManager
data_manager = DataManager()

# Exportações para acesso rápido
db = data_manager.db
categorized_terms = data_manager.categorized_terms
search_engine = data_manager.search_engine
save_data = data_manager.save_data
save_partial = data_manager.save_partial
reload_search_engine = data_manager.reload_search_engine
