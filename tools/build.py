"""Build the LARMORX documentation site into _site/.

    python tools/build.py              build into _site/ and check it
    python tools/build.py --serve      build, serve, rebuild on every change
    python tools/build.py --preview    also write _preview/index.html, the home
                                       page as one self-contained file

Pages are Markdown with YAML front matter (content/*.md), rendered first as
Jinja (so a page can use the site's data and helpers), then as Markdown, then
into a layout from templates/. Static files are copied from static/.

Every build checks what it wrote: internal links and their anchors, the main
repository's files that pages link to (when that repository is checked out
next to this one, ../larmorx, or given with --main-repo), one h1 per page,
heading levels that do not skip, and leftovers of the template language.
Problems stop the build (exit status 1).
"""

from __future__ import annotations

import argparse
import base64
import html
import re
import shutil
import sys
import threading
import time
from dataclasses import dataclass, field
from html.parser import HTMLParser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urljoin, urlsplit

import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined
from markdown_it import MarkdownIt
from markupsafe import Markup

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
TEMPLATES = ROOT / "templates"
STATIC = ROOT / "static"
DATA = ROOT / "data"
OUT = ROOT / "_site"
PREVIEW = ROOT / "_preview"
DEFAULT_MAIN_REPO = ROOT.parent / "larmorx"
GOOGLE_FONTS = ("https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1"
                "&family=Inter:wght@400;500;600&family=JetBrains+Mono&display=swap")


# ----------------------------------------------------------------- pages
@dataclass
class Page:
    source: Path
    url: str                      # "" for the home page, "validation/", "404.html"
    meta: dict
    body: str
    html: str = ""
    toc: list = field(default_factory=list)

    @property
    def out(self) -> Path:
        return OUT / (self.url + "index.html" if self.url == "" or self.url.endswith("/") else self.url)

    @property
    def path(self) -> str:
        """The page's path on the site, from its root: "/", "/validation/"."""
        return "/" + self.url

    @property
    def title(self) -> str:
        return self.meta.get("title", "")


def read_page(path: Path) -> Page:
    text = path.read_text(encoding="utf-8")
    meta, body = {}, text
    if text.startswith("---\n"):
        end = text.find("\n---\n", 4)
        if end < 0:
            raise SystemExit(f"{path}: front matter not closed")
        meta = yaml.safe_load(text[4:end]) or {}
        body = text[end + 5:]
    rel = path.relative_to(CONTENT).as_posix()
    if rel == "index.md":
        url = ""
    elif rel == "404.md":
        url = "404.html"
    elif rel.endswith("/index.md"):
        url = rel[: -len("index.md")]
    else:
        url = rel[: -len(".md")] + "/"
    return Page(path, url, meta, body)


def slug(text: str) -> str:
    s = re.sub(r"<[^>]+>", "", text).lower()
    s = re.sub(r"[^\w\s-]", "", s)
    return re.sub(r"[\s_]+", "-", s).strip("-")


# -------------------------------------------------------------- markdown
def make_markdown(site: dict, repo_paths: set) -> MarkdownIt:
    md = MarkdownIt("commonmark", {"html": True, "typographer": True})
    md.enable(["table", "replacements", "smartquotes"])

    def repo_links(state):
        # `[text](repo:docs/x.md)`: a file in the main repository.
        def walk(tokens):
            for t in tokens:
                if t.type == "link_open":
                    href = t.attrGet("href") or ""
                    if href.startswith("repo:"):
                        t.attrSet("href", repo_url(site, href[5:], repo_paths))
                    elif href.startswith("/") and "link" in state.env:
                        # a path on this site, made relative to the page
                        t.attrSet("href", state.env["link"](href))
                if t.children:
                    walk(t.children)
        walk(state.tokens)

    def heading_ids(state):
        # Every h2-h4 gets an id: its slug, or `{#id}` written after it.
        seen = set()
        toks = state.tokens
        for i, t in enumerate(toks):
            if t.type != "heading_open" or t.tag not in ("h2", "h3", "h4"):
                continue
            inline = toks[i + 1]
            m = re.search(r"\s*\{#([\w-]+)\}\s*$", inline.content)
            if m:
                ident = m.group(1)
                inline.content = inline.content[: m.start()]
                last = inline.children[-1] if inline.children else None
                if last is not None and last.type == "text":
                    last.content = re.sub(r"\s*\{#[\w-]+\}\s*$", "", last.content)
            else:
                ident = slug(inline.content)
            base, n = ident, 2
            while ident in seen:
                ident, n = f"{base}-{n}", n + 1
            seen.add(ident)
            t.attrSet("id", ident)
            text = "".join(c.content for c in (inline.children or []) if c.type in ("text", "code_inline"))
            state.env.setdefault("toc", []).append({"level": int(t.tag[1]), "id": ident, "text": text})

    md.core.ruler.push("repo_links", repo_links)
    md.core.ruler.push("heading_ids", heading_ids)

    def fence(self, tokens, idx, options, env):
        t = tokens[idx]
        lang = t.info.strip().split()[0] if t.info.strip() else ""
        lines = []
        for line in t.content.rstrip("\n").split("\n"):
            m = re.search(r"(^|\s)(#.*)$", line) if lang in ("bash", "sh", "python", "console") else None
            if m:
                lines.append(html.escape(line[: m.start(2)]) + '<span class="c">' + html.escape(m.group(2)) + "</span>")
            else:
                lines.append(html.escape(line))
        attr = f' data-lang="{lang}"' if lang else ""
        label = f'<span class="code-lang">{lang}</span>' if lang else ""
        return (f'<div class="code"{attr}>{label}<button class="code-copy" type="button">Copy</button>'
                f'<pre><code>{chr(10).join(lines)}</code></pre></div>\n')

    md.add_render_rule("fence", fence)
    md.add_render_rule("table_open", lambda *a: '<div class="table-wrap"><table>\n')
    md.add_render_rule("table_close", lambda *a: "</table></div>\n")
    return md


def repo_url(site: dict, path: str, repo_paths: set) -> str:
    path = path.lstrip("/")
    repo_paths.add(path)
    base = site["repo_tree"] if path.endswith("/") or path == "" else site["repo_blob"]
    return base + path


# ---------------------------------------------------------------- build
class Site:
    def __init__(self, main_repo: Path | None):
        self.site = yaml.safe_load((ROOT / "site.yml").read_text(encoding="utf-8"))
        self.data = {p.stem: yaml.safe_load(p.read_text(encoding="utf-8")) for p in sorted(DATA.glob("*.yml"))}
        self.main_repo = main_repo
        self.repo_paths: set[str] = set()
        self.md = make_markdown(self.site, self.repo_paths)
        self.base_path = urlsplit(self.site["base_url"]).path  # "/larmorx_documentation/"

    # A link from `page` to a path on this site ("/static/x.css", "/#a"):
    # relative, so the site works under any prefix and from the disk. The 404
    # page is served at any depth, so its links are absolute.
    def link(self, page: Page, target: str) -> str:
        if not target.startswith("/"):
            return target
        if page.url == "404.html":
            return self.base_path + target[1:]
        depth = page.url.count("/")
        rel = "../" * depth + target[1:]
        if rel == "" or rel.startswith("#"):
            rel = "./" + rel
        return rel

    def helpers(self, page: Page) -> dict:
        md = self.md

        def md_inline(text) -> Markup:
            return Markup(md.renderInline(str(text or ""), {"link": lambda t: self.link(page, t)}))

        def acronym(text) -> Markup:
            # "*L*ibrary of ..." marks the letters that make the name.
            out = html.escape(str(text))
            return Markup(re.sub(r"\*([^*]+)\*", r"<b>\1</b>", out))

        return {
            "site": self.site, "data": self.data, "page": page,
            "link": lambda t: self.link(page, t),
            "repo": lambda p: repo_url(self.site, p, self.repo_paths),
            "eco": {e["id"]: e for e in self.data.get("ecosystems", [])},
            "nav": [{"title": i["title"], "href": self.link(page, i["url"]),
                     "current": i["url"].split("#")[0] == page.path and "#" not in i["url"]}
                    for i in self.site.get("nav", [])],
            "docs_nav": [{"title": i["title"], "href": self.link(page, i["url"]),
                          "current": i["url"] == page.path} for i in self.site.get("docs", [])],
            "md_inline": md_inline, "acronym": acronym,
        }

    def env(self) -> Environment:
        env = Environment(loader=FileSystemLoader(TEMPLATES), undefined=StrictUndefined, autoescape=True,
                          trim_blocks=False, lstrip_blocks=False)
        return env

    def build(self) -> int:
        t0 = time.time()
        if OUT.exists():
            shutil.rmtree(OUT)
        shutil.copytree(STATIC, OUT / "static")
        (OUT / ".nojekyll").write_text("", encoding="utf-8")
        pages = [read_page(p) for p in sorted(CONTENT.rglob("*.md"))]
        tenv = self.env()
        for page in pages:
            h = self.helpers(page)
            for k in ("md_inline", "acronym"):
                tenv.filters[k] = h[k]
            # `{#id}` after a heading is Markdown here, not a Jinja comment
            cenv = Environment(undefined=StrictUndefined, autoescape=False,
                               comment_start_string="{##", comment_end_string="##}")
            cenv.filters.update({"md_inline": h["md_inline"], "acronym": h["acronym"]})
            body = cenv.from_string(page.body).render(**h)
            env: dict = {"link": h["link"]}
            page.html = Markup(self.md.render(body, env))
            page.toc = [e for e in env.get("toc", []) if e["level"] in (2, 3)]
            page.meta.setdefault("description", self.site["description"])
            ctx = dict(h)
            ctx["page"] = PageView(page, self.site)
            template = page.meta.get("template", "404" if page.url == "404.html" else "doc")
            out = tenv.get_template(f"{template}.html").render(**ctx)
            page.out.parent.mkdir(parents=True, exist_ok=True)
            page.out.write_text(out, encoding="utf-8")
        self.sitemap(pages)
        problems, notes = check(OUT, self.base_path, self.repo_paths, self.main_repo)
        for n in notes:
            print(f"note: {n}")
        for p in problems:
            print(f"PROBLEM: {p}")
        print(f"built {len(pages)} pages in {time.time() - t0:.2f} s; {len(problems)} problems")
        return 1 if problems else 0

    def sitemap(self, pages) -> None:
        urls = [self.site["base_url"] + p.url for p in pages if p.url != "404.html"]
        body = "".join(f"<url><loc>{html.escape(u)}</loc></url>" for u in urls)
        (OUT / "sitemap.xml").write_text(
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{body}</urlset>\n', encoding="utf-8")


class PageView:
    """What a layout sees of a page."""

    def __init__(self, page: Page, site: dict):
        self.meta = page.meta
        self.html = page.html
        self.toc = page.toc
        self.url = page.url
        self.is_home = page.url == ""
        self.title = page.meta.get("title", site["title"])
        self.description = page.meta.get("description") or site["description"]
        self.canonical = site["base_url"] + page.url if page.url != "404.html" else ""


# ---------------------------------------------------------------- checks
class Collector(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids: set[str] = set()
        self.refs: list[tuple[str, str]] = []
        self.headings: list[int] = []
        self.text: list[str] = []
        self._skip = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.add(a["id"])
        if tag in ("script", "style"):
            self._skip += 1
        for name in ("href", "src"):
            if a.get(name) is not None and tag in ("a", "link", "img", "script", "use", "source", "iframe"):
                if not (tag == "link" and a.get("rel") in ("preconnect", "dns-prefetch")):
                    self.refs.append((tag, a[name]))
        for name in ("data-src",):
            if a.get(name):
                self.refs.append((tag, a[name]))
        if re.fullmatch(r"h[1-6]", tag):
            self.headings.append(int(tag[1]))

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self._skip -= 1

    def handle_data(self, data):
        if not self._skip:
            self.text.append(data)


def check(out: Path, base_path: str, repo_paths: set, main_repo: Path | None):
    problems, notes = [], []
    pages = {}
    for f in sorted(out.rglob("*.html")):
        c = Collector()
        c.feed(f.read_text(encoding="utf-8"))
        pages[f] = c
    origin = "https://site.invalid"
    for f, c in pages.items():
        rel = f.relative_to(out).as_posix()
        page_url = origin + base_path + rel
        h1 = c.headings.count(1)
        if h1 != 1:
            problems.append(f"{rel}: {h1} h1 headings (one expected)")
        for a, b in zip(c.headings, c.headings[1:]):
            if b > a + 1:
                problems.append(f"{rel}: heading h{a} followed by h{b}")
                break
        text = "".join(c.text)
        if "{{" in text or "{%" in text:
            problems.append(f"{rel}: a template expression was left in the text")
        for tag, ref in c.refs:
            if ref.startswith(("http://", "https://", "mailto:", "data:", "javascript:", "//")):
                continue
            if ref.startswith("#"):
                if ref[1:] and ref[1:] not in c.ids and ref != "#top":
                    problems.append(f"{rel}: <{tag}> {ref}: no such id on this page")
                continue
            target = urljoin(page_url, ref)
            parts = urlsplit(target)
            if not parts.path.startswith(base_path):
                problems.append(f"{rel}: <{tag}> {ref}: outside the site")
                continue
            path = out / unquote(parts.path[len(base_path):])
            if parts.path.endswith("/") or path.is_dir():
                path = path / "index.html"
            if not path.exists():
                problems.append(f"{rel}: <{tag}> {ref}: {path.relative_to(out).as_posix()} does not exist")
                continue
            if parts.fragment and path.suffix == ".html":
                ids = pages[path].ids if path in pages else set()
                if parts.fragment not in ids:
                    problems.append(f"{rel}: <{tag}> {ref}: no id {parts.fragment!r} in {path.relative_to(out).as_posix()}")
    if main_repo and (main_repo / ".git").exists():
        for p in sorted(repo_paths):
            if not (main_repo / p).exists():
                problems.append(f"main repository: {p} does not exist (in {main_repo})")
        notes.append(f"{len(repo_paths)} links into the main repository checked against {main_repo}")
    else:
        notes.append(f"{len(repo_paths)} links into the main repository not checked (no checkout found; --main-repo)")
    return problems, notes


# --------------------------------------------------------------- preview
def preview(site: dict) -> Path:
    """The home page as one file: CSS and JavaScript inline, the hero's data
    and pictures as data URIs, the fonts from Google Fonts."""
    page = (OUT / "index.html").read_text(encoding="utf-8")
    css = (OUT / "static/css/site.css").read_text(encoding="utf-8")
    css = re.sub(r"@font-face\s*\{[^}]*\}\s*", "", css)

    def data_uri(rel: str, mime: str) -> str:
        return f"data:{mime};base64," + base64.b64encode((OUT / rel).read_bytes()).decode()

    page = re.sub(r'<link rel="preload"[^>]*>\n?', "", page)
    page = page.replace('<link rel="stylesheet" href="static/css/site.css">',
                        '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
                        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
                        f'<link rel="stylesheet" href="{html.escape(GOOGLE_FONTS)}">\n<style>\n{css}</style>')
    for js in ("site.js", "hero.js"):
        code = (OUT / "static/js" / js).read_text(encoding="utf-8")
        page = page.replace(f'<script src="static/js/{js}" defer></script>', f"<script>\n{code}</script>")
    page = page.replace('data-src="static/hero/hero.bin"',
                        f'data-src="{data_uri("static/hero/hero.bin", "application/octet-stream")}"')
    for theme in ("light", "dark"):
        page = page.replace(f'src="static/hero/hero-{theme}.svg"',
                            f'src="{data_uri(f"static/hero/hero-{theme}.svg", "image/svg+xml")}"')
    page = page.replace('href="static/brand/favicon.svg"',
                        f'href="{data_uri("static/brand/favicon.svg", "image/svg+xml")}"')
    page = re.sub(r'<link rel="apple-touch-icon"[^>]*>\n?', "", page)
    page = page.replace('href="./"', 'href="#top"').replace('href="./#', 'href="#')
    # Every other link into this site goes to the published site.
    page = re.sub(r'(href|src)="(?!https?:|data:|#|mailto:)([^"]+)"',
                  lambda m: f'{m.group(1)}="{site["base_url"]}{m.group(2)}"', page)
    PREVIEW.mkdir(exist_ok=True)
    out = PREVIEW / "index.html"
    out.write_text(page, encoding="utf-8")
    left = re.findall(r'(?:src|href)="(?!https?:|data:|#|mailto:)[^"]+"', page)
    if left:
        print("PROBLEM: the preview still refers to local files:", left[:5])
    size = out.stat().st_size
    print(f"preview: {out.relative_to(ROOT)} ({size / 1e6:.2f} MB)")
    if size > 5e6:
        print("PROBLEM: the preview is larger than 5 MB")
    return out


# ----------------------------------------------------------------- serve
def serve(port: int, build) -> None:
    sitecfg = yaml.safe_load((ROOT / "site.yml").read_text(encoding="utf-8"))
    base = urlsplit(sitecfg["base_url"]).path

    class Handler(SimpleHTTPRequestHandler):
        def __init__(self, *a, **kw):
            super().__init__(*a, directory=str(OUT), **kw)

        def do_GET(self):
            path = urlsplit(self.path).path
            if not path.startswith(base):
                self.send_response(302)
                self.send_header("Location", base)
                self.end_headers()
                return
            self.path = "/" + self.path[len(base):]
            local = Path(self.translate_path(self.path))
            if not local.exists():
                self.send_response(404)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write((OUT / "404.html").read_bytes())
                return
            super().do_GET()

        def end_headers(self):
            self.send_header("Cache-Control", "no-store")
            super().end_headers()

        def log_message(self, *a):
            pass

    def snapshot():
        files = [ROOT / "site.yml", Path(__file__)]
        for d in (CONTENT, TEMPLATES, STATIC, DATA):
            files += [p for p in d.rglob("*") if p.is_file()]
        return {p: p.stat().st_mtime for p in files}

    def watch():
        last = snapshot()
        while True:
            time.sleep(0.8)
            now = snapshot()
            if now != last:
                last = now
                try:
                    build()
                except Exception as e:  # keep serving; show the error
                    print(f"build failed: {e}")

    threading.Thread(target=watch, daemon=True).start()
    httpd = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"serving http://localhost:{port}{base} (Ctrl+C to stop)")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--serve", action="store_true", help="serve _site and rebuild on every change")
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--preview", action="store_true", help="also write _preview/index.html")
    ap.add_argument("--main-repo", type=Path, default=DEFAULT_MAIN_REPO,
                    help="a checkout of the main repository, to check the links into it (default: ../larmorx)")
    args = ap.parse_args(argv)

    def build() -> int:
        s = Site(args.main_repo)
        status = s.build()
        if args.preview and status == 0:
            preview(s.site)
        return status

    status = build()
    if args.serve:
        serve(args.port, build)
        return 0
    return status


if __name__ == "__main__":
    sys.exit(main())
