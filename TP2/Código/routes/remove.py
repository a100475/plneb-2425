from flask import render_template, request, redirect, flash, Blueprint
from utils.data_loader import data_manager

remove_bp = Blueprint('remove', __name__)

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def eliminar_conceito_helper(conceito):
    """Remove a concept from both db and categorized_terms"""
    # Remove from main database
    if conceito in data_manager.db:
        del data_manager.db[conceito]

    # Remove from categories
    for cat, val in data_manager.categorized_terms.items():
        if conceito in val.get("termos", []):
            val["termos"].remove(conceito)
    
    # Reload search engine after data changes
    data_manager.reload_search_engine()

# =============================================================================
# ROUTES
# =============================================================================

@remove_bp.route('/eliminar/<string:conceito>', methods=['POST'])
def eliminar_conceito(conceito):
    """Eliminar um conceito"""
    if conceito not in data_manager.db:
        return render_template('error.html', message='Conceito não encontrado'), 404

    table_referrer = request.form.get('table_referrer', '/tabela')
    
    eliminar_conceito_helper(conceito)
    
    if data_manager.save_data():
        flash(f'O conceito "{conceito}" foi eliminado com sucesso!', 'success')
    else:
        flash('Erro ao salvar as alterações após eliminação!', 'error')
    
    return redirect(table_referrer)