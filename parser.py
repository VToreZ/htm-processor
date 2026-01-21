"""
Парсер HTM файлов с извлечением данных из секций "Сравнение".
"""

import re
from typing import Dict, List, Optional

from calculator import evaluate


def parse_htm(file_path: str) -> List[Dict]:
    """
    Парсит HTM файл и извлекает данные из секций "Сравнение".

    Args:
        file_path: Путь к HTM файлу

    Returns:
        Список словарей с данными:
        [{"row": int, "column": int, "value": float}, ...]
    """
    # Читаем файл в кодировке windows-1251
    with open(file_path, "r", encoding="windows-1251") as f:
        content = f.read()

    # Заменяем HTML-сущности
    content = content.replace("&lt;", "<").replace("&gt;", ">")

    results = []

    # Находим все блоки TD
    td_blocks = re.findall(r"<TD>(.*?)</TD>", content, re.DOTALL | re.IGNORECASE)

    for td_block in td_blocks:
        # Проверяем, содержит ли блок "Сравнение" (регистронезависимо)
        if not re.search(r"сравнение", td_block, re.IGNORECASE):
            continue

        # Извлекаем все параграфы
        paragraphs = re.findall(
            r"<P[^>]*>(.*?)</P>", td_block, re.DOTALL | re.IGNORECASE
        )

        # Обрабатываем параграфы
        i = 0
        while i < len(paragraphs):
            p_text = paragraphs[i].strip()

            # Пропускаем заголовки (содержат <B><I>)
            if "<B>" in p_text or "<I>" in p_text:
                i += 1
                continue

            # Ищем номер графы и строки в текущем параграфе
            row, column = extract_row_column(p_text)

            if row is not None and column is not None:
                # Следующий параграф должен содержать значение
                if i + 1 < len(paragraphs):
                    value_text = paragraphs[i + 1].strip()
                    value = extract_value(value_text)

                    if value is not None:
                        results.append({"row": row, "column": column, "value": value})
                    i += 2
                    continue

            i += 1

    return results


def extract_row_column(text: str) -> tuple:
    """
    Извлекает номер строки и графы из текста.

    Паттерны:
    - "графа N : с.M" или "графа N : строка M"
    - "г.N" для графы
    - "с.M" или "строка M" для строки

    Returns:
        (row, column) или (None, None) если не найдено
    """
    text = text.lower()

    row = None
    column = None

    # Ищем номер графы
    # Паттерн: "графа N" или "г.N" или "г. N"
    column_match = re.search(r"(?:графа\s*|г\.\s*)(\d+)", text)
    if column_match:
        column = int(column_match.group(1))

    # Ищем номер строки
    # Паттерн: "с.M" или "строка M" или "с. M"
    row_match = re.search(r"(?:с\.\s*|строка\s*)(\d+)", text)
    if row_match:
        row = int(row_match.group(1))

    return row, column


def extract_value(text: str) -> Optional[float]:
    """
    Извлекает значение из текста параграфа.
    Берёт правую часть после символа <> и вычисляет если есть арифметика.

    Args:
        text: Текст параграфа (например, "0 <> 37197" или "0 <> 191+0+0")

    Returns:
        Вычисленное значение или None
    """
    # Удаляем HTML теги
    text = re.sub(r"<[^>]+>", "", text)

    # Ищем паттерн "... <> ..."
    # Символ <> может быть записан как <> или < >
    match = re.search(r"<\s*>\s*(.+)$", text)
    if not match:
        return None

    right_part = match.group(1).strip()

    # Если правая часть пустая
    if not right_part:
        return None

    # Пытаемся вычислить выражение
    try:
        # Убираем возможные лишние символы в конце
        right_part = re.sub(r"[^\d+\-*/().\s]", "", right_part)
        right_part = right_part.strip()

        if not right_part:
            return None

        result = evaluate(right_part)
        return result
    except (ValueError, ZeroDivisionError):
        return None


if __name__ == "__main__":
    import sys

    # Тест на примере файла
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = "dist/input.HTM"

    try:
        results = parse_htm(file_path)
        print(f"Найдено {len(results)} записей:")
        for i, r in enumerate(results[:20]):  # Показываем первые 20
            print(f"  {i + 1}. Строка {r['row']}, Графа {r['column']}: {r['value']}")
        if len(results) > 20:
            print(f"  ... и ещё {len(results) - 20} записей")
    except FileNotFoundError:
        print(f"Файл не найден: {file_path}")
    except Exception as e:
        print(f"Ошибка: {e}")
