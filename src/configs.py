import argparse
import logging
from logging.handlers import RotatingFileHandler

from constants import LOG_FORMAT, LOG_DIR, DATETIME_FORMAT


def configure_logging():
    LOG_DIR.mkdir()
    log_file = LOG_DIR / 'pep_parser.log'
    rotating_handler = RotatingFileHandler(
        log_file, maxBytes=10 ** 6, backupCount=5
    )
    logging.basicConfig(
        datefmt=DATETIME_FORMAT,
        format=LOG_FORMAT,
        level=logging.INFO,
        handlers=(rotating_handler, logging.StreamHandler())
    )


def configure_argument_parser(available_modes):
    parser = argparse.ArgumentParser(
        description='Парсер документации Python'
    )
    parser.add_argument(
        'mode',
        choices=available_modes,
        help='Режимы работы парсера'
    )
    parser.add_argument(
        '-o',
        '--output',
        choices=('pretty', 'file'),
        help='Дополнительные способы вывода данных'
    )
    parser.add_argument(
        '-c',
        '--clear-cache',
        action='store_true',
        help='Очистка кеша'
    )
    return parser
