from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from config import Config
from database.models import db, Book, Student, Loan, Category, BookCopy
from sqlalchemy import func, or_, extract
from datetime import datetime, timedelta
from utils.helpers import format_date, days_ago, days_remaining

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)

    # Adicionando funções utilitárias ao ambiente Jinja2
    app.jinja_env.filters['format_date'] = format_date
    app.jinja_env.filters['days_ago'] = days_ago
    app.jinja_env.filters['days_remaining'] = days_remaining

    with app.app_context():
        db.create_all()

    @app.route('/')
    def dashboard():
        total_books = db.session.query(func.count(Book.id)).scalar()
        total_students = db.session.query(func.count(Student.id)).filter_by(active=True).scalar()
        active_loans = db.session.query(func.count(Loan.id)).filter(Loan.status == 'active').scalar()
        overdue_loans = db.session.query(func.count(Loan.id)).filter(
            Loan.status == 'active', Loan.expected_return_date < datetime.now().date()
        ).scalar()

        recent_books = Book.query.order_by(Book.created_date.desc()).limit(5).all()
        recent_loans = db.session.query(Loan, Book, Student).join(Book).join(Student).filter(
            Loan.status == 'active'
        ).order_by(Loan.loan_date.desc()).limit(5).all()

        return render_template('dashboard.html',
                              total_books=total_books,
                              total_students=total_students,
                              active_loans=active_loans,
                              overdue_loans=overdue_loans,
                              recent_books=recent_books,
                              recent_loans=recent_loans)

    # --- Rotas de Livros ---
    @app.route('/books', methods=['GET'])
    def search_books():
        page = request.args.get('page', 1, type=int)
        search = request.args.get('search', '').strip()
        category_filter = request.args.get('category', '')

        query = Book.query
        if search:
            search_terms = search.split()
            for term in search_terms:
                query = query.filter(
                    or_(
                        Book.title.ilike(f'%{term}%'),
                        Book.author.ilike(f'%{term}%'),
                        Book.isbn.ilike(f'%{term}%'),
                        Book.qr_code.ilike(f'%{term}%')
                    )
                )
        if category_filter:
            query = query.filter_by(category=category_filter)

        books = query.order_by(Book.title).paginate(page=page, per_page=Config.BOOKS_PER_PAGE, error_out=False)
        categories = Category.query.filter_by(active=True).order_by(Category.name).all()

        return render_template('books/search_books.html',
                              books=books,
                              categories=categories,
                              search=search,
                              category_filter=category_filter)

    @app.route('/books/add', methods=['GET', 'POST'])
    def add_book():
        if request.method == 'POST':
            try:
                publication_year = request.form.get('publication_year')
                total_copies = request.form.get('total_copies')
                if not total_copies or not total_copies.isdigit() or int(total_copies) < 1:
                    raise ValueError("Número de cópias inválido")
                total_copies = int(total_copies)

                qr_code = request.form.get('qr_code', '').strip() or None
                isbn = request.form.get('isbn', '').strip() or None

                if qr_code and qr_code == isbn:
                    qr_code = None
                elif qr_code and Book.query.filter_by(qr_code=qr_code).first():
                    raise ValueError("O código QR já está em uso por outro livro")

                new_book = Book(
                    title=request.form['title'],
                    author=request.form['author'],
                    isbn=isbn,
                    total_copies=total_copies,
                    category=request.form['category'],
                    publisher=request.form.get('publisher', '').strip() or None,
                    publication_year=int(publication_year) if publication_year and publication_year.isdigit() else None,
                    description=request.form.get('description', '').strip() or None,
                    qr_code=qr_code
                )

                db.session.add(new_book)
                db.session.flush()

                base_shelf = request.form.get('base_shelf', 'A').upper()
                base_section = request.form.get('base_section', '1')

                for i in range(1, total_copies + 1):
                    copy = BookCopy(
                        book_id=new_book.id,
                        copy_number=i,
                        shelf=request.form.get(f'shelf_{i}', base_shelf),
                        shelf_section=request.form.get(f'shelf_section_{i}', base_section),
                        position_number=int(request.form.get(f'position_number_{i}', str(i))),
                        status='available',
                        condition=request.form.get(f'condition_{i}', 'good'),
                        notes=request.form.get(f'notes_{i}', '').strip() or None
                    )
                    db.session.add(copy)

                db.session.commit()
                flash('Livro cadastrado com sucesso!', 'success')
                return redirect(url_for('search_books'))
            except ValueError as ve:
                db.session.rollback()
                flash(f'Erro de validação: {str(ve)}', 'error')
            except Exception as e:
                db.session.rollback()
                flash(f'Erro ao cadastrar livro: {str(e)}', 'error')

        categories = Category.query.filter_by(active=True).order_by(Category.name).all()
        return render_template('books/add_book.html', categories=categories)

    @app.route('/books/<book_id>')
    def book_details(book_id):
        book = Book.query.get_or_404(book_id)
        copies = BookCopy.query.filter_by(book_id=book_id).order_by(BookCopy.copy_number).all()
        loans = Loan.query.filter_by(book_id=book_id).order_by(Loan.loan_date.desc()).limit(10).all()
        return render_template('books/book_details.html', book=book, copies=copies, loans=loans)

    @app.route('/books/<book_id>/edit', methods=['GET', 'POST'])
    def edit_book(book_id):
        book = Book.query.get_or_404(book_id)
        if request.method == 'POST':
            try:
                publication_year = request.form.get('publication_year')
                book.title = request.form['title']
                book.author = request.form['author']
                book.isbn = request.form.get('isbn', '').strip() or None
                book.category = request.form['category']
                book.publisher = request.form.get('publisher', '').strip() or None
                book.publication_year = int(publication_year) if publication_year and publication_year.isdigit() else None
                book.description = request.form.get('description', '').strip() or None
                book.qr_code = request.form.get('qr_code', '').strip() or None
                book.updated_date = datetime.utcnow()

                db.session.commit()
                flash('Livro atualizado com sucesso!', 'success')
                return redirect(url_for('book_details', book_id=book_id))
            except ValueError as ve:
                db.session.rollback()
                flash(f'Erro de validação: {str(ve)}', 'error')
            except Exception as e:
                db.session.rollback()
                flash(f'Erro ao atualizar livro: {str(e)}', 'error')

        categories = Category.query.filter_by(active=True).order_by(Category.name).all()
        return render_template('books/edit_book.html', book=book, categories=categories)

    @app.route('/books/<book_id>/delete', methods=['POST'])
    def delete_book(book_id):
        book = Book.query.get_or_404(book_id)
        active_loans = Loan.query.filter_by(book_id=book_id, status='active').count()
        if active_loans > 0:
            flash('Não é possível excluir este livro. Há empréstimos ativos.', 'error')
            return redirect(url_for('book_details', book_id=book_id))

        try:
            BookCopy.query.filter_by(book_id=book_id).delete()
            db.session.delete(book)
            db.session.commit()
            flash('Livro excluído com sucesso!', 'success')
            return redirect(url_for('search_books'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao excluir livro: {str(e)}', 'error')
            return redirect(url_for('book_details', book_id=book_id))

    # --- Rotas de Empréstimos ---
    @app.route('/loans')
    def loans():
        page = request.args.get('page', 1, type=int)
        status_filter = request.args.get('status', '')
        search = request.args.get('search', '')
        class_filter = request.args.get('class_filter', '')

        query = Loan.query
        if status_filter:
            if status_filter == 'overdue':
                query = query.filter(Loan.status == 'active', Loan.expected_return_date < datetime.now().date())
            elif status_filter in ['active', 'returned']:
                query = query.filter(Loan.status == status_filter)
        if search:
            search_term = f"%{search}%"
            query = query.join(Student).join(Book).filter(
                or_(Student.name.ilike(search_term), Book.title.ilike(search_term))
            )
        if class_filter:
            query = query.join(Student).filter(Student.class_room == class_filter)

        loans = query.order_by(Loan.loan_date.desc()).paginate(page=page, per_page=20, error_out=False)
        active_loans = db.session.query(func.count(Loan.id)).filter(Loan.status == 'active').scalar()
        returned_loans = db.session.query(func.count(Loan.id)).filter(
            Loan.status == 'returned',
            extract('month', Loan.actual_return_date) == datetime.now().month,
            extract('year', Loan.actual_return_date) == datetime.now().year
        ).scalar()
        overdue_loans = db.session.query(func.count(Loan.id)).filter(
            Loan.status == 'active', Loan.expected_return_date < datetime.now().date()
        ).scalar()
        due_this_week = db.session.query(func.count(Loan.id)).filter(
            Loan.status == 'active',
            Loan.expected_return_date >= datetime.now().date(),
            Loan.expected_return_date <= (datetime.now() + timedelta(days=7)).date()
        ).scalar()
        classes = [c[0] for c in db.session.query(Student.class_room).filter(
            Student.active == True, Student.class_room.isnot(None)
        ).distinct().order_by(Student.class_room).all()]

        return render_template('loans/loans.html',
                              loans=loans,
                              active_loans=active_loans,
                              returned_loans=returned_loans,
                              overdue_loans=overdue_loans,
                              due_this_week=due_this_week,
                              status_filter=status_filter,
                              search=search,
                              class_filter=class_filter,
                              classes=classes)

    @app.route('/loans/new', methods=['GET', 'POST'])
    def new_loan():
        student_id = request.args.get('student_id')
        book_id = request.args.get('book_id')
        today = datetime.now().date()
        return_date = today + timedelta(days=7)  # Calcular data de devolução padrão
        if request.method == 'POST':
            step = request.form.get('step', '1')
            if step == 'scan_book' or (not book_id and step == '1'):
                qr_code = request.form.get('qr_code')
                book = Book.query.filter_by(qr_code=qr_code).first()
                if not book:
                    flash('Livro não encontrado com este código!', 'error')
                    return render_template('loans/new_loan.html', step=1)
                available_copy = BookCopy.query.filter_by(book_id=book.id, status='available').first()
                if not available_copy:
                    flash('Este livro não possui exemplares disponíveis!', 'error')
                    return render_template('loans/new_loan.html', step=1)
                students = Student.query.filter_by(active=True).order_by(Student.name).all()
                return render_template('loans/new_loan.html', step=2, book=book, copy=available_copy, students=students, today=today, return_date=return_date)
            elif step == 'select_student':
                book_id = request.form['book_id'] or book_id
                copy_id = request.form['copy_id']
                student_id = request.form['student_id'] or student_id
                book = Book.query.get(book_id)
                copy = BookCopy.query.get(copy_id)
                student = Student.query.get(student_id)
                if not all([book, copy, student]):
                    flash('Dados inválidos para o empréstimo!', 'error')
                    return redirect(url_for('new_loan'))
                return render_template('loans/new_loan.html', step=3, book=book, copy=copy, student=student, today=today, return_date=return_date)
            elif step == 'confirm_loan':
                try:
                    loan_date = datetime.strptime(request.form['loan_date'], '%Y-%m-%d').date()
                    expected_return_date = datetime.strptime(request.form['expected_return_date'], '%Y-%m-%d').date()
                    if expected_return_date < loan_date:
                        raise ValueError("Data de devolução não pode ser anterior à data de empréstimo")
                    new_loan = Loan(
                        student_id=request.form['student_id'],
                        book_id=request.form['book_id'],
                        book_copy_id=request.form['copy_id'],
                        loan_date=loan_date,
                        expected_return_date=expected_return_date,
                        notes=request.form.get('notes', '').strip() or None,
                        status='active'
                    )
                    copy = BookCopy.query.get(request.form['copy_id'])
                    copy.status = 'loaned'
                    db.session.add(new_loan)
                    db.session.commit()
                    flash('Empréstimo realizado com sucesso!', 'success')
                    return redirect(url_for('loans'))
                except ValueError as ve:
                    db.session.rollback()
                    flash(f'Erro de validação: {str(ve)}', 'error')
                except Exception as e:
                    db.session.rollback()
                    flash(f'Erro ao realizar empréstimo: {str(e)}', 'error')
        elif book_id and student_id:
            # Ambos aluno e livro fornecidos, vá diretamente para a confirmação
            book = Book.query.get(book_id)
            student = Student.query.get(student_id)
            if not book or book.available_copies == 0:
                flash('Livro não encontrado ou sem exemplares disponíveis!', 'error')
                return redirect(url_for('search_books'))
            if not student or not student.active:
                flash('Aluno não encontrado ou inativo!', 'error')
                return redirect(url_for('students'))
            available_copy = BookCopy.query.filter_by(book_id=book.id, status='available').first()
            if not available_copy:
                flash('Não há exemplares disponíveis para este livro!', 'error')
                return redirect(url_for('search_books'))
            return render_template('loans/new_loan.html', step=3, book=book, copy=available_copy, student=student, today=today, return_date=return_date)
        elif book_id:
            # Apenas livro fornecido, liste alunos para seleção
            book = Book.query.get(book_id)
            if not book or book.available_copies == 0:
                flash('Livro não encontrado ou sem exemplares disponíveis!', 'error')
                return redirect(url_for('search_books'))
            available_copy = BookCopy.query.filter_by(book_id=book.id, status='available').first()
            if not available_copy:
                flash('Não há exemplares disponíveis para este livro!', 'error')
                return redirect(url_for('search_books'))
            students = Student.query.filter_by(active=True).order_by(Student.name).all()
            return render_template('loans/new_loan.html', step=2, book=book, copy=available_copy, students=students, today=today, return_date=return_date)
        elif student_id:
            # Apenas aluno fornecido, liste livros para seleção
            student = Student.query.get(student_id)
            if not student or not student.active:
                flash('Aluno não encontrado ou inativo!', 'error')
                return redirect(url_for('students'))
            books = Book.query.filter(Book.available_copies > 0).order_by(Book.title).all()
            return render_template('loans/new_loan.html', step=1, student=student, books=books, today=today, return_date=return_date)
        students = Student.query.filter_by(active=True).order_by(Student.name).all()
        return render_template('loans/new_loan.html', step=1, students=students, today=today, return_date=return_date)

    @app.route('/loans/<loan_id>/return', methods=['POST'])
    def return_loan(loan_id):
        loan = Loan.query.get_or_404(loan_id)
        if loan.status != 'active':
            flash('Este empréstimo já foi finalizado!', 'error')
            return redirect(url_for('loans'))
        try:
            loan.status = 'returned'
            loan.actual_return_date = datetime.now().date()
            copy = BookCopy.query.get(loan.book_copy_id)
            copy.status = 'available'
            db.session.commit()
            flash('Devolução registrada com sucesso!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao registrar devolução: {str(e)}', 'error')
        return redirect(url_for('loans'))

    @app.route('/loans/<loan_id>')
    def loan_details(loan_id):
        loan = Loan.query.get_or_404(loan_id)
        return render_template('loans/loan_details.html', loan=loan)

    # --- Rotas de Alunos ---
    @app.route('/students')
    def students():
        page = request.args.get('page', 1, type=int)
        search = request.args.get('search', '')
        class_filter = request.args.get('class_filter', '')

        query = Student.query.filter_by(active=True)
        if search:
            search_term = f"%{search}%"
            query = query.filter(or_(
                Student.name.ilike(search_term),
                Student.registration_number.ilike(search_term),
                Student.class_room.ilike(search_term)
            ))
        if class_filter:
            query = query.filter(Student.class_room == class_filter)

        students = query.order_by(Student.name).paginate(page=page, per_page=20, error_out=False)
        classes = [c[0] for c in db.session.query(Student.class_room).filter(
            Student.active == True, Student.class_room.isnot(None)
        ).distinct().order_by(Student.class_room).all()]

        # Agrupar alunos por turma para o template
        students_by_class = {}
        for student in students.items:
            class_room = student.class_room or "Sem Turma"
            if class_room not in students_by_class:
                students_by_class[class_room] = []
            students_by_class[class_room].append(student)

        return render_template('students/students.html',
                              students=students,
                              classes=classes,
                              search=search,
                              class_filter=class_filter,
                              students_by_class=students_by_class)

    @app.route('/students/add', methods=['GET', 'POST'])
    def add_student():
        if request.method == 'POST':
            try:
                birth_year = request.form.get('birth_year')
                if not birth_year or not birth_year.isdigit() or int(birth_year) < 1900 or int(birth_year) > datetime.now().year:
                    raise ValueError("Ano de nascimento inválido (deve ser entre 1900 e o ano atual)")
                new_student = Student(
                    name=request.form['name'].strip(),
                    class_room=request.form['class_room'].strip(),
                    birth_year=int(birth_year),
                    phone=request.form.get('phone', '').strip() or None,
                    address=request.form.get('address', '').strip() or None,
                    guardian_name=request.form['guardian_name'].strip(),
                    guardian_phone=request.form.get('guardian_phone', '').strip() or None,
                    registration_number=request.form.get('registration_number', '').strip() or None,
                    active=True
                )
                db.session.add(new_student)
                db.session.commit()
                flash('Aluno cadastrado com sucesso!', 'success')
                return redirect(url_for('students'))
            except ValueError as ve:
                db.session.rollback()
                flash(f'Erro de validação: {str(ve)}', 'error')
            except Exception as e:
                db.session.rollback()
                flash(f'Erro ao cadastrar aluno: {str(e)}', 'error')
        return render_template('students/add_student.html')

    @app.route('/students/<student_id>/edit', methods=['GET', 'POST'])
    def edit_student(student_id):
        student = Student.query.get_or_404(student_id)
        if request.method == 'POST':
            try:
                birth_year = request.form.get('birth_year')
                if not birth_year or not birth_year.isdigit() or int(birth_year) < 1900 or int(birth_year) > datetime.now().year:
                    raise ValueError("Ano de nascimento inválido (deve ser entre 1900 e o ano atual)")
                student.name = request.form['name'].strip()
                student.class_room = request.form['class_room'].strip()
                student.birth_year = int(birth_year)
                student.phone = request.form.get('phone', '').strip() or None
                student.address = request.form.get('address', '').strip() or None
                student.guardian_name = request.form['guardian_name'].strip()
                student.guardian_phone = request.form.get('guardian_phone', '').strip() or None
                student.registration_number = request.form.get('registration_number', '').strip() or None
                student.updated_date = datetime.utcnow()
                db.session.commit()
                flash('Aluno atualizado com sucesso!', 'success')
                return redirect(url_for('students'))
            except ValueError as ve:
                db.session.rollback()
                flash(f'Erro de validação: {str(ve)}', 'error')
            except Exception as e:
                db.session.rollback()
                flash(f'Erro ao atualizar aluno: {str(e)}', 'error')
        return render_template('students/edit_student.html', student=student)

    @app.route('/students/<student_id>/delete', methods=['POST'])
    def delete_student(student_id):
        student = Student.query.get_or_404(student_id)
        active_loans = Loan.query.filter_by(student_id=student_id, status='active').count()
        if active_loans > 0:
            flash('Não é possível excluir este aluno. Há empréstimos ativos.', 'error')
            return redirect(url_for('students'))
        try:
            student.active = False
            db.session.commit()
            flash('Aluno removido com sucesso!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao remover aluno: {str(e)}', 'error')
        return redirect(url_for('students'))

    # --- Rotas de Categorias ---
    @app.route('/categories')
    def categories():
        page = request.args.get('page', 1, type=int)
        search = request.args.get('search', '')

        query = Category.query
        if search:
            search_term = f"%{search}%"
            query = query.filter(or_(
                Category.name.ilike(search_term),
                Category.description.ilike(search_term)
            ))

        categories = query.order_by(Category.name).paginate(page=page, per_page=20, error_out=False)
        return render_template('categories/categories.html', categories=categories, search=search)

    @app.route('/categories/add', methods=['GET', 'POST'])
    def add_category():
        if request.method == 'POST':
            try:
                new_category = Category(
                    name=request.form['name'],
                    description=request.form.get('description', '').strip() or None,
                    color=request.form.get('color', '#3b82f6'),
                    active=True
                )
                db.session.add(new_category)
                db.session.commit()
                flash('Categoria cadastrada com sucesso!', 'success')
                return redirect(url_for('categories'))
            except Exception as e:
                db.session.rollback()
                flash(f'Erro ao cadastrar categoria: {str(e)}', 'error')
        return render_template('categories/add_category.html')

    @app.route('/categories/<category_id>/edit', methods=['GET', 'POST'])
    def edit_category(category_id):
        category = Category.query.get_or_404(category_id)
        if request.method == 'POST':
            try:
                category.name = request.form['name']
                category.description = request.form.get('description', '').strip() or None
                category.color = request.form.get('color', '#3b82f6')
                category.updated_date = datetime.utcnow()
                db.session.commit()
                flash('Categoria atualizada com sucesso!', 'success')
                return redirect(url_for('categories'))
            except Exception as e:
                db.session.rollback()
                flash(f'Erro ao atualizar categoria: {str(e)}', 'error')
        return render_template('categories/add_category.html', category=category)

    @app.route('/categories/<category_id>/delete', methods=['POST'])
    def delete_category(category_id):
        category = Category.query.get_or_404(category_id)
        books_count = Book.query.filter_by(category=category_id).count()
        if books_count > 0:
            flash(f'Não é possível excluir esta categoria. Há {books_count} livro(s) usando ela.', 'error')
            return redirect(url_for('categories'))
        try:
            db.session.delete(category)
            db.session.commit()
            flash('Categoria excluída com sucesso!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao excluir categoria: {str(e)}', 'error')
        return redirect(url_for('categories'))

    # --- Rotas de Relatórios ---
    @app.route('/reports')
    def reports():
        total_books = Book.query.count()
        total_students = Student.query.filter_by(active=True).count()
        total_loans = Loan.query.count()
        books_this_month = Book.query.filter(
            extract('month', Book.created_date) == datetime.now().month,
            extract('year', Book.created_date) == datetime.now().year
        ).count()
        students_this_month = Student.query.filter(
            extract('month', Student.created_date) == datetime.now().month,
            extract('year', Student.created_date) == datetime.now().year
        ).filter_by(active=True).count()
        loans_this_month = Loan.query.filter(
            extract('month', Loan.loan_date) == datetime.now().month,
            extract('year', Loan.loan_date) == datetime.now().year
        ).count()
        active_loans = db.session.query(func.count(Loan.id)).filter(Loan.status == 'active').scalar()
        overdue_loans = db.session.query(func.count(Loan.id)).filter(
            Loan.status == 'active', Loan.expected_return_date < datetime.now().date()
        ).scalar()
        returned_loans = db.session.query(func.count(Loan.id)).filter(
            Loan.status == 'returned',
            extract('month', Loan.actual_return_date) == datetime.now().month,
            extract('year', Loan.actual_return_date) == datetime.now().year
        ).scalar()
        due_this_week = db.session.query(func.count(Loan.id)).filter(
            Loan.status == 'active',
            Loan.expected_return_date >= datetime.now().date(),
            Loan.expected_return_date <= (datetime.now() + timedelta(days=7)).date()
        ).scalar()

        top_books = db.session.query(
            Book.title, Book.author, func.count(Loan.id).label('loan_count')
        ).join(Loan, Book.id == Loan.book_id).group_by(
            Book.id, Book.title, Book.author
        ).order_by(func.count(Loan.id).desc()).limit(10).all()

        top_students = db.session.query(
            Student.name, Student.class_room, func.count(Loan.id).label('loan_count')
        ).join(Loan, Student.id == Loan.student_id).group_by(
            Student.id, Student.name, Student.class_room
        ).order_by(func.count(Loan.id).desc()).limit(10).all()

        top_classes = db.session.query(
            Student.class_room, func.count(Student.id).label('student_count'),
            func.count(Loan.id).label('loan_count')
        ).join(Loan, Student.id == Loan.student_id, isouter=True).group_by(
            Student.class_room
        ).order_by(func.count(Loan.id).desc()).limit(10).all()

        monthly_loans = db.session.query(
            extract('month', Loan.loan_date).label('month'),
            extract('year', Loan.loan_date).label('year'),
            func.count(Loan.id).label('count')
        ).filter(Loan.loan_date >= (datetime.now() - timedelta(days=180)).date()).group_by(
            extract('year', Loan.loan_date), extract('month', Loan.loan_date)
        ).order_by(extract('year', Loan.loan_date), extract('month', Loan.loan_date)).all()
        loans_chart_data = {
            'labels': [f"{m}/{y}" for m, y, _ in monthly_loans],
            'data': [c for _, _, c in monthly_loans]
        }

        books_by_category = db.session.query(
            Category.name, func.count(Book.id).label('book_count')
        ).join(Book, Category.id == Book.category).group_by(
            Category.id, Category.name
        ).order_by(func.count(Book.id).desc()).all()
        categories_chart_data = {
            'labels': [c[0] for c in books_by_category],
            'data': [c[1] for c in books_by_category]
        }

        total_copies = db.session.query(func.count(BookCopy.id)).scalar()
        loaned_copies = db.session.query(func.count(BookCopy.id)).filter(BookCopy.status == 'loaned').scalar()
        utilization_rate = (loaned_copies / total_copies * 100) if total_copies > 0 else 0

        return render_template('reports/reports.html',
                              total_books=total_books,
                              total_students=total_students,
                              total_loans=total_loans,
                              books_this_month=books_this_month,
                              students_this_month=students_this_month,
                              loans_this_month=loans_this_month,
                              active_loans=active_loans,
                              overdue_loans=overdue_loans,
                              returned_loans=returned_loans,
                              due_this_week=due_this_week,
                              top_books=top_books,
                              top_students=top_students,
                              top_classes=top_classes,
                              loans_chart_data=loans_chart_data,
                              categories_chart_data=categories_chart_data,
                              utilization_rate=round(utilization_rate, 2))

    # --- APIs para AJAX ---
    @app.route('/api/students/search')
    def api_search_students():
        query = request.args.get('q', '')
        students = Student.query.filter(
            Student.active == True, Student.name.ilike(f'%{query}%')
        ).limit(10).all()
        return jsonify([{
            'id': s.id,
            'name': s.name,
            'class_room': s.class_room,
            'registration_number': s.registration_number
        } for s in students])

    @app.route('/api/books/search')
    def api_search_books():
        query = request.args.get('q', '')
        books = Book.query.filter(
            or_(Book.title.ilike(f'%{query}%'), Book.qr_code.ilike(f'%{query}%'))
        ).limit(10).all()
        return jsonify([{
            'id': b.id,
            'title': b.title,
            'author': b.author,
            'available_copies': b.available_copies
        } for b in books])

    @app.route('/api/scan-qr', methods=['POST'])
    def scan_qr():
        try:
            data = request.get_json()
            if not data or 'qr_code' not in data:
                return jsonify({'success': False, 'message': 'Código não fornecido'}), 400
            
            qr_code = data['qr_code'].strip()
            if not qr_code:
                return jsonify({'success': False, 'message': 'Código inválido'}), 400
            
            book = Book.query.filter_by(qr_code=qr_code).first()
            if not book:
                clean_code = qr_code.replace('-', '').replace(' ', '')
                book = Book.query.filter_by(isbn=clean_code).first()
            
            if book:
                return jsonify({
                    'success': True,
                    'book': {
                        'id': book.id,
                        'title': book.title,
                        'author': book.author,
                        'available_copies': book.available_copies
                    }
                })
            else:
                return jsonify({'success': False, 'message': 'Livro não encontrado'}), 404
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500

    @app.route('/api/book-copies/<int:book_id>')
    def api_book_copies(book_id):
        try:
            book = Book.query.get_or_404(book_id)
            copies = BookCopy.query.filter_by(book_id=book_id).all()
            return jsonify({
                'success': True,
                'copies': [{
                    'id': copy.id,
                    'copy_number': copy.copy_number,
                    'location': f"{copy.shelf}-{copy.shelf_section}-{copy.position_number}",
                    'condition': copy.condition,
                    'status': copy.status
                } for copy in copies]
            })
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500

    @app.route('/api/charts-data')
    def api_charts_data():
        try:
            monthly_loans = db.session.query(
                extract('month', Loan.loan_date).label('month'),
                extract('year', Loan.loan_date).label('year'),
                func.count(Loan.id).label('count')
            ).filter(Loan.loan_date >= (datetime.now() - timedelta(days=180)).date()).group_by(
                extract('year', Loan.loan_date), extract('month', Loan.loan_date)
            ).order_by(extract('year', Loan.loan_date), extract('month', Loan.loan_date)).all()
            
            books_by_category = db.session.query(
                Category.name, func.count(Book.id).label('book_count')
            ).join(Book, Category.id == Book.category).group_by(Category.id, Category.name).all()
            
            return jsonify({
                'success': True,
                'loans': {
                    'labels': [f"{m}/{y}" for m, y, _ in monthly_loans],
                    'values': [c for _, _, c in monthly_loans]
                },
                'categories': {
                    'labels': [c[0] for c in books_by_category],
                    'values': [c[1] for c in books_by_category]
                },
                'status': {
                    'labels': ['Disponíveis', 'Emprestados', 'Manutenção'],
                    'values': [
                        db.session.query(func.count(BookCopy.id)).filter(BookCopy.status == 'available').scalar(),
                        db.session.query(func.count(BookCopy.id)).filter(BookCopy.status == 'loaned').scalar(),
                        db.session.query(func.count(BookCopy.id)).filter(BookCopy.status == 'maintenance').scalar()
                    ]
                }
            })
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0')
        