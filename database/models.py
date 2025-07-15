from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import uuid

db = SQLAlchemy()

def generate_uuid():
    return str(uuid.uuid4())

class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    color = db.Column(db.String(7), default='#3b82f6')
    active = db.Column(db.Boolean, default=True)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    updated_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamento - CORRIGIDO
    books = db.relationship('Book', backref='category_obj', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'color': self.color,
            'active': self.active,
            'created_date': self.created_date.isoformat() if self.created_date else None
        }

class Book(db.Model):
    __tablename__ = 'books'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(200), nullable=False)
    isbn = db.Column(db.String(20))
    total_copies = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(36), db.ForeignKey('categories.id'))
    publisher = db.Column(db.String(200))
    publication_year = db.Column(db.Integer)
    description = db.Column(db.Text)
    cover_image = db.Column(db.String(500))
    qr_code = db.Column(db.String(100), unique=True)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    updated_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos - CORRIGIDOS
    copies = db.relationship('BookCopy', backref='book', lazy=True, cascade='all, delete-orphan')
    loans = db.relationship('Loan', backref='book', lazy=True)
    
    @property
    def available_copies(self):
        return len([copy for copy in self.copies if copy.status == 'available'])
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'isbn': self.isbn,
            'total_copies': self.total_copies,
            'available_copies': self.available_copies,
            'category': self.category,
            'category_name': self.category_obj.name if self.category_obj else None,
            'publisher': self.publisher,
            'publication_year': self.publication_year,
            'description': self.description,
            'cover_image': self.cover_image,
            'qr_code': self.qr_code,
            'created_date': self.created_date.isoformat() if self.created_date else None
        }

class BookCopy(db.Model):
    __tablename__ = 'book_copies'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    book_id = db.Column(db.String(36), db.ForeignKey('books.id'), nullable=False)
    copy_number = db.Column(db.Integer, nullable=False)
    shelf = db.Column(db.String(10), nullable=False)
    shelf_section = db.Column(db.String(10), nullable=False)
    position_number = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='available')  # available, loaned, maintenance, lost
    condition = db.Column(db.String(20), default='good')  # excellent, good, fair, poor
    notes = db.Column(db.Text)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    updated_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamento - CORRIGIDO
    loans = db.relationship('Loan', backref='book_copy', lazy=True)
    
    @property
    def location(self):
        return f"{self.shelf}-{self.shelf_section}-{self.position_number}"
    
    def to_dict(self):
        return {
            'id': self.id,
            'book_id': self.book_id,
            'copy_number': self.copy_number,
            'shelf': self.shelf,
            'shelf_section': self.shelf_section,
            'position_number': self.position_number,
            'location': self.location,
            'status': self.status,
            'condition': self.condition,
            'notes': self.notes
        }

class Student(db.Model):
    __tablename__ = 'students'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    name = db.Column(db.String(200), nullable=False)
    class_room = db.Column(db.String(50), nullable=False)
    birth_year = db.Column(db.Integer, nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    guardian_name = db.Column(db.String(200), nullable=False)
    guardian_phone = db.Column(db.String(20))
    registration_number = db.Column(db.String(50), unique=True)
    active = db.Column(db.Boolean, default=True)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    updated_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamento - CORRIGIDO
    loans = db.relationship('Loan', backref='student', lazy=True)
    
    @property
    def age(self):
        return datetime.now().year - self.birth_year
    
    @property
    def total_loans(self):
        return len(self.loans)
    
    @property
    def active_loans(self):
        return len([loan for loan in self.loans if loan.status == 'active'])
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'class_room': self.class_room,
            'birth_year': self.birth_year,
            'age': self.age,
            'phone': self.phone,
            'address': self.address,
            'guardian_name': self.guardian_name,
            'guardian_phone': self.guardian_phone,
            'registration_number': self.registration_number,
            'active': self.active,
            'total_loans': self.total_loans,
            'active_loans': self.active_loans
        }

class Loan(db.Model):
    __tablename__ = 'loans'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    student_id = db.Column(db.String(36), db.ForeignKey('students.id'), nullable=False)
    book_id = db.Column(db.String(36), db.ForeignKey('books.id'), nullable=False)
    book_copy_id = db.Column(db.String(36), db.ForeignKey('book_copies.id'), nullable=False)
    loan_date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    expected_return_date = db.Column(db.Date, nullable=False)
    actual_return_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='active')  # active, returned, overdue
    notes = db.Column(db.Text)
    librarian_id = db.Column(db.String(36))  # Para futuras implementações
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    updated_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @property
    def is_overdue(self):
        if self.status == 'active' and self.expected_return_date:
            return datetime.now().date() > self.expected_return_date
        return False
    
    @property
    def days_overdue(self):
        if self.is_overdue:
            return (datetime.now().date() - self.expected_return_date).days
        return 0
    
    @property
    def days_remaining(self):
        if self.status == 'active' and self.expected_return_date:
            delta = self.expected_return_date - datetime.now().date()
            return delta.days
        return 0
    
    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'book_id': self.book_id,
            'book_copy_id': self.book_copy_id,
            'loan_date': self.loan_date.isoformat() if self.loan_date else None,
            'expected_return_date': self.expected_return_date.isoformat() if self.expected_return_date else None,
            'actual_return_date': self.actual_return_date.isoformat() if self.actual_return_date else None,
            'status': self.status,
            'notes': self.notes,
            'is_overdue': self.is_overdue,
            'days_overdue': self.days_overdue,
            'days_remaining': self.days_remaining
        }
    