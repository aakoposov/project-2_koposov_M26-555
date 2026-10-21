import shlex

import prompt
from prettytable import PrettyTable

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

META_FILE = "db_meta.json"


def print_help():

    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип>"
          " .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print("<command> insert into <имя_таблицы> values (<значение1>, ...)"
          " - создать запись")
    print("<command> select from <имя_таблицы> [where <столбец> = <значение>]"
          " - прочитать записи")
    print("<command> update <имя_таблицы> set <столбец> = <значение> where <столбец> ="
          " <значение> - обновить запись")
    print("<command> delete from <имя_таблицы> where <столбец> ="
          " <значение> - удалить запись")
    print("<command> info <имя_таблицы> - информация о таблице")

    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def run():
    print('***База данных***')
    print_help()
    while True:
        metadata = load_metadata(META_FILE)
        user_input = prompt.string(">>>Введите команду: ")
        try:
            args = shlex.split(user_input)
        except ValueError:
            print(f'Некорректное значение: {user_input}. Попробуйте снова.')
            continue
        if not args:
            continue
        command = args[0]
        match command:
            case "create_table":
                if len(args) >= 3:
                    metadata = create_table(metadata, args[1], args[2:])
                    save_metadata(META_FILE, metadata)
                else:
                    print(f'Некорректное значение: {user_input}. Попробуйте снова.')
            case "drop_table":
                if len(args) == 2:
                    metadata = drop_table(metadata, args[1])
                    save_metadata(META_FILE, metadata)
                else:
                    print(f'Некорректное значение: {user_input}. Попробуйте снова.')
            case "insert":
                if not(len(args) >= 5 and args[1] == "into" and args[3] == "values"):
                    print(f'Некорректное значение: {user_input}. Попробуйте снова.')
                    continue
                table_name = args[2]
                try:
                    values = parse_values_list(user_input.split("values", 1)[1])
                except ValueError:
                    print(f'Некорректное значение: {user_input}. Попробуйте снова.')
                    continue
                if table_name not in metadata:
                    print(f'Ошибка: Таблица "{table_name}" не существует.')
                    continue
                table_data = load_table_data(table_name)
                table_data = insert(metadata, table_name, values, table_data)
                save_table_data(table_name, table_data)
            case "select":
                if not (len(args) >= 3 and args[1] == "from"):
                    print(f'Некорректное значение: {user_input}. Попробуйте снова.')
                    continue
                table_name = args[2]
                if table_name not in metadata:
                    print(f'Ошибка: Таблица "{table_name}" не существует.')
                    continue
                where_clause = None
                if len(args) > 3 and args[3] == "where":
                    try:
                        where_clause = parse_condition(user_input.split("where", 1)[1])
                    except ValueError:
                        print(f"Некорректное значение: {user_input}. Попробуйте снова.")
                        continue
                table_data = load_table_data(table_name)
                rows = select(table_data, where_clause)
                names = [column.split(":")[0] for column in metadata[table_name]]
                table = PrettyTable()
                table.field_names = names
                for record in rows:
                    table.add_row([record[name] for name in names])
                print(table)
            case "delete":
                if not (len(args) >= 5 and args[1] == "from" and args[3] == "where"):
                    print(f"Некорректное значение: {user_input}. Попробуйте снова.")
                    continue
                table_name = args[2]
                if table_name not in metadata:
                    print(f'Ошибка: Таблица "{table_name}" не существует.')
                    continue
                try:
                    where_clause = parse_condition(user_input.split("where", 1)[1])
                except ValueError:
                    print(f"Некорректное значение: {user_input}. Попробуйте снова.")
                    continue
                table_data = load_table_data(table_name)
                found = select(table_data, where_clause)
                if len(found) == 0:
                    print('Записей не найдено')
                    continue
                new_data = delete(table_data, where_clause)
                save_table_data(table_name, new_data)
                for record in found:
                    print(f'Запись с ID={record["ID"]} успешно удалена из таблицы '
                          f'"{table_name}".')
            case "update":
                if not (
                        len(args) >= 6
                        and args[2] == "set"
                        and "where" in args
                ):
                    print(f"Некорректное значение: {user_input}. Попробуйте снова.")
                    continue
                table_name = args[1]
                if table_name not in metadata:
                    print(f'Ошибка: Таблица "{table_name}" не существует.')
                    continue
                try:
                    rest = user_input.split(" set ", 1)[1]
                    set_part, where_part = rest.split(" where ", 1)
                    set_clause = parse_condition(set_part)
                    where_clause = parse_condition(where_part)
                except (ValueError, IndexError):
                    print(f"Некорректное значение: {user_input}. Попробуйте снова.")
                    continue
                table_data = load_table_data(table_name)
                found = select(table_data, where_clause)
                if not found:
                    print("Записей по условию не найдено.")
                    continue
                new_data = update(table_data, set_clause, where_clause)
                save_table_data(table_name, new_data)
                for record in found:
                    print(
                        f'Запись с ID={record["ID"]} в таблице '
                        f'"{table_name}" успешно обновлена.'
                    )
            case "info":
                if len(args) != 2:
                    print(f"Некорректное значение: {user_input}. Попробуйте снова.")
                    continue
                table_name = args[1]
                if table_name not in metadata:
                    print(f'Ошибка: Таблица "{table_name}" не существует.')
                    continue
                table_data = load_table_data(table_name)
                print(f"Таблица: {table_name}")
                print(f"Столбцы: {', '.join(metadata[table_name])}")
                print(f"Количество записей: {len(table_data)}")
            case "list_tables":
                for table_name in metadata:
                    print(f'- {table_name}')
            case "help":
                print_help()
            case "exit":
                break
            case _:
                print(f'Функции {command} нет. Попробуйте снова.')

