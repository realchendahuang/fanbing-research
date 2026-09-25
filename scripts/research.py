#!/usr/bin/env python3
"""Offline tools for a source-grounded, single-person research repository.

Python 3.11+, standard library only. Does not fetch URLs, execute source
content, contact the research subject, or publish any changes.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import date
import json
from pathlib import Path
import re
import sys
from typing import Any
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
DATASETS = (
    'sources', 'claims', 'timeline', 'works', 'patterns',
    'reading-queue', 'predictions', 'experiments', 'review-log',
)
SUPPORTED_SCHEMA_KEYS = {
    '$schema', 'title', 'description', 'type', 'required', 'properties',
    'additionalProperties', 'items', 'minItems', 'uniqueItems', 'minLength',
    'minimum', 'enum', 'pattern', 'format',
}
STATUS_NAMES = {
    'page_read': '已读所标正文范围',
    'partial_read': '部分阅读',
    'index_only': '仅目录/入口',
    'shownotes_only': '仅节目说明，未核听',
}
ROLE_NAMES = {
    'publication': '材料发表', 'retrospective_event': '事后自述的事件',
    'bibliographic': '书目日期', 'event': '事件日期',
}
START_MARKER = '<!-- STATS:START -->'
END_MARKER = '<!-- STATS:END -->'


def load_json(path: Path) -> Any:
    """Read UTF-8 JSON with actionable file errors."""
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f'{path}: {exc}') from exc


def load_data(root: Path) -> tuple[dict[str, Any], dict[str, list[dict[str, Any]]]]:
    person = load_json(root / 'person.json')
    data = {name: load_json(root / 'data' / f'{name}.json') for name in DATASETS}
    return person, data


def date_precision(value: str | None) -> str:
    """Validate an actual calendar value, retaining partial precision."""
    if value is None:
        return 'unknown'
    if not isinstance(value, str) or not re.fullmatch(r'\d{4}(?:-\d{2})?(?:-\d{2})?', value):
        raise ValueError(f'invalid date: {value!r}')
    parts = [int(x) for x in value.split('-')]
    date(parts[0], parts[1] if len(parts) > 1 else 1,
         parts[2] if len(parts) > 2 else 1)
    return {1: 'year', 2: 'month', 3: 'day'}[len(parts)]


def schema_errors(value: Any, schema: dict[str, Any], where: str = '$') -> list[str]:
    """Validate only the documented schema subset; fail on unknown keywords."""
    errors: list[str] = []
    unknown = set(schema) - SUPPORTED_SCHEMA_KEYS
    if unknown:
        errors.append(f'{where}: unsupported schema keywords: {sorted(unknown)}')
    kind = schema.get('type')
    kinds = kind if isinstance(kind, list) else [kind] if kind else []
    checks = {
        'null': lambda x: x is None,
        'string': lambda x: isinstance(x, str),
        'integer': lambda x: isinstance(x, int) and not isinstance(x, bool),
        'number': lambda x: isinstance(x, (int, float)) and not isinstance(x, bool),
        'boolean': lambda x: isinstance(x, bool),
        'array': lambda x: isinstance(x, list),
        'object': lambda x: isinstance(x, dict),
    }
    if kinds and not any(k in checks and checks[k](value) for k in kinds):
        errors.append(f'{where}: expected {kinds}, got {type(value).__name__}')
        return errors
    if 'enum' in schema and value not in schema['enum']:
        errors.append(f'{where}: value is not in enum')
    if value is None:
        return errors
    if isinstance(value, str):
        if len(value) < schema.get('minLength', 0):
            errors.append(f'{where}: string too short')
        if 'pattern' in schema and re.search(schema['pattern'], value) is None:
            errors.append(f'{where}: does not match {schema["pattern"]}')
        if schema.get('format') == 'date':
            try:
                if date_precision(value) != 'day':
                    raise ValueError('full date required')
            except ValueError:
                errors.append(f'{where}: invalid calendar date')
        elif schema.get('format') == 'uri':
            try:
                u = urlsplit(value)
                if u.scheme not in ('http', 'https') or not u.netloc or any(c.isspace() for c in value):
                    raise ValueError('not an HTTP(S) URL')
                if u.username is not None or u.password is not None:
                    raise ValueError('credentials in URL')
            except ValueError:
                errors.append(f'{where}: invalid or credential-bearing HTTP(S) URL')
        elif 'format' in schema:
            errors.append(f'{where}: unsupported format {schema["format"]}')
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if 'minimum' in schema and value < schema['minimum']:
            errors.append(f'{where}: below minimum')
    if isinstance(value, list):
        if len(value) < schema.get('minItems', 0):
            errors.append(f'{where}: too few items')
        if schema.get('uniqueItems'):
            tokens = [json.dumps(x, sort_keys=True, ensure_ascii=False) for x in value]
            if len(tokens) != len(set(tokens)):
                errors.append(f'{where}: duplicate items')
        for i, item in enumerate(value):
            if 'items' in schema:
                errors.extend(schema_errors(item, schema['items'], f'{where}[{i}]'))
    if isinstance(value, dict):
        for key in schema.get('required', []):
            if key not in value:
                errors.append(f'{where}: missing required field {key}')
        props = schema.get('properties', {})
        if schema.get('additionalProperties') is False:
            for key in value.keys() - props.keys():
                errors.append(f'{where}: unknown field {key}')
        for key in value.keys() & props.keys():
            errors.extend(schema_errors(value[key], props[key], f'{where}.{key}'))
    return errors


def _local_path(root: Path, base: Path, link: str) -> Path | None:
    """Resolve a local link without permitting paths outside the repository."""
    if link.startswith(('#', 'http://', 'https://', 'mailto:', 'data:', 'sandbox:')):
        return None
    target = unquote(link.split('#', 1)[0].split('?', 1)[0])
    if not target:
        return None
    p = (base / target).resolve()
    if not p.is_relative_to(root.resolve()):
        raise ValueError(f'path escapes repository: {link}')
    return p


def validate(root: Path, *, check_links: bool = True) -> list[str]:
    errors: list[str] = []
    try:
        person, data = load_data(root)
    except ValueError as exc:
        return [str(exc)]
    for name, value in [('person', person), *data.items()]:
        try:
            schema = load_json(root / 'schemas' / f'{name}.schema.json')
            errors.extend(schema_errors(value, schema, name))
        except ValueError as exc:
            errors.append(str(exc))
    # Type/shape errors are reported first rather than cascading to tracebacks.
    if errors:
        return errors
    ids: dict[str, set[str]] = {}
    for name, rows in data.items():
        if name == 'review-log':
            continue
        values = [row['id'] for row in rows]
        ids[name] = set(values)
        duplicates = [k for k, n in Counter(values).items() if n > 1]
        if duplicates:
            errors.append(f'{name}: duplicate IDs {duplicates}')
    urls = [s['url'].rstrip('/') for s in data['sources']]
    if len(urls) != len(set(urls)):
        errors.append('sources: duplicate canonical URLs; check duplicates before adding')
    ref_map = {
        'source_ids': 'sources', 'date_source_ids': 'sources',
        'official_identity_source_ids': 'sources', 'outcome_source_ids': 'sources',
        'claim_ids': 'claims', 'counter_claim_ids': 'claims', 'pattern_ids': 'patterns',
    }
    for name, rows in [('person', [person]), *data.items()]:
        for row in rows:
            label = f'{name}:{row.get("id", "record")}'
            for field, destination in ref_map.items():
                for ref in row.get(field, []):
                    if ref not in ids[destination]:
                        errors.append(f'{label}.{field}: unknown reference {ref}')
            if 'published_at' in row or ('date_precision' in row and 'date' in row):
                value = row.get('published_at', row.get('date'))
                try:
                    if date_precision(value) != row['date_precision']:
                        errors.append(f'{label}: date precision mismatch')
                except ValueError as exc:
                    errors.append(f'{label}: {exc}')
            for key in ('made_on', 'started_on'):
                if row.get(key) is not None:
                    try:
                        date_precision(row[key])
                    except ValueError as exc:
                        errors.append(f'{label}.{key}: {exc}')
            if row.get('checked_at', person['as_of']) > person['as_of']:
                errors.append(f'{label}: checked_at is after person.as_of')
    claims = {c['id']: c for c in data['claims']}
    for p in data['patterns']:
        required: set[str] = set()
        for cid in p['claim_ids'] + p['counter_claim_ids']:
            if cid in claims:
                required.update(claims[cid]['source_ids'])
        missing = required - set(p['source_ids'])
        if missing:
            errors.append(f'{p["id"]}: sources missing from supporting/counter claims: {sorted(missing)}')
        try:
            dest = _local_path(root, root, p['path'])
            if dest is None or not dest.is_file():
                errors.append(f'{p["id"]}: pattern file missing: {p["path"]}')
        except ValueError as exc:
            errors.append(f'{p["id"]}: {exc}')
    for p in data['predictions']:
        if p['status'] in ('supported', 'not_supported', 'indeterminate'):
            if not p['assessment'] or not p['outcome_source_ids']:
                errors.append(f'{p["id"]}: an assessment needs text and outcome sources')
    for x in data['experiments']:
        if x['status'] in ('running', 'completed') and x['started_on'] is None:
            errors.append(f'{x["id"]}: started experiment needs started_on')
        if x['status'] == 'completed' and not x['result']:
            errors.append(f'{x["id"]}: completed experiment needs actual result')
    if check_links:
        # Plain inline Markdown links in this repository; no network requests.
        for path in sorted(root.rglob('*.md')):
            if any(part in ('.git', '.venv', 'local-only') for part in path.parts):
                continue
            text = path.read_text(encoding='utf-8')
            text_no_fences = re.sub(r'```.*?```', '', text, flags=re.S)
            text_no_fences = re.sub(r'`[^`\n]+`', '', text_no_fences)
            for link in re.findall(r'!?\[[^\]\n]*\]\(([^)\n]+)\)', text_no_fences):
                raw = link.strip().strip('<>')
                try:
                    target = _local_path(root, path.parent, raw)
                    if target is not None and not target.exists():
                        errors.append(f'{path.relative_to(root)}: missing local link {raw}')
                except ValueError as exc:
                    errors.append(f'{path.relative_to(root)}: {exc}')
            for ref in set(re.findall(r'\bS\d{3,}\b', text_no_fences)):
                if ref not in ids['sources']:
                    errors.append(f'{path.relative_to(root)}: unknown source ID {ref}')
    return errors


def _table(text: Any) -> str:
    return str(text).replace('|', '\\|').replace('\n', ' ')


def _links(refs: list[str], prefix: str) -> str:
    return ' '.join(f'[{x}]({prefix}{x}.md)' for x in refs) or '—'


def stats_summary(root: Path) -> dict[str, Any]:
    person, data = load_data(root)
    return {
        'name': person['slug'], 'version': person['version'], 'as_of': person['as_of'],
        'counts': {name: len(rows) for name, rows in data.items()},
        'source_review_status': dict(sorted(Counter(s['review_status'] for s in data['sources']).items())),
        'case_studies': len([p for p in (root/'research/cases').glob('*.md') if p.name != 'README.md']),
    }


def generated_files(root: Path) -> dict[str, str]:
    """Produce deterministic Markdown views, without fetching external content."""
    person, d = load_data(root)
    out: dict[str, str] = {}
    counts = stats_summary(root)
    state = counts['source_review_status']
    stats_lines = [
        '| 内容 | 当前数量与范围 |', '| --- | --- |',
        f'| 来源记录 | {len(d["sources"])}，包含入口、目录及节目说明；不是全文已读篇数 |',
        f'| 有出处的主张 | {len(d["claims"])}，区分页面事实与本人自述 |',
        f'| 时间节点 | {len(d["timeline"])}，保留日/月/年精度 |',
        f'| 作品与项目条目 | {len(d["works"])}，注明本轮实际查看范围 |',
        f'| 原创案例 / 工作假设 | {counts["case_studies"]} / {len(d["patterns"])} |',
        f'| 待研究任务 | {len(d["reading-queue"])} |',
        f'| 已登记预测 / 实验 | {len(d["predictions"])} / {len(d["experiments"])}；不为凑数编造结果 |',
    ]
    summary = '\n'.join(stats_lines)
    statuses = '\n'.join(f'| {STATUS_NAMES[k]} | {n} |' for k, n in state.items())
    out['sources/STATS.md'] = f'''# 收录与阅读范围统计

由规范数据生成。核对日期：{person['as_of']}，版本：{person['version']}。

{summary}

## 来源查看状态

| 状态 | 数量 |
| --- | --- |
{statuses}

`page_read` 也仅表示来源卡上写明的范围；书籍 README 不等于读完书。归档页、代码仓库入口和节目说明都不是完整正文。全部条目的准确范围见 [来源目录](README.md)。

独立人工复核：初始研究仍待完成。源码存在不证明运行成功，商业介绍不证明已经交付，页面核对不证明事实已经独立核实。
'''
    README = (root/'README.md').read_text(encoding='utf-8')
    if README.count(START_MARKER) != 1 or README.count(END_MARKER) != 1:
        raise ValueError('README.md must have exactly one pair of STATS markers')
    before, tail = README.split(START_MARKER)
    _, after = tail.split(END_MARKER)
    out['README.md'] = before + START_MARKER + '\n' + summary + '\n' + END_MARKER + after
    rows = []
    for s in d['sources']:
        date_display = s['published_at'] or '未确认'
        rows.append(f'| [{s["id"]}](cards/{s["id"]}.md) | {_table(date_display)} | {_table(s["title"])} | {STATUS_NAMES[s["review_status"]]} |')
        datesrc = _links(s['date_source_ids'], '')
        # Sibling source cards use only the filename as a relative target.
        related = [c for c in d['claims'] if s['id'] in c['source_ids']]
        related_text = ' '.join(f'[{c["id"]}](../../research/CLAIMS.md#{c["id"].lower()})' for c in related) or '暂无主张；作为入口或阅读线索保留。'
        out[f'sources/cards/{s["id"]}.md'] = f'''# {s['id']}｜{s['title']}

> 自动生成自 `data/sources.json`；请编辑规范数据后重新 build。

**原始来源：** [{s['title']}]({s['url']})

| 字段 | 记录 |
| --- | --- |
| 类型 | {s['source_type']} |
| 来源性质 | {s['evidence_origin']} |
| 依赖组 | {s['independence_group']} |
| 发表日期 | {date_display} |
| 日期精度 | {s['date_precision']} |
| 核对日期 | {s['checked_at']} |
| 阅读状态 | {STATUS_NAMES[s['review_status']]} |

## 实际核对范围

{s['verification_scope']}

定位：{s['locator']}。

## 本轮注释

{s['summary']}

## 日期与版本限制

{s['date_basis']}。日期关联来源：{datesrc}。

已验证历史快照：{s['archive_url'] or '未登记。不要据此推断没有快照。'}

本轮核对可来自浏览器返回的缓存；没有保存网页全文，不保证当前页面等同原始历史版本。

## 权利说明

{s['rights_note']}

## 被哪些主张使用

{related_text}
'''
    out['sources/README.md'] = '''# 来源目录

> 自动生成自 `data/sources.json`。这里是选读来源与入口索引，不是全文镜像。

先看 [统计与阅读状态](STATS.md)、[来源地图](ORIGIN_MAP.md) 和 [研究缺口](../research/GAPS.md)。每张卡写明实际读到哪里、日期依据、来源依赖与权利边界。

| ID | 发表日期 | 来源 | 本轮查看状态 |
| --- | --- | --- | --- |
''' + '\n'.join(rows) + '\n'
    ev_rows = []
    for e in sorted(d['timeline'], key=lambda x: (x['date'], x['id'])):
        refs = _links(e['source_ids'], '../sources/cards/')
        ev_rows.append(f'| {e["id"]} | {e["date"]} | {ROLE_NAMES[e["date_role"]]} | {_table(e["title"])} | {refs} |')
    out['timeline/README.md'] = '''# 历史时间线

> 自动生成自 `data/timeline.json`。不把选样空白当成没有活动。

“材料发表”只表示所引材料发布，不是行动首次发生；“事后自述”保留回顾性质；“书目日期”本轮主要来自作者仓库。完整事件限制见规范数据及来源卡。只知年份/月的日期不会补造成某日；表格按文本日期排序，同年未知月份项目的位置不代表先后。

| ID | 日期 | 日期性质 | 记录 | 来源 |
| --- | --- | --- | --- | --- |
''' + '\n'.join(ev_rows) + '\n'
    work_rows = []
    for v in d['works']:
        work_rows.append(f'| {v["id"]} | {_table(v["title"])} | {v["work_type"]} | {_table(v["coverage_note"])} | {_links(v["source_ids"], "../sources/cards/")} |')
    out['works/README.md'] = '''# 作品与项目目录

> 自动生成自 `data/works.json`。作品存在、当前运营、本人原创与商业效果是不同问题。

书籍阅读站视作相应作品的一个公开入口；同组个人工具和课程分别登记，不冒充完整著作目录。未确认的其他书目与署名角色进入 [研究队列](../research/QUEUE.md)。

| ID | 作品 / 项目 | 类型 | 本轮范围与限制 | 来源 |
| --- | --- | --- | --- | --- |
''' + '\n'.join(work_rows) + '\n'
    claim_sections = ['# 证据主张表\n\n> 自动生成自 `data/claims.json`。`documented` 表示可查页面/作品事实，`self_report` 表示本人自述；二者都应阅读具体限制。\n']
    for c in d['claims']:
        claim_sections.append(f'''<a id="{c['id'].lower()}"></a>
## {c['id']} · {c['kind']}

{c['statement']}

来源：{_links(c['source_ids'], '../sources/cards/')}；定位：{c['locator']}。

**限制：** {c['limits']} 核对日期：{c['checked_at']}。
''')
    out['research/CLAIMS.md'] = '\n'.join(claim_sections)
    pattern_rows = []
    for p in d['patterns']:
        pattern_rows.append(f'| [{p["id"]}]({Path(p["path"]).name}) | {_table(p["title"])} | {p["confidence"]} | {_table(p["limitations"])} |')
    out['research/patterns/README.md'] = '''# 模式：待验证的研究解释

> 自动生成自 `data/patterns.json`。这里不是对人物的评分、人格测量或成功概率。

每个模式都有来源、支持主张、反向或限制性材料、替代解释和削弱条件。当前仍以本人自述为主，不因同一人有多个网页而提升独立性。“案例组数”是观察情境数，不是独立信源数。

| ID | 模式 | 当前信心 | 限制 |
| --- | --- | --- | --- |
''' + '\n'.join(pattern_rows) + '\n'
    queue_sections = ['# 下一步研究队列\n\n> 自动生成自 `data/reading-queue.json`。任务尚待执行；不是后台监控计划。\n']
    for q in sorted(d['reading-queue'], key=lambda x:(x['priority'], x['id'])):
        queue_sections.append(f'''## {q['id']} · {q['priority']} · {q['topic']}

状态：{q['status']}。问题：{q['question']}

下一步：{q['next_action']}

线索：{_links(q['source_ids'], '../sources/cards/')}
''')
    out['research/QUEUE.md'] = '\n'.join(queue_sections)
    return {p: body.rstrip() + '\n' for p, body in out.items()}


def build(root: Path, *, check: bool = False) -> list[str]:
    outputs = generated_files(root)
    stale: list[str] = []
    for rel, text in outputs.items():
        target = root / rel
        if not target.is_file() or target.read_text(encoding='utf-8') != text:
            stale.append(rel)
            if not check:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(text, encoding='utf-8')
    # Generated cards from removed sources must not linger as valid-looking evidence.
    for old in (root/'sources/cards').glob('S*.md'):
        rel = old.relative_to(root).as_posix()
        if rel not in outputs:
            stale.append(rel)
            if not check:
                old.unlink()
    return stale


def search(root: Path, query: str, limit: int = 20) -> list[dict[str, str]]:
    if not query.strip():
        raise ValueError('search query must not be empty')
    _, data = load_data(root)
    needle = query.casefold()
    hits: list[dict[str, str]] = []
    for name, rows in data.items():
        for row in rows:
            blob = json.dumps(row, ensure_ascii=False)
            if needle in blob.casefold():
                title = row.get('title', row.get('statement', row.get('topic', row.get('method', 'record'))))
                hits.append({'path': f'data/{name}.json', 'id': row.get('id', ''), 'text': title})
    # Avoid duplicate generated views; also search interpretive Markdown documents.
    generated = set(generated_files(root))
    for path in sorted((root/'research').rglob('*.md')):
        rel = path.relative_to(root).as_posix()
        if rel in generated:
            continue
        for line in path.read_text(encoding='utf-8').splitlines():
            if needle in line.casefold():
                hits.append({'path': rel, 'id': '', 'text': line[:240]})
                break
    return hits[:limit]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT, help='repository root (default: script parent)')
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('validate', help='validate schemas, dates, references and local file links')
    sub.add_parser('stats', help='show exact record counts and reading statuses')
    b = sub.add_parser('build', help='regenerate readable views from canonical JSON')
    b.add_argument('--check', action='store_true', help='do not write; return failure when generated files differ')
    q = sub.add_parser('search', help='offline literal search, not semantic retrieval')
    q.add_argument('query')
    q.add_argument('--limit', type=int, default=20)
    args = parser.parse_args(argv)
    root = args.root.resolve()
    try:
        if args.command == 'stats':
            print(json.dumps(stats_summary(root), ensure_ascii=False, indent=2))
        elif args.command == 'validate':
            errors = validate(root)
            if errors:
                for error in errors:
                    print(f'ERROR: {error}', file=sys.stderr)
                print(f'FAIL: {len(errors)} validation errors', file=sys.stderr)
                return 1
            print('PASS: schema subset, calendar dates, IDs, references and local file links.')
            print('Not checked: external availability, historical truth, source sufficiency or copyright.')
        elif args.command == 'build':
            errors = validate(root, check_links=False)
            if errors:
                for error in errors:
                    print(f'ERROR: {error}', file=sys.stderr)
                return 1
            changed = build(root, check=args.check)
            if args.check and changed:
                for path in changed:
                    print(f'generated file differs: {path}', file=sys.stderr)
                return 1
            print(f'PASS: generated views are current.' if args.check else f'Built views; {len(changed)} file(s) changed.')
        else:
            if args.limit < 1:
                raise ValueError('--limit must be at least 1')
            hits = search(root, args.query, args.limit)
            for hit in hits:
                print(f'{hit["path"]} {hit["id"]}\n  {hit["text"]}')
            print(f'{len(hits)} result(s); literal offline search, limited to {args.limit}.')
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
