"""Главный цикл программы и обработка пользовательских команд."""

import shlex

import prompt
from prettytable import PrettyTable

from primitive_db.constants import (
    ID_NAME,
    KEYWORD_FROM,
    KEYWORD_INTO,
    KEYWORD_SET,
    KEYWORD_VALUES,
    KEYWORD_WHERE,
    META_FILE,
    MSG_INVALID,
    MSG_NOT_FOUND,
    MSG_TABLE_MISSING,
    PROMPT_TEXT,
)
from primitive_db.core import (
    create_table,
    delete,
    drop_table,
    insert,
    select,
    update,
)
from primitive_db.parser import parse_condition, parse_values_list
from primitive_db.utils import (
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
)


def print_help():
    """Печатает справку по командам."""
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print(
        "<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу"
    )
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print(
        "<command> insert into <имя_таблицы> values (<значение1>, ...)"
        " - создать запись"
    )
    print(
        "<command> select from <имя_таблицы> [where <столбец> = <значение>]"
        " - прочитать записи"
    )
    print(
        "<command> update <имя_таблицы> set <столбец> = <значение>"
        " where <столбец> = <значение> - обновить запись"
    )
    print(
        "<command> delete from <имя_таблицы> where <столбец> = <значение>"
        " - удалить запись"
    )
    print("<command> info <имя_таблицы> - информация о таблице")

    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def print_invalid(user_input):
    """Сообщает о некорректном вводе."""
    print(MSG_INVALID.format(user_input))


def run():
    """Главный цикл программы."""
    print("***База данных***")
    print_help()
    while True:
        metadata = load_metadata(META_FILE)
        user_input = prompt.string(PROMPT_TEXT)
        try:
            args = shlex.split(user_input)
        except ValueError:
            print_invalid(user_input)
            continue
        if not args:
            continue
        command = args[0]
        match command:
            case "create_table":
                if len(args) < 3:
                    print_invalid(user_input)
                    continue
                result = create_table(metadata, args[1], args[2:])
                if result is not None:
                    save_metadata(META_FILE, result)
            case "drop_table":
                if len(args) != 2:
                    print_invalid(user_input)
                    continue
                result = drop_table(metadata, args[1])
                if result is not None:
                    save_metadata(META_FILE, result)
            case "insert":
                if not (
                    len(args) >= 5
                    and args[1] == KEYWORD_INTO
                    and args[3] == KEYWORD_VALUES
                ):
                    print_invalid(user_input)
                    continue
                table_name = args[2]
                values_part = user_input.split(KEYWORD_VALUES, 1)[1]
                try:
                    values = parse_values_list(values_part)
                except ValueError:
                    print_invalid(user_input)
                    continue
                if table_name not in metadata:
                    print(MSG_TABLE_MISSING.format(table_name))
                    continue
                table_data = load_table_data(table_name)
                result = insert(metadata, table_name, values, table_data)
                if result is not None:
                    save_table_data(table_name, result)
            case "select":
                if not (len(args) >= 3 and args[1] == KEYWORD_FROM):
                    print_invalid(user_input)
                    continue
                table_name = args[2]
                if table_name not in metadata:
                    print(MSG_TABLE_MISSING.format(table_name))
                    continue
                where_clause = None
                if len(args) > 3 and args[3] == KEYWORD_WHERE:
                    where_part = user_input.split(KEYWORD_WHERE, 1)[1]
                    try:
                        where_clause = parse_condition(where_part)
                    except ValueError:
                        print_invalid(user_input)
                        continue
                table_data = load_table_data(table_name)
                rows = select(table_data, where_clause)
                if rows is None:
                    continue
                names = [column.split(":")[0] for column in metadata[table_name]]
                table = PrettyTable()
                table.field_names = names
                for record in rows:
                    table.add_row([record[name] for name in names])
                print(table)
            case "delete":
                if not (
                    len(args) >= 5
                    and args[1] == KEYWORD_FROM
                    and args[3] == KEYWORD_WHERE
                ):
                    print_invalid(user_input)
                    continue
                table_name = args[2]
                if table_name not in metadata:
                    print(MSG_TABLE_MISSING.format(table_name))
                    continue
                where_part = user_input.split(KEYWORD_WHERE, 1)[1]
                try:
                    where_clause = parse_condition(where_part)
                except ValueError:
                    print_invalid(user_input)
                    continue
                table_data = load_table_data(table_name)
                found = select(table_data, where_clause)
                if not found:
                    print(MSG_NOT_FOUND)
                    continue
                new_data = delete(table_data, where_clause)
                if new_data is None or len(new_data) == len(table_data):
                    continue
                save_table_data(table_name, new_data)
                for record in found:
                    print(
                        f"Запись с ID={record[ID_NAME]} успешно удалена "
                        f'из таблицы "{table_name}".'
                    )
            case "update":
                if not (
                    len(args) >= 6
                    and args[2] == KEYWORD_SET
                    and KEYWORD_WHERE in args
                ):
                    print_invalid(user_input)
                    continue
                table_name = args[1]
                if table_name not in metadata:
                    print(MSG_TABLE_MISSING.format(table_name))
                    continue
                try:
                    rest = user_input.split(f" {KEYWORD_SET} ", 1)[1]
                    set_part, where_part = rest.split(f" {KEYWORD_WHERE} ", 1)
                    set_clause = parse_condition(set_part)
                    where_clause = parse_condition(where_part)
                except (ValueError, IndexError):
                    print_invalid(user_input)
                    continue
                table_data = load_table_data(table_name)
                found = select(table_data, where_clause)
                if not found:
                    print(MSG_NOT_FOUND)
                    continue
                ids = [record[ID_NAME] for record in found]
                new_data = update(table_data, set_clause, where_clause)
                if new_data is None:
                    continue
                save_table_data(table_name, new_data)
                for record_id in ids:
                    print(
                        f"Запись с ID={record_id} в таблице "
                        f'"{table_name}" успешно обновлена.'
                    )
            case "info":
                if len(args) != 2:
                    print_invalid(user_input)
                    continue
                table_name = args[1]
                if table_name not in metadata:
                    print(MSG_TABLE_MISSING.format(table_name))
                    continue
                table_data = load_table_data(table_name)
                print(f"Таблица: {table_name}")
                print(f"Столбцы: {', '.join(metadata[table_name])}")
                print(f"Количество записей: {len(table_data)}")
            case "list_tables":
                for table_name in metadata:
                    print(f"- {table_name}")
            case "help":
                print_help()
            case "exit":
                break
            case _:
                print(f"Функции {command} нет. Попробуйте снова.")