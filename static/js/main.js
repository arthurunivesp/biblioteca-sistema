// ========================================
// SALA DE LEITURA - JAVASCRIPT PRINCIPAL
// ========================================

document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

/**
 * Inicializar aplicação
 */
function initializeApp() {
    console.log('🚀 Inicializando Sala de Leitura...');
    
    // Inicializar componentes
    initScanner();
    initLocationForms();
    initDataTables();
    initTooltips();
    initAlerts();
    initFormValidation();
    
    console.log('✅ Sala de Leitura inicializada!');
}

/**
 * Scanner QR/Código de Barras
 */
function initScanner() {
    const scannerInputs = document.querySelectorAll('#scannerInput, .scanner-input');
    
    scannerInputs.forEach(input => {
        if (input) {
            // Auto-focus para leitores USB
            input.addEventListener('focus', function() {
                this.placeholder = 'Aguardando leitura do código...';
                this.classList.add('scanner-active');
            });
            
            input.addEventListener('blur', function() {
                this.placeholder = 'Passe o leitor ou digite o código...';
                this.classList.remove('scanner-active');
            });
            
            // Processar código quando Enter for pressionado
            input.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    processScannedCode(this.value.trim());
                }
            });
            
            // Processar automaticamente após um breve delay (para leitores rápidos)
            let scanTimeout;
            input.addEventListener('input', function() {
                clearTimeout(scanTimeout);
                const code = this.value.trim();
                
                if (code.length >= 8) { // Mínimo para ISBN/QR
                    scanTimeout = setTimeout(() => {
                        processScannedCode(code);
                    }, 500); // 500ms de delay
                }
            });
        }
    });
}

/**
 * Processar código escaneado
 */
function processScannedCode(code) {
    if (!code) return;
    
    console.log('📱 Código escaneado:', code);
    
    // Mostrar loading
    showLoading('Processando código...');
    
    // Fazer requisição para API
    fetch('/api/scan-qr', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ qr_code: code })
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();
        
        if (data.success) {
            showSuccess(`Livro encontrado: ${data.book.title}`);
            
            // Se estiver na página de empréstimo, preencher dados
            if (window.location.pathname.includes('/loans/new')) {
                fillLoanForm(data.book);
            }
            // Se estiver na página de busca, mostrar detalhes
            else if (window.location.pathname.includes('/books')) {
                showBookDetails(data.book);
            }
        } else {
            showError(data.message || 'Código não encontrado');
        }
    })
    .catch(error => {
        hideLoading();
        console.error('Erro ao processar código:', error);
        showError('Erro ao processar código. Tente novamente.');
    });
}

/**
 * Preencher formulário de empréstimo
 */
function fillLoanForm(book) {
    // Selecionar livro no dropdown
    const bookSelect = document.getElementById('book_id');
    if (bookSelect) {
        bookSelect.value = book.id;
        bookSelect.dispatchEvent(new Event('change'));
    }
    
    // Carregar exemplares disponíveis
    loadBookCopies(book.id);
}

/**
 * Carregar exemplares de um livro
 */
function loadBookCopies(bookId) {
    fetch(`/api/book-copies/${bookId}`)
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const copySelect = document.getElementById('book_copy_id');
            if (copySelect) {
                copySelect.innerHTML = '<option value="">Selecione o exemplar...</option>';
                
                data.copies.forEach(copy => {
                    const option = document.createElement('option');
                    option.value = copy.id;
                    option.textContent = `Exemplar ${copy.copy_number} - ${copy.location} (${copy.condition})`;
                    copySelect.appendChild(option);
                });
            }
        }
    })
    .catch(error => {
        console.error('Erro ao carregar exemplares:', error);
    });
}

/**
 * Formulários de localização
 */
function initLocationForms() {
    const totalCopiesInput = document.getElementById('total_copies');
    
    if (totalCopiesInput) {
        totalCopiesInput.addEventListener('input', function() {
            const totalCopies = parseInt(this.value) || 1;
            generateLocationForms(totalCopies);
        });
    }
}

/**
 * Gerar formulários de localização
 */
function generateLocationForms(totalCopies) {
    const container = document.getElementById('locationFormsContainer');
    if (!container) return;
    
    container.innerHTML = '';
    
    for (let i = 1; i <= totalCopies; i++) {
        const formHtml = `
            <div class="location-card fade-in" style="animation-delay: ${i * 0.1}s">
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <h6 class="mb-0">
                        <i class="fas fa-book me-2"></i>
                        Exemplar ${i}
                    </h6>
                    <span class="location-badge" id="location-preview-${i}">
                        Localização: ?-?-?
                    </span>
                </div>
                
                <div class="row">
                    <div class="col-md-3">
                        <label class="form-label">Estante *</label>
                        <input type="text" class="form-control" name="shelf_${i}" 
                               placeholder="A, B, C..." required maxlength="2"
                               oninput="updateLocationPreview(${i})">
                    </div>
                    <div class="col-md-3">
                        <label class="form-label">Prateleira *</label>
                        <input type="text" class="form-control" name="shelf_section_${i}" 
                               placeholder="1, 2, 3..." required maxlength="2"
                               oninput="updateLocationPreview(${i})">
                    </div>
                    <div class="col-md-3">
                        <label class="form-label">Posição *</label>
                        <input type="number" class="form-control" name="position_number_${i}" 
                               value="${i}" min="1" max="999" required
                               oninput="updateLocationPreview(${i})">
                    </div>
                    <div class="col-md-3">
                        <label class="form-label">Estado</label>
                        <select class="form-select" name="condition_${i}">
                            <option value="excellent">Excelente</option>
                            <option value="good" selected>Bom</option>
                            <option value="fair">Regular</option>
                            <option value="poor">Ruim</option>
                        </select>
                    </div>
                </div>
                
                <div class="mt-3">
                    <label class="form-label">Observações</label>
                    <input type="text" class="form-control" name="notes_${i}" 
                           placeholder="Observações específicas sobre este exemplar...">
                </div>
            </div>
        `;
        
        container.innerHTML += formHtml;
    }
    
    // Auto-preencher localizações sequenciais
    autoFillSequentialLocations();
}

/**
 * Auto-preencher localizações sequenciais
 */
function autoFillSequentialLocations() {
    const baseShelfInput = document.getElementById('baseShelf');
    const baseSectionInput = document.getElementById('baseSection');
    
    if (baseShelfInput && baseSectionInput) {
        function updateAllLocations() {
            const baseShelf = baseShelfInput.value.toUpperCase();
            const baseSection = baseSectionInput.value;
            
            const totalCopies = parseInt(document.getElementById('total_copies').value) || 1;
            
            for (let i = 1; i <= totalCopies; i++) {
                const shelfInput = document.querySelector(`input[name="shelf_${i}"]`);
                const sectionInput = document.querySelector(`input[name="shelf_section_${i}"]`);
                
                if (shelfInput && sectionInput) {
                    shelfInput.value = baseShelf;
                    sectionInput.value = baseSection;
                    updateLocationPreview(i);
                }
            }
        }
        
        baseShelfInput.addEventListener('input', updateAllLocations);
        baseSectionInput.addEventListener('input', updateAllLocations);
    }
}

/**
 * Atualizar preview da localização
 */
function updateLocationPreview(copyNumber) {
    const shelf = document.querySelector(`input[name="shelf_${copyNumber}"]`).value || '?';
    const section = document.querySelector(`input[name="shelf_section_${copyNumber}"]`).value || '?';
    const position = document.querySelector(`input[name="position_number_${copyNumber}"]`).value || '?';
    
    const preview = document.getElementById(`location-preview-${copyNumber}`);
    if (preview) {
        preview.textContent = `Localização: ${shelf}-${section}-${position}`;
    }
}

/**
 * Inicializar DataTables
 */
function initDataTables() {
    // Se jQuery e DataTables estiverem disponíveis
    if (typeof $ !== 'undefined' && $.fn.DataTable) {
        $('.data-table').DataTable({
            language: {
                url: '//cdn.datatables.net/plug-ins/1.13.7/i18n/pt-BR.json'
            },
            responsive: true,
            pageLength: 25,
            order: [[0, 'desc']] // Ordenar por data decrescente
        });
    }
}

/**
 * Inicializar tooltips
 */
function initTooltips() {
    // Bootstrap tooltips
    if (typeof bootstrap !== 'undefined') {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
}

/**
 * Inicializar alertas auto-dismiss
 */
function initAlerts() {
    const alerts = document.querySelectorAll('.alert');
    
    alerts.forEach(alert => {
        // Auto-dismiss após 5 segundos
        setTimeout(() => {
            if (alert && alert.parentNode) {
                alert.style.transition = 'opacity 0.5s ease';
                alert.style.opacity = '0';
                
                setTimeout(() => {
                    if (alert.parentNode) {
                        alert.parentNode.removeChild(alert);
                    }
                }, 500);
            }
        }, 5000);
    });
}

/**
 * Validação de formulários
 */
function initFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
                
                // Focar no primeiro campo inválido
                const firstInvalid = form.querySelector(':invalid');
                if (firstInvalid) {
                    firstInvalid.focus();
                }
            }
            
            form.classList.add('was-validated');
        });
    });
}

/**
 * Funções de UI
 */
function showLoading(message = 'Carregando...') {
    // Criar ou atualizar loading
    let loading = document.getElementById('loadingToast');
    
    if (!loading) {
        loading = document.createElement('div');
        loading.id = 'loadingToast';
        loading.className = 'toast show position-fixed top-0 end-0 m-3';
        loading.style.zIndex = '9999';
        document.body.appendChild(loading);
    }
    
    loading.innerHTML = `
        <div class="toast-header bg-primary text-white">
            <div class="loading-spinner me-2"></div>
            <strong class="me-auto">${message}</strong>
        </div>
    `;
}

function hideLoading() {
    const loading = document.getElementById('loadingToast');
    if (loading) {
        loading.remove();
    }
}

function showSuccess(message) {
    showToast(message, 'success');
}

function showError(message) {
    showToast(message, 'danger');
}

function showInfo(message) {
    showToast(message, 'info');
}

function showToast(message, type = 'info') {
    const toastId = 'toast-' + Date.now();
    const toast = document.createElement('div');
    toast.id = toastId;
    toast.className = 'toast show position-fixed top-0 end-0 m-3 fade-in';
    toast.style.zIndex = '9999';
    
    const bgClass = type === 'success' ? 'bg-success' : 
                   type === 'danger' ? 'bg-danger' : 
                   type === 'warning' ? 'bg-warning' : 'bg-info';
    
    const icon = type === 'success' ? 'fas fa-check-circle' :
                type === 'danger' ? 'fas fa-exclamation-circle' :
                type === 'warning' ? 'fas fa-exclamation-triangle' : 'fas fa-info-circle';
    
    toast.innerHTML = `
        <div class="toast-header ${bgClass} text-white">
            <i class="${icon} me-2"></i>
            <strong class="me-auto">
                ${type === 'success' ? 'Sucesso' : 
                  type === 'danger' ? 'Erro' : 
                  type === 'warning' ? 'Atenção' : 'Informação'}
            </strong>
            <button type="button" class="btn-close btn-close-white" onclick="removeToast('${toastId}')"></button>
        </div>
        <div class="toast-body">
            ${message}
        </div>
    `;
    
    document.body.appendChild(toast);
    
    // Auto-remove após 5 segundos
    setTimeout(() => {
        removeToast(toastId);
    }, 5000);
}

function removeToast(toastId) {
    const toast = document.getElementById(toastId);
    if (toast) {
        toast.style.transition = 'opacity 0.3s ease';
        toast.style.opacity = '0';
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }
}

/**
 * Confirmação de exclusão
 */
function confirmDelete(message = 'Tem certeza que deseja excluir este item?') {
    return confirm(message);
}

/**
 * Formatação de dados
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR');
}

function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('pt-BR');
}

/**
 * Utilitários de busca
 */
function searchTable(inputId, tableId) {
    const input = document.getElementById(inputId);
    const table = document.getElementById(tableId);
    
    if (!input || !table) return;
    
    input.addEventListener('input', function() {
        const filter = this.value.toLowerCase();
        const rows = table.getElementsByTagName('tr');
        
        for (let i = 1; i < rows.length; i++) { // Pular header
            const row = rows[i];
            const cells = row.getElementsByTagName('td');
            let found = false;
            
            for (let j = 0; j < cells.length; j++) {
                const cell = cells[j];
                if (cell.textContent.toLowerCase().includes(filter)) {
                    found = true;
                    break;
                }
            }
            
            row.style.display = found ? '' : 'none';
        }
    });
}

/**
 * Controle de formulários dinâmicos
 */
function addFormRow(containerId, templateId) {
    const container = document.getElementById(containerId);
    const template = document.getElementById(templateId);
    
    if (!container || !template) return;
    
    const newRow = template.cloneNode(true);
    newRow.style.display = 'block';
    newRow.removeAttribute('id');
    
    // Atualizar nomes dos campos
    const inputs = newRow.querySelectorAll('input, select, textarea');
    inputs.forEach(input => {
        const name = input.getAttribute('name');
        if (name) {
            const timestamp = Date.now();
            input.setAttribute('name', `${name}_${timestamp}`);
        }
    });
    
    container.appendChild(newRow);
}

function removeFormRow(button) {
    const row = button.closest('.form-row, .location-card, .dynamic-row');
    if (row) {
        row.style.transition = 'opacity 0.3s ease';
        row.style.opacity = '0';
        setTimeout(() => {
            if (row.parentNode) {
                row.parentNode.removeChild(row);
            }
        }, 300);
    }
}

/**
 * Máscara para campos
 */
function applyPhoneMask(input) {
    input.addEventListener('input', function() {
        let value = this.value.replace(/\D/g, '');
        value = value.replace(/^(\d{2})(\d)/g, '($1) $2');
        value = value.replace(/(\d)(\d{4})$/, '$1-$2');
        this.value = value;
    });
}

// Aplicar máscaras automaticamente
document.addEventListener('DOMContentLoaded', function() {
    const phoneInputs = document.querySelectorAll('input[name*="phone"], input[type="tel"]');
    phoneInputs.forEach(applyPhoneMask);
});

/**
 * Estatísticas em tempo real
 */
function updateStats() {
    fetch('/api/stats')
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Atualizar contadores
            Object.keys(data.stats).forEach(key => {
                const element = document.getElementById(`stat-${key}`);
                if (element) {
                    element.textContent = data.stats[key];
                }
            });
        }
    })
    .catch(error => {
        console.error('Erro ao atualizar estatísticas:', error);
    });
}

// Atualizar estatísticas a cada 30 segundos
setInterval(updateStats, 30000);

/**
 * Funções específicas para cada página
 */

// Dashboard
if (window.location.pathname === '/') {
    // Código específico do dashboard
    console.log('📊 Dashboard carregado');
}

// Página de livros
if (window.location.pathname.includes('/books')) {
    console.log('📚 Página de livros carregada');
    
    // Inicializar busca em tempo real
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        let searchTimeout;
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                // Auto-submit do formulário de busca
                this.form.submit();
            }, 1000);
        });
    }
}

// Página de empréstimos
if (window.location.pathname.includes('/loans')) {
    console.log('📖 Página de empréstimos carregada');
    
    // Calcular dias de atraso
    const overdueElements = document.querySelectorAll('.days-overdue');
    overdueElements.forEach(element => {
        const expectedDate = new Date(element.dataset.expectedDate);
        const today = new Date();
        const diffTime = today - expectedDate;
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        
        if (diffDays > 0) {
            element.textContent = `${diffDays} dias de atraso`;
            element.classList.add('text-danger');
        }
    });
}

console.log('✅ JavaScript principal carregado!');