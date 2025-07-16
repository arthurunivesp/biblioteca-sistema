// ========================================
// SCANNER QR CODE / CÓDIGO DE BARRAS
// ========================================

class BarcodeScanner {
    constructor() {
        this.isActive = false;
        this.lastScanTime = 0;
        this.scanDelay = 1000; // 1 segundo entre scans
        this.init();
    }
    
    init() {
        console.log('🔍 Inicializando Scanner de Código de Barras...');
        this.setupScannerInputs();
        this.setupKeyboardListener();
    }
    
    setupScannerInputs() {
        const scannerInputs = document.querySelectorAll('.scanner-input, #scannerInput');
        
        scannerInputs.forEach(input => {
            // Auto-focus para leitores USB
            input.addEventListener('focus', () => {
                this.activateScanner(input);
            });
            
            input.addEventListener('blur', () => {
                this.deactivateScanner(input);
            });
            
            // Processar código quando Enter for pressionado
            input.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    this.processCode(input.value.trim(), input);
                }
            });
            
            // Auto-processar após delay (para leitores rápidos)
            let inputTimeout;
            input.addEventListener('input', () => {
                clearTimeout(inputTimeout);
                const code = input.value.trim();
                
                // Processar automaticamente códigos com tamanho típico
                if (code.length >= 8 && code.length <= 20) {
                    inputTimeout = setTimeout(() => {
                        this.processCode(code, input);
                    }, 500);
                }
            });
        });
    }
    
    setupKeyboardListener() {
        let scanBuffer = '';
        let scanTimeout;
        
        // Escutar entrada rápida do teclado (característica dos leitores USB)
        document.addEventListener('keypress', (e) => {
            // Ignorar se estiver digitando em um campo
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
                return;
            }
            
            const char = String.fromCharCode(e.which);
            
            // Resetar buffer se demorar muito entre caracteres
            clearTimeout(scanTimeout);
            
            // Adicionar caractere ao buffer
            scanBuffer += char;
            
            // Processar se Enter for pressionado
            if (e.key === 'Enter' || e.which === 13) {
                if (scanBuffer.length >= 8) {
                    this.processCode(scanBuffer.trim());
                }
                scanBuffer = '';
                return;
            }
            
            // Auto-processar após 100ms (leitores são muito rápidos)
            scanTimeout = setTimeout(() => {
                if (scanBuffer.length >= 8 && scanBuffer.length <= 20) {
                    this.processCode(scanBuffer.trim());
                }
                scanBuffer = '';
            }, 100);
        });
    }
    
    activateScanner(input) {
        this.isActive = true;
        input.placeholder = '🔍 Aguardando leitura do código...';
        input.classList.add('scanner-active', 'border-primary');
        
        // Adicionar indicador visual
        this.addScannerIndicator(input);
    }
    
    deactivateScanner(input) {
        this.isActive = false;
        input.placeholder = 'Passe o leitor ou digite o código...';
        input.classList.remove('scanner-active', 'border-primary');
        
        // Remover indicador visual
        this.removeScannerIndicator(input);
    }
    
    addScannerIndicator(input) {
        const indicator = document.createElement('div');
        indicator.className = 'scanner-indicator';
        indicator.innerHTML = `
            <div class="d-flex align-items-center text-primary">
                <div class="spinner-border spinner-border-sm me-2" role="status"></div>
                <small>Scanner ativo - passe o código</small>
            </div>
        `;
        
        input.parentNode.appendChild(indicator);
    }
    
    removeScannerIndicator(input) {
        const indicator = input.parentNode.querySelector('.scanner-indicator');
        if (indicator) {
            indicator.remove();
        }
    }
    
    processCode(code, inputElement = null) {
        // Evitar processamento duplo
        const now = Date.now();
        if (now - this.lastScanTime < this.scanDelay) {
            return;
        }
        this.lastScanTime = now;
        
        if (!code || code.length < 8) {
            this.showError('Código inválido ou muito curto');
            return;
        }
        
        console.log('📱 Código escaneado:', code);
        
        // Feedback visual
        if (inputElement) {
            inputElement.value = code;
            inputElement.classList.add('border-success');
            setTimeout(() => {
                inputElement.classList.remove('border-success');
            }, 2000);
        }
        
        // Som de sucesso (se disponível)
        this.playBeep();
        
        // Processar baseado no contexto da página
        this.handleCodeByContext(code);
    }
    
    handleCodeByContext(code) {
        const path = window.location.pathname;
        
        if (path.includes('/books/add') || path.includes('/books/edit')) {
            this.handleBookForm(code);
        } else if (path.includes('/loans/new')) {
            this.handleNewLoan(code);
        } else if (path.includes('/books')) {
            this.handleBookSearch(code);
        } else {
            this.handleGenericScan(code);
        }
    }
    
    handleBookForm(code) {
        // Preencher campo QR Code e ISBN
        const qrCodeInput = document.querySelector('input[name="qr_code"]');
        const isbnInput = document.querySelector('input[name="isbn"]');
        if (qrCodeInput) {
            qrCodeInput.value = code;
            this.showSuccess('Código QR adicionado ao livro');
        }
        if (isbnInput) {
            isbnInput.value = code; // Preenche o ISBN com o código escaneado
            this.showSuccess('ISBN preenchido com o código escaneado');
        }
        
        // Tentar buscar informações do livro por ISBN
        if (this.isISBN(code)) {
            this.searchBookByISBN(code);
        }
    }
    
    handleNewLoan(code) {
        this.showLoading('Buscando livro...');
        
        fetch('/api/scan-qr', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ qr_code: code })
        })
        .then(response => response.json())
        .then(data => {
            this.hideLoading();
            
            if (data.success) {
                this.fillLoanForm(data.book);
                this.showSuccess(`Livro selecionado: ${data.book.title}`);
            } else {
                this.showError(data.message || 'Livro não encontrado');
            }
        })
        .catch(error => {
            this.hideLoading();
            console.error('Erro ao buscar livro:', error);
            this.showError('Erro ao buscar livro. Tente novamente.');
        });
    }
    
    handleBookSearch(code) {
        // Preencher campo de busca
        const searchInput = document.querySelector('input[name="search"]');
        if (searchInput) {
            searchInput.value = code;
            
            // Submeter formulário de busca
            const form = searchInput.closest('form');
            if (form) {
                form.submit();
            }
        }
    }
    
    handleGenericScan(code) {
        // Mostrar modal com opções
        this.showScanResult(code);
    }
    
    fillLoanForm(book) {
        // Selecionar livro
        const bookSelect = document.getElementById('book_id');
        if (bookSelect) {
            bookSelect.value = book.id;
            bookSelect.dispatchEvent(new Event('change'));
        }
        
        // Carregar exemplares
        this.loadBookCopies(book.id);
    }
    
    loadBookCopies(bookId) {
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
                    
                    // Auto-selecionar primeiro exemplar se houver apenas um
                    if (data.copies.length === 1) {
                        copySelect.value = data.copies[0].id;
                    }
                }
            }
        })
        .catch(error => {
            console.error('Erro ao carregar exemplares:', error);
        });
    }
    
    searchBookByISBN(isbn) {
        // Implementar busca em APIs externas (Google Books, etc.)
        // Por enquanto, apenas preencher o campo ISBN
        const isbnInput = document.querySelector('input[name="isbn"]');
        if (isbnInput) {
            isbnInput.value = isbn;
        }
    }
    
    isISBN(code) {
        // Verificar se é um ISBN válido
        const cleanCode = code.replace(/[-\s]/g, '');
        return cleanCode.length === 10 || cleanCode.length === 13;
    }
    
    showScanResult(code) {
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.innerHTML = `
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">
                            <i class="fas fa-qrcode me-2"></i>
                            Código Escaneado
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="alert alert-success">
                            <strong>Código:</strong> ${code}
                        </div>
                        <p>O que você gostaria de fazer?</p>
                        <div class="d-grid gap-2">
                            <a href="/books?search=${encodeURIComponent(code)}" class="btn btn-primary">
                                <i class="fas fa-search me-2"></i>
                                Buscar Livro
                            </a>
                            <a href="/loans/new" class="btn btn-success">
                                <i class="fas fa-plus me-2"></i>
                                Novo Empréstimo
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
        
        modal.addEventListener('hidden.bs.modal', () => {
            modal.remove();
        });
    }
    
    playBeep() {
        // Tentar reproduzir som de beep
        try {
            const audio = new Audio('data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbZ2oJ...');
            audio.volume = 0.3;
            audio.play().catch(() => {
                // Ignorar erro se não conseguir reproduzir
            });
        } catch (e) {
            // Beep visual se não conseguir som
            document.body.style.background = '#4ade80';
            setTimeout(() => {
                document.body.style.background = '';
            }, 100);
        }
    }
    
    showLoading(message = 'Processando...') {
        let loading = document.getElementById('scannerLoading');
        
        if (!loading) {
            loading = document.createElement('div');
            loading.id = 'scannerLoading';
            loading.className = 'position-fixed top-50 start-50 translate-middle';
            loading.style.zIndex = '9999';
            document.body.appendChild(loading);
        }
        
        loading.innerHTML = `
            <div class="card border-0 shadow-lg">
                <div class="card-body text-center">
                    <div class="spinner-border text-primary mb-3" role="status"></div>
                    <div>${message}</div>
                </div>
            </div>
        `;
        
        loading.style.display = 'block';
    }
    
    hideLoading() {
        const loading = document.getElementById('scannerLoading');
        if (loading) {
            loading.style.display = 'none';
        }
    }
    
    showSuccess(message) {
        this.showToast(message, 'success');
    }
    
    showError(message) {
        this.showToast(message, 'danger');
    }
    
    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast show position-fixed top-0 end-0 m-3`;
        toast.style.zIndex = '9999';
        
        const bgClass = type === 'success' ? 'bg-success' : 
                       type === 'danger' ? 'bg-danger' : 'bg-info';
        
        const icon = type === 'success' ? 'fas fa-check-circle' : 
                    type === 'danger' ? 'fas fa-exclamation-circle' : 'fas fa-info-circle';
        
        toast.innerHTML = `
            <div class="toast-header ${bgClass} text-white">
                <i class="${icon} me-2"></i>
                <strong class="me-auto">Scanner</strong>
                <button type="button" class="btn-close btn-close-white" onclick="this.closest('.toast').remove()"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        `;
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            if (toast.parentNode) {
                toast.remove();
            }
        }, 5000);
    }
}

// Inicializar scanner quando a página carregar
document.addEventListener('DOMContentLoaded', function() {
    window.barcodeScanner = new BarcodeScanner();
    console.log('✅ Scanner de código de barras inicializado!');
});
