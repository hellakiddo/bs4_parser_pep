import csv
import datetime as dt
import logging
from prettytable import PrettyTable

from constants import BASE_DIR, DATETIME_FORMAT


def control_output(input_data, cli_args):
    output = cli_args.output
    if output == 'file':
        OUTPUT_TYPES[output](input_data, cli_args)
    else:
        OUTPUT_TYPES[output](input_data)


def default_output(input_data):
    for row in input_data:
        print(*row)


def pretty_output(input_data):
    table = PrettyTable()
    table.field_names = input_data[0]
    table.align = 'l'
    table.add_rows(input_data[1:])
    print(table)


def file_output(input_data, cli_args):
    results_dir = BASE_DIR / 'results'
    results_dir.mkdir()
    parser_mode = cli_args.mode
    formatted_dt = dt.datetime.now().strftime(DATETIME_FORMAT)
    file_name = f'{parser_mode}_{formatted_dt}.csv'
    file_path = f'{results_dir}/{file_name}'
    with open(file_path, 'w', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(input_data)
    logging.info(
        f'Файл с результатами был сохранён: {file_path}'
    )


OUTPUT_TYPES = {
    'pretty': pretty_output,
    'file': file_output,
    None: default_output,
}