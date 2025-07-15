from datetime import datetime, date

def format_date(value, format='%d/%m/%Y'):
    """Formata um objeto de data ou datetime para uma string."""
    if value is None:
        return ""
    if isinstance(value, str):
        # Tenta converter string para data se necessário
        try:
            value = datetime.fromisoformat(value).date()
        except ValueError:
            return value
    return value.strftime(format)

def days_ago(value):
    """Calcula há quantos dias uma data ocorreu."""
    if value is None:
        return ""
    if isinstance(value, datetime):
        value = value.date()
    delta = date.today() - value
    if delta.days == 0:
        return "hoje"
    if delta.days == 1:
        return "ontem"
    return f"há {delta.days} dias"

def days_remaining(value):
    """Calcula quantos dias faltam para uma data."""
    if value is None:
        return 0
    if isinstance(value, datetime):
        value = value.date()
    delta = value - date.today()
    return delta.days
