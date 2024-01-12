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
LOG_MESSAGE_TEMPLATE = (
    '\n'
    'Несовпадающие статусы:\n'
    '{}\n'
    'Статус в карте: {}\n'
    'Ожидаемые статусы: {}\n'
)

LOG_DIR = 'logs'
RESULTS_DIR = 'results'
DOWNLOADS_DIRECTORY = 'downloads'


PRETTY_OUTPUT = 'pretty'
FILE_OUTPUT = 'file'

NO_SIDEBAR_FUNCTIONS = 'На боковой панели не найдено ни одной версии'
