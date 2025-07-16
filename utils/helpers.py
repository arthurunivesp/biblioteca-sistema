from datetime import datetime, date

def format_date(value, format='%Y-%m-%d'):
    """Formata um objeto de data ou datetime para uma string."""
    if value is None:
        return ""
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value).date()
        except ValueError:
            return value
    elif not isinstance(value, (datetime, date)):
        return str(value)
    return value.strftime(format)

def days_ago(value):
    """Calcula há quantos dias uma data ocorreu."""
    if value is None:
        return ""
    if isinstance(value, datetime):
        value = value.date()
    elif not isinstance(value, date):
        try:
            value = datetime.fromisoformat(str(value)).date()
        except (ValueError, TypeError):
            return ""
    delta = date.today() - value
    if delta.days == 0:
        return "hoje"
    if delta.days == 1:
        return "ontem"
    if delta.days > 0:
        return f"há {delta.days} dias"
    return f"em {abs(delta.days)} dias"  # Para datas futuras

def days_remaining(value):
    """Calcula quantos dias faltam para uma data."""
    if value is None:
        return 0
    if isinstance(value, datetime):
        value = value.date()
    elif not isinstance(value, date):
        try:
            value = datetime.fromisoformat(str(value)).date()
        except (ValueError, TypeError):
            return 0
    delta = value - date.today()
    return max(0, delta.days)  # Retorna 0 se a data já passou
