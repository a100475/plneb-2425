from flask import Blueprint, render_template
from utils.stats import get_statistics
from utils.data_loader import data_manager

stats_bp = Blueprint('stats', __name__)

@stats_bp.route('/estatisticas')
def show_statistics():
    try:
        dictionary_data = data_manager.db
        
        if not dictionary_data:
            return render_template('stats.html', error="Nenhum dado disponível para análise.")
        
        stats = get_statistics(dictionary_data)
        return render_template('stats.html', stats=stats)
    
    except Exception as e:
        return render_template('stats.html', error=f"Erro ao carregar estatísticas: {str(e)}")
