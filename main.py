import sys
import os
import random
import string
import re

def banner():
    print(r'''
______      _____               ______       _   _____ _      __                     _             
| ___ \    |  ___|              | ___ \     | | |  _  | |    / _|                   | |            
| |_/ /   _| |__  __ _ ___ _   _| |_/ / __ _| |_| | | | |__ | |_ _   _ ___  ___ __ _| |_ ___  _ __ 
|  __/ | | |  __|/ _` / __| | | | ___ \/ _` | __| | | | '_ \|  _| | | / __|/ __/ _` | __/ _ \| '__|
| |  | |_| | |__| (_| \__ \ |_| | |_/ / (_| | |_\ \_/ / |_) | | | |_| \__ \ (_| (_| | || (_) | |   
\_|   \__, \____/\__,_|___/\__, \____/ \__,_|\__|\___/|_.__/|_|  \__,_|___/\___\__,_|\__\___/|_|   
       __/ |                __/ |                                                                  
      |___/                |___/                                                                   
    ''')

def log(stage, total, description):
    print(f"[{stage}/{total}] {description}")

def random_string(length):
    return ''.join(random.choices(string.ascii_letters, k=length))

def insert_fake_vars(ch):
    if ch == '%':
        return '%'
    elif ch == '\n':
        return '\n'
    else:
        return f"{ch}%{random_string(random.randint(3, 7))}%"

def random_junk_line():
    opcje = [
        f'set {random_string(5)}={random.randint(1,9999)}',
        f'title {random_string(7)}',
        f'set /a {random_string(4)}={random.randint(10,99)}*{random.randint(10,99)}',
        f'if "%random%"=="{random.randint(100,999)}" echo {random_string(5)}',
        f'echo {random_string(5)} >nul'
    ]
    return random.choice(opcje)

def obfuscate_content(script, passes=2, junk_lines=80):
    label_map = {}
    label_pattern = re.compile(r'^\s*:(\w+)', re.MULTILINE)

    for label in re.findall(label_pattern, script):
        obf_name = ':' + random_string(random.randint(6, 10))
        label_map[label] = obf_name

    for old, new in label_map.items():
        script = re.sub(rf'(?<!\w)(goto\s+):?{re.escape(old)}(?!\w)', rf'\1{new}', script, flags=re.IGNORECASE)
        script = re.sub(rf'(?<!\w)(call\s+):?{re.escape(old)}(?!\w)', rf'\1{new}', script, flags=re.IGNORECASE)
        script = re.sub(rf'(?<!\w):{re.escape(old)}(?!\w)', new, script)

    for i in range(passes):
        log(i + 1, passes, f"Obfuscation pass {i + 1}")
        if i == 0:
            current = script
        else:
            current = batchfile_obfuscated

        batchfile_obfuscated = ''
        var_charset = '@ 0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
        var_expansion_charset = '_ÄÅÇÉÑÖÜáàâäãåçéèêëíìîïñóòôöõúùûüabcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
        variable_name = ''.join(random.choices(var_expansion_charset, k=random.randint(3, 5)))
        shuffled_chars = list(var_charset)
        random.shuffle(shuffled_chars)
        expanded_string = ''.join(shuffled_chars)

        table = {char: f'%{variable_name}:~{idx},1%' for idx, char in enumerate(shuffled_chars)}

        batchfile_obfuscated += '@echo off\n'
        batchfile_obfuscated += f'set "{variable_name}={expanded_string}"\n'

        for _ in range(junk_lines):
            batchfile_obfuscated += random_junk_line() + '\n'

        convert_var = False
        convert_label = False
        new_line = True

        for line in current.splitlines(keepends=True):
            if line.strip().lower().startswith('title '):
                batchfile_obfuscated += line
                continue
            if line.strip().startswith(':'):
                batchfile_obfuscated += line
                continue

            for ch in line:
                if new_line and ch == ':':
                    convert_label = True

                if ch == '\n':
                    new_line = True
                    convert_var = False
                    convert_label = False
                else:
                    new_line = False

                if ch == ' ':
                    convert_label = False

                if not convert_var and ch in ['%', '!']:
                    convert_var = True
                elif convert_var and ch in ['%', '!']:
                    convert_var = False
                    convert_label = False

                if not convert_var and not convert_label and not new_line:
                    if ch in table:
                        junk = f'%{random_string(random.randint(3, 6))}%' if random.randint(1, 4) == 2 else ''
                        batchfile_obfuscated += table[ch] + junk
                    else:
                        batchfile_obfuscated += insert_fake_vars(ch)
                else:
                    batchfile_obfuscated += ch

            if random.randint(1, 3) == 2:
                batchfile_obfuscated += random_junk_line() + '\n'

    return batchfile_obfuscated

def save_obfuscated_code(path):
    log(1, 5, "Reading original file")
    try:
        with open(path, 'r', encoding='utf-8') as fileobj:
            original_script = fileobj.read()
    except:
        print('[-] Unable to read the file.')
        return

    log(2, 5, "Generating obfuscated code")
    output = os.path.splitext(path)[0] + "_obfuscated"
    out_path = f"{output}.bat"

    final_script = obfuscate_content(original_script, passes=2, junk_lines=100)

    log(3, 5, "Appending final footer and comment")
    final_script += '\nREM Obfuscated using PyEasyBatObfuscator\n'
    final_script += 'echo This code was obfuscated by PyEasyBatObfuscator\n'

    log(4, 5, "Saving obfuscated file")
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(final_script)

    log(5, 5, f"Done: {out_path}")
    print(f'[✔] Obfuscated file saved to: {out_path}')

if __name__ == '__main__':
    banner()
    if len(sys.argv) != 2:
        print('Use: python main.py file.bat')
    else:
        save_obfuscated_code(sys.argv[1])
