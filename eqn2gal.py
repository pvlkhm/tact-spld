#!/usr/bin/env python3
import re
import sys

def convert_eqn_to_galette(input_file, output_file):
    with open(input_file, 'r') as f:
        lines = f.readlines()
    
    converted = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Парсим строку вида OUT = expression;
        match = re.match(r'^([a-zA-Z_][a-zA-Z0-9_\[\]]*)\s*=\s*(.+?);?$', line)
        if not match:
            continue
            
        out_signal = match.group(1)
        expr = match.group(2).rstrip(';')
        
        # Преобразуем имена сигналов: y[0] -> Y0, a[0] -> A0, etc.
        def rename_signal(m):
            name = m.group(1)
            index = m.group(2)
            return name.upper() + index
        
        # Ищем паттерны вида y[0], a[15], и т.д.
        expr = re.sub(r'([a-zA-Z]+)\[(\d+)\]', rename_signal, expr)
        
        # Заменяем операторы для формата Galette
        expr = expr.replace('&', ' * ')
        expr = expr.replace('|', ' + ')
        # Убираем лишние пробелы
        expr = re.sub(r'\s*\*\s*', ' * ', expr)
        expr = re.sub(r'\s*\+\s*', ' + ', expr)
        
        # NOT: !A -> /A
        expr = re.sub(r'!\s*([a-zA-Z0-9_]+)', r'/\1', expr)
        
        # Заменяем оставшиеся идентификаторы на верхний регистр
        parts = re.split(r'(\s+|[()*/+])', expr)
        new_parts = []
        for part in parts:
            if re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', part):
                new_parts.append(part.upper())
            else:
                new_parts.append(part)
        expr = ''.join(new_parts)
        
        # Убираем множественные пробелы
        expr = re.sub(r'\s+', ' ', expr).strip()
        
        # Формируем выходную строку
        out_signal_upper = out_signal.upper()
        if '[' in out_signal:
            out_signal_upper = re.sub(r'([a-zA-Z]+)\[(\d+)\]', lambda m: m.group(1).upper() + m.group(2), out_signal)
        
        converted.append(f"{out_signal_upper} = {expr};")
    
    # Записываем результат
    with open(output_file, 'w') as f:
        f.write('\n'.join(converted))
        f.write('\n')
    
    print(f"Конвертация завершена. Результат в {output_file}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 eqn2galette.py input.eqn output.pld")
        sys.exit(1)
    
    convert_eqn_to_galette(sys.argv[1], sys.argv[2])
