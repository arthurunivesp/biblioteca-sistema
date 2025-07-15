#!/usr/bin/env python3
"""
Script para inicializar o banco de dados da Sala de Leitura
"""

import sys
import os

# Adicionar o diretório pai ao path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from database.models import db, Category

def init_database():
    """Inicializar banco de dados e dados básicos"""
    app = create_app()
    
    with app.app_context():
        print("🗄️  Criando tabelas do banco de dados...")
        db.create_all()
        
        print("📚 Inserindo categorias básicas...")
        create_basic_categories()
        
        print("✅ Banco de dados inicializado com sucesso!")
        print(f"📍 Localização: {app.config['SQLALCHEMY_DATABASE_URI']}")

def create_basic_categories():
    """Criar categorias básicas do sistema"""
    try:
        # Verificar se já existem categorias
        if Category.query.count() > 0:
            print("⚠️  Categorias já existem, pulando criação...")
            return
        
        categories = [
            {"name": "Ficção Científica", "description": "Histórias baseadas em ciência e tecnologia futurística", "color": "#3b82f6"},
            {"name": "Fantasy", "description": "Histórias com elementos mágicos e mundos imaginários", "color": "#8b5cf6"},
            {"name": "Romance", "description": "Histórias centradas em relacionamentos amorosos", "color": "#ec4899"},
            {"name": "Suspense", "description": "Histórias que mantêm o leitor em tensão", "color": "#ef4444"},
            {"name": "Terror/Horror", "description": "Histórias para assustar e causar medo", "color": "#991b1b"},
            {"name": "Mistério/Policial", "description": "Histórias de investigação e crimes", "color": "#374151"},
            {"name": "Thriller", "description": "Histórias de ação intensa e adrenalina", "color": "#dc2626"},
            {"name": "Aventura", "description": "Histórias de expedições e jornadas emocionantes", "color": "#f97316"},
            {"name": "Drama", "description": "Histórias focadas em conflitos humanos profundos", "color": "#6b7280"},
            {"name": "Comédia", "description": "Histórias humorísticas e divertidas", "color": "#eab308"},
            {"name": "Biografia", "description": "Histórias reais de vidas de pessoas importantes", "color": "#10b981"},
            {"name": "Autobiografia", "description": "Relatos pessoais escritos pelo próprio autor", "color": "#059669"},
            {"name": "História", "description": "Livros sobre eventos e períodos históricos", "color": "#92400e"},
            {"name": "Filosofia", "description": "Obras sobre pensamento e reflexões filosóficas", "color": "#7c3aed"},
            {"name": "Psicologia", "description": "Livros sobre comportamento e mente humana", "color": "#db2777"},
            {"name": "Autoajuda", "description": "Livros para desenvolvimento pessoal", "color": "#06b6d4"},
            {"name": "Negócios", "description": "Livros sobre empreendedorismo e gestão", "color": "#065f46"},
            {"name": "Economia", "description": "Obras sobre sistema econômico e finanças", "color": "#047857"},
            {"name": "Política", "description": "Livros sobre sistemas políticos e governo", "color": "#1f2937"},
            {"name": "Religião/Espiritualidade", "description": "Obras sobre fé, religião e espiritualidade", "color": "#7c2d12"},
            {"name": "Ciência", "description": "Livros de divulgação científica", "color": "#0369a1"},
            {"name": "Medicina", "description": "Livros sobre saúde e medicina", "color": "#dc2626"},
            {"name": "Tecnologia", "description": "Livros sobre inovação e tecnologia", "color": "#4338ca"},
            {"name": "Informática", "description": "Livros sobre computação e programação", "color": "#1e40af"},
            {"name": "Engenharia", "description": "Livros técnicos de engenharia", "color": "#374151"},
            {"name": "Matemática", "description": "Livros sobre matemática e estatística", "color": "#6366f1"},
            {"name": "Física", "description": "Obras sobre física e suas aplicações", "color": "#3730a3"},
            {"name": "Química", "description": "Livros sobre química e suas aplicações", "color": "#059669"},
            {"name": "Biologia", "description": "Obras sobre vida e organismos", "color": "#16a34a"},
            {"name": "Geografia", "description": "Livros sobre lugares e mapas do mundo", "color": "#15803d"},
            {"name": "Arte", "description": "Livros sobre pintura, escultura e artes visuais", "color": "#be185d"},
            {"name": "Música", "description": "Obras sobre teoria musical e história da música", "color": "#c2410c"},
            {"name": "Teatro", "description": "Peças teatrais e teoria do teatro", "color": "#a21caf"},
            {"name": "Cinema", "description": "Livros sobre filmes e teoria cinematográfica", "color": "#1f2937"},
            {"name": "Literatura Clássica", "description": "Grandes obras da literatura mundial", "color": "#92400e"},
            {"name": "Literatura Brasileira", "description": "Obras de autores brasileiros", "color": "#16a34a"},
            {"name": "Literatura Estrangeira", "description": "Obras traduzidas de outros países", "color": "#0ea5e9"},
            {"name": "Poesia", "description": "Coletâneas de poemas e obras poéticas", "color": "#ec4899"},
            {"name": "Crônicas", "description": "Textos curtos do cotidiano", "color": "#f59e0b"},
            {"name": "Contos", "description": "Narrativas curtas e concisas", "color": "#84cc16"},
            {"name": "Ensaios", "description": "Textos reflexivos sobre diversos temas", "color": "#06b6d4"},
            {"name": "Infantil (0-6 anos)", "description": "Livros para primeira infância", "color": "#f97316"},
            {"name": "Infantil (7-10 anos)", "description": "Livros para crianças em idade escolar", "color": "#eab308"},
            {"name": "Juvenil (11-14 anos)", "description": "Livros para pré-adolescentes", "color": "#8b5cf6"},
            {"name": "Young Adult (15-18 anos)", "description": "Livros para adolescentes", "color": "#ec4899"},
            {"name": "Didático", "description": "Livros para ensino e aprendizagem", "color": "#059669"},
            {"name": "Paradidático", "description": "Material de apoio educacional", "color": "#10b981"},
            {"name": "Dicionários", "description": "Obras de consulta linguística", "color": "#374151"},
            {"name": "Enciclopédias", "description": "Obras de consulta geral", "color": "#6b7280"},
            {"name": "Guias e Manuais", "description": "Instruções e orientações práticas", "color": "#0891b2"},
            {"name": "HQs/Quadrinhos", "description": "Histórias em quadrinhos", "color": "#dc2626"},
            {"name": "Mangás", "description": "Quadrinhos japoneses", "color": "#f59e0b"},
            {"name": "Culinária", "description": "Livros de receitas e gastronomia", "color": "#ea580c"},
            {"name": "Esportes", "description": "Livros sobre atividades esportivas", "color": "#16a34a"},
            {"name": "Hobbies", "description": "Livros sobre passatempos e hobbies", "color": "#a855f7"},
            {"name": "Viagem", "description": "Guias de viagem e relatos", "color": "#0ea5e9"},
            {"name": "Fotografia", "description": "Técnicas e arte fotográfica", "color": "#6366f1"},
            {"name": "Outros", "description": "Livros que não se encaixam nas outras categorias", "color": "#6b7280"}
        ]
        
        for cat_data in categories:
            category = Category(**cat_data)
            db.session.add(category)
        
        db.session.commit()
        print(f"✅ {len(categories)} categorias criadas com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao criar categorias: {e}")
        db.session.rollback()

if __name__ == '__main__':
    init_database()