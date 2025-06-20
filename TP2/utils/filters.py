import re
import unicodedata


# Filtra apenas conceitos com descrição em português
def filter_with_descriptions(dictionary):
    return {
        term: data for term, data in dictionary.items()
        if data.get("desc", None)
    }


# Filtra apenas conceitos sem descrição em português - útil para sugerir termos que precisem de melhorias
def filter_without_descriptions(dictionary):
    return {
        term: data for term, data in dictionary.items()
        if not data.get("desc", None)
    }


# Filtra conceitos por disponibilidade de uma tradução
def filter_by_translation(dictionary, language):
    translation_key = f"traducao_{language}"
    return {
        term: data for term, data in dictionary.items()
        if data.get(translation_key, None)
    }


# Filtra conceitos por letra inicial
def filter_by_first_letter(dictionary, letter):
    def normalize_char(char):
        return unicodedata.normalize('NFD', char).encode('ascii', 'ignore').decode('ascii').lower()
    
    def get_first_alpha_char(term):
        for char in term:
            if char.isalpha():
                return normalize_char(char)
        return None
    
    target_letter = normalize_char(letter)
    
    return {
        term: data for term, data in dictionary.items()
        if get_first_alpha_char(term) == target_letter
    }


# Filtra conceitos por categoria gramatical
def filter_by_lexical_category(dictionary, category):
    def normalize_category(cat):
        cat = cat.lower().strip()
        if cat == "s.f.":
            return "n f"
        elif cat == "s.m.":
            return "n m"
        return cat
    
    normalized_target = normalize_category(category)
    
    return {
        term: data for term, data in dictionary.items()
        if normalize_category(data.get("lex_cat", "")) == normalized_target
    }


# Filtra conceitos por comprimento do termo
def filter_by_length(dictionary, min_length=0, max_length=float("inf")):
    return {
        term: data for term, data in dictionary.items()
        if min_length <= len(term) <= max_length
    }


# Filtra conceitos cujo termo é apenas uma palavra
def filter_single_terms(dictionary):
    return {
        term: data for term, data in dictionary.items()
        if " " not in term and "-" not in term and "/" not in term
    }


# Filtra conceitos cujo termo tem mais que uma palavra (i.e espaço, hífen ou slash)
def filter_compound_terms(dictionary):
    return {
        term: data for term, data in dictionary.items()
        if " " in term or "-" in term or "/" in term
    }


# Filtra conceitos cujo termo contém uma susbtring específica
def filter_by_substring(dictionary, substring, case_sensitive=False):
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


# Filtra conceitos cujo term é capturado por uma regex específica
def filter_by_regex(dictionary, pattern, case_sensitive=False):
    try:
        if case_sensitive:
            regex = re.compile(pattern)
        else:
            regex = re.compile(pattern, re.IGNORECASE)
        
        return {
            term: data for term, data in dictionary.items()
            if regex.search(term)
        }
    except re.error:  # Caso o pattern de regex seja inválido
        return {}


# Filtra conceitos pela categoria em que se enquadram
def filter_by_category(dic, cat_dict, cat):
    return {
        term: data for term, data in dic.items()
        if term in set(cat_dict[cat]["termos"])
    }


# Permite o encadeamento de filtros
def combine_filters(dictionary, *filter_functions):
    result = dictionary
    for filter_func in filter_functions:
        result = filter_func(result)
    return result
