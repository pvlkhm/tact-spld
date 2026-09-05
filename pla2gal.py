#!/usr/bin/env python3
import sys
import re

def pla_to_galette(pla_file, output_file):
    with open(pla_file, 'r') as f:
        lines = f.readlines()
    
    # Парсим PLA
    in_names = []
    out_names = []
    terms = []
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line or line.startswith('#'):
            i += 1
            continue
            
        if line.startswith('.i'):
            parts = line.split()
            if len(parts) == 2 and parts[1].isdigit():
                num_inputs = int(parts[1])
            else:
                in_names = parts[1:]
                num_inputs = len(in_names)
        elif line.startswith('.o'):
            parts = line.split()
            if len(parts) == 2 and parts[1].isdigit():
                num_outputs = int(parts[1])
            else:
                out_names = parts[1:]
                num_outputs = len(out_names)
        elif line.startswith('.ilb'):
            in_names = line.split()[1:]
        elif line.startswith('.ob'):
            out_names = line.split()[1:]
        elif line.startswith('.p'):
            num_terms = int(line.split()[1])
        elif line.startswith('.e'):
            break
        elif line and not line.startswith('.'):
            parts = line.split()
            if len(parts) >= 2:
                in_bits = parts[0]
                out_bits = parts[1]
                terms.append((in_bits, out_bits))
        i += 1
    
    if not in_names:
        in_names = [f'X{i}' for i in range(num_inputs)]
    if not out_names:
        out_names = [f'Y{i}' for i in range(num_outputs)]
    
    out_terms = {name: [] for name in out_names}
    
    for in_bits, out_bits in terms:
        out_bits = out_bits[:len(out_names)]
        for j, out_char in enumerate(out_bits):
            if out_char == '1':
                term = []
                in_bits_padded = in_bits.ljust(num_inputs, '-')
                for k, in_char in enumerate(in_bits_padded[:len(in_names)]):
                    if in_char == '1':
                        term.append(in_names[k])
                    elif in_char == '0':
                        term.append('/' + in_names[k])
                if term:
                    out_terms[out_names[j]].append(' * '.join(term))
                else:
                    out_terms[out_names[j]].append('1')
    
    with open(output_file, 'w') as f:
        for out_name in out_names:
            if out_terms[out_name]:
                unique_terms = list(set(out_terms[out_name]))
                terms_sorted = sorted(unique_terms, key=len)
                
                def clean_name(name):
                    return re.sub(r'([a-zA-Z]+)\[(\d+)\]', lambda m: m.group(1).upper() + m.group(2), name)
                
                terms_clean = [clean_name(t) for t in terms_sorted]
                # Склеиваем через + без скобок
                eq = ' + '.join(terms_clean)
                f.write(f"{clean_name(out_name)} = {eq};\n")
            else:
                f.write(f"{clean_name(out_name)} = 0;\n")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 pla2gal.py input.pla output.pld")
        sys.exit(1)
    pla_to_galette(sys.argv[1], sys.argv[2])
