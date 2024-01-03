import logging
from requests import RequestException
from exceptions import ParserFindTagException, NoResponseException


def get_response(session, url):
    try:
        response = session.get(url)
        response.encoding = 'utf-8'
        return response
    except RequestException as error:
        logging.exception(
            f'Ошибка при загрузке страницы {url}',
            stack_info=True
        )
        raise NoResponseException(
            f'Нет ответа от страницы {url}, Ошибка соединения: {error}'
        )


def find_tag(soup, tag, attrs=None):
    search_tag = soup.find(tag, attrs=attrs if attrs else {})
    if search_tag is None:
        error_msg = f'Не найден тег {tag} {attrs}'
        logging.error(error_msg, stack_info=True)
        raise ParserFindTagException(error_msg)
    return search_tag
