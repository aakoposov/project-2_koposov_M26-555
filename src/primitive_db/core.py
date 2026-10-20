VALID_TYPES = ['int', 'bool', 'str']


def create_table(metadata, table_name, columns):
    if table_name in metadata:
        print('Ошибка! Такая таблица уже есть!')
        return metadata

    for column in columns:
        if len(column.split(':')) != 2 or column.split(':')[1] not in VALID_TYPES:
            print(f'Некорректное значение: {column}. Попробуйте снова.')
            return metadata

    table_columns = ['ID:int'] + columns
    metadata[table_name] = table_columns
    print(f'Таблица "{table_name}" успешно создана со столбцами: '
          f'{", ".join(table_columns)}')
    return metadata


def drop_table(metadata, table_name):
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return metadata
    del metadata[table_name]
    print(f'Таблица "{table_name}" успешно удалена.')
    return metadata


def insert(metadata, table_name, values, table_data):
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return table_data

    columns = metadata[table_name][1:]
    if len(columns) != len(values):
        print(f"Ошибка: ожидается {len(columns)} значений, получено {len(values)}.")
        return table_data

    record = {"ID": len(table_data) + 1}
    for column, value in zip(columns, values):
        name, type_name = column.split(":")
        if type(value).__name__ != type_name:
            print(f"Некорректное значение: {value}. Попробуйте снова.")
            return table_data
        record[name] = value

    table_data.append(record)
    print(f'Запись с ID={record["ID"]} успешно добавлена в таблицу "{table_name}".')
    return table_data




