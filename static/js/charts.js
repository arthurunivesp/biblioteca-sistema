// ========================================
// GRÁFICOS E RELATÓRIOS
// ========================================

class ReportsCharts {
    constructor() {
        this.charts = {};
        this.init();
    }
    
    init() {
        console.log('📊 Inicializando gráficos de relatórios...');
        
        if (window.location.pathname.includes('/reports')) {
            this.loadReportCharts();
        }
        
        if (window.location.pathname === '/') {
            this.loadDashboardCharts();
        }
    }
    
    loadReportCharts() {
        // Gráfico de empréstimos por mês
        this.createLoansChart();
        
        // Gráfico de categorias mais populares
        this.createCategoriesChart();
        
        // Gráfico de status dos livros
        this.createBooksStatusChart();
    }
    
    loadDashboardCharts() {
        // Mini gráficos para o dashboard
        this.createMiniStatsCharts();
    }
    
    createLoansChart() {
        const ctx = document.getElementById('loansChart');
        if (!ctx) return;
        
        // Dados mockados - em produção viria da API
        const data = {
            labels: ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun'],
            datasets: [{
                label: 'Empréstimos',
                data: [12, 19, 15, 25, 22, 18],
                borderColor: '#3b82f6',
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4
            }]
        };
        
        this.charts.loans = new Chart(ctx, {
            type: 'line',
            data: data,
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: false
                    },
                    title: {
                        display: true,
                        text: 'Empréstimos por Mês'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
    }
    
    createCategoriesChart() {
        const ctx = document.getElementById('categoriesChart');
        if (!ctx) return;
        
        const data = {
            labels: ['Ficção', 'Romance', 'Técnico', 'Infantil', 'História'],
            datasets: [{
                data: [30, 25, 20, 15, 10],
                backgroundColor: [
                    '#3b82f6',
                    '#ec4899',
                    '#10b981',
                    '#f59e0b',
                    '#8b5cf6'
                ],
                borderWidth: 2,
                borderColor: '#ffffff'
            }]
        };
        
        this.charts.categories = new Chart(ctx, {
            type: 'doughnut',
            data: data,
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    },
                    title: {
                        display: true,
                        text: 'Categorias Mais Emprestadas'
                    }
                }
            }
        });
    }
    
    createBooksStatusChart() {
        const ctx = document.getElementById('booksStatusChart');
        if (!ctx) return;
        
        const data = {
            labels: ['Disponíveis', 'Emprestados', 'Manutenção'],
            datasets: [{
                data: [150, 45, 5],
                backgroundColor: ['#10b981', '#f59e0b', '#ef4444'],
                borderWidth: 2,
                borderColor: '#ffffff'
            }]
        };
        
        this.charts.status = new Chart(ctx, {
            type: 'pie',
            data: data,
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    },
                    title: {
                        display: true,
                        text: 'Status dos Livros'
                    }
                }
            }
        });
    }
    
    createMiniStatsCharts() {
        // Gráfico sparkline para empréstimos
        this.createSparkline('sparklineLoans', [5, 8, 12, 15, 18, 22, 25]);
        
        // Gráfico sparkline para novos cadastros
        this.createSparkline('sparklineBooks', [2, 4, 3, 6, 8, 5, 7]);
    }
    
    createSparkline(elementId, data) {
        const ctx = document.getElementById(elementId);
        if (!ctx) return;
        
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['', '', '', '', '', '', ''],
                datasets: [{
                    data: data,
                    borderColor: '#3b82f6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    pointRadius: 0,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    x: {
                        display: false
                    },
                    y: {
                        display: false
                    }
                },
                elements: {
                    point: {
                        radius: 0
                    }
                }
            }
        });
    }
    
    // Atualizar gráficos com dados reais da API
    updateCharts() {
        fetch('/api/charts-data')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.updateLoansChart(data.loans);
                this.updateCategoriesChart(data.categories);
                this.updateBooksStatusChart(data.status);
            }
        })
        .catch(error => {
            console.error('Erro ao atualizar gráficos:', error);
        });
    }
    
    updateLoansChart(data) {
        if (this.charts.loans) {
            this.charts.loans.data.labels = data.labels;
            this.charts.loans.data.datasets[0].data = data.values;
            this.charts.loans.update();
        }
    }
    
    updateCategoriesChart(data) {
        if (this.charts.categories) {
            this.charts.categories.data.labels = data.labels;
            this.charts.categories.data.datasets[0].data = data.values;
            this.charts.categories.update();
        }
    }
    
    updateBooksStatusChart(data) {
        if (this.charts.status) {
            this.charts.status.data.labels = data.labels;
            this.charts.status.data.datasets[0].data = data.values;
            this.charts.status.update();
        }
    }
    
    // Exportar gráfico como imagem
    exportChart(chartName) {
        const chart = this.charts[chartName];
        if (chart) {
            const link = document.createElement('a');
            link.download = `relatorio-${chartName}.png`;
            link.href = chart.toBase64Image();
            link.click();
        }
    }
    
    // Redimensionar gráficos quando necessário
    resizeCharts() {
        Object.values(this.charts).forEach(chart => {
            chart.resize();
        });
    }
}

// Inicializar gráficos quando Chart.js estiver disponível
document.addEventListener('DOMContentLoaded', function() {
    if (typeof Chart !== 'undefined') {
        window.reportsCharts = new ReportsCharts();
        console.log('✅ Gráficos de relatórios inicializados!');
        
        // Atualizar gráficos quando a janela for redimensionada
        window.addEventListener('resize', () => {
            if (window.reportsCharts) {
                window.reportsCharts.resizeCharts();
            }
        });
    } else {
        console.warn('⚠️ Chart.js não encontrado - gráficos desabilitados');
    }
});
