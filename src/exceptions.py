class ParserFindTagException(Exception):
    """Парсер не может найти тег."""
    pass


class NoResponseException(Exception):
    """От URL нет ответа."""
    pass


class NoVersionsFoundError(Exception):
    """Версия не найдена."""
    pass
