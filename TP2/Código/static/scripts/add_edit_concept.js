document.addEventListener('DOMContentLoaded', function() {
    // Função para alternar a visibilidade dos botões de eliminar
    function toggleRemoveButtons(container, rowClass) {
        const rows = container.querySelectorAll(`.${rowClass}`);
        rows.forEach((row, index) => {
            const removeBtn = row.querySelector('.remove-sinonimo, .remove-sinonimo-ca, .remove-sigla');
            if (rows.length > 1) {
                removeBtn.style.display = 'block';
            } else {
                removeBtn.style.display = 'none';
            }
        });
    }

    // Validação para o campo de descrição em Catalão
    const descCaType = document.getElementById('desc_ca_type');
    const descCaText = document.getElementById('desc_ca_text');
    const form = document.querySelector('form');

    function validateDescCa() {
        const typeValue = descCaType.value.trim();
        const textValue = descCaText.value.trim();

        descCaType.classList.remove('is-invalid');
        descCaText.classList.remove('is-invalid');

        const existingErrors = document.querySelectorAll('.desc-ca-error');
        existingErrors.forEach(error => error.remove());

        if ((typeValue && !textValue) || (!typeValue && textValue)) {
            if (typeValue && !textValue) {
                descCaText.classList.add('is-invalid');
                showValidationMessage(descCaText, 'Se fornecer o tipo, deve também fornecer a descrição.');
            }
            if (!typeValue && textValue) {
                descCaType.classList.add('is-invalid');
                showValidationMessage(descCaType, 'Se fornecer a descrição, deve também fornecer o tipo.');
            }
            return false;
        }
        return true;
    }

    function showValidationMessage(element, message) {
        const feedback = document.createElement('div');
        feedback.className = 'invalid-feedback desc-ca-error';
        feedback.textContent = message;
        element.parentNode.appendChild(feedback);
    }

    form.addEventListener('submit', function(e) {
        if (!validateDescCa()) {
            e.preventDefault();
            e.stopPropagation();
        }
    });

    descCaType.addEventListener('input', validateDescCa);
    descCaText.addEventListener('input', validateDescCa);

    // Adicionar campos de sinónimos em Português
    document.getElementById('add-sinonimo-pt').addEventListener('click', function() {
        const container = document.getElementById('sinonimos-container');
        const newRow = document.createElement('div');
        newRow.className = 'row g-2 mb-2 sinonimo-row';
        newRow.innerHTML = `
            <div class="col-md-6">
                <input type="text" class="form-control" name="sinonimo_pt_term[]" placeholder="Sinónimo">
            </div>
            <div class="col-md-4">
                <select class="form-select" name="sinonimo_pt_lex[]">
                    <option value="">Categoria Lexical</option>
                    <option value="n m">Substantivo masculino</option>
                    <option value="n f">Substantivo feminino</option>
                    <option value="adj">Adjetivo</option>
                    <option value="v">Verbo</option>
                    <option value="adv">Advérbio</option>
                    <option value="prep">Preposição</option>
                    <option value="conj">Conjunção</option>
                    <option value="interj">Interjeição</option>
                </select>
            </div>
            <div class="col-md-2">
                <button type="button" class="btn btn-outline-danger remove-sinonimo">
                    <i class="bi bi-trash"></i>
                </button>
            </div>
        `;
        container.appendChild(newRow);
        toggleRemoveButtons(container, 'sinonimo-row');
    });

    // Adicionar campos de sinónimos em Catalão
    document.getElementById('add-sinonimo-ca').addEventListener('click', function() {
        const container = document.getElementById('sinonimos-ca-container');
        const newRow = document.createElement('div');
        newRow.className = 'row g-2 mb-2 sinonimo-ca-row';
        newRow.innerHTML = `
            <div class="col-md-6">
                <input type="text" class="form-control" name="sinonimo_ca_term[]" placeholder="Sinónimo (Catalão)">
            </div>
            <div class="col-md-4">
                <select class="form-select" name="sinonimo_ca_lex[]">
                    <option value="">Categoria Lexical</option>
                    <option value="n m">Substantivo masculino</option>
                    <option value="n f">Substantivo feminino</option>
                    <option value="adj">Adjetivo</option>
                    <option value="v">Verbo</option>
                    <option value="adv">Advérbio</option>
                    <option value="prep">Preposição</option>
                    <option value="conj">Conjunção</option>
                    <option value="interj">Interjeição</option>
                </select>
            </div>
            <div class="col-md-2">
                <button type="button" class="btn btn-outline-danger remove-sinonimo-ca">
                    <i class="bi bi-trash"></i>
                </button>
            </div>
        `;
        container.appendChild(newRow);
        toggleRemoveButtons(container, 'sinonimo-ca-row');
    });

    // Adicionar campos de siglas
    document.getElementById('add-sigla').addEventListener('click', function() {
        const container = document.getElementById('siglas-container');
        const newRow = document.createElement('div');
        newRow.className = 'row g-2 mb-2 sigla-row';
        newRow.innerHTML = `
            <div class="col-md-6">
                <input type="text" class="form-control" name="sigla_term[]" placeholder="Sigla/Abreviação">
            </div>
            <div class="col-md-4">
                <select class="form-select" name="sigla_lex[]">
                    <option value="">Categoria Lexical</option>
                    <option value="n m">Substantivo masculino</option>
                    <option value="n f">Substantivo feminino</option>
                    <option value="adj">Adjetivo</option>
                    <option value="v">Verbo</option>
                    <option value="adv">Advérbio</option>
                    <option value="prep">Preposição</option>
                    <option value="conj">Conjunção</option>
                    <option value="interj">Interjeição</option>
                </select>
            </div>
            <div class="col-md-2">
                <button type="button" class="btn btn-outline-danger remove-sigla">
                    <i class="bi bi-trash"></i>
                </button>
            </div>
        `;
        container.appendChild(newRow);
        toggleRemoveButtons(container, 'sigla-row');
    });

    document.addEventListener('click', function(e) {
        if (e.target.closest('.remove-sinonimo')) {
            const row = e.target.closest('.sinonimo-row');
            const container = document.getElementById('sinonimos-container');
            row.remove();
            toggleRemoveButtons(container, 'sinonimo-row');
        }
        
        if (e.target.closest('.remove-sinonimo-ca')) {
            const row = e.target.closest('.sinonimo-ca-row');
            const container = document.getElementById('sinonimos-ca-container');
            row.remove();
            toggleRemoveButtons(container, 'sinonimo-ca-row');
        }
        
        if (e.target.closest('.remove-sigla')) {
            const row = e.target.closest('.sigla-row');
            const container = document.getElementById('siglas-container');
            row.remove();
            toggleRemoveButtons(container, 'sigla-row');
        }
    });

    // Visibilidade inicial dos botões de eliminar
    toggleRemoveButtons(document.getElementById('sinonimos-container'), 'sinonimo-row');
    toggleRemoveButtons(document.getElementById('sinonimos-ca-container'), 'sinonimo-ca-row');
    toggleRemoveButtons(document.getElementById('siglas-container'), 'sigla-row');

    const textareas = document.querySelectorAll('textarea');
    textareas.forEach(textarea => {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = this.scrollHeight + 'px';
        });
    });
});