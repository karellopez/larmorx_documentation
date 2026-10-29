"""The validation evidence on the site's pages: worked examples, metrics, verdicts, charts and
the case explorer, rendered as HTML from the JSON that larmorx exports
(``python -m larmorx_validation evidence <tool> --site <this repository>``, the main
repository's ``docs/figures.md``) into ``static/evidence/<tool>.json``.

Everything here is static HTML that works without JavaScript: the examples' still panels and
their metrics, the charts as bars and dots positioned in HTML, the full table of cases.
``static/js/evidence.js`` makes them interactive from the same JSON. Numbers are never computed
here, only formatted: each one carries ``data-ev`` (its JSON pointer), and the review check
(``tools/review/shoot.mjs --eval`` with ``LX_EVIDENCE.check()``, README.md) compares what
a page shows with the JSON.
"""

from __future__ import annotations

import html
import json
import math
import re
from pathlib import Path

from markupsafe import Markup

ROLE_LABELS = {
    "input": "Input",
    "original": "Original program",
    "fmriprep": "fMRIPrep's own output",
    "reference": "Original, as a reference",
    "larmorx": "LARMORX",
}


def esc(s) -> str:
    return html.escape(str(s), quote=True)


def ptr(*parts) -> str:
    """A JSON pointer (RFC 6901)."""
    return "".join("/" + str(p).replace("~", "~0").replace("/", "~1") for p in parts)


# ------------------------------------------------------------------------------- numbers


def fmt_count(n) -> str:
    return f"{int(n):,}"


def fmt_sig(x, digits: int = 3) -> str:
    """``x`` with ``digits`` significant digits, as Python's ``g`` format writes it, with a
    true minus sign."""
    if x is None:
        return "–"
    if x == 0:
        return "0"
    s = f"{x:.{digits}g}"
    if "e" in s:
        m, e = s.split("e")
        s = f"{m}e{int(e)}"
    return s.replace("-", "−")


def fmt_share(x) -> str:
    if x == 0:
        return "0 %"
    if x == 1:
        return "100 %"
    return fmt_sig(100 * x, 3) + " %"


def fmt_seconds(x) -> str:
    return fmt_sig(x, 3) + " s"


def _shortest(x: float, max_digits: int, same) -> str:
    expo = x != 0 and (abs(x) < 1e-3 or abs(x) >= 1e7)
    t = ""
    for p in range(1, max_digits + 1):
        t = f"{x:.{p - 1}e}" if expo else f"{x:.{p}g}"
        if same(float(t)):
            break
    if "e" in t:
        m, e = t.split("e")
        if "." in m:
            m = m.rstrip("0").rstrip(".")
        t = f"{m}e{int(e)}"
    return t.replace("-", "−")


def fmt_f32(x) -> str:
    """The fewest digits that give back the float32 value ``x``."""
    import struct

    if x == 0:
        return "0"

    def same(y: float) -> bool:
        return struct.unpack("<f", struct.pack("<f", y))[0] == x

    return _shortest(float(x), 9, same)


def fmt_f64(x) -> str:
    """The fewest digits that give back the float64 value ``x``."""
    if x == 0:
        return "0"
    return _shortest(float(x), 17, lambda y: y == x)


FORMATS = {
    "sig": lambda v: fmt_sig(v, 3),
    "sig2": lambda v: fmt_sig(v, 2),
    "sig4": lambda v: fmt_sig(v, 4),
    "sig6": lambda v: fmt_sig(v, 6),
    "count": fmt_count,
    "f32": fmt_f32,
    "f64": fmt_f64,
    "share": fmt_share,
    "seconds": fmt_seconds,
}


class Evidence:
    """The evidence helpers of one page (links are relative to it)."""

    def __init__(self, root: Path, verdicts: list[dict], link, repo, md_inline, problems: list):
        self.root = root
        self.verdicts = {v["id"]: v for v in verdicts}
        self.order = [v["id"] for v in verdicts]
        self.link = link
        self.repo = repo
        self.md_inline = md_inline
        self.problems = problems
        self._docs: dict[str, dict] = {}

    # ------------------------------------------------------------------ data

    def doc(self, tool: str) -> dict:
        if tool not in self._docs:
            path = self.root / "static" / "evidence" / f"{tool}.json"
            if not path.is_file():
                raise SystemExit(f"evidence {tool!r}: {path.relative_to(self.root)} does not exist")
            doc = json.loads(path.read_text(encoding="utf-8"))
            self._check(tool, doc)
            self._docs[tool] = doc
        return self._docs[tool]

    def _check(self, tool: str, doc: dict) -> None:
        for v in set(re.findall(r'"verdict": "([^"]+)"', json.dumps(doc))):
            if v not in self.verdicts:
                self.problems.append(f"evidence {tool}: unknown verdict {v!r} (data/verdicts.yml)")
        blobs = self.root / "static" / "evidence" / "blobs"
        for name in set(re.findall(r"\b[0-9a-f]{24}\.(?:bin|webp)\b", json.dumps(doc))):
            if not (blobs / name).is_file():
                self.problems.append(f"evidence {tool}: blob {name} is missing")

    def num(self, tool: str, pointer: str, text: str, cls: str = "num") -> str:
        return f'<span class="{cls}" data-ev="{esc(tool)}:{esc(pointer)}">{esc(text)}</span>'

    def href(self, target: str) -> str:
        """A link from the evidence JSON: a repository path (``docs/...#anchor``) or a path
        on this site (``/validation/#...``)."""
        if target.startswith("/"):
            return self.link(target)
        path, _, anchor = target.partition("#")
        return self.repo(path) + (f"#{anchor}" if anchor else "")

    def text(self, s: str) -> Markup:
        """A sentence from the JSON, with Markdown's inline code and links."""
        return self.md_inline(s)

    # -------------------------------------------------------------- verdicts

    def verdict(self, vid: str, count=None, label: str | None = None, tool: str = "", pointer=""):
        v = self.verdicts.get(vid)
        if v is None:
            self.problems.append(f"unknown verdict {vid!r}")
            return Markup(esc(vid))
        n = ""
        if count is not None:
            n = " " + (self.num(tool, pointer, fmt_count(count)) if tool else esc(count))
        return Markup(
            f'<a class="verdict v-{esc(vid)}" href="{self.link("/validation/#verdict-" + vid)}" '
            f'title="{esc(v["means"])}"><i aria-hidden="true"></i>'
            f'<span>{esc(label or v["label"])}</span>{n}</a>'
        )

    def legend(self, ids: list[str] | None = None) -> Markup:
        ids = ids or self.order
        items = "".join(f"<li>{self.verdict(i, label=self.verdicts[i]['label'])}</li>" for i in ids)
        return Markup(f'<ul class="verdict-legend">{items}</ul>')

    def taxonomy(self) -> Markup:
        """The Validation page's definitions, one per verdict, each an anchor."""
        rows = []
        for v in self.verdicts.values():
            rows.append(
                f'<div class="vdef" id="verdict-{esc(v["id"])}"><dt><span class="verdict v-{esc(v["id"])}">'
                f'<i aria-hidden="true"></i><span>{esc(v["label"])}</span></span></dt>'
                f'<dd><p>{esc(v["means"])}</p><p class="vdef-matters">{esc(v["matters"])}</p></dd></div>'
            )
        return Markup(f'<dl class="vdefs">{"".join(rows)}</dl>')

    # ------------------------------------------------------------- examples

    def example(self, tool: str, ex_id: str) -> Markup:
        doc = self.doc(tool)
        k, ex = next(((i, e) for i, e in enumerate(doc["examples"]) if e["id"] == ex_id), (None, None))
        if ex is None:
            raise SystemExit(f"evidence {tool}: no example {ex_id!r}")
        base = ptr("examples", k)
        src = self.link(f"/static/evidence/{tool}.json")
        blobs = self.link("/static/evidence/blobs/")
        poster = ex["poster"]
        panels = {p["id"]: p for p in ex["panels"]}
        diffs = {d["id"]: d for d in ex["diffs"]}
        out = ex["default"]["output"]
        cells = []
        for pid in ex["default"]["panels"]:
            p = panels[pid]
            img = poster["panels"].get(pid)
            role = ROLE_LABELS.get(p["role"], p["role"])
            cells.append(
                f'<figure class="ev-panel role-{esc(p["role"])}" data-panel="{esc(pid)}">'
                f'<div class="ev-canvas" style="aspect-ratio:{poster["aspect"]}">'
                + (f'<img src="{blobs}{img}" alt="" loading="lazy" decoding="async">' if img else "")
                + f'</div><figcaption><span class="ev-role">{esc(role)}</span>'
                f'<span class="ev-label">{esc(p["label"])}</span>'
                + (f'<span class="ev-sub">{esc(p["sub"])}</span>' if p.get("sub") else "")
                + "</figcaption></figure>"
            )
        for did in ex["default"]["diffs"]:
            dd = diffs[did]
            j = ex["diffs"].index(dd)
            m = dd["metrics"][out] if out in dd["metrics"] else next(iter(dd["metrics"].values()))
            img = poster["diffs"].get(did)
            body = (
                f'<img src="{blobs}{img}" alt="" loading="lazy" decoding="async">'
                if img and not m["identical"]
                else '<p class="ev-identical"><b>Bit-identical</b><span>'
                + self.num(tool, ptr("examples", k, "diffs", j, "metrics", out, "voxels"), fmt_count(m["voxels"]))
                + " of " + self.num(tool, ptr("examples", k, "diffs", j, "metrics", out, "voxels"), fmt_count(m["voxels"]))
                + " voxels equal</span></p>"
            )
            rng = poster.get("ranges", {}).get(did)
            scale = ""
            if rng and not m["identical"]:
                scale = f'<span class="ev-sub ev-range">scale ±{esc(fmt_sig(rng))}</span>'
            cells.append(
                f'<figure class="ev-panel ev-diff kind-{esc(dd["kind"])}" data-diff="{esc(did)}">'
                f'<div class="ev-canvas" style="aspect-ratio:{poster["aspect"]}">{body}</div>'
                f'<figcaption><span class="ev-role">{esc(dd["role_label"])}</span>'
                f'<span class="ev-label">{esc(dd["label"])}</span>{scale}</figcaption></figure>'
            )
        note = (
            f'<p class="ev-still">{esc(poster["caption"])} '
            '<span class="ev-nojs">The interactive viewer needs JavaScript; the metrics below are '
            "complete without it.</span></p>"
        )
        view = ex.get("view") or {}
        if view.get("kind") == "slices":
            vox = ", ".join(str(int(v) + 1) for v in view["voxel"])
            note += (
                '<p class="ev-viewnote">Stored for this example: three full-resolution slices, '
                f"one per plane, through display voxel ({vox}): where the main comparison differs most, or the field's centre where nothing differs; "
                "every metric is computed over every voxel of the files.</p>"
            )
        facts = "".join(
            f"<dt>{esc(f['label'])}</dt><dd>{self.text(f['text'])}</dd>" for f in ex["facts"]
        )
        html_ = (
            f'<section class="ev-example" id="example-{esc(ex_id)}" data-ev-tool="{esc(tool)}" '
            f'data-ev-example="{esc(ex_id)}" data-ev-src="{src}" data-ev-blobs="{blobs}">'
            f'<div class="ev-head"><p class="kicker">Worked example</p>'
            f'<p class="ev-title">{esc(ex["title"])}</p>'
            f'<p class="ev-sum">{self.text(ex["summary"])}</p>'
            f'<dl class="ev-facts">{facts}</dl>'
            + self.credits_html(doc, ex.get("credits", []), "Data shown")
            + "</div>"
            f'<div class="ev-viewer"><div class="ev-panels">{"".join(cells)}</div>{note}</div>'
            + "".join(
                self.lines_html(tool, spec, ptr("examples", k, "lines", lid))
                for lid, spec in ex.get("lines", {}).items()
            )
            + self.chain(tool, k)
            + self.metrics(tool, k)
            + "".join(
                self.table_html(tool, t, ptr("examples", k, "tables", i))
                for i, t in enumerate(ex.get("tables", []))
            )
            + self.provenance(tool, ex)
            + "</section>"
        )
        return Markup(html_)

    def chain(self, tool: str, k: int) -> str:
        ex = self.doc(tool)["examples"][k]
        ch = ex.get("chain")
        if not ch:
            return ""
        items = []
        for i, step in enumerate(ch["steps"]):
            nodes = "".join(
                f'<li class="role-{esc(n["role"])}"><span>{esc(n["label"])}</span>'
                + (f'<small>{esc(n["sub"])}</small>' if n.get("sub") else "")
                + "</li>"
                for n in step["nodes"]
            )
            items.append(f'<li class="ev-chain-step"><ul class="ev-chain-nodes">{nodes}</ul></li>')
            if i < len(ch["links"]):
                link = ch["links"][i]
                p = ptr("examples", k, "chain", "links", i, "max_abs")
                what = (
                    "bit-identical"
                    if link["max_abs"] == 0
                    else "max |Δ| " + self.num(tool, p, fmt_sig(link["max_abs"]))
                )
                items.append(
                    f'<li class="ev-chain-link{" is-zero" if link["max_abs"] == 0 else ""}">'
                    f'<span class="ev-chain-cause">{esc(link["cause"])}</span>'
                    f'<span class="ev-chain-delta">{what}</span></li>'
                )
        return (
            f'<div class="ev-chain"><p class="ev-chain-title">{esc(ch["title"])}</p>'
            f'<ol class="ev-chain-flow">{"".join(items)}</ol>'
            f'<p class="ev-chain-note">{self.text(ch["note"])}</p></div>'
        )

    GROUPS = (
        ("main fmriprep", "LARMORX against the original program and fMRIPrep"),
        ("check", "LARMORX against itself: threads and modes"),
        ("variability", "The original against itself: the yardstick"),
    )

    def metrics(self, tool: str, k: int) -> str:
        """One row per comparison and output, grouped: LARMORX against the original, LARMORX
        against itself, the original against itself. A comparison that gives the same bytes in
        every output is one row."""
        ex = self.doc(tool)["examples"][k]
        outputs = ex["outputs"]
        multi = len(outputs) > 1
        ncol = 6 if multi else 5
        head = (
            "<tr><th scope=col class=cmph>Comparison (A − B), verdict and reason</th>"
            + ("<th scope=col>Output</th>" if multi else "")
            + "<th scope=col class=n>max |Δ|</th><th scope=col class=n>Values that differ</th>"
            "<th scope=col class=n>RMS of Δ</th><th scope=col class=n>max |Δ| ÷ range</th>"
            "<th scope=col class=n>1 − NCC</th></tr>"
        )
        body = []
        for kinds, title in ex.get("groups") or self.GROUPS:
            group = [(j, d) for j, d in enumerate(ex["diffs"]) if d["kind"] in kinds.split()]
            if not group:
                continue
            body.append(
                f'<tbody class="grp"><tr class="grp-head"><th colspan="{ncol + 1}" scope=colgroup>'
                f"{esc(title)}</th></tr>"
            )
            for j, d in group:
                outs = [o for o in outputs if o["id"] in d["metrics"]]
                same = all(d["metrics"][o["id"]]["identical"] for o in outs)
                links = " ".join(
                    f'<a href="{self.href(lk["href"])}">{esc(lk["label"])}</a>'
                    for lk in d.get("links", [])
                )
                chip = (
                    self.verdict(d["verdict"])
                    if d.get("verdict")
                    else Markup('<span class="ev-ref">reference</span>')
                )
                rows_n = 1 if same else len(outs)
                span = f' rowspan="{rows_n}"' if rows_n > 1 else ""
                head_cell = (
                    f'<th scope="row"{span} class="cmp"><span class="cmp-label">{esc(d["label"])}</span>'
                    f'<span class="cmp-verdict">{chip}</span><span class="cmp-why">{self.text(d["reason"])}'
                    + (f' <span class="ev-links">{links}</span>' if links else "")
                    + "</span></th>"
                )
                if same:
                    o = outs[0]
                    p = ptr("examples", k, "diffs", j, "metrics", o["id"], "voxels")
                    what = "both outputs" if len(outs) == 2 else "every output" if len(outs) > 2 else o["label"]
                    cells = [head_cell]
                    if multi:
                        cells.append(f"<td class=out>{esc(what)}</td>")
                    n = self.num(tool, p, fmt_count(d["metrics"][o["id"]]["voxels"]))
                    cells.append(f'<td colspan="5" class="same">identical: 0 of {n} values differ</td>')
                    body.append(f'<tr class="kind-{esc(d["kind"])} first is-same">{"".join(cells)}</tr>')
                    continue
                for oi, o in enumerate(outs):
                    m = d["metrics"][o["id"]]

                    def p(key, jj=j, oo=o["id"]):
                        return ptr("examples", k, "diffs", jj, "metrics", oo, key)

                    differ = (
                        self.num(tool, p("differ"), fmt_count(m["differ"]))
                        + " of "
                        + self.num(tool, p("voxels"), fmt_count(m["voxels"]))
                        + (
                            f' <small>({self.num(tool, p("share"), fmt_share(m["share"]))})</small>'
                            if m["differ"]
                            else ""
                        )
                    )
                    unit = o.get("stored_unit")
                    max_abs = self.num(tool, p("max_abs"), fmt_sig(m["max_abs"]))
                    if unit and "max_abs_stored" in m and m["max_abs"]:
                        stored = self.num(tool, p("max_abs_stored"), fmt_sig(m["max_abs_stored"]))
                        max_abs += f" <small>({stored} {esc(unit)}{'' if m['max_abs_stored'] == 1 else 's'})</small>"
                    cells = [head_cell] if oi == 0 else []
                    if multi:
                        cells.append(f"<td class=out>{esc(o['label'])}</td>")
                    cells += [
                        f"<td class=n>{max_abs}</td>",
                        f"<td class=n>{differ}</td>",
                        f'<td class=n>{self.num(tool, p("rms"), fmt_sig(m["rms"]))}</td>',
                        f'<td class=n>{self.num(tool, p("max_rel_range"), fmt_sig(m["max_rel_range"]))}</td>',
                        f'<td class=n>{self.num(tool, p("one_minus_ncc"), fmt_sig(m["one_minus_ncc"]))}</td>',
                    ]
                    cls = f'kind-{esc(d["kind"])}{" first" if oi == 0 else ""}'
                    body.append(f'<tr class="{cls}">{"".join(cells)}</tr>')
            body.append("</tbody>")
        cap = self.text(ex["metrics_note"])
        return (
            '<div class="ev-metrics"><p class="ev-metrics-title">Every comparison, computed in '
            "float64 over every voxel of the outputs</p>"
            f'<div class="table-wrap"><table class="ev-mtable"><thead>{head}</thead>'
            f'{"".join(body)}</table></div><p class="ev-metrics-note">{cap}</p></div>'
        )

    # ---------------------------------------------------------------- credits

    def credit_item(self, c: dict) -> str:
        """One dataset's credit line (the JSON's ``credits``, from larmorx-testdata's catalog):
        its name and version, DOI, licence; for CC BY the attribution and the changes made, for
        CC BY-SA also the share-alike notice."""
        doi = f', doi:<a href="https://doi.org/{esc(c["doi"])}">{esc(c["doi"])}</a>' if c.get("doi") else ""
        lic_url = self.link(c["licence_url"]) if c.get("licence_url", "").startswith("/") else c.get("licence_url", "")
        lic = f'<a href="{esc(lic_url)}">{esc(c["licence_name"])}</a>' if lic_url else esc(c["licence_name"])
        out = (
            f'<li data-credit="{esc(c["id"])}"><a href="{esc(c["url"])}">{esc(c["title"])}</a> '
            f'({esc(c["source"])}, version {esc(c["version"])}{doi}), {lic}.'
        )
        if c.get("attribution"):
            out += (
                f' <span class="ev-attr">Attribution: {esc(c["citation"])} The images shown are '
                "adapted from it: reoriented to RAS, cropped to the region shown, masked outside "
                "it, and shown as the outputs of the programs compared.</span>"
            )
        if c.get("share_alike"):
            out += (
                ' <span class="ev-attr">Share-alike: the images adapted from this dataset are '
                "shared under the same licence, CC BY-SA.</span>"
            )
        return out + "</li>"

    def credits_html(self, doc: dict, ids: list[str], title: str) -> str:
        cs = [doc.get("credits", {}).get(i) for i in ids]
        cs = [c for c in cs if c]
        if not cs:
            return ""
        return (
            f'<div class="ev-credit"><p class="ev-credit-title">{esc(title)}</p>'
            f'<ul>{"".join(self.credit_item(c) for c in cs)}</ul></div>'
        )

    def page_credits(self) -> Markup:
        """Every dataset the page's evidence shows or names (its examples, cases and tables),
        credited once at the page's end; empty on a page without evidence."""
        seen: dict[str, dict] = {}
        for doc in self._docs.values():
            for cid, c in (doc.get("credits") or {}).items():
                seen.setdefault(cid, c)
        if not seen:
            return Markup("")
        items = "".join(self.credit_item(c) for c in seen.values())
        return Markup(
            '<section class="ev-credits-page" aria-labelledby="data-credits">'
            '<h2 id="data-credits">Data credits</h2>'
            "<p>The data this page shows or names: each dataset with its version, DOI and licence, "
            "from LARMORX's test-data catalog. Public-domain dedications (CC0, PDDL) ask nothing; "
            "the datasets are cited all the same.</p>"
            f'<ul class="ev-credit-list">{items}</ul></section>'
        )

    # ------------------------------------------------------------- data panel

    def panel_table(self) -> Markup:
        """The data panel's datasets (``static/evidence/panel.json``): one row each."""
        doc = self.doc("panel")
        rows = []
        for i, d in enumerate(doc["datasets"]):
            p = ptr("datasets", i)
            who = esc(d["subject"]) + (f", {esc(d['session'])}" if d.get("session") else "")
            age = d.get("age", "")
            extra = [f"{esc(age)} y" if age.replace(".", "", 1).isdigit() else esc(age), esc(d.get("sex", ""))]
            extra = [x for x in extra if x]
            if extra:
                who += f'<small>{", ".join(extra)}</small>'
            run = f"<code>{esc(d['fmriprep_run'])}</code>"
            if d.get("fmriprep_options") and d["fmriprep_options"] != "--fs-no-reconall":
                run += f" <small>{esc(d['fmriprep_options'])}</small>"
            run += f"<small>{esc(d.get('fmriprep_status', ''))}</small>"
            rows.append(
                f'<tr id="panel-{esc(d["id"])}"><th scope=row><span class="tname">{esc(d["id"])}</span>'
                f"<small>{who}</small></th><td>{esc(d['scanner'])}</td><td>{esc(d['role'])}</td>"
                f"<td>{esc(d['credit']['licence'])}</td>"
                f'<td class=n>{self.num("panel", p + "/files", fmt_count(d["files"]))}</td>'
                f'<td class=n>{self.num("panel", p + "/megabytes", fmt_sig(d["megabytes"], 3))} MB</td>'
                f"<td>{run}</td></tr>"
            )
        tot = doc["totals"]
        rows.append(
            '<tr class="is-total"><th scope=row>Total</th><td></td><td></td><td></td>'
            f'<td class=n>{self.num("panel", "/totals/files", fmt_count(tot["files"]))}</td>'
            f'<td class=n>{self.num("panel", "/totals/gigabytes", fmt_sig(tot["gigabytes"], 3))} GB</td><td></td></tr>'
        )
        return Markup(
            '<div class="table-wrap ev-panel-table"><table class="ev-ttable"><thead><tr>'
            "<th scope=col>Dataset, subject</th><th scope=col>Scanner</th><th scope=col>Why it is in the panel</th>"
            "<th scope=col>Licence</th><th scope=col class=n>Files</th><th scope=col class=n>Size</th>"
            "<th scope=col>fMRIPrep 25.2.6 oracle run</th></tr></thead>"
            f'<tbody>{"".join(rows)}</tbody></table></div>'
        )

    def panel_coverage(self) -> Markup:
        """Which dataset covers which criterion."""
        doc = self.doc("panel")
        ds = doc["datasets"]
        head = "<tr><th scope=col>Criterion</th>" + "".join(
            f'<th scope=col class="vh"><span>{esc(d["id"])}</span></th>' for d in ds
        ) + "<th scope=col class=n>Datasets</th></tr>"
        rows, group = [], None
        for c in doc["criteria"]:
            if c["group"] != group:
                group = c["group"]
                rows.append(f'<tr class="grp-head"><th colspan="{len(ds) + 2}" scope=colgroup>{esc(group)}</th></tr>')
            marks = [c["id"] in d["covers"] for d in ds]
            cells = "".join(
                f'<td class="cv{" on" if m else ""}">' + ('<span aria-label="yes">●</span>' if m else "") + "</td>"
                for m in marks
            )
            rows.append(f"<tr><th scope=row>{esc(c['label'])}</th>{cells}<td class=n>{sum(marks)}</td></tr>")
        return Markup(
            f'<div class="table-wrap ev-coverage"><table><thead>{head}</thead><tbody>{"".join(rows)}</tbody></table></div>'
        )

    def panel_details(self) -> Markup:
        """Per dataset: its credit line and the defacing check of each anatomical image."""
        doc = self.doc("panel")
        parts = []
        for d in doc["datasets"]:
            rows = "".join(
                f"<tr><th scope=row><code>{esc(a['file'])}</code></th><td>{esc(a['defacing'])}</td>"
                f"<td>{'the head, cropped to it' if a['show'] == 'head' else 'brain-masked views only'}</td></tr>"
                for a in d["anat"]
            )
            note = f'<p class="ev-chart-note">{esc(d["note"])}</p>' if d.get("note") else ""
            parts.append(
                f'<div class="ev-panel-ds" id="data-{esc(d["id"])}"><p class="ev-metrics-title">{esc(d["id"])}: '
                f'{esc(d["credit"]["title"])}</p><ul class="ev-credit-list">{self.credit_item(d["credit"])}</ul>{note}'
                '<div class="table-wrap"><table class="ev-ttable"><thead><tr><th scope=col>Anatomical image</th>'
                "<th scope=col>Defacing, as checked</th><th scope=col>The site may show</th></tr></thead>"
                f"<tbody>{rows}</tbody></table></div></div>"
            )
        return Markup("".join(parts))

    def provenance(self, tool: str, ex: dict) -> str:
        src = self.link(f"/static/evidence/{tool}.json")
        items = "".join(f"<li>{self.text(t)}</li>" for t in ex["provenance"])
        return (
            f'<details class="ev-prov"><summary>Provenance of this example</summary><ul>{items}</ul>'
            f'<p>Every number above is in <a href="{src}">{esc(tool)}.json</a>, exported by '
            f"<code>python -m larmorx_validation evidence {esc(tool)}</code>.</p></details>"
        )

    # --------------------------------------------------------------- charts

    def agreement(self, tool: str, impl: str) -> Markup:
        doc = self.doc(tool)
        k, im = next((i, x) for i, x in enumerate(doc["implementations"]) if x["id"] == impl)
        rows = im["agreement"]
        target = f"cases-{impl}" if len(doc["implementations"]) > 1 and doc.get("cases_per_impl") else "cases"
        top = max(sum(r["counts"].values()) for r in rows) or 1
        out = []
        for ri, r in enumerate(rows):
            total = sum(r["counts"].values())
            segs = []
            parts = []
            for v in self.order:
                n = r["counts"].get(v)
                if not n:
                    continue
                pp = ptr("implementations", k, "agreement", ri, "counts", v)
                label = self.verdicts[v]["label"]
                parts.append(f"{n} {label.lower()}")
                segs.append(
                    f'<a class="seg v-{esc(v)}" style="flex-grow:{n}" href="#{esc(target)}" '
                    f'data-filter-category="{esc(r["category"])}" data-filter-verdict="{esc(v)}" '
                    f'data-filter-impl="{esc(impl)}" title="{esc(r["category"])}: {n} {esc(label.lower())}">'
                    f'<span class="seg-n">{self.num(tool, pp, fmt_count(n))}</span></a>'
                )
            out.append(
                f'<div class="ev-agree-row"><span class="ev-agree-cat">{esc(r["category"]).replace("/", "/<wbr>")}</span>'
                f'<div class="ev-agree-track"><div class="ev-bar" style="width:{100 * total / top:.3f}%" '
                f'role="group" aria-label="{esc(r["category"])}: {total} cases: {esc(", ".join(parts))}">{"".join(segs)}</div></div>'
                f'<span class="ev-agree-n">{total}</span></div>'
            )
        present = [v for v in self.order if any(v in r["counts"] for r in rows)]
        totals = im["summary"]["verdicts"]
        legend = "".join(
            f"<li>{self.verdict(v, count=totals.get(v, 0), tool=tool, pointer=ptr('implementations', k, 'summary', 'verdicts', v))}</li>"
            for v in present
        )
        cases = self.num(tool, ptr("implementations", k, "summary", "cases"), fmt_count(im["summary"]["cases"]))
        return Markup(
            f'<figure class="ev-chart ev-agree" data-impl="{esc(impl)}">'
            f'<figcaption class="ev-chart-title">{esc(im["label"])}: {cases} cases of the '
            f'<a href="{self.href(im["record"])}">record</a>, by category and verdict</figcaption>'
            f'<div class="ev-agree-rows">{"".join(out)}</div>'
            f'<ul class="verdict-legend">{legend}</ul>'
            f'<p class="ev-chart-note">Select a segment to list its cases below.</p></figure>'
        )

    def band(self, tool: str) -> Markup:
        doc = self.doc(tool)
        b = doc["band"]
        lo, hi = b["axis"]
        span = math.log10(hi) - math.log10(lo)

        def x(v):
            v = min(max(v, lo), hi)
            return 100 * (math.log10(v) - math.log10(lo)) / span

        rows = []
        for i, r in enumerate(b["rows"]):
            dots = []
            for key, cls, name in (("ratio_max", "d-max", "largest |Δ|"), ("ratio_ncc", "d-ncc", "1 − NCC")):
                v = r[key]
                if v is None:
                    continue
                pp = ptr("band", "rows", i, key)
                dots.append(
                    f'<span class="dot {cls}" style="left:{x(v):.3f}%" title="{esc(name)}: '
                    f'{fmt_sig(v, 2)} × ANTs\' band"><b class="visually-hidden">{esc(name)} '
                    f'{self.num(tool, pp, fmt_sig(v, 2))} × the band</b></span>'
                )
            rows.append(
                f'<li><span class="ev-band-case"><code>{esc(r["case"])}</code> <small>{esc(r["output"])}</small></span>'
                f'<span class="ev-band-track">{"".join(dots)}</span></li>'
            )
        ticks = "".join(
            f'<span style="left:{x(t):.3f}%">{esc(lbl)}</span>' for t, lbl in b["ticks"]
        )
        one = x(1.0)
        return Markup(
            f'<figure class="ev-chart ev-band" style="--one:{one:.3f}%">'
            f'<figcaption class="ev-chart-title">{esc(b["title"])}</figcaption>'
            f'<ul class="ev-band-key"><li><span class="dot d-max"></span>largest |Δ| ÷ ANTs\' largest |Δ| between its thread counts</li>'
            f'<li><span class="dot d-ncc"></span>(1 − NCC) ÷ ANTs\' (1 − NCC) between its thread counts</li>'
            f'<li><span class="band-swatch"></span>inside ANTs\' own thread-to-thread variability (&lt; 1)</li></ul>'
            f'<ol class="ev-band-rows">{"".join(rows)}</ol>'
            f'<div class="ev-band-axis"><span class="ev-band-pad"></span><span class="ev-band-ticks">{ticks}</span></div>'
            f'<p class="ev-chart-note">{self.text(b["note"])}</p></figure>'
        )

    def speed(self, tool: str) -> Markup:
        doc = self.doc(tool)
        s = doc.get("speed")
        if not s:
            return Markup("")
        lo, hi = s["axis"]
        span = math.log10(hi) - math.log10(lo)

        def x(v):
            return 100 * (math.log10(min(max(v, lo), hi)) - math.log10(lo)) / span

        rows = []
        for i, r in enumerate(s["rows"]):
            dots = []
            for j, ser in enumerate(s["series"]):
                v = r["seconds"].get(ser["id"])
                if v is None:
                    continue
                pp = ptr("speed", "rows", i, "seconds", ser["id"])
                dots.append(
                    f'<span class="dot s-{esc(ser["mark"])}" style="left:{x(v):.3f}%" title="{esc(ser["label"])}: '
                    f'{fmt_seconds(v)}"><b class="visually-hidden">{esc(ser["label"])} '
                    f'{self.num(tool, pp, fmt_sig(v))} s</b></span>'
                )
            ratio = ""
            if r.get("speedup"):
                ratio = (
                    '<span class="ev-speed-x">'
                    + self.num(tool, ptr("speed", "rows", i, "speedup"), fmt_sig(r["speedup"], 2))
                    + "×</span>"
                )
            rows.append(
                f'<li><span class="ev-band-case">{esc(r["label"])}</span>'
                f'<span class="ev-band-track">{"".join(dots)}</span>{ratio}</li>'
            )
        key = "".join(
            f'<li><span class="dot s-{esc(ser["mark"])}"></span>{esc(ser["label"])}</li>' for ser in s["series"]
        )
        ticks = "".join(f'<span style="left:{x(t):.3f}%">{esc(lbl)}</span>' for t, lbl in s["ticks"])
        return Markup(
            f'<figure class="ev-chart ev-speed"><figcaption class="ev-chart-title">{esc(s["title"])}</figcaption>'
            f'<ul class="ev-band-key">{key}</ul><ol class="ev-band-rows">{"".join(rows)}</ol>'
            f'<div class="ev-band-axis"><span class="ev-band-pad"></span><span class="ev-band-ticks">{ticks}</span></div>'
            f'<p class="ev-chart-note">{self.text(s["note"])}</p></figure>'
        )

    # ----------------------------------------------------------------- tables

    def table_html(self, tool: str, t: dict, base: str) -> str:
        """A table of the JSON (``tables``): text and numbers, each number with its pointer;
        a cell may carry a verdict."""
        cols = t["columns"]
        head = "".join(
            f'<th scope=col{" class=n" if c.get("num") else ""}>{esc(c["label"])}</th>' for c in cols
        )
        body = []
        for i, r in enumerate(t["rows"]):
            cells = [
                f'<th scope=row>{self.text(r["head"])}'
                + (f'<small>{self.text(r["sub"])}</small>' if r.get("sub") else "")
                + "</th>"
            ]
            for j, c in enumerate(r["cells"]):
                num = cols[j + 1].get("num") if j + 1 < len(cols) else False
                if "verdict" in c:
                    inner = str(self.verdict(c["verdict"]))
                    if c.get("text"):
                        inner += f'<span class="why">{self.text(c["text"])}</span>'
                elif "v" in c:
                    fmt = FORMATS.get(c.get("fmt", "sig"), FORMATS["sig"])
                    inner = self.num(tool, f"{base}/rows/{i}/cells/{j}/v", fmt(c["v"]))
                    if c.get("unit"):
                        inner += f" <small>{esc(c['unit'])}</small>"
                else:
                    inner = str(self.text(c.get("text", "")))
                cls = ' class="n"' if num else ""
                cells.append(f"<td{cls}>{inner}</td>")
            rc = f' class="{esc(r["class"])}"' if r.get("class") else ""
            body.append(f'<tr{rc}>{"".join(cells)}</tr>')
        note = f'<p class="ev-metrics-note">{self.text(t["note"])}</p>' if t.get("note") else ""
        return (
            f'<div class="ev-table" id="table-{esc(t["id"])}"><p class="ev-metrics-title">{self.text(t["title"])}</p>'
            f'<div class="table-wrap"><table class="ev-ttable"><thead><tr>{head}</tr></thead>'
            f'<tbody>{"".join(body)}</tbody></table></div>{note}</div>'
        )

    def table(self, tool: str, tid: str) -> Markup:
        doc = self.doc(tool)
        k, t = next(((i, x) for i, x in enumerate(doc.get("tables", [])) if x["id"] == tid), (None, None))
        if t is None:
            raise SystemExit(f"evidence {tool}: no table {tid!r}")
        return Markup(f'<figure class="ev-chart ev-tablefig">{self.table_html(tool, t, ptr("tables", k))}</figure>')

    # ------------------------------------------------------------------ dots

    def dots(self, tool: str, did: str) -> Markup:
        """Dots on a log axis, one row per item and a dot per series (speed, thread bands);
        a zero sits at the axis' left edge."""
        s = self.doc(tool)["dots"][did]
        if not s:
            return Markup("")
        lo, hi = s["axis"]
        span = math.log10(hi) - math.log10(lo)
        unit = s.get("unit", "")

        def x(v):
            if v <= 0:
                return 0.0
            return 100 * (math.log10(min(max(v, lo), hi)) - math.log10(lo)) / span

        fmt = FORMATS.get(s.get("fmt", "sig"), FORMATS["sig"])
        rows = []
        for i, r in enumerate(s["rows"]):
            pts = []
            for ser in s["series"]:
                v = r["values"].get(ser["id"])
                if v is None:
                    continue
                pp = ptr("dots", did, "rows", i, "values", ser["id"])
                shown = fmt(v) + (f" {unit}" if unit else "")
                pts.append(
                    f'<span class="dot s-{esc(ser["mark"])}{" is-zero" if v <= 0 else ""}" style="left:{x(v):.3f}%" '
                    f'title="{esc(ser["label"])}: {esc(shown)}"><b class="visually-hidden">{esc(ser["label"])} '
                    f'{self.num(tool, pp, fmt(v))}{(" " + esc(unit)) if unit else ""}</b></span>'
                )
            extra = ""
            if r.get("ratio") is not None:
                extra = (
                    '<span class="ev-speed-x">'
                    + self.num(tool, ptr("dots", did, "rows", i, "ratio"), fmt_sig(r["ratio"], 2))
                    + "×</span>"
                )
            label = f'<code>{esc(r["label"])}</code>' if r.get("code") else esc(r["label"])
            rows.append(
                f'<li><span class="ev-band-case">{label}</span>'
                f'<span class="ev-band-track">{"".join(pts)}</span>{extra}</li>'
            )
        key = "".join(
            f'<li><span class="dot s-{esc(ser["mark"])}"></span>{esc(ser["label"])}</li>' for ser in s["series"]
        )
        ticks = "".join(f'<span style="left:{x(t):.3f}%">{esc(lbl)}</span>' for t, lbl in s["ticks"])
        cls = "ev-speed" if any(r.get("ratio") is not None for r in s["rows"]) else "ev-dots"
        return Markup(
            f'<figure class="ev-chart {cls}"><figcaption class="ev-chart-title">{esc(s["title"])}</figcaption>'
            f'<ul class="ev-band-key">{key}</ul><ol class="ev-band-rows">{"".join(rows)}</ol>'
            f'<div class="ev-band-axis"><span class="ev-band-pad"></span><span class="ev-band-ticks">{ticks}</span></div>'
            f'<p class="ev-chart-note">{self.text(s["note"])}</p></figure>'
        )

    # ----------------------------------------------------------------- lines

    def lines(self, tool: str, lid: str) -> Markup:
        """Line charts sharing one x axis (the JSON's ``lines``)."""
        doc = self.doc(tool)
        return Markup(self.lines_html(tool, doc["lines"][lid], ptr("lines", lid)))

    def lines_html(self, tool: str, spec: dict, base: str) -> str:
        """Panels of lines over one x axis, drawn as SVG (the script redraws them to the
        column's width and reads the values under the pointer); a table of statistics below."""
        src = self.link(f"/static/evidence/{tool}.json")
        key = "".join(
            f'<li><i class="ln-key ln-{esc(sr["mark"])}"></i>{esc(sr["label"])}</li>' for sr in spec["key"]
        )
        svgs = "".join(self._lines_svg(p, spec) for p in spec["panels"])
        stats = ""
        if spec.get("stats"):
            stats = self.table_html(tool, spec["stats"], base + "/stats")
        return (
            f'<figure class="ev-chart ev-lines" data-ev-src="{src}" data-ev-lines="{esc(base)}" data-ev-tool="{esc(tool)}">'
            f'<figcaption class="ev-chart-title">{esc(spec["title"])}</figcaption>'
            f'<ul class="ev-series-key ev-lines-key">{key}</ul><div class="ev-lines-panels">{svgs}</div>'
            f'<p class="ev-chart-note">{self.text(spec["note"])}</p>{stats}</figure>'
        )

    @staticmethod
    def _lines_svg(p: dict, spec: dict) -> str:
        W, H, ml, mr, mt, mb = 760, 120, 60, 10, 18, 8
        xs = spec["x"]
        x0, x1 = xs[0], xs[-1]
        ys = [v for sr in p["series"] for v in sr["y"] if v is not None]
        for b in p.get("bands", []):
            ys += b["lo"] + b["hi"]
        lo, hi = min(ys), max(ys)
        if lo == hi:
            lo, hi = lo - 1, hi + 1
        pad = (hi - lo) * 0.06
        y0, y1 = lo - pad, hi + pad

        def X(v):
            return ml + (W - ml - mr) * (v - x0) / ((x1 - x0) or 1)

        def Y(v):
            return mt + (H - mt - mb) * (1 - (v - y0) / (y1 - y0))

        out = [f'<svg class="ev-lines-svg" viewBox="0 0 {W} {H}" role="img" aria-label="{esc(p["label"])}">']
        for b in p.get("bands", []):
            pts = [f"{X(x):.1f},{Y(v):.1f}" for x, v in zip(xs, b["hi"])]
            pts += [f"{X(x):.1f},{Y(v):.1f}" for x, v in reversed(list(zip(xs, b["lo"])))]
            out.append(f'<polygon class="ln-band ln-{esc(b["mark"])}" points="{" ".join(pts)}"/>')
        if y0 < 0 < y1:
            out.append(f'<line class="ln-zero" x1="{ml}" x2="{W - mr}" y1="{Y(0):.1f}" y2="{Y(0):.1f}"/>')
        for sr in p["series"]:
            pts = " ".join(f"{X(x):.1f},{Y(v):.1f}" for x, v in zip(xs, sr["y"]) if v is not None)
            out.append(f'<polyline class="ln ln-{esc(sr["mark"])}" points="{pts}"/>')
        out.append(f'<text class="ln-label" x="{ml}" y="12">{esc(p["label"])}</text>')
        for v in (hi, lo):
            out.append(f'<text class="ln-tick" x="{ml - 6}" y="{Y(v) + 4:.1f}" text-anchor="end">{esc(fmt_sig(v, 3))}</text>')
        out.append("</svg>")
        return "".join(out)

    # --------------------------------------------------------- case explorer

    def cases(self, tool: str, impl: str | None = None) -> Markup:
        """Every case of the tool's records; with ``impl``, only that implementation's (one
        explorer per program on a page of several)."""
        doc = self.doc(tool)
        impls = doc["implementations"]
        if impl is not None:
            impls = [i for i in impls if i["id"] == impl]
        multi = len(impls) > 1
        head = (
            "<tr><th scope=col data-sort=id>Case</th><th scope=col data-sort=category>Category</th>"
            "<th scope=col>What it tests</th>"
            + "".join(
                f'<th scope=col data-sort="v-{esc(i["id"])}">{esc(i["short"]) if multi else "Verdict"}</th>'
                for i in impls
            )
            + "<th scope=col>Checks</th></tr>"
        )
        rows = []
        listed = [c for c in doc["cases"] if impl is None or impl in c["results"]]
        for c in listed:
            cells = [
                f'<th scope="row" class="cid"><code>{esc(c["id"])}</code>'
                + (
                    f' <a class="ev-to-example" href="#example-{esc(c["example"])}">worked example</a>'
                    if c.get("example")
                    else ""
                )
                + "</th>",
                f"<td class=cat>{esc(c['category'])}</td>",
                f'<td class=what><span>{esc(c["description"])}</span>'
                + (
                    f'<details class="cmd"><summary>command line</summary><code class="cmdline">'
                    f'{esc(c["command"])}</code></details>'
                    if c.get("command")
                    else ""
                )
                + "</td>",
            ]
            data = [f'data-category="{esc(c["category"])}"']
            checks = []
            for i in impls:
                r = c["results"].get(i["id"])
                if r is None:
                    cells.append("<td class=vd>–</td>")
                    continue
                data.append(f'data-v-{esc(i["id"])}="{esc(r["verdict"])}"')
                reason = f'<p class="why">{self.text(r["reason"])}</p>' if r.get("reason") else ""
                cells.append(f"<td class=vd>{self.verdict(r['verdict'])}{reason}</td>")
                checks.append(r["checks"])
            cells.append(f'<td class="n chk">{esc(" · ".join(dict.fromkeys(checks)))}</td>')
            rows.append(
                f'<tr id="case={esc(c["id"])}" {" ".join(data)} data-id="{esc(c["id"])}">{"".join(cells)}</tr>'
            )
        if impl is None:
            n = self.num(tool, ptr("cases_total"), fmt_count(doc["cases_total"]))
            box_id = "cases"
        else:
            k = next(i for i, x in enumerate(doc["implementations"]) if x["id"] == impl)
            n = self.num(tool, ptr("implementations", k, "summary", "cases"), fmt_count(len(listed)))
            box_id = f"cases-{impl}"
        return Markup(
            f'<div class="ev-cases" id="{esc(box_id)}" data-ev-tool="{esc(tool)}" '
            f'data-impls="{esc(",".join(i["id"] for i in impls))}">'
            f'<p class="ev-cases-count">{n} cases</p>'
            f'<div class="table-wrap ev-cases-wrap"><table class="ev-ctable"><thead>{head}</thead>'
            f'<tbody>{"".join(rows)}</tbody></table></div></div>'
        )

    # ------------------------------------------------------- random testing

    #: Random testing's outcomes (its own, not the verdict taxonomy), in table order.
    DIFFTEST_COLUMNS = (
        ("agree", "Agree", "the parity runner passed: bit-identical where the tool must be, within the record's thresholds for a clean-room original, or both programs rejected the input alike"),
        ("explained", "glibc", "differs from the original as built only through glibc's maths: identical once it runs with correctly rounded functions"),
        ("notice", "Notices", "a correction named where it changed nothing this input shows (D13 notices are meant to fire exactly where the result differs)"),
        ("undefined", "Undefined", "the original's values depend on memory it never wrote or on the clock: not comparable (a defect larmorx names)"),
        ("differ", "Differ", "a difference: shrunk to its smallest reproducer, then fixed, registered or reported"),
        ("memory", "Heavy", "a run exceeded the case's memory limit (3 GiB, no swap), or was predicted to: queued as a heavy case and run to its end later, one at a time, in a large box"),
        ("guard", "Guard", "predicted over the case's memory limit: not compared; LARMORX's default stopped at once with its guard's clear error (ANTS-162, AFNI-75), the original's predicted need recorded"),
    )
    DIFFTEST_STATUS = {
        "fixed": "fixed in LARMORX",
        "register": "a defect of the original, in the register",
        "open": "open (a clean-room original's difference, reported for its agent)",
        "harness": "the comparison's own mistake, corrected",
        "explained": "an expected difference, measured and explained (no mistake, no defect)",
        "unclear": "not yet triaged",
    }

    def _difftest(self) -> dict:
        return self.doc("difftest")

    def _difftest_rows(self, tools: list[tuple[str, int, dict]], with_page: bool) -> str:
        rows = []
        for pi, ti, t in tools:
            p = ptr("pages", pi, "tools", ti)
            name = esc(t["label"])
            if with_page:
                page = self._difftest()["pages"][pi]["page"]
                name = f'<a href="{self.link(page)}">{name}</a>'
            impls = ", ".join(t["implementations"])
            cells = [
                f"<th scope=row>{name}<small>{esc(impls)}</small></th>",
                f'<td class=n>{self.num("difftest", p + "/cases", fmt_count(t["cases"]))}</td>',
                f'<td class=n>{self.num("difftest", p + "/extreme", fmt_count(t.get("extreme", 0)))}</td>',
                f'<td class=n>{self.num("difftest", p + "/options_covered", fmt_count(t["options_covered"]))}</td>',
            ]
            for key, _, _ in self.DIFFTEST_COLUMNS:
                n = t["outcomes"].get(key, 0)
                cells.append(
                    f'<td class="n{" zero" if not n else ""}">'
                    + (self.num("difftest", f"{p}/outcomes/{key}", fmt_count(n)) if n else "·")
                    + "</td>"
                )
            n = t["unclear"]
            cells.append(f'<td class="n{" zero" if not n else ""}">' + (self.num("difftest", p + "/unclear", fmt_count(n)) if n else "·") + "</td>")
            rows.append(f"<tr>{''.join(cells)}</tr>")
        return "".join(rows)

    def _difftest_head(self, first: str) -> str:
        cols = "".join(f'<th scope=col class=n title="{esc(m)}">{esc(lab)}</th>' for _, lab, m in self.DIFFTEST_COLUMNS)
        return (
            f"<tr><th scope=col>{esc(first)}</th><th scope=col class=n>Random cases</th>"
            "<th scope=col class=n title=\"the cases drawn as the extreme share of the run (odd units, extreme voxel sizes); the others are realistic\">Extreme</th>"
            f'<th scope=col class=n title="distinct options and option values drawn">Options covered</th>{cols}'
            '<th scope=col class=n title="timed out or crashed: for the orchestrator">Unclear</th></tr>'
        )

    def _difftest_notices(self, tools: list[tuple[str, int, dict]]) -> str:
        """The D13 notices each tool named where the correction changed nothing the input
        shows (the *Notices* column), defect by defect."""
        parts = []
        for pi, ti, t in tools:
            items = []
            for ni, n in enumerate(t.get("notices", [])):
                p = ptr("pages", pi, "tools", ti, "notices", ni)
                items.append(f'{esc(n["defect"])} ({self.num("difftest", p + "/cases", fmt_count(n["cases"]))})')
            if items:
                parts.append(f"{esc(t['label'])}: {', '.join(items)}")
        if not parts:
            return ""
        return (
            '<p class="ev-metrics-note">Notices: a correction named in a case where it changed '
            f"nothing the input shows (defect, cases): {'; '.join(parts)}.</p>"
        )

    def _difftest_differences(self, tools: list[tuple[str, int, dict]]) -> str:
        items = []
        for pi, ti, t in tools:
            for di, d in enumerate(t["differences"]):
                p = ptr("pages", pi, "tools", ti, "differences", di)
                status = self.DIFFTEST_STATUS.get(d["status"], d["status"])
                link = f' (<a href="{self.href(d["link"])}">{esc(d.get("defect") or "details")}</a>)' if d.get("link") else ""
                checks = ", ".join(d["checks"])
                items.append(
                    f'<li><span class="ev-dt-status ev-dt-{esc(d["status"])}">{esc(status)}</span> '
                    f'{esc(t["label"])} ({esc(d["implementation"])}), {self.num("difftest", p + "/cases", fmt_count(d["cases"]))} '
                    f'case(s): <code>{esc(checks)}</code>: {self.text(d["explanation"])}{link}</li>'
                )
        if not items:
            return '<p class="ev-chart-note">No difference.</p>'
        return f'<ul class="ev-dt-diffs">{"".join(items)}</ul>'

    def _difftest_heavy(self, tools: list[tuple[str, int, dict]]) -> str:
        """The cases over the run's memory limit, and what became of them once run to their
        end in the large box (``difftest --heavy``)."""
        items = []
        for pi, ti, t in tools:
            for hi, h in enumerate(t.get("heavy", [])):
                result = h["result"]
                if result == "waiting":
                    state = "waiting to be run to its end in the large box"
                elif result.startswith("beyond"):
                    # Predicted from the original's sizing law, not run (heavy_predict.py).
                    state = f"{esc(result)}: predicted, not run"
                elif result.startswith("pending"):
                    # Kept with its prediction and command for a larger machine (heavy_pending.py).
                    state = f"{esc(result)}: not run here"
                else:
                    peak = str(h.get("peak") or "")
                    try:
                        number, unit = peak.split()
                        peak = f"{float(number):.1f} {unit}"
                    except ValueError:
                        pass
                    state = f"run to its end: {esc(result)}" + (
                        f", the run's peak {esc(peak)}" if peak else ""
                    )
                items.append(f"<code>{esc(h['case'])}</code> ({state})")
        if not items:
            return ""
        return (
            '<p class="ev-metrics-note">Heavy cases (a run over the memory limit of a case, '
            f"queued and run to its end later, one at a time, in a large box): {'; '.join(items)}.</p>"
        )

    def random_testing(self, page: str) -> Markup:
        """A tool page's panel: the latest long run's random cases of the page's tools, their
        outcomes, and what was done about each difference (``static/evidence/difftest.json``)."""
        d = self._difftest()
        tools = [(pi, ti, t) for pi, pg in enumerate(d["pages"]) if pg["page"] == page for ti, t in enumerate(pg["tools"])]
        if not tools:
            self.problems.append(f"random testing: no tool of {page} in static/evidence/difftest.json")
            return Markup("")
        n = d["night"]
        title = (
            f'Random testing, the long run of {esc(n["date"])} (seed <code>{esc(n["seed"])}</code>, '
            f'{self.num("difftest", "/night/hours", fmt_sig(n["hours"]))} h for '
            f'{self.num("difftest", "/night/tools", fmt_count(n["tools"]))} tools): random valid inputs and '
            "option combinations through the original program and LARMORX"
        )
        note = (
            f'Every case is drawn from its tool, the run\'s seed and its number, and replays anywhere: '
            f'<a href="{self.href(d["how"])}">how random testing works</a>; each difference\'s triage: '
            f'<a href="{self.href(d["triage"])}">{esc(d["triage"])}</a>.'
        )
        return Markup(
            f'<figure class="ev-chart ev-tablefig ev-difftest" id="random-testing-panel"><div class="ev-table">'
            f'<p class="ev-metrics-title">{title}</p>'
            f'<div class="table-wrap"><table class="ev-ttable"><thead>{self._difftest_head("Tool")}</thead>'
            f"<tbody>{self._difftest_rows(tools, with_page=False)}</tbody></table></div>"
            f"{self._difftest_differences(tools)}{self._difftest_notices(tools)}{self._difftest_heavy(tools)}"
            f'<p class="ev-metrics-note">{note}</p></div></figure>'
        )

    def random_testing_summary(self) -> Markup:
        """The Validation page's table: every tool's random cases of the latest long run."""
        d = self._difftest()
        tools = [(pi, ti, t) for pi, pg in enumerate(d["pages"]) for ti, t in enumerate(pg["tools"])]
        n = d["night"]
        total = self.num("difftest", "/night/cases", fmt_count(n["cases"]))
        return Markup(
            f'<figure class="ev-chart ev-tablefig ev-difftest" id="random-testing-summary"><div class="ev-table">'
            f'<p class="ev-metrics-title">The long run of {esc(n["date"])}: {total} random cases '
            f'({self.num("difftest", "/night/hours", fmt_sig(n["hours"]))} h, seed <code>{esc(n["seed"])}</code>)</p>'
            f'<div class="table-wrap"><table class="ev-ttable"><thead>{self._difftest_head("Tool")}</thead>'
            f"<tbody>{self._difftest_rows(tools, with_page=True)}</tbody></table></div>"
            f"{self._difftest_differences(tools)}{self._difftest_notices(tools)}{self._difftest_heavy(tools)}"
            f'<p class="ev-metrics-note"><a href="{self.href(d["how"])}">How random testing works</a>; '
            f'each difference\'s triage: <a href="{self.href(d["triage"])}">{esc(d["triage"])}</a>.</p></div></figure>'
        )

    # ------------------------------------------------------- validation page

    def matrix(self, tools: list[dict]) -> Markup:
        """Every tool × implementation × verdict counts, from ``static/evidence/summary.json``."""
        path = self.root / "static" / "evidence" / "summary.json"
        summary = json.loads(path.read_text(encoding="utf-8"))
        pages = {t["url"]: t for t in tools}
        unclassified = any(
            im["verdicts"].get("unclassified") for t in summary["tools"] for im in t["implementations"]
        )
        cols = [*self.order, *(["unclassified"] if unclassified else [])]
        head = (
            "<tr><th scope=col>Tool</th><th scope=col>Implementation</th><th scope=col>Cases</th>"
            + "".join(
                f'<th scope=col class="vh"><a class="verdict v-{esc(v)} is-key" href="#verdict-{esc(v)}">'
                f'<i aria-hidden="true"></i><span>{esc(self.verdicts[v]["short"])}</span></a></th>'
                for v in self.order
            )
            + (
                '<th scope=col class="vh"><span class="verdict v-unclassified is-key"><i aria-hidden="true"></i>'
                "<span>within thresholds, not yet classified</span></span></th>"
                if unclassified
                else ""
            )
            + "</tr>"
        )
        rows = []
        for ti, t in enumerate(summary["tools"]):
            for ii, im in enumerate(t["implementations"]):
                first = ii == 0
                span = f' rowspan="{len(t["implementations"])}"' if len(t["implementations"]) > 1 else ""
                cells = []
                if first:
                    page = pages.get(t["page"])
                    name = esc(t["title"])
                    if page:
                        name = f'<a href="{self.link(t["page"])}">{name}</a>'
                    cells.append(f'<th scope=row{span} class="eco-{esc(t["eco"])}"><span class="tname"><span class="dot"></span><span>{name}</span></span></th>')
                rec = f'<a href="{self.href(im["record"])}">{esc(im["label"])}</a>'
                status = (
                    ' <span class="status-tag status-tag--experimental">experimental</span>'
                    if im["status"] == "experimental"
                    else ""
                )
                cells.append(f"<td class=impl>{rec}{status}</td>")
                p = ptr("tools", ti, "implementations", ii)
                cells.append(f'<td class=n>{self.num("summary", p + "/cases", fmt_count(im["cases"]))}</td>')
                for v in cols:
                    n = im["verdicts"].get(v, 0)
                    cells.append(
                        f'<td class="n{" zero" if not n else ""}">'
                        + (self.num("summary", p + "/verdicts/" + v, fmt_count(n)) if n else "·")
                        + "</td>"
                    )
                rows.append(f"<tr>{''.join(cells)}</tr>")
        note = self.text(summary["note"])
        return Markup(
            f'<div class="table-wrap ev-matrix"><table><thead>{head}</thead><tbody>{"".join(rows)}</tbody></table></div>'
            f'<p class="ev-chart-note">{note}</p>'
        )
