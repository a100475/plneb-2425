from utils.filters import filter_with_descriptions, filter_compound_terms
import unicodedata


# Obtém todas as linguagens de tradução disponíveis no dicionário
def get_available_translations(dictionary): 
    languages = set()
    for data in dictionary.values():
        for key in data.keys():
            if key.startswith("traducao_"):
                lang_code = key.replace("traducao_", "")
                languages.add(lang_code)
    return languages


# Obtém todas as classes gramaticais presentes no dicionário
def get_available_lexical_categories(dictionary):
    categories = set()
    for data in dictionary.values():
        if data.get("lex_cat"):
            categories.add(data["lex_cat"])
    return categories


# Obtém o número de termos que começam por cada letra do alfabeto
def get_alphabet_coverage(dictionary):
    def normalize_char(char):
        return unicodedata.normalize('NFD', char).encode('ascii', 'ignore').decode('ascii').lower()
    
    def get_first_alpha_char(term):
        """Get the first alphabetical character from a term, ignoring punctuation"""
        for char in term:
            if char.isalpha():
                return normalize_char(char)
        return None
    
    alphabet_count = {}
    for term in dictionary.keys():
        first_letter = get_first_alpha_char(term)
        if first_letter:
            first_letter = first_letter.upper()
            alphabet_count[first_letter] = alphabet_count.get(first_letter, 0) + 1
    
    return dict(sorted(alphabet_count.items(), key=lambda d: d[1], reverse=True))


# Filtra termos que têm traduções disponíveis
def filter_with_translations(dictionary):
    with_translations = {}
    for term, data in dictionary.items():
        for key in data.keys():
            if key.startswith("traducao_"):
                with_translations[term] = data
                break
    return with_translations


# Filtra termos que têm sinônimos disponíveis
def filter_with_synonyms(dictionary):
    with_synonyms = {}
    for term, data in dictionary.items():
        if data.get("sinonimos") and len(data["sinonimos"]) > 0:
            with_synonyms[term] = data
    return with_synonyms


# Fornece uma lista completa de estatísticas sobre o dicionário
def get_statistics(dictionary):
    total_entries = len(dictionary)
    with_descriptions = len(filter_with_descriptions(dictionary))
    compound_terms_count = len(filter_compound_terms(dictionary))
    with_translations_count = len(filter_with_translations(dictionary))
    with_synonyms_count = len(filter_with_synonyms(dictionary))

    stats = {
        "total_entries": total_entries,
        "entries_with_descriptions": with_descriptions,
        "entries_without_descriptions": total_entries - with_descriptions,
        "compound_terms": compound_terms_count,
        "single_terms": total_entries - compound_terms_count,
        "entries_with_translations": with_translations_count,
        "entries_without_translations": total_entries - with_translations_count,
        "entries_with_synonyms": with_synonyms_count,
        "entries_without_synonyms": total_entries - with_synonyms_count,
        "available_translations": sorted(list(get_available_translations(dictionary))),
        "available_categories": sorted(list(get_available_lexical_categories(dictionary))),
        "alphabet_coverage": get_alphabet_coverage(dictionary)
    }

    if total_entries > 0:
        stats['description_percentage'] = round((with_descriptions / total_entries) * 100, 1)
        stats['no_description_percentage'] = round(((total_entries - with_descriptions) / total_entries) * 100, 1)
        stats['compound_percentage'] = round((compound_terms_count / total_entries) * 100, 1)
        stats['single_percentage'] = round(((total_entries - compound_terms_count) / total_entries) * 100, 1)
        stats['translation_percentage'] = round((with_translations_count / total_entries) * 100, 1)
        stats['no_translation_percentage'] = round(((total_entries - with_translations_count) / total_entries) * 100, 1)
        stats['synonym_percentage'] = round((with_synonyms_count / total_entries) * 100, 1)
        stats['no_synonym_percentage'] = round(((total_entries - with_synonyms_count) / total_entries) * 100, 1)
    else:
        for key in ['description_percentage', 'no_description_percentage', 'compound_percentage', 
                   'single_percentage', 'translation_percentage', 'no_translation_percentage',
                   'synonym_percentage', 'no_synonym_percentage']:
            stats[key] = 0.0
    
    return stats


if __name__ == "__main__":
    from search_engine import SearchEngine
    
    print("A testar estatísticas com dados do SearchEngine...")
    engine = SearchEngine()
    test_data = engine.data_source
    
    if not test_data:
        print("Nenhum dado carregado do SearchEngine")
        exit()
    
    print(f"A testar com {len(test_data)} entradas")
    
    languages = get_available_translations(test_data)
    print(f"Traduções disponíveis: {languages}")
    
    categories = get_available_lexical_categories(test_data)
    print(f"Classes lexicais: {categories}")
    
    with_translations = filter_with_translations(test_data)
    print(f"Entradas com traduções: {len(with_translations)}")
    
    with_synonyms = filter_with_synonyms(test_data)
    print(f"Entradas com sinónimos: {len(with_synonyms)}")
    
    alphabet = get_alphabet_coverage(test_data)
    print(f"Cobertura alfabética: {alphabet}")
    
    print("\nEstatísticas completas:")
    stats = get_statistics(test_data)
    for key, value in stats.items():
        if key == "alphabet_coverage":
            print(f"  {key}: {len(value)} letras cobertas")
        elif key.endswith("_percentage"):
            print(f"  {key}: {value}%")
        else:
            print(f"  {key}: {value}")
    
    print("Testes das estatísticas concluídos!")
