$(document).ready(function() {
    $('#tabela_conceitos').hide();
    
    const table = $('#tabela_conceitos').DataTable({
        "language": {
            "url": "https://cdn.datatables.net/plug-ins/1.13.7/i18n/pt-BR.json"
        },
        "pageLength": 25,
        "order": [[ 0, "asc" ]],
        "columnDefs": [
            { "orderable": false, "targets": 2 }
        ],
        "searching": false,
        "dom": "<'row'<'col-sm-12 col-md-6'l><'col-sm-12 col-md-6'<'custom-buttons'>>>" +
               "<'row'<'col-sm-12'tr>>" +
               "<'row'<'col-sm-12 col-md-5'i><'col-sm-12 col-md-7'p>>",
        "initComplete": function(settings, json) {
            $('.custom-buttons').html(`
                <div class="d-flex justify-content-end align-items-center flex-wrap gap-2">
                    <div class="form-check form-check-inline">
                        <input class="form-check-input" type="checkbox" id="case_sensitive" name="case_sensitive" value="true"
                               ${$('input[name="case_sensitive"]').val() === 'true' ? 'checked' : ''}>
                        <label class="form-check-label" for="case_sensitive">
                            <small>Case Sensitive</small>
                        </label>
                    </div>
                    <div class="form-check form-check-inline">
                        <input class="form-check-input" type="checkbox" id="is_regex" name="is_regex" value="true"
                               ${$('input[name="is_regex"]').val() === 'true' ? 'checked' : ''}>
                        <label class="form-check-label" for="is_regex">
                            <small>Regex</small>
                        </label>
                    </div>
                    <button type="button" class="btn btn-success" data-bs-toggle="modal" data-bs-target="#advancedFiltersModal">
                        <i class="bi bi-sliders me-1"></i>Avançado
                    </button>
                    <button type="submit" form="filterForm" class="btn btn-primary">
                        <i class="bi bi-search me-1"></i>Pesquisar
                    </button>
                    <a href="/tabela" class="btn btn-outline-secondary">
                        <i class="bi bi-arrow-clockwise me-1"></i>Limpar
                    </a>
                </div>
            `);
            
            $('#case_sensitive').on('change', function() {
                $('input[name="case_sensitive"]').val(this.checked ? 'true' : '');
            });
            
            $('#is_regex').on('change', function() {
                $('input[name="is_regex"]').val(this.checked ? 'true' : '');
            });
            
            $('#table-loading').hide();
            $('#tabela_conceitos').fadeIn();
        }
    });
});