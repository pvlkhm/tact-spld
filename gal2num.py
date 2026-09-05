#!/usr/bin/env python3
"""
Анализатор PLD-файлов для GAL16V8/GAL22V10.
Подсчитывает количество термов (product terms) для каждого выхода.
"""

import re
import sys

def count_terms_in_expression(expr):
    """
    Подсчитывает количество термов в выражении.
    Терм — это часть, разделенная оператором '+' (ИЛИ).
    Учитывает инверсии и составные термы.
    """
    if not expr:
        return 0

    # Убираем пробелы
    expr = expr.replace(' ', '')

    # Разбиваем по '+' на термы
    terms = expr.split('+')

    # Убираем пустые термы
    terms = [t for t in terms if t]

    return len(terms)

def analyze_pld_file(filepath):
    """
    Анализирует PLD-файл и возвращает словарь с количеством термов для каждого выхода.
    """
    with open(filepath, 'r') as f:
        content = f.read()

    # Убираем комментарии (строки, начинающиеся с ';' или '/* */')
    lines = []
    in_multiline_comment = False

    for line in content.split('\n'):
        # Многострочные комментарии /* */
        if '/*' in line and '*/' in line:
            # Одна строка с комментарием
            line = line[:line.find('/*')]
        elif '/*' in line:
            in_multiline_comment = True
            line = line[:line.find('/*')]
        elif '*/' in line:
            in_multiline_comment = False
            line = line[line.find('*/') + 2:]
        elif in_multiline_comment:
            continue

        # Однострочные комментарии ;
        if ';' in line and not line.strip().startswith('Name') and not line.strip().startswith('Device'):
            # Проверяем, не является ли ';' частью уравнения
            # Если это уравнение, оно заканчивается на ';'
            if not line.strip().endswith(';'):
                line = line[:line.find(';')]

        # Пропускаем пустые строки
        if line.strip():
            lines.append(line.strip())

    # Ищем уравнения вида SIGNAL = EXPRESSION;
    results = {}
    total_terms = 0

    for line in lines:
        # Пропускаем строки с объявлением пинов
        if line.startswith('CLK') or line.startswith('/OE') or line.startswith('Name') or line.startswith('Device'):
            continue

        # Ищем уравнение
        match = re.match(r'^([A-Za-z0-9_]+)\s*=\s*(.+?);?$', line)
        if match:
            signal = match.group(1)
            expr = match.group(2).rstrip(';')

            # Пропускаем строки, которые являются сборкой из других сигналов
            # (например, Y3 = P1 + P2 + P3)
            # Они считаются отдельно
            term_count = count_terms_in_expression(expr)

            # Если выражение содержит только имена сигналов с '+' между ними,
            # это сборка, а не логические термы
            is_assembly = True
            for part in expr.split('+'):
                part = part.strip()
                if '*' in part or '/' in part or '!' in part:
                    is_assembly = False
                    break
                # Проверяем, что это просто имя сигнала
                if not re.match(r'^[A-Za-z0-9_]+$', part):
                    is_assembly = False
                    break

            if is_assembly:
                # Это сборка, считаем количество сигналов
                term_count = len(expr.split('+'))

            results[signal] = term_count
            total_terms += term_count

    return results, total_terms

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 analyze_pld.py <file.pld>")
        sys.exit(1)

    filepath = sys.argv[1]

    try:
        results, total_terms = analyze_pld_file(filepath)

        print("=" * 50)
        print(f"Анализ файла: {filepath}")
        print("=" * 50)
        print()
        print("Количество термов (product terms) по выходам:")
        print("-" * 40)

        # Сортируем по количеству термов (по убыванию)
        sorted_results = sorted(results.items(), key=lambda x: x[1], reverse=True)

        max_terms = 0
        for signal, count in sorted_results:
            status = "✅" if count <= 8 else "❌"
            print(f"  {signal:10} : {count:3} термов  {status}")
            if count > max_terms:
                max_terms = count

        print("-" * 40)
        print(f"  Всего термов: {total_terms}")
        print(f"  Максимум на один выход: {max_terms}")
        print()
        print("Ограничения GAL16V8 (Complex Mode):")
        print("  - Внутренние пины (13-18): максимум 8 термов")
        print("  - Крайние пины (12, 19): максимум 7 термов")
        print()
        print("Ограничения GAL22V10:")
        print("  - Максимум 16 термов на макроячейку")
        print()

        # Проверка на превышение лимита
        over_limit = [s for s, c in results.items() if c > 8]
        if over_limit:
            print("⚠️  ВНИМАНИЕ! Следующие выходы превышают лимит 8 термов:")
            for s in over_limit:
                print(f"    - {s} ({results[s]} термов)")
        else:
            print("✅ Все выходы укладываются в лимит 8 термов.")

    except FileNotFoundError:
        print(f"Ошибка: файл '{filepath}' не найден.")
        sys.exit(1)
    except Exception as e:
        print(f"Ошибка при анализе: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()