from flask import render_template, request, redirect, flash, Blueprint, session
from utils.data_loader import db, save_data

add_bp = Blueprint('add', __name__)

@add_bp.route('/adicionar', methods=['GET', 'POST'])
def adicionar():
    if request.method == 'GET':
        session.pop('_flashes', None)
        return render_template('adicionar.html')
        
    if request.method == 'POST':
        termo = request.form.get('termo')

        if termo in db:
            flash(f'Erro: O termo "{termo}" já existe na base de dados!', 'error')
            return render_template('adicionar.html')

        entry = {}

        # Categoria Lexical
        if request.form.get('lex_cat'):
            entry['lex_cat'] = request.form.get('lex_cat')

        # Descrição em Português
        if request.form.get('desc'):
            entry['desc'] = [line.strip() for line in request.form.get('desc').split('\n') if line.strip()]
        
        # Sinónimos em Português
        sinonimo_pt_terms = request.form.getlist('sinonimo_pt_term[]')
        sinonimo_pt_lex = request.form.getlist('sinonimo_pt_lex[]')
        
        if sinonimo_pt_terms:
            sinonimos = []
            for i, term in enumerate(sinonimo_pt_terms):
                if term.strip():
                    lex_cat = sinonimo_pt_lex[i] if i < len(sinonimo_pt_lex) and sinonimo_pt_lex[i] else None
                    sinonimo_obj = {
                        "term": term.strip(),
                        "lex_cat": lex_cat
                    }
                    sinonimos.append(sinonimo_obj)
            
            if sinonimos:
                entry['sinonimos'] = sinonimos

        # Sinónimos em Catalão
        sinonimo_ca_terms = request.form.getlist('sinonimo_ca_term[]')
        sinonimo_ca_lex = request.form.getlist('sinonimo_ca_lex[]')
        
        if sinonimo_ca_terms:
            sinonimos_ca = []
            for i, term in enumerate(sinonimo_ca_terms):
                if term.strip():
                    lex_cat = sinonimo_ca_lex[i] if i < len(sinonimo_ca_lex) and sinonimo_ca_lex[i] else None
                    sinonimo_obj = {
                        "term": term.strip(),
                        "lex_cat": lex_cat
                    }
                    sinonimos_ca.append(sinonimo_obj)
            
            if sinonimos_ca:
                entry['sinonimos_ca'] = sinonimos_ca
        
        # Siglas
        sigla_terms = request.form.getlist('sigla_term[]')
        sigla_lex = request.form.getlist('sigla_lex[]')
        
        if sigla_terms:
            siglas = []
            for i, term in enumerate(sigla_terms):
                if term.strip():
                    lex_cat = sigla_lex[i] if i < len(sigla_lex) and sigla_lex[i] else None
                    sigla_obj = {
                        "term": term.strip(),
                        "lex_cat": lex_cat
                    }
                    siglas.append(sigla_obj)
            
            if siglas:
                entry['sigla'] = siglas
        
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
            return render_template('adicionar.html')

        if desc_ca_type and not desc_ca_text:
            flash('Erro: Se fornecer um tipo para a descrição em Catalão, deve também fornecer o texto.', 'error')
            return render_template('adicionar.html')
        
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

        db[termo] = entry
        
        if save_data():
            flash(f'Conceito "{termo}" adicionado com sucesso!', 'success')
        else:
            flash('Erro ao salvar os dados!', 'error')
        
        return redirect('/detalhes/' + termo)