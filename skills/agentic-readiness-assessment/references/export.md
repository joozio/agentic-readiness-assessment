# Optional HTML and PDF export

The Markdown assessment is canonical. It remains readable, reviewable and shareable
without Python or this exporter. The optional
[standard-library renderer](../scripts/render_report.py) creates a self-contained
HTML view; it does not validate or reinterpret assessment conclusions.

## Use

Python 3.9 or newer is sufficient for HTML:

```sh
python3 scripts/render_report.py reports/agentic-readiness.md
python3 scripts/render_report.py reports/agentic-readiness.md --output readiness.html
```

The default HTML path replaces the report's `.md` suffix with `.html`. Existing
outputs are never replaced unless `--force` is explicit. Source/output collisions
and HTML/PDF destination collisions are always refused, including with `--force`.
The destination directory must already exist.

PDF is opt-in and requires WeasyPrint to be installed separately already:

```sh
python3 scripts/render_report.py reports/agentic-readiness.md --pdf
python3 scripts/render_report.py reports/agentic-readiness.md --pdf readiness.pdf
```

The HTML is written first. If WeasyPrint is unavailable or PDF conversion fails,
the command returns a concise error and leaves the HTML available. The exporter
never installs packages.

## Rendering and safety decisions

- The renderer supports headings, paragraphs, lists, block quotes, fenced code,
  simple inline emphasis/links and tables. Unknown or additive report prose and
  fields remain visible rather than being rejected. This intentionally avoids a
  second rigid report schema.
- All report-derived text and attributes are escaped with `html.escape`. Python's
  documentation explicitly recommends it for displaying text containing HTML
  metacharacters: [html — HyperText Markup Language support](https://docs.python.org/3/library/html.html).
- URL parsing alone is not treated as validation; Python warns that `urlsplit()`
  does not validate inputs. Links use a narrow allowlist: HTTP(S), simple `mailto:`,
  safe fragments and non-traversing relative artifact paths:
  [urllib.parse — Parse URLs into components](https://docs.python.org/3/library/urllib.parse.html#url-parsing-security).
- Markdown images and raw HTML are shown as text, never activated. The generated
  document contains no scripts, external styles, fonts or media, and a restrictive
  meta Content Security Policy provides defense in depth. The HTML Standard defines
  meta-delivered CSP and requires UTF-8 for HTML documents:
  [HTML Standard — document metadata](https://html.spec.whatwg.org/multipage/semantics.html#the-meta-element).
- PDF rendering supplies a URL fetcher that rejects every resource request and no
  base URL. WeasyPrint's own security guidance notes that its default fetcher can
  open HTTP and local `file:` URLs and recommends a custom fetcher for untrusted
  input: [WeasyPrint First Steps — Security](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#security).

## Accessibility and portability

The output uses semantic headings, lists, code and table headers; visible focus;
high-contrast colors; responsive type and a single-column layout. Tables scroll
horizontally when their meaning requires two-dimensional presentation. These
choices follow the W3C guidance on
[descriptive headings](https://www.w3.org/WAI/WCAG22/Understanding/headings-and-labels.html),
[4.5:1 text contrast](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html)
and [reflow at 320 CSS pixels](https://www.w3.org/WAI/WCAG22/Understanding/reflow.html).
Print CSS allows content to flow to any number of pages; there are no fixed page
counts, remote assets, web fonts or JavaScript requirements.

This is a compact Markdown subset, not a CommonMark implementation. Deeply nested
lists, footnotes, reference-style links and complex inline nesting remain legible
as source-like text but may not receive specialized styling. A generated HTML file
can contain clickable external links; opening one is an explicit user navigation,
not an automatic fetch. Relative evidence links remain links rather than embedded
attachments, so share their adjacent files with the HTML when recipients need to
open them. PDF conversion blocks all report-triggered resource reads,
but—as with any document renderer—resource limits and process sandboxing remain the
caller's responsibility for adversarially large inputs.
