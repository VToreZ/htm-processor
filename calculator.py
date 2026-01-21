"""
Безопасный калькулятор арифметических выражений.
Поддерживает: +, -, *, /
"""

import re
from typing import Union


def evaluate(expression: str) -> Union[float, int]:
    """
    Безопасное вычисление арифметического выражения.

    Args:
        expression: Строка с арифметическим выражением (например, "191+0+0")

    Returns:
        Результат вычисления (int если целое, иначе float)

    Raises:
        ValueError: Если выражение некорректно
    """
    # Удаляем пробелы
    expr = expression.replace(" ", "")

    # Проверяем что выражение содержит только допустимые символы
    if not re.match(r'^[\d+\-*/().]+$', expr):
        raise ValueError(f"Недопустимые символы в выражении: {expression}")

    # Проверяем на пустое выражение
    if not expr:
        raise ValueError("Пустое выражение")

    try:
        # Токенизация
        tokens = tokenize(expr)
        # Вычисление с учетом приоритета операций
        result = parse_expression(tokens)

        # Возвращаем int если результат целый
        if isinstance(result, float) and result.is_integer():
            return int(result)
        return result
    except Exception as e:
        raise ValueError(f"Ошибка вычисления выражения '{expression}': {e}")


def tokenize(expr: str) -> list:
    """Разбивает выражение на токены (числа и операторы)."""
    tokens = []
    i = 0

    while i < len(expr):
        char = expr[i]

        if char.isdigit() or char == '.':
            # Собираем число
            num_str = ""
            while i < len(expr) and (expr[i].isdigit() or expr[i] == '.'):
                num_str += expr[i]
                i += 1

            # Преобразуем в число
            if '.' in num_str:
                tokens.append(float(num_str))
            else:
                tokens.append(int(num_str))
        elif char in "+-*/()":
            tokens.append(char)
            i += 1
        else:
            i += 1

    return tokens


def parse_expression(tokens: list) -> float:
    """
    Парсит и вычисляет выражение с учетом приоритета операций.
    Использует рекурсивный спуск.
    """
    pos = [0]  # Используем список для мутабельности в замыкании

    def parse_additive():
        """Обрабатывает + и -"""
        result = parse_multiplicative()

        while pos[0] < len(tokens) and tokens[pos[0]] in "+-":
            op = tokens[pos[0]]
            pos[0] += 1
            right = parse_multiplicative()

            if op == '+':
                result += right
            else:
                result -= right

        return result

    def parse_multiplicative():
        """Обрабатывает * и /"""
        result = parse_primary()

        while pos[0] < len(tokens) and tokens[pos[0]] in "*/":
            op = tokens[pos[0]]
            pos[0] += 1
            right = parse_primary()

            if op == '*':
                result *= right
            else:
                if right == 0:
                    raise ValueError("Деление на ноль")
                result /= right

        return result

    def parse_primary():
        """Обрабатывает числа и скобки"""
        if pos[0] >= len(tokens):
            raise ValueError("Неожиданный конец выражения")

        token = tokens[pos[0]]

        # Унарный минус
        if token == '-':
            pos[0] += 1
            return -parse_primary()

        # Унарный плюс
        if token == '+':
            pos[0] += 1
            return parse_primary()

        # Скобки
        if token == '(':
            pos[0] += 1
            result = parse_additive()
            if pos[0] < len(tokens) and tokens[pos[0]] == ')':
                pos[0] += 1
            return result

        # Число
        if isinstance(token, (int, float)):
            pos[0] += 1
            return float(token)

        raise ValueError(f"Неожиданный токен: {token}")

    result = parse_additive()
    return result


if __name__ == "__main__":
    # Тесты
    test_cases = [
        ("191+0+0", 191),
        ("472+2783+0", 3255),
        ("8-0", 8),
        ("10*5", 50),
        ("100/4", 25),
        ("2+3*4", 14),
        ("(2+3)*4", 20),
        ("10-5+3", 8),
        ("-5+10", 5),
    ]

    print("Тестирование калькулятора:")
    for expr, expected in test_cases:
        result = evaluate(expr)
        status = "OK" if result == expected else f"FAIL (expected {expected})"
        print(f"  {expr} = {result} [{status}]")
