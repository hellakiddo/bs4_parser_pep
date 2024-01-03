import logging
import os
import re
from urllib.parse import urljoin
import requests_cache
from bs4 import BeautifulSoup
from tqdm import tqdm
from collections import defaultdict

from configs import configure_argument_parser, configure_logging
from constants import (
    BASE_DIR, EXPECTED_STATUS, MAIN_DOC_URL, MAIN_PEP_URL
)
from outputs import control_output
from utils import find_tag, get_response


def parse_section(session, base_url, section_id, headers):
    section_url = urljoin(base_url, section_id)
    response = get_response(session, section_url)
    soup = BeautifulSoup(response.text, 'lxml')
    section_div = find_tag(
        soup, 'section', attrs={'id': section_id}
    )
    div_with_ul = find_tag(
        section_div, 'div', attrs={'class': 'toctree-wrapper'}
    )
    sections = div_with_ul.find_all('li', attrs={'class': 'toctree-l1'})
    results = headers

    for section in tqdm(sections, desc=f'Выполнение парсинга {section_id}'):
        version_a_tag = find_tag(section, 'a')
        href = version_a_tag['href']
        version_link = urljoin(base_url, href)
        response = get_response(session, version_link)
        soup = BeautifulSoup(response.text, 'lxml')
        h1 = find_tag(soup, 'h1')
        dl = find_tag(soup, 'dl')
        dl_text = dl.text.replace('\n', ' ')
        result_row = (version_link, h1.text, dl_text)
        results.append(result_row)

    return results


def whats_new(session):
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    response = get_response(session, whats_new_url)
    soup = BeautifulSoup(
        response.text, features='lxml'
    )
    main_div = find_tag(
        soup, 'section', attrs={'id': 'what-s-new-in-python'}
    )
    div_with_ul = find_tag(
        main_div, 'div', attrs={'class': 'toctree-wrapper'}
    )
    sections_by_python = div_with_ul.find_all(
        'li', attrs={'class': 'toctree-l1'}
    )
    result = [
        ('Ссылка на статью', 'Заголовок', 'Редактор, Автор')
    ]
    for section in tqdm(
            sections_by_python, desc='Выполнение парсинга'
    ):
        version_a_tag = find_tag(section, 'a')
        href = version_a_tag['href']
        version_link = urljoin(whats_new_url, href)
        response = get_response(session, version_link)
        soup = BeautifulSoup(response.text,
                             features='lxml')
        h1 = find_tag(soup, 'h1')
        dl = find_tag(soup, 'dl')
        dl_text = dl.text.replace('\n', ' ')
        result.append(
            (version_link, h1.text, dl_text)
        )
    return result


def latest_versions(session):
    response = get_response(session, MAIN_DOC_URL)
    soup = BeautifulSoup(response.text, 'lxml')
    sidebar = find_tag(
        soup, 'div', attrs={'class': 'sphinxsidebarwrapper'}
    )
    ul_tags = sidebar.find_all('ul')

    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
    else:
        raise Exception('Ничего нет')

    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
    results = [('Ссылка на документацию', 'Версия', 'Статус')]

    for a_tag in a_tags:
        link = a_tag['href']
        text_match = re.search(pattern, a_tag.text)
        version, status = text_match.groups() if text_match else (
            a_tag.text, ''
        )
        result_row = (link, version, status)
        results.append(result_row)

    return results


def download(session):
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    response = get_response(session, downloads_url)
    soup = BeautifulSoup(response.text, 'lxml')
    main_tag = find_tag(
        soup, 'div', {'role': 'main'}
    )
    table_tag = find_tag(
        main_tag, 'table', {'class': 'docutils'}
    )
    pdf_tag = find_tag(
        table_tag, 'a', {'href': re.compile(r'.+pdf-a4\.zip$')}
    )
    pdf_link = urljoin(
        downloads_url, pdf_tag['href']
    )
    filename = pdf_link.split('/')[-1]
    downloads_dir = BASE_DIR / 'downloads'
    downloads_dir.mkdir()
    archive_path = downloads_dir / filename
    response = session.get(pdf_link)

    with open(archive_path, 'wb') as file:
        file.write(response.content)
    logging.info('Архив загружен')


def pep(session):
    response = get_response(session, MAIN_PEP_URL)
    soup = BeautifulSoup(response.text, 'lxml')
    main_tag = find_tag(
        soup, 'section', {'id': 'numerical-index'}
    )
    peps_row = main_tag.find_all('tr')
    count_status_in_card = defaultdict()
    results = ()

    for i in range(1, len(peps_row)):
        pep_href_tag = peps_row[i].a['href']
        pep_link = urljoin(MAIN_PEP_URL, pep_href_tag)
        response = get_response(session, pep_link)
        soup = BeautifulSoup(response.text, 'lxml')
        main_card_tag = find_tag(
            soup, 'section', {'id': 'pep-content'}
        )
        main_card = find_tag(
            main_card_tag, 'dl', {'class': 'rfc2822 field-list simple'}
        )

        for tag in main_card:
            if tag.name == 'dt' and tag.text == 'Status:':
                card_status = tag.next_sibling.next_sibling.string
                count_status_in_card[card_status] += 1
                if len(peps_row[i].td.text) != 1:
                    table_status = peps_row[i].td.text[1:]
                    if card_status[0] != table_status:
                        logging.info(
                            '\n'
                            'Несовпадающие статусы:\n'
                            f'{pep_link}\n'
                            f'Статус в карте: {card_status}\n'
                            f'Ожидаемые статусы:'
                            f' {EXPECTED_STATUS[table_status]}\n'
                        )
    for key, value in count_status_in_card.items():
        results.append((key, str(value)))
    results.append(('Total', len(peps_row) - 1))

    return results


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep,
}


def main():
    configure_logging()
    logging.info('Парсер начал работать')
    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()
    logging.info(
        f'Аргументы командной строки: {args}'
    )
    session = requests_cache.CachedSession()
    if args.clear_cache:
        session.cache.clear()
    parser_mode = args.mode
    results = MODE_TO_FUNCTION[parser_mode](session)
    if results is not None:
        output_folder = BASE_DIR / 'results'
        output_folder.mkdir()
        output_file = os.path.join(
            output_folder, f'{parser_mode}_output.csv'
        )
        control_output(results, args)
        logging.info(
            f'Данные сохранены в {output_file}'
        )
    logging.info(
        'Парсер завершил работу.'
    )


if __name__ == '__main__':
    main()
