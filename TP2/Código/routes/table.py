from flask import render_template, request, Blueprint
from utils.data_loader import db, categorized_terms, search_engine
from utils.filters import (filter_by_category, filter_with_descriptions, filter_without_descriptions,
                    filter_by_translation, filter_by_first_letter, filter_by_length,
                    filter_single_terms, filter_compound_terms, filter_by_substring)
from functools import partial
import re

table_bp = Blueprint('table', __name__)

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def highlight_matches(text, query, case_sensitive=False):
    """Destaca as correspondências de pesquisa no texto"""
    if not query or not text:
        return text
    
    escaped_query = re.escape(query)
    flags = 0 if case_sensitive else re.IGNORECASE
    pattern = re.compile(f'({escaped_query})', flags)
    highlighted = pattern.sub(r'<strong>\1</strong>', str(text))
    
    return highlighted

def get_available_languages():
    """Obtém todas as linguagens de tradução disponíveis"""
    languages = set()
    for data in db.values():
        for key in data.keys():
            if key.startswith("traducao_"):
                lang_code = key.replace("traducao_", "")
                languages.add(lang_code)
    return sorted(list(languages))

def get_available_letters():
    """Obtém todas as letras iniciais disponíveis"""
    letters = set()
    for term in db.keys():
        first_char = next((char.upper() for char in term if char.isalpha()), None)
        if first_char:
            letters.add(first_char)
    return sorted(list(letters))

def build_filters(request_args):
    """Constrói a lista de filtros baseada nos parâmetros da requisição"""
    filters = []
    
    # Filtros principais (visíveis na página)
    category = request_args.get('category')
    if category and category != 'all':
        filters.append(partial(filter_by_category, cat_dict=categorized_terms, cat=category))
    
    translation_lang = request_args.get('translation_lang')
    if translation_lang and translation_lang != 'none':
        filters.append(partial(filter_by_translation, language=translation_lang))
    
    # Filtros avançados (modal)
    
    # Filtro de descrições (agora nos filtros avançados)
    if request_args.get('has_description') == 'true':
        filters.append(filter_with_descriptions)
    elif request_args.get('no_description') == 'true':
        filters.append(filter_without_descriptions)
    
    # Filtro de letra inicial
    first_letter = request_args.get('first_letter')
    if first_letter and first_letter != 'all':
        filters.append(partial(filter_by_first_letter, letter=first_letter))
    
    # Filtro de comprimento
    min_length = request_args.get('min_length', type=int)
    max_length = request_args.get('max_length', type=int)
    if min_length is not None or max_length is not None:
        min_len = min_length if min_length is not None else 0
        max_len = max_length if max_length is not None else float('inf')
        if min_len > 0 or max_len < float('inf'):
            filters.append(partial(filter_by_length, min_length=min_len, max_length=max_len))
    
    # Filtro de tipo de termo
    term_type = request_args.get('term_type')
    if term_type == 'single':
        filters.append(filter_single_terms)
    elif term_type == 'compound':
        filters.append(filter_compound_terms)
    
    return filters

def apply_highlighting(filtered_db, query, case_sensitive=False):
    """Aplica destaque às correspondências de pesquisa"""
    if not query:
        return
        
    for conceito, info in filtered_db.items():
        info['highlighted_name'] = highlight_matches(conceito, query, case_sensitive=case_sensitive)
        
        if info.get('desc'):
            highlighted_desc = []
            for desc in info['desc']:
                highlighted_desc.append(highlight_matches(desc, query, case_sensitive=case_sensitive))
            info['highlighted_desc'] = highlighted_desc

# =============================================================================
# ROUTES
# =============================================================================

@table_bp.route('/tabela')
def tabela():
    """Página principal da tabela de conceitos"""
    # Parâmetros da requisição
    query = request.args.get('search', '')
    case_sensitive = request.args.get('case_sensitive') == 'true'
    is_regex = request.args.get('is_regex') == 'true'
    
    # Construir todos os filtros (principais + avançados)
    all_filters = build_filters(request.args)
    
    # Aplicar pesquisa e filtros usando o search_engine
    if query or all_filters:
        filtered_db = search_engine.search(
            query if query else "", 
            case_sensitive=case_sensitive,
            is_regex=is_regex,
            filters=all_filters if all_filters else None
        )
        
        # Aplicar destaque se houver consulta (não aplicar destaque em regex para evitar problemas)
        if query and not is_regex:
            apply_highlighting(filtered_db, query, case_sensitive=case_sensitive)
    else:
        # Se não há query nem filtros, mostrar tudo
        filtered_db = db
    
    # Dados para o template
    template_data = {
        'title': 'Tabela de Conceitos',
        'db': filtered_db,
        'categories': list(categorized_terms.keys()),
        'available_languages': get_available_languages(),
        'available_letters': get_available_letters(),
        'search_query': query,
        
        # Parâmetros principais atuais
        'current_search': query,
        'current_category': request.args.get('category', ''),
        'current_translation_lang': request.args.get('translation_lang', ''),
        
        # Opções de pesquisa
        'current_case_sensitive': request.args.get('case_sensitive', ''),
        'current_is_regex': request.args.get('is_regex', ''),
        
        # Parâmetros de filtros avançados atuais
        'current_has_description': request.args.get('has_description', ''),
        'current_no_description': request.args.get('no_description', ''),
        'current_first_letter': request.args.get('first_letter', ''),
        'current_min_length': request.args.get('min_length', ''),
        'current_max_length': request.args.get('max_length', ''),
        'current_term_type': request.args.get('term_type', ''),
    }
    
    return render_template('table.html', **template_data)