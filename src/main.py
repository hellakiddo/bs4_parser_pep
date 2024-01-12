import logging
import re
from collections import defaultdict
from urllib.parse import urljoin

import requests
import requests_cache
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import (
    BASE_DIR, EXPECTED_STATUS, MAIN_DOC_URL,
    MAIN_PEP_URL,
    DOWNLOADS_DIRECTORY, LOG_MESSAGE_TEMPLATE
)
from exceptions import NoVersionsFoundError
from outputs import control_output
from utils import find_tag, create_soup

DOWNLOAD_SUCCESS_MESSAGE = 'Архив успешно загружен'
LOG_MESSAGE_START = 'Парсер начал работать'
LOG_MESSAGE_ARGS = 'Аргументы командной строки: {}'
LOG_MESSAGE_CACHE_CLEARED = 'Кэш очищен'
LOG_MESSAGE_END = 'Парсер завершил работу.'
LOG_ERROR_MESSAGE = "Ошибка при создании soup для {}: {}"
LOG_MAIN_ERROR_MESSAGE = "Произошла ошибка: {}"
NO_SIDEBAR_FUNCTIONS = 'На боковой панели не найдено ни одной версии'

def whats_new(session):
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    soup = create_soup(session, whats_new_url)
    sections_by_python = soup.select(
        '#what-s-new-in-python div.toctree-wrapper li.toctree-l1 a'
    )
    result = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]
    error_messages = []
    for version_a_tag in tqdm(sections_by_python, desc='Выполнение парсинга'):
        href = version_a_tag['href']
        version_link = urljoin(whats_new_url, href)
        if version_a_tag:
            continue
        try:
            soup = create_soup(session, version_link)
            h1 = find_tag(soup, 'h1')
            dl = find_tag(soup, 'dl')
            dl_text = dl.text.replace('\n', ' ')
            processed_data = (version_link, h1.text, dl_text)
            result.append(processed_data)
        except requests.RequestException as e:
            error_message = "Ошибка при создании soup для {}: {}".format(
                version_link, e
            )
            error_messages.append(error_message)
    for error_message in error_messages:
        logging.error(error_message)

    return result

def latest_versions(session):
    soup = create_soup(session, MAIN_DOC_URL)
    sidebar = find_tag(soup, 'div', attrs={'class': 'sphinxsidebarwrapper'})
    ul_tags = sidebar.find_all('ul')

    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
    else:
        raise NoVersionsFoundError(
            NO_SIDEBAR_FUNCTIONS
        )

    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
    results = [('Ссылка на документацию', 'Версия', 'Статус')]

    for a_tag in a_tags:
        text_match = re.search(pattern, a_tag.text)
        version, status = text_match.groups() if text_match else (
            a_tag.text, ''
        )
        results.append((a_tag['href'], version, status))

    return results


def download(session):
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    soup = create_soup(session, downloads_url)
    pdf_link = soup.select_one(
        'div[role="main"] table.docutils a[href$="pdf-a4.zip"]'
    )['href']
    pdf_link = urljoin(downloads_url, pdf_link)
    DOWNLOADS_DIR = BASE_DIR / DOWNLOADS_DIRECTORY
    DOWNLOADS_DIR.mkdir(parents=False, exist_ok=True)
    archive_path = DOWNLOADS_DIR / pdf_link.split('/')[-1]
    response = session.get(pdf_link)

    with open(archive_path, 'wb') as file:
        file.write(response.content)
    logging.info(DOWNLOAD_SUCCESS_MESSAGE)


def pep(session):
    soup = create_soup(session, MAIN_PEP_URL)
    main_tag = find_tag(
        soup, 'section', {'id': 'numerical-index'}
    )
    peps_row = main_tag.find_all('tr')
    count_status_in_cards = defaultdict(int)
    log_messages = []

    for pep_row in tqdm(peps_row[1:], desc="Обработка строк PEP"):
        pep_href_tag = pep_row.a['href']
        pep_link = urljoin(MAIN_PEP_URL, pep_href_tag)
        try:
            soup = create_soup(session, pep_link)
            main_card_tag = find_tag(
                soup, 'section', {'id': 'pep-content'}
            )
            main_card = find_tag(
                main_card_tag, 'dl', {'class': 'rfc2822 field-list simple'}
            )
        except requests.RequestException as e:
            log_messages.append(LOG_ERROR_MESSAGE.format(pep_link, e))
            continue
        for row, tag in enumerate(main_card):
            if tag.name == 'dt' and tag.text == 'Status:':
                continue
            card_status = tag.next_sibling.next_sibling.string
            count_status_in_cards[card_status] += 1
            if len(peps_row[row + 1].td.text) != 1:
                table_status = peps_row[row + 1].td.text[1:]
                if card_status[0] != table_status:
                    log_messages.append(LOG_MESSAGE_TEMPLATE.format(
                        pep_link, card_status, ', '.join(
                            EXPECTED_STATUS[table_status]
                        )
                    ))
    return [
        ('Статус', 'Количество'),
        *count_status_in_cards.items(),
        ('Всего', len(peps_row) - 1),
    ]


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep,
}


def main():
    try:
        configure_logging()
        logging.info(LOG_MESSAGE_START)
        arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
        args = arg_parser.parse_args()
        logging.info(LOG_MESSAGE_ARGS.format(args))
        session = requests_cache.CachedSession()
        if args.clear_cache:
            session.cache.clear()
            logging.info(LOG_MESSAGE_CACHE_CLEARED)
        parser_mode = args.mode
        results = MODE_TO_FUNCTION[parser_mode](session)
        if results is not None:
            control_output(results, parser_mode, args)
    except Exception as e:
        logging.error(LOG_MAIN_ERROR_MESSAGE.format(e))


if __name__ == '__main__':
    main()
