import logging
from bs4 import BeautifulSoup

from requests import RequestException

from exceptions import ParserFindTagException


def get_response(session, url, default_encoding='utf-8'):
    try:
        response = session.get(url)
        response.encoding = default_encoding
        return response
    except RequestException as error:
        error_message = (
            'Нет ответа от страницы {}, Ошибка соединения: {}'.format(
                url, error
            )
        )
        logging.exception(error_message, stack_info=True)
        raise ConnectionError(error_message)


def find_tag(soup, tag, attrs=None):
    search_tag = soup.find(tag, attrs=attrs if attrs else {})
    if search_tag is None:
        error_message = 'Не найден тег {} {}'.format(tag, attrs)
        raise ParserFindTagException(error_message)
    return search_tag

PARSE_FORMAT = 'lxml'

def create_soup(session, url, parse_format=PARSE_FORMAT):
    return BeautifulSoup(get_response(session, url).text, parse_format)
