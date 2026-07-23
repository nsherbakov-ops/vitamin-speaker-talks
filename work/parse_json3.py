# -*- coding: utf-8 -*-
import json, sys, re

def parse_json3(path):
    with open(path, encoding='utf-8') as f:
        data = json.load(f)
    lines = []
    for ev in data.get('events', []):
        segs = ev.get('segs')
        if not segs:
            continue
        text = ''.join(s.get('utf8', '') for s in segs)
        text = text.replace('\n', ' ').strip()
        if text:
            lines.append(text)
    # dedup consecutive identical lines (rolling-caption artifact)
    out = []
    for ln in lines:
        if out and out[-1] == ln:
            continue
        out.append(ln)
    full = ' '.join(out)
    full = re.sub(r'\s+', ' ', full).strip()
    return full

if __name__ == '__main__':
    txt = parse_json3(sys.argv[1])
    print(f"CHARS={len(txt)} WORDS={len(txt.split())}")
    print("--- first 800 ---")
    print(txt[:800])
    print("--- last 400 ---")
    print(txt[-400:])
