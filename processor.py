"""
Модуль обработки файлов .01
Читает данные, применяет значения из HTM, сохраняет результат.
"""

import os
from parser import parse_htm
from typing import Dict, List, Tuple


def load_file_01(file_path: str) -> Tuple[List[str], List[List[str]]]:
    """
    Загружает файл .01 и разделяет на заголовки и данные.

    Args:
        file_path: Путь к файлу .01

    Returns:
        (headers, data) - список строк заголовков и список строк данных
    """
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Первые 2 строки - заголовки
    headers = lines[:2] if len(lines) >= 2 else lines

    # Остальные - данные
    data = []
    for line in lines[2:]:
        # Разбиваем строку по пробелам
        parts = line.strip().split()
        data.append(parts)

    return headers, data


def save_file_01(file_path: str, headers: List[str], data: List[List[str]]):
    """
    Сохраняет данные в файл .01.

    Args:
        file_path: Путь к файлу
        headers: Список строк заголовков
        data: Список строк данных
    """
    with open(file_path, "w", encoding="utf-8") as f:
        # Записываем заголовки
        for header in headers:
            if not header.endswith("\n"):
                header += "\n"
            f.write(header)

        # Записываем данные
        for row in data:
            f.write(" ".join(str(x) for x in row) + "\n")


def apply_values(
    data: List[List[str]], values: List[Dict]
) -> Tuple[int, int, List[str]]:
    """
    Применяет значения из HTM к данным файла .01.

    Args:
        data: Данные из файла .01 (список строк, каждая строка - список значений)
        values: Список значений из HTM [{"row": int, "column": int, "value": float}, ...]

    Returns:
        (applied_count, skipped_count, errors) - статистика применения
    """
    applied = 0
    skipped = 0
    errors = []

    for entry in values:
        row_num = entry["row"]
        col_num = entry["column"]
        value = entry["value"]

        # Индекс строки в data (row_num - 1, т.к. в файле строки начинаются с 1)
        row_idx = row_num - 1

        # Проверяем границы
        if row_idx < 0 or row_idx >= len(data):
            errors.append(f"Строка {row_num} вне диапазона (макс: {len(data)})")
            skipped += 1
            continue

        # Индекс столбца (графа N = столбец N в data, где столбец 0 = номер строки)
        col_idx = col_num

        # Расширяем строку если нужно
        while len(data[row_idx]) <= col_idx:
            data[row_idx].append("0")

        # Форматируем значение (целое или с точкой)
        if isinstance(value, float) and value.is_integer():
            value_str = str(int(value))
        else:
            value_str = str(value)

        # Применяем значение
        data[row_idx][col_idx] = value_str
        applied += 1

    return applied, skipped, errors


def process(htm_path: str, file_01_path: str, output_path: str = None) -> Dict:
    """
    Основная функция обработки.

    Args:
        htm_path: Путь к HTM файлу
        file_01_path: Путь к файлу .01
        output_path: Путь для сохранения результата (если None, генерируется автоматически)

    Returns:
        Словарь со статистикой:
        {
            "parsed_count": int,
            "applied_count": int,
            "skipped_count": int,
            "output_path": str,
            "errors": list
        }
    """
    # Генерируем путь для результата если не указан
    if output_path is None:
        base, ext = os.path.splitext(file_01_path)
        output_path = f"{base}_result{ext}"

    # Парсим HTM
    values = parse_htm(htm_path)

    # Загружаем файл .01
    headers, data = load_file_01(file_01_path)

    # Применяем значения
    applied, skipped, errors = apply_values(data, values)

    # Сохраняем результат
    save_file_01(output_path, headers, data)

    return {
        "parsed_count": len(values),
        "applied_count": applied,
        "skipped_count": skipped,
        "output_path": output_path,
        "errors": errors,
    }


if __name__ == "__main__":
    import sys

    # Тест на примере файлов
    htm_path = sys.argv[1] if len(sys.argv) > 1 else "dist/input.HTM"
    file_01_path = sys.argv[2] if len(sys.argv) > 2 else "dist/412.01"

    try:
        result = process(htm_path, file_01_path)
        print(f"Обработка завершена:")
        print(f"  Найдено записей в HTM: {result['parsed_count']}")
        print(f"  Применено: {result['applied_count']}")
        print(f"  Пропущено: {result['skipped_count']}")
        print(f"  Результат сохранён: {result['output_path']}")

        if result["errors"]:
            print(f"  Ошибки:")
            for err in result["errors"][:10]:
                print(f"    - {err}")
    except FileNotFoundError as e:
        print(f"Файл не найден: {e}")
    except Exception as e:
        print(f"Ошибка: {e}")
