from flask import render_template, request, redirect, flash, Blueprint, session
from utils.data_loader import db, categorized_terms, save_data

edit_bp = Blueprint('edit', __name__)


# Editar um conceito
@edit_bp.route('/editar/<string:conceito>', methods=['GET'])
def editar_conceito(conceito):
    if conceito not in db:
        return render_template('error.html', message='Conceito não encontrado'), 404

    session.pop('_flashes', None)
    
    info = db[conceito]
    return render_template('editar.html', conceito=conceito, info=info)


@edit_bp.route('/editar/<string:conceito>', methods=['POST'])
def guardar_edicao(conceito):
    if conceito not in db:
        return render_template('error.html', message='Conceito não encontrado'), 404

    # Nome do termo atualizado
    new_name = request.form.get('termo', conceito).strip()
    
    entry = {}

    # Categoria Lexical
    if request.form.get('lex_cat'):
        entry['lex_cat'] = request.form.get('lex_cat')

    # Descrição em Português
    if request.form.get('desc'):
        entry['desc'] = [line.strip() for line in request.form.get('desc').split('\n') if line.strip()]
    
    # Traduções
    translation_mappings = {
        'ca': 'lex_cat_ca',
        'es': 'lex_cat_es', 
        'en': 'lex_cat_en',
        'fr': 'lex_cat_fr',
        'ar': 'lex_cat_ar',
        'nl': 'lex_cat_nl',
        'oc': 'lex_cat_oc',
        'eu': 'lex_cat_eu',
        'gl': 'lex_cat_gl'
    }
    
    for lang, lex_field in translation_mappings.items():
        term_field = f'traducao_{lang}_term'
        
        term_value = request.form.get(term_field, '').strip()
        lex_value = request.form.get(lex_field, '').strip()
        
        if term_value:
            translation_obj = {
                "term": term_value,
                "lex_cat": lex_value if lex_value else None
            }
            entry[f'traducao_{lang}'] = [translation_obj]

    # Descrição em Catalão
    desc_ca_type = request.form.get('desc_ca_type', '').strip()
    desc_ca_text = request.form.get('desc_ca_text', '').strip()
    
    if desc_ca_text and not desc_ca_type:
        flash('Erro: Se fornecer uma descrição em Catalão, deve também fornecer o tipo.', 'error')
        return render_template('editar.html', conceito=conceito, info=db[conceito])
    
    if desc_ca_type and not desc_ca_text:
        flash('Erro: Se fornecer um tipo para a descrição em Catalão, deve também fornecer o texto.', 'error')
        return render_template('editar.html', conceito=conceito, info=db[conceito])
    
    if desc_ca_text and desc_ca_type:
        desc_ca_obj = {
            "type": desc_ca_type,
            "text": desc_ca_text
        }
        entry['desc_ca'] = desc_ca_obj

    # Código CAS
    if request.form.get('CAS'):
        entry['CAS'] = request.form.get('CAS')
    
    # Nota em Catalão
    if request.form.get('note_ca'):
        entry['note_ca'] = [request.form.get('note_ca')]
    
    # Abonações
    if request.form.get('abonacoes'):
        entry['abonacoes'] = request.form.get('abonacoes')
    
    # Informação da Enciclopédia
    if request.form.get('informacao_enciclopedia'):
        entry['informacao_enciclopedia'] = request.form.get('informacao_enciclopedia')

    # Troca de nome do conceito
    if new_name != conceito:
        del db[conceito]
        for cat in categorized_terms:
            if conceito in categorized_terms[cat]["termos"]:
                categorized_terms[cat]["termos"].remove(conceito)
                categorized_terms[cat]["termos"].append(new_name)
                break
        conceito = new_name

    db[conceito] = entry

    if save_data():
        flash(f'Conceito "{conceito}" editado com sucesso!', 'success')
    else:
        flash('Erro ao salvar as alterações!', 'error')

    return redirect('/detalhes/' + conceito)