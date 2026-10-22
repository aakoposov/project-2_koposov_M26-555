"""Декораторы и замыкание для кэширования"""

import time
from functools import wraps

import prompt

from primitive_db.constants import CONFIRM_ANSWER


def handle_db_errors(func):
    """Перехватывает типичные ошибки БД и печатает сообщение"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            print(
                "Ошибка: Файл данных не найден. "
                "Возможно, база данных не инициализирована."
            )
        except KeyError as e:
            print(f"Ошибка: Таблица или столбец {e} не найден.")
        except ValueError as e:
            print(f"Ошибка валидации: {e}")
        except Exception as e:
            print(f"Произошла непредвиденная ошибка: {e}")

    return wrapper


def confirm_action(action_name):
    """Запрашивает подтверждение перед действием"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            answer = prompt.string(
                f'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: '
            )
            if answer.strip().lower() != CONFIRM_ANSWER:
                print("Операция отменена.")
                return args[0]
            return func(*args, **kwargs)

        return wrapper

    return decorator


def log_time(func):
    """Выводит время выполнения функции"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.monotonic()
        result = func(*args, **kwargs)
        elapsed = time.monotonic() - start
        print(f"Функция {func.__name__} выполнилась за {elapsed:.3f} секунд.")
        return result

    return wrapper


def create_cacher():
    """Возвращает функцию cache_result с кэшем в замыкании"""
    cache = {}

    def cache_result(key, value_func):
        if key in cache:
            return cache[key]
        result = value_func()
        cache[key] = result
        return result

    return cache_result