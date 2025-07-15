# 📚 Sistema de Biblioteca - Sala de Leitura

Sistema completo de gestão de biblioteca escolar desenvolvido em Flask.

## 🚀 Funcionalidades

- ✅ **Gestão de Livros**: Cadastro, edição, busca e controle de exemplares
- ✅ **Localização Inteligente**: Sistema de estantes, prateleiras e posições
- ✅ **Gestão de Alunos**: Cadastro completo com responsáveis
- ✅ **Sistema de Empréstimos**: Controle completo de empréstimos e devoluções
- ✅ **Scanner QR/Código de Barras**: Leitor USB integrado
- ✅ **Categorias Personalizáveis**: 50+ gêneros literários pré-cadastrados
- ✅ **Relatórios Completos**: Rankings e estatísticas
- ✅ **Interface Moderna**: Bootstrap 5 + design responsivo

## 🛠️ Instalação

### Pré-requisitos
- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

### 1. Clone ou baixe o projeto
```bash
# Se usar Git
git clone <seu-repositorio>
cd sala-de-leitura

# Ou extraia o ZIP baixado
2. Crie um ambiente virtual (RECOMENDADO)
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
3. Instale as dependências
pip install -r requirements.txt
4. Configure o banco de dados
python database/init_db.py
5. Execute a aplicação
python run.py
6. Acesse o sistema
Abra seu navegador e vá para: http://localhost:5000

📖 Como Usar
1. Dashboard
Visão geral do sistema
Estatísticas em tempo real
Ações rápidas
2. Cadastrar Livros
Scanner QR/código de barras USB
Localização automática de exemplares
Sistema: Estante-Prateleira-Posição (Ex: A-1-5)
3. Gestão de Alunos
Cadastro completo
Dados do responsável
Controle de turmas
4. Empréstimos
Scanner para identificar livros
Seleção de alunos
Controle de datas e devoluções
5. Relatórios
Top leitores
Livros mais emprestados
Estatísticas por turma
🔧 Configuração Avançada
Personalizar Configurações
Edite o arquivo config.py:

# Duração padrão dos empréstimos (dias)
LOANS_DURATION_DAYS = 14

# Livros por página
BOOKS_PER_PAGE = 20
Backup do Banco de Dados
O arquivo database/database.db contém todos os dados. Faça backup regularmente!

📱 Uso do Leitor de Código de Barras
Conecte o leitor USB
No sistema, clique em "Escanear"
Clique no campo de entrada
Passe o leitor sobre o código
O código aparece automaticamente
🐛 Resolução de Problemas
Erro de Dependências
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
Erro de Banco de Dados
rm database/database.db
python database/init_db.py
Porta em Uso
Edite run.py e mude a porta:

app.run(debug=True, port=5001)
📞 Suporte
Criado para gestão eficiente de bibliotecas escolares. Sistema otimizado para bibliotecários e professores.

📄 Licença
Projeto educacional - uso livre para escolas e instituições de ensino.


📁 Estrutura Completa do Projeto
sala-de-leitura/
├── README.md
├── requirements.txt
├── config.py
├── app.py
├── run.py
├── .env.example
├── .gitignore
├── database/
│   ├── __init__.py
│   ├── models.py
│   └── init_db.py
├── static/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   ├── main.js
│   │   ├── scanner.js
│   │   └── charts.js
│   └── images/
│       └── logo.png
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   ├── books/
│   │   ├── add_book.html
│   │   ├── search_books.html
│   │   ├── edit_book.html
│   │   └── book_details.html
│   ├── students/
│   │   ├── students.html
│   │   ├── add_student.html
│   │   └── edit_student.html
│   ├── loans/
│   │   ├── loans.html
│   │   ├── new_loan.html
│   │   └── loan_details.html
│   ├── categories/
│   │   ├── categories.html
│   │   └── add_category.html
│   └── reports/
│       └── reports.html
└── utils/
    ├── __init__.py
    └── helpers.py