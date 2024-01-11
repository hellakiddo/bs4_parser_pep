from prettytable import PrettyTable

import csv
import datetime as dt
import logging
import os

from constants import (
    BASE_DIR, DATETIME_FORMAT,
    LOG_MESSAGE_FILE_SAVED,
    LOG_MESSAGE_RESULTS_SAVED
)


def control_output(input_data, cli_args, output_type=None):
    output_type = output_type or cli_args.output
    OUTPUT_TYPES.get(output_type, default_output)(input_data, cli_args)


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
    results_dir = BASE_DIR / 'results'
    results_dir.mkdir()
    parser_mode = cli_args.mode
    formatted_dt = dt.datetime.now().strftime(DATETIME_FORMAT)
    file_name = f'{parser_mode}_{formatted_dt}.csv'
    file_path = f'{results_dir}/{file_name}'
    with open(file_path, 'w', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(input_data)
    logging.info(LOG_MESSAGE_FILE_SAVED.format(file_path))


OUTPUT_TYPES = {
    'pretty': pretty_output,
    'file': file_output,
    None: default_output,
}


def save_results(results, parser_mode, args):
    try:
        output_folder = BASE_DIR / 'results'
        output_folder.mkdir()
        output_file = os.path.join(
            output_folder, f'{parser_mode}_output.csv'
        )
        control_output(results, args)
        logging.info(LOG_MESSAGE_RESULTS_SAVED.format(output_file))
        return LOG_MESSAGE_RESULTS_SAVED.format(output_file)
    except Exception as e:
        logging.error(
            f'Произошла ошибка при сохранении результатов: {str(e)}'
        )
