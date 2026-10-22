# Primitive DB

Учебный проект: примитивная база данных на Python.

## Установка и запуск
Через Makefile:

```
make install
make run
```

Из исходников:

```
uv sync
uv run database
```

Как установленный пакет:

```
uv build
uv tool install dist/*.whl
database
```

Проверка кода линтером:

```
make lint
```

## Управление таблицами

Структура таблиц хранится в `db_meta.json`. Столбец `ID:int` добавляется
автоматически. Поддерживаемые типы: `int`, `str`, `bool`.

- `create_table <таблица> <столбец1:тип> <столбец2:тип> ...` — создать таблицу
- `list_tables` — показать список всех таблиц
- `drop_table <таблица>` — удалить таблицу
- `help` — справка
- `exit` — выход

Пример:

```
>>>Введите команду: create_table users name:str age:int is_active:bool
Таблица "users" успешно создана со столбцами: ID:int, name:str, age:int, is_active:bool
>>>Введите команду: list_tables
- users
```

## CRUD-операции

Данные каждой таблицы хранятся в отдельном файле `data/<имя_таблицы>.json`,
структура таблиц в `db_meta.json`. Столбец `ID` добавляется автоматически.

Строковые значения всегда пишутся в кавычках, булевы значения: `true` / `false`.

## Команды

- `insert into <таблица> values (<значение1>, <значение2>, ...)` — добавить запись
- `select from <таблица>` — показать все записи
- `select from <таблица> where <столбец> = <значение>` — показать записи по условию
- `update <таблица> set <столбец> = <значение> where <столбец> = <значение>` — обновить записи
- `delete from <таблица> where <столбец> = <значение>` — удалить записи
- `info <таблица>` — информация о таблице

## Пример

```
>>>Введите команду: create_table users name:str age:int is_active:bool
>>>Введите команду: insert into users values ("Sergei", 28, true)
Запись с ID=1 успешно добавлена в таблицу "users".
>>>Введите команду: select from users where age = 28
+----+--------+-----+-----------+
| ID |  name  | age | is_active |
+----+--------+-----+-----------+
| 1  | Sergei | 28  |    True   |
+----+--------+-----+-----------+
>>>Введите команду: update users set age = 29 where name = "Sergei"
Запись с ID=1 в таблице "users" успешно обновлена.
>>>Введите команду: delete from users where ID = 1
Запись с ID=1 успешно удалена из таблицы "users".
>>>Введите команду: info users
Таблица: users
Столбцы: ID:int, name:str, age:int, is_active:bool
Количество записей: 0
```

## Декораторы и обработка ошибок

- Ошибки базы данных перехватываются декоратором `handle_db_errors`.
- Опасные операции (`drop_table`, `delete`) требуют подтверждения `[y/n]`.
- Время выполнения `select` и `insert` выводится в консоль (`log_time`).
- Результаты `select` кэшируются (замыкание `create_cacher`).

## Демонстрация
   [![asciicast](https://asciinema.org/a/xybapEjiXYDIgNnH.svg)](https://asciinema.org/a/xybapEjiXYDIgNnH)

