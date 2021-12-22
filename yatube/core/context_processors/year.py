import datetime


def year(request):
    year = datetime.datetime.today().year
    """Добавляет переменную с текущим годом."""
    return {
        'year': year
    }
