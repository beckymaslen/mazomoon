"""Copies each post's view total from Rebecca's Google Sheet (see tools/comments-apps-script.gs) into the post file
as `views: N`, so it shows next to the title in Pages CMS. Run daily by .github/workflows/views.yml."""
import json, os, re, sys, urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import blog  # noqa: E402

ROOT = blog.ROOT


def main():
    if not blog.COMMENTS_URL:
        print('No COMMENTS_URL set, nothing to do.')
        return
    with urllib.request.urlopen(blog.COMMENTS_URL + '?views=all', timeout=60) as r:
        data = json.load(r)
    counts = data.get('views') or {}
    b = blog.Blog(open(os.path.join(ROOT, 'src', 'site.html'), encoding='utf-8').read())
    changed = 0
    for p in b.all:
        n = sum(int(counts.get(x) or 0) for x in [p['path']] + list(p['old']))
        path = os.path.join(ROOT, 'content', p['folder'], p['file'])
        text = open(path, encoding='utf-8').read()
        m = re.match(r'---\r?\n(.*?)\r?\n---', text, re.S)
        if not m:
            continue
        head = m.group(1)
        if re.search(r'^views:', head, re.M):
            new = re.sub(r'^views:.*$', f'views: {n}', head, count=1, flags=re.M)
        elif n:
            new = head + f'\nviews: {n}'
        else:
            continue
        if new != head:
            open(path, 'w', encoding='utf-8').write(text[:m.start(1)] + new + text[m.end(1):])
            changed += 1
    print(f'Updated view counts in {changed} post(s).')


if __name__ == '__main__':
    main()
