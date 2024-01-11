from pathlib import Path

MAIN_DOC_URL = 'https://docs.python.org/3/'
MAIN_PEP_URL = 'https://peps.python.org/'

BASE_DIR = Path(__file__).parent

DATETIME_FORMAT = '%Y-%m-%d_%H-%M-%S'
LOG_FORMAT = '"%(asctime)s - %(levelname)s - %(message)s"'

EXPECTED_STATUS = {
    'A': ['Active', 'Accepted'],
    'D': ['Deferred'],
    'F': ['Final'],
    'P': ['Provisional'],
    'R': ['Rejected'],
    'S': ['Superseded'],
    'W': ['Withdrawn'],
    '': ['Draft', 'Active'],
}
LOG_DIR = f'{BASE_DIR}/logs'
RESULTS_DIR = f'{BASE_DIR}/results'
DOWNLOADS_DIR = f'{BASE_DIR}/downloads'

PRETTY_OUTPUT = 'pretty'
FILE_OUTPUT = 'file'

LOG_MESSAGE_START = 'Парсер начал работать'
LOG_MESSAGE_ARGS = 'Аргументы командной строки: {}'
LOG_MESSAGE_CACHE_CLEARED = 'Кэш очищен'
LOG_MESSAGE_RESULTS_SAVED = 'Данные сохранены в {}'
LOG_MESSAGE_END = 'Парсер завершил работу.'
LOG_MESSAGE_FILE_SAVED = 'Файл с результатами был сохранён: {}'

