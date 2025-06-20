function applyAdvancedFilters() {
    const descRadios = document.querySelectorAll('input[name="description_radio"]');
    let selectedDesc = '';
    for (const radio of descRadios) {
        if (radio.checked) {
            selectedDesc = radio.value;
            break;
        }
    }
    
    document.querySelector('input[name="has_description"]').value = 
        selectedDesc === 'with' ? 'true' : '';
    document.querySelector('input[name="no_description"]').value = 
        selectedDesc === 'without' ? 'true' : '';
    
    document.querySelector('input[name="first_letter"]').value = 
        document.getElementById('first_letter').value;
    
    document.querySelector('input[name="min_length"]').value = 
        document.getElementById('min_length').value;
    
    document.querySelector('input[name="max_length"]').value = 
        document.getElementById('max_length').value;
    
    const termTypeRadios = document.querySelectorAll('input[name="term_type_radio"]');
    let selectedTermType = '';
    for (const radio of termTypeRadios) {
        if (radio.checked) {
            selectedTermType = radio.value === 'all' ? '' : radio.value;
            break;
        }
    }
    document.querySelector('input[name="term_type"]').value = selectedTermType;
    
    const modal = bootstrap.Modal.getInstance(document.getElementById('advancedFiltersModal'));
    modal.hide();
    document.getElementById('filterForm').submit();
}

function clearAdvancedFilters() {
    document.getElementById('desc_all').checked = true;
    document.getElementById('first_letter').value = 'all';
    document.getElementById('min_length').value = '';
    document.getElementById('max_length').value = '';
    document.getElementById('term_type_all').checked = true;
    
    document.querySelector('input[name="has_description"]').value = '';
    document.querySelector('input[name="no_description"]').value = '';
    document.querySelector('input[name="first_letter"]').value = '';
    document.querySelector('input[name="min_length"]').value = '';
    document.querySelector('input[name="max_length"]').value = '';
    document.querySelector('input[name="term_type"]').value = '';
}