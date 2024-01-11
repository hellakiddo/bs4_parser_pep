import logging
from http import HTTPStatus
import re
import requests_cache

from urllib.parse import urljoin
from bs4 import BeautifulSoup
from tqdm import tqdm
from collections import defaultdict

from configs import configure_argument_parser, configure_logging
from constants import (
    BASE_DIR, EXPECTED_STATUS, MAIN_DOC_URL,
    MAIN_PEP_URL, LOG_MESSAGE_START, LOG_MESSAGE_ARGS,
    LOG_MESSAGE_CACHE_CLEARED
)
from outputs import save_results
from src.exceptions import NoVersionsFoundError
from utils import find_tag, get_response


def create_soup(session, url):
    response = get_response(session, url)
    return BeautifulSoup(
        response.text, 'lxml'
    ) if response.status_code == HTTPStatus.OK else None

def process_section_item(session, base_url, section_item):
    version_a_tag = find_tag(section_item, 'a')
    href = version_a_tag['href']
    version_link = urljoin(base_url, href)
    response = get_response(session, version_link)
    soup = create_soup(session, version_link)

    if soup is not None:
        h1 = find_tag(soup, 'h1')
        dl = find_tag(soup, 'dl')
        dl_text = dl.text.replace('\n', ' ')
        return version_link, h1.text, dl_text

    return None


def whats_new(session):
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    soup = create_soup(session, whats_new_url)
    if soup is None:
        logging.error("Произошла ошибка во время парсинга.")
        return []
    sections_by_python = soup.select(
        '#what-s-new-in-python div.toctree-wrapper li.toctree-l1'
    )
    result = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]

    for section_item in tqdm(sections_by_python, desc='Выполнение парсинга'):
        processed_data = process_section_item(
            session, whats_new_url, section_item
        )
        if processed_data is not None:
            result.append(processed_data)

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
            'На боковой панели не найдено ни одной версии'
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
    DOWNLOADS_DIR = BASE_DIR / 'downloads'
    DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)
    archive_path = DOWNLOADS_DIR / pdf_link.split('/')[-1]
    response = session.get(pdf_link)

    with open(archive_path, 'wb') as file:
        file.write(response.content)
    logging.info('Архив загружен')


def pep(session):
    soup = create_soup(session, MAIN_PEP_URL)
    main_tag = find_tag(
        soup, 'section', {'id': 'numerical-index'}
    )
    peps_row = main_tag.find_all('tr')
    count_status_in_card = defaultdict(int)
    results = []
    log_message = ""
    for pep_row in tqdm(peps_row[1:], desc="Processing PEP rows"):
        pep_href_tag = pep_row.a['href']
        pep_link = urljoin(MAIN_PEP_URL, pep_href_tag)
        soup = create_soup(session, pep_link)
        main_card_tag = find_tag(
            soup, 'section', {'id': 'pep-content'}
        )
        main_card = find_tag(
            main_card_tag, 'dl', {'class': 'rfc2822 field-list simple'}
        )
        for i, tag in enumerate(main_card):
            if tag.name == 'dt' and tag.text == 'Status:':
                card_status = tag.next_sibling.next_sibling.string
                count_status_in_card[card_status] += 1
                if len(peps_row[i + 1].td.text) != 1:
                    table_status = peps_row[i + 1].td.text[1:]
                    if card_status[0] != table_status:
                        log_message += (
                            '\n'
                            'Несовпадающие статусы:\n'
                            f'{pep_link}\n'
                            f'Статус в карте: {card_status}\n'
                            f'Ожидаемые статусы:'
                            f' {EXPECTED_STATUS[table_status]}\n'
                        )
                        continue

        for key, value in count_status_in_card.items():
            results.append((key, str(value)))
        results.append(('Total', len(peps_row) - 1))
    logging.info(log_message)

    return results


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep,
}


def main():
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
        save_results(results, parser_mode, args)

if __name__ == '__main__':
    main()

