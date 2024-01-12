import csv
import datetime as dt
import logging

from prettytable import PrettyTable


from constants import (
    BASE_DIR, DATETIME_FORMAT, RESULTS_DIR, PRETTY_OUTPUT, FILE_OUTPUT
)

LOG_MESSAGE_FILE_SAVED = 'Файл с результатами был сохранён: {}'
LOG_MESSAGE_RESULTS_SAVED = 'Данные сохранены в {}'


def control_output(input_data, cli_args):
    OUTPUT_TYPES.get(cli_args.output )(input_data, cli_args)


def default_output(input_data, cli_args):
    for row in input_data:
        print(*row)


def pretty_output(input_data, cli_args):
    table = PrettyTable()
    table.field_names = input_data[0]
    table.align = 'l'
    table.add_rows(input_data[1:])
    print(table)


def file_output(input_data, cli_args):
    results_dir = BASE_DIR / RESULTS_DIR
    results_dir.mkdir()
    parser_mode = cli_args.mode
    formatted_dt = dt.datetime.now().strftime(DATETIME_FORMAT)
    file_name = f'{parser_mode}_{formatted_dt}.csv'
    file_path = f'{results_dir}/{file_name}'
    with open(file_path, 'w', encoding='utf-8') as file:
        csv.writer(file, dialect=csv.excel).writerows(input_data)
    logging.info(LOG_MESSAGE_FILE_SAVED.format(file_path))


OUTPUT_TYPES = {
    PRETTY_OUTPUT: pretty_output,
    FILE_OUTPUT: file_output,
    None: default_output,
}
