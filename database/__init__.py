# Este arquivo faz com que Python trate database/ como um pacote
from .models import db, Book, Student, Loan, Category, BookCopy

__all__ = ['db', 'Book', 'Student', 'Loan', 'Category', 'BookCopy']
