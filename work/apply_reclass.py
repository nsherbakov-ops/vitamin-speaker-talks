# -*- coding: utf-8 -*-
"""Apply the 32-folder reclassification described by reclass_map.tsv.

reclass_map.tsv rows: path<TAB>vid<TAB>start_t<TAB>old<TAB>new<TAB>title
(produced by reclassify.py). This script performs the two persistent edits
so a future pipeline re-run cannot revert the folders:

  1. splits/<vid>.json — patch each long segment's "category" to `new`,
     keyed by (video_id, start_t). Style-preserving dump keeps diffs to the
     changed values only (pretty indent=1 files stay pretty; compact stay
     compact; trailing newline preserved).
  2. transcripts/<old>/<file> — for rows where old!=new, move the file to
     transcripts/<new>/ and rewrite its "Категория:" header line. Files that
     stay put still get their header corrected if it drifted.

keep.tsv (short talks) is handled separately by classify.py importing
reclassify.classify(). Run reindex.py afterwards to refresh INDEX.md.
"""
import os, csv, json, glob
import reclassify

WORK = os.path.dirname(os.path.abspath(__file__))
SPLITS = os.path.join(WORK, 'splits')
TRANS = os.path.join(WORK, '..', 'transcripts')
MAP = os.path.join(WORK, 'reclass_map.tsv')


def dump_like(orig_text, d):
    """Serialize d matching orig_text's whitespace style (verified to
    round-trip all 75 splits files byte-for-byte before any edit)."""
    if orig_text.count('\n') > 2:
        s = json.dumps(d, ensure_ascii=False, indent=1)
    else:
        s = json.dumps(d, ensure_ascii=False, separators=(',', ':'))
    if orig_text.endswith('\n'):
        s += '\n'
    return s


def rewrite_cat(txt, new):
    """Line-based replace of the 'Категория:' header line (byte-exact
    elsewhere; trailing newline preserved by split/join symmetry)."""
    lines = txt.split('\n')
    for i, ln in enumerate(lines):
        if ln.startswith('Категория:'):
            lines[i] = f'Категория: {new}'
            return '\n'.join(lines)
    return None  # no header line — signal caller


def load_map():
    rows = []
    with open(MAP, encoding='utf-8') as f:
        for r in csv.reader(f, delimiter='\t'):
            path, vid, st, old, new, title = r
            rows.append(dict(path=os.path.normpath(path), vid=vid, st=st,
                             old=old, new=new, title=title))
    return rows


def patch_splits(rows):
    newcat = {}
    for r in rows:
        if r['st'] != '':
            newcat[(r['vid'], str(int(r['st'])))] = r['new']
    pf = ps = 0
    for fp in sorted(glob.glob(os.path.join(SPLITS, '*.json'))):
        orig = open(fp, encoding='utf-8').read()
        d = json.loads(orig)
        vid = d.get('video_id')
        changed = False
        for s in d.get('segments', []):
            if s.get('drop'):
                # dropped segments emit no file; classify by topic so their
                # category stays on the current taxonomy (internal coherence).
                nc = reclassify.classify(s.get('topic') or '')
            else:
                nc = newcat.get((vid, str(int(s.get('start_t', 0)))))
            if nc and s.get('category') != nc:
                s['category'] = nc
                changed = True
                ps += 1
        if changed:
            with open(fp, 'w', encoding='utf-8') as o:
                o.write(dump_like(orig, d))
            pf += 1
    return pf, ps


def move_and_rewrite(rows):
    moved = header_only = missing = 0
    for r in rows:
        src, old, new = r['path'], r['old'], r['new']
        if not os.path.exists(src):
            print(f'  MISSING src: {src}'); missing += 1; continue
        txt = open(src, encoding='utf-8').read()
        newtxt = rewrite_cat(txt, new)
        if newtxt is None:
            print(f'  NO Категория header: {src}'); missing += 1; continue
        if old == new:
            if newtxt != txt:
                open(src, 'w', encoding='utf-8').write(newtxt)
                header_only += 1
            continue
        dstdir = os.path.join(TRANS, new)
        os.makedirs(dstdir, exist_ok=True)
        base = os.path.basename(src)
        stem, ext = os.path.splitext(base)
        dst = os.path.join(dstdir, base)
        i = 2
        while os.path.exists(dst):
            dst = os.path.join(dstdir, f'{stem}_{i}{ext}'); i += 1
        open(dst, 'w', encoding='utf-8').write(newtxt)
        os.remove(src)
        moved += 1
    return moved, header_only, missing


def main():
    rows = load_map()
    pf, ps = patch_splits(rows)
    print(f'splits: patched {ps} segments across {pf} files')
    mv, ho, miss = move_and_rewrite(rows)
    print(f'files: moved {mv}, header-only {ho}, problems {miss}')


if __name__ == '__main__':
    main()
