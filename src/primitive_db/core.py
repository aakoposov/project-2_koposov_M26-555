"""Управление таблицами и CRUD-операции"""

from primitive_db.constants import ID_COLUMN, VALID_TYPES
from primitive_db.decorators import (
    confirm_action,
    create_cacher,
    handle_db_errors,
    log_time,
)

cache_result = create_cacher()


def matches(record, where_clause):
    """Проверяет, подходит ли запись под условие where"""
    for key, value in where_clause.items():
        if record.get(key) != value:
            return False
    return True


@handle_db_errors
def create_table(metadata, table_name, columns):
    """Создаёт таблицу, добавляя столбец ID:int, и возвращает метаданные"""
    if table_name in metadata:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return metadata

    for column in columns:
        parts = column.split(":")
        if len(parts) != 2 or parts[1] not in VALID_TYPES:
            print(f"Некорректное значение: {column}. Попробуйте снова.")
            return metadata

    table_columns = [ID_COLUMN] + columns
    metadata[table_name] = table_columns
    print(
        f'Таблица "{table_name}" успешно создана со столбцами: '
        f'{", ".join(table_columns)}'
    )
    return metadata


@handle_db_errors
@confirm_action("удаление таблицы")
def drop_table(metadata, table_name):
    """Удаляет таблицу"""
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return metadata
    del metadata[table_name]
    print(f'Таблица "{table_name}" успешно удалена.')
    return metadata


@handle_db_errors
@log_time
def insert(metadata, table_name, values, table_data):
    """Добавляет запись в таблицу"""
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return table_data

    columns = metadata[table_name][1:]
    if len(columns) != len(values):
        print(f"Ошибка: ожидается {len(columns)} значений, получено {len(values)}.")
        return table_data

    new_id = max((row["ID"] for row in table_data), default=0) + 1
    record = {"ID": new_id}
    for column, value in zip(columns, values):
        name, type_name = column.split(":")
        if type(value).__name__ != type_name:
            print(f"Некорректное значение: {value}. Попробуйте снова.")
            return table_data
        record[name] = value

    table_data.append(record)
    print(f'Запись с ID={new_id} успешно добавлена в таблицу "{table_name}".')
    return table_data


@handle_db_errors
@log_time
def select(table_data, where_clause=None):
    """Возвращает записи по условию, результат кэшируется"""
    key = f"{table_data}|{where_clause}"

    def compute():
        if where_clause is None:
            return table_data
        return [record for record in table_data if matches(record, where_clause)]

    return cache_result(key, compute)


@handle_db_errors
def update(table_data, set_clause, where_clause):
    """Обновляет записи по условию"""
    for record in table_data:
        if matches(record, where_clause):
            record.update(set_clause)
    return table_data


@handle_db_errors
@confirm_action("удаление записи")
def delete(table_data, where_clause):
    """Удаляет записи по условию"""
    return [record for record in table_data if not matches(record, where_clause)]