from .models import *
import re


def asm_to_sections(content):
    reg = r"^;[\s]*[-]+"
    header = ""
    section = ""
    ret = []
    now = []

    matches = 0
    for line in content:
        if re.match(reg, line) is not None:
            matches += 1
        if matches % 2 == 1:
            if header != "" and section != "":
                now.append(header)
                now.append(section)
                ret.append(now)
                header = ""
                section = ""
                now = []
            header += line
        else:
            section += line
    if header != ret[-1][0] or section != ret[-1][0]:
        now.append(header)
        now.append(section)
        ret.append(now)

    return ret


def code_to_sections(file):
    sections_to_delete = Section.objects.filter(file=file)
    sections_to_delete.delete()
    lines = file.code.splitlines()
    start_asm = r"^[\s]*__asm__"
    end_asm = r"^*);"
    directive = r"^[\s]*#"
    comment = r"^[\s]*//"
    var_dec = r"^[\s]*\b(?:(?:auto\s*|const\s*|unsigned\s*|signed\s*|register\s*|volatile\s*|static\s*|void\s*|short\s*|long\s*|char\s*|int\s*|float\s*|double\s*|_Bool\s*|complex\s*)+)(?:\s+\*?\*?\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s*[\[;,=)]"
    empty = r"^[\s]*$"
    start = 0
    num = 1
    is_asm = False
    content = ""
    last_type = "NONE"
    for line in lines:
        if is_asm and re.match(end_asm, line):
            s = Section(begin=start, end=num, file=file, content=content, type="ASM")
            s.save()
            is_asm = False
        elif is_asm:
            content += line
        elif re.match(start_asm, line) is not None:
            is_asm = True
            start = num
            content += line
        elif re.match(directive, line) is not None:
            if last_type == "D":
                content += line
            else:
                s = Section(begin=start, end=num - 1, file=file, content=content, type=last_type)
                s.save()
                start = num
                content = line
                last_type = "D"
        elif re.match(comment, line) is not None:
            if last_type == "COM":
                content += line
            else:
                s = Section(begin=start, end=num - 1, file=file, content=content, type=last_type)
                s.save()
                start = num
                content = line
                last_type = "COM"
        elif re.match(var_dec, line) is not None:
            if last_type == "VAR":
                content += line
            else:
                s = Section(begin=start, end=num - 1, file=file, content=content, type=last_type)
                s.save()
                start = num
                content = line
                last_type = "VAR"
        elif re.match(empty, line) is not None:
            if last_type == "EMP":
                content += line
            else:
                s = Section(begin=start, end=num - 1, file=file, content=content, type=last_type)
                s.save()
                start = num
                content = line
                last_type = "EMP"
        else:
            if last_type == "PRC":
                content += line
            else:
                s = Section(begin=start, end=num - 1, file=file, content=content, type=last_type)
                s.save()
                start = num
                content = line
                last_type = "PRC"
        num += 1
    s = Section(begin=start, end=num - 1, file=file, content=content, type=last_type)
    s.save()