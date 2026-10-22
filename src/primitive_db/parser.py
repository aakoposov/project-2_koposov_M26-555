def parse_value(text):
    """Преобразует строку в значение: строку, bool или int"""
    new_text = text.strip()
    if len(new_text) >= 2 and new_text[0] == new_text[-1] and new_text[0] in "\"'":
        return new_text[1:-1]
    if new_text.lower() == 'true':
        return True
    elif new_text.lower() == 'false':
        return False
    elif new_text.isdigit():
        return int(new_text)
    else:
        raise ValueError(f"Некорректное значение: {text}")


def parse_condition(text):
    """Разбирает условие вида 'age = 28' в словарь {'age': 28}"""
    parts = text.split('=',1)
    if len(parts) != 2:
        raise ValueError(f"Некорректное значение: {text}")
    column = parts[0].strip()
    value = parse_value(parts[1])
    return {column: value}


def parse_values_list(text):
    """Разбирает '("Sergei", 28, true)' в список значений"""
    new_text = text.strip()
    if not (new_text.endswith(')') and new_text.startswith('(')):
        raise ValueError(f"Некорректное значение: {text}")
    parts = new_text[1:-1].split(',')
    result = []
    for part in parts:
        result.append(parse_value(part))
    return result


