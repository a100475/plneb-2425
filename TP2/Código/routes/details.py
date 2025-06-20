from flask import render_template, Blueprint
from utils.data_loader import db, categorized_terms
import re

details_bp = Blueprint('details', __name__)

# =============================================================================
# CONSTANTS AND MAPPINGS
# =============================================================================

# Mapeamento de categorias lexicais para strings amigáveis
LEX_CAT_MAPPING = {
    'adj': 'Adjetivo',
    'n': 'Nome',
    'n f': 'Nome feminino',
    'n f pl': 'Nome feminino plural',
    'n m': 'Nome masculino',
    'n m pl': 'Nome masculino plural',
    'n m, f': 'Nome masculino/feminino',
    'v intr': 'Verbo intransitivo',
    'v tr': 'Verbo transitivo'
}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_friendly_lex_cat(lex_cat):
    """Converte categoria lexical para formato amigável"""
    if not lex_cat:
        return 'N/A'
    return LEX_CAT_MAPPING.get(lex_cat, lex_cat)

def link_desc(text, db_keys, current_concept=None):
    """Função auxiliar para adicionar links às descrições"""
    if not text:
        return text
    
    entradas = {k.lower(): k for k in db_keys if k != current_concept}
    
    sorted_keys = sorted(entradas.keys(), key=lambda x: (-len(x)))
    
    result_text = text
    processed_ranges = []
    
    for key in sorted_keys:
        actual_key = entradas[key]
        pattern = r'\b' + re.escape(key.lower()) + r'\b'
        
        for match in re.finditer(pattern, result_text.lower()):
            start, end = match.span()
            
            if any(start < existing_end and end > existing_start 
                   for existing_start, existing_end in processed_ranges):
                continue
            
            original_text = result_text[start:end]

            link = f'<a href="/detalhes/{actual_key}" class="concept-link text-primary text-decoration-underline" title="Ver detalhes de {key}">{original_text}</a>'
            
            new_end = start + len(link)
            processed_ranges.append((start, new_end))
            
            result_text = result_text[:start] + link + result_text[end:]
            
            offset = len(link) - len(original_text)
            processed_ranges = [(s + offset if s > start else s, 
                               e + offset if e > start else e) 
                              for s, e in processed_ranges[:-1]] + [(start, new_end)]
            break
    
    return result_text

# =============================================================================
# ROUTES
# =============================================================================

@details_bp.route('/detalhes/<string:conceito>')
def detalhes(conceito):
    """Página de Detalhes do Conceito"""
    if conceito not in db:
        return render_template('error.html', message='Conceito não encontrado'), 404
    
    info = db.get(conceito, {})

    for cat in categorized_terms:
        if conceito in set(categorized_terms[cat]["termos"]):
            info['categoria'] = cat
            break
    
    # Adicionar versão amigável da categoria lexical
    info['friendly_lex_cat'] = get_friendly_lex_cat(info.get('lex_cat'))

    if info.get('desc'):
        linked_descriptions = []
        has_links = False
        
        for desc in info['desc']:
            linked_desc = link_desc(desc, db.keys(), conceito)
            linked_descriptions.append(linked_desc)
            
            if '<a href=' in linked_desc:
                has_links = True
        
        if has_links:
            info['linked_desc'] = linked_descriptions           
    
    if info.get('abonacoes'):
        res = link_desc(info['abonacoes'], db.keys(), conceito)

        if '<a href=' in res:
            info['linked_abonacoes'] = res
    
    if info.get('informacao_enciclopedia'):
        res = link_desc(info['informacao_enciclopedia'], db.keys(), conceito)

        if '<a href=' in res:
            info['linked_informacao_enciclopedia'] = res

    return render_template('details.html', 
                           conceito=conceito, 
                           info=info, 
                           db=db, 
                           title='Detalhes do Conceito')