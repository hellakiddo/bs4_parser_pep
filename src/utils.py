from requests import RequestException

from bs4 import BeautifulSoup

from exceptions import ParserFindTagException

ERROR_MESSAGE_GET_RESPONSE ='Нет ответа от страницы {}, Ошибка соединения: {}'
ERROR_MESSAGE_FIND_TAG = 'Не найден тег {} {}'


def get_response(session, url, encoding='utf-8'):
    try:
        response = session.get(url)
        response.encoding = encoding
        return response
    except RequestException as error:
        raise ConnectionError(ERROR_MESSAGE_GET_RESPONSE.format(url, error))


def find_tag(soup, tag, attrs=None):
    search_tag = soup.find(tag, attrs=attrs if attrs else {})
    if search_tag is None:
        raise ParserFindTagException(
            ERROR_MESSAGE_FIND_TAG.format(tag, attrs)
        )
    return search_tag



def create_soup(session, url, parse_format='lxml'):
    return BeautifulSoup(get_response(session, url).text, parse_format)
