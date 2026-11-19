import argparse
import json
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
REF = re.compile(r'`([^`]+\.(?:tsx|ts|mjs|cjs|js))`\s*·\s*`([^`]+?)\+(\d+)(?:~\+(\d+))?`')
PATH = re.compile(r'(?<![A-Za-z0-9_])((?:[\w@.~+-]+/)*[\w@.-]+\.(?:tsx|ts|mjs|cjs|js|json|yaml|yml|py|sh|md))(?![A-Za-z0-9_])')


def symbols(files=()):
    return json.loads(subprocess.check_output(['node', str(HERE / 'sr_symbols.cjs'), *files], cwd=ROOT, text=True))


def is_test(file):
    return bool(re.search(r'(^|/)(__tests__|tests|scripts)/|\.(test|spec)\.', file))


def locate(rows, name):
    matches = [r for r in rows if r['symbol'] == name or r['name'] == name]
    production = [r for r in matches if not is_test(r['file'])]
    return production or matches


def resolve(raw, doc):
    raw = unquote(raw)
    if raw.startswith('file://'):
        return Path(raw[7:])
    target = Path(raw)
    for parent in [doc.parent, *doc.parent.parents, ROOT]:
        candidate = parent / target
        if candidate.exists():
            return candidate.resolve()
    return None


def prose(text):
    fence = None
    for number, line in enumerate(text.splitlines(), 1):
        match = re.match(r'^\s*(`{3,}|~{3,})', line)
        if match:
            token = match[1]
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence):
                fence = None
            continue
        if fence is None:
            yield number, line


def anchors(text):
    result, seen = set(), {}
    for _, line in prose(text):
        result.update(re.findall(r'<a\s+(?:id|name)=[\"\']([^\"\']+)', line))
        if re.match(r'^#{1,6}\s', line):
            title = re.sub(r'^#+\s+', '', line).strip().replace('`', '').replace('\\', '')
            base = re.sub(r'[^\w\- ]', '', title).lower().replace(' ', '-')
            count = seen.get(base, 0)
            seen[base] = count + 1
            result.add(base if not count else f'{base}-{count}')
    return result


def verify(docs, strict=False):
    rows = symbols()
    by_file = {}
    for row in rows:
        by_file.setdefault(row['file'], []).append(row)
    tracked = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT, text=True).split('\0')
    errors, notes, count = [], [], 0
    for doc in docs:
        text = doc.read_text()
        for number, line in prose(text):
            label = f'{doc.relative_to(ROOT) if doc.is_relative_to(ROOT) else doc}:{number}'
            for match in REF.finditer(line):
                count += 1
                file, symbol, lo, hi = match.groups()
                target = resolve(file, doc)
                relative = str(target.relative_to(ROOT)) if target and target.is_relative_to(ROOT) else file
                found = [r for r in by_file.get(relative, []) if r['symbol'] == symbol]
                if not found:
                    errors.append(f'{label} 符号不存在或归属不明确: {file} · {symbol}')
                elif not any(0 <= int(lo) <= int(hi or lo) <= r['end'] - r['start'] for r in found):
                    errors.append(f'{label} 偏移越界: {symbol}+{lo}~+{hi or lo}')
            for target_text in re.findall(r'\]\(([^)\s]+)\)', line):
                if re.match(r'^(https?:|mailto:|skill:)', target_text):
                    continue
                raw, _, fragment = target_text.partition('#')
                target = resolve(raw, doc) if raw else doc
                if not target or not target.exists():
                    errors.append(f'{label} 链接文件不存在: {target_text}')
                elif fragment and target.suffix == '.md' and unquote(fragment) not in anchors(target.read_text()):
                    errors.append(f'{label} 文档锚点不存在: {target_text}')
                elif re.fullmatch(r'L\d+', fragment) and int(fragment[1:]) > len(target.read_text().splitlines()):
                    errors.append(f'{label} 源码链接行号越界: {target_text}')
            for match in PATH.finditer(line):
                raw = match[1]
                if resolve(raw, doc):
                    continue
                if match.start() > 0 and line[match.start() - 1] == '/':
                    category = 'URL或绝对路径'
                elif any(word in line for word in ['不存在', '已删除', '旧路径', '错误示例']):
                    category = '说明性引用'
                elif '/' not in raw and any(Path(p).name == raw for p in tracked):
                    category = '裸名缩写'
                elif '/' not in raw or raw.startswith(('~/', '.env')) or any(word in line for word in ['运行期', '生成文件', '构建产物', '示例路径', '通配']):
                    category = '非仓库文件名'
                else:
                    category = '疑似失效'
                notes.append(f'{label} {category}: {raw}')
                if strict and category == '疑似失效':
                    errors.append(notes[-1])
    return {'documents': len(docs), 'symbolReferences': count, 'errors': errors, 'pathNotes': sorted(set(notes)), 'limitations': ['不证明自然语言、调用方向或偏移处内容正确', '历史裸行号与未采用统一格式的符号引用需人工迁移核对', 'Mermaid仅由独立结构检查器检查；不在此工具中验证渲染']}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['locate', 'outline', 'offset', 'verify'])
    parser.add_argument('values', nargs='+')
    parser.add_argument('--top', action='store_true')
    parser.add_argument('--strict', action='store_true')
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()
    if args.command == 'verify':
        docs = []
        for value in args.values:
            target = Path(value).resolve()
            docs.extend(sorted(target.rglob('*.md')) if target.is_dir() else [target])
        report = verify(docs, args.strict)
        if args.json:
            print(json.dumps(report, ensure_ascii=False, indent=2))
        else:
            print(f"文档 {report['documents']}；符号引用 {report['symbolReferences']}；错误 {len(report['errors'])}；路径分类 {len(report['pathNotes'])}")
            print('\n'.join(report['errors'][:60]))
        return bool(report['errors'])
    rows = symbols(args.values[:1] if args.command in ('outline', 'offset') else ())
    if args.command == 'outline':
        found = [r for r in rows if not args.top or r['top']]
    elif args.command == 'offset':
        if len(args.values) != 2:
            parser.error('offset 需要 FILE SYM')
        found = [r for r in rows if r['symbol'] == args.values[1]]
    else:
        found = [r for name in args.values for r in locate(rows, name)]
    if args.json:
        print(json.dumps(found, ensure_ascii=False, indent=2))
    else:
        for row in found:
            print(f"{row['file']} · {row['symbol']} +0 = {row['start']}；结束 {row['end']}；{row['kind']} {row['summary']}")
    return not bool(found)


if __name__ == '__main__':
    sys.exit(main())
