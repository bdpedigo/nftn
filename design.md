# Notes from the Neuropil — Requirements

**Status:** Draft, in progress **Working name:** Notes from the Neuropil **Purpose of this doc:** Capture requirements for the blog so we can evaluate frameworks later. Framework selection is explicitly deferred.

---

## 1. Concept

Notes from the Neuropil is a blog where people submit something weird they found in Neuroglancer, and the team responds with a short-story-style post explaining (or speculating about) what it is. Posts are written by scientists who should only have to write markdown — rendering, styling, and publishing are handled by the site infrastructure.

**Expected scale:** roughly 10 posts per year, many from one-off contributors. Build speed is not a concern; contributor friction is.

---

## 2. Authoring

| ID | Requirement | Priority |
| --- | --- | --- |
| A1 | Posts are authored in markdown, stored in a GitHub repo. | Must |
| A2 | Authors should not need to touch rendering, layout, or theming options. Sensible defaults for everything. | Must |
| A3 | Posts support inline links, images, and academic citations. | Must |
| A4 | Citations use a single shared `.bib` file in the repo as the source of truth. Authors add entries there as needed and cite with a simple inline syntax (e.g. `[@key]`); a reference list is generated automatically per post. Formatting need not be journal-strict, but must be identical across all pages. | Must |
| A5 | Author metadata lives in a single central authors file (one source of truth). Posts reference authors by a short ID in frontmatter. Each entry has a name plus optional metadata such as GitHub handle, personal website, ORCID, etc. Rendered consistently on every post. | Must |
| A5a | An author ID with no entry in the authors file must still render something reasonable (e.g. the ID as plain text) rather than failing the build or showing nothing. | Must |
| A6 | Support embedded interactive 3D models (e.g. mesh viewers) within a post. | Reach |

---

## 3. Neuroglancer Image Package (standalone)

The Neuroglancer → image renderer is a separate Python package with its own requirements document (see *Neuroglancer Image Package — Requirements*). Summary of what the site depends on from it:

- Installable as a dependency in the site build.
- Headless, no GPU, runs on a standard CI runner within bounded time.
- Takes a Neuroglancer link or state, returns a PNG in the blog's house style.
- Deterministic output with a stable cache key, so the site can skip unchanged renders.
- Fails loudly with actionable errors.

Requirement IDs P1–P11 in that document are referenced from this one where relevant.

---

## 4. Neuroglancer Integration in the Site

How the site uses the package and surfaces Neuroglancer content to readers.

| ID | Requirement | Priority |
| --- | --- | --- |
| N1 | Authors paste a Neuroglancer link into markdown and do nothing else — no local pre-step, no committing rendered images. | Must |
| N2 | Image generation runs automatically as part of the site build, calling the package (see the package requirements doc). | Must |
| N3 | Rendered images are cached so each build only renders new or changed links, not every image in every post. | Must |
| N4 | Images produced this way are the primary source of figures in posts. | Should |
| N5 | Every Neuroglancer link is surfaced to readers as a consistent button/badge-style icon, styled the same across all pages. | Must |
| N6 | Optionally embed the live Neuroglancer viewer directly in a page, as an alternative to (or alongside) a static image. | Nice-to-have |
| N7 | If a render fails during a build, the build should surface the error clearly (especially in PR previews) so a contributor can fix their link. | Should |

**Open questions**

- Where does the cache live? Options: committed to the repo (simple, but grows), a CI cache (fast, but evictable), or external object storage (durable, needs credentials in CI).
- Should a failed render block the build, or degrade to a placeholder image plus a warning?

---

## 5. Contribution Workflow

| ID | Requirement | Priority |
| --- | --- | --- |
| C1 | Contributions come in as pull requests to the GitHub repo. | Must |
| C2 | Every PR gets an automatically built preview of the rendered site so a one-off contributor can see their post without a local setup. | Must |
| C3 | Low barrier for a scientist who will contribute exactly once. | Must |

---

## 6. Site Structure & Navigation

| ID | Requirement | Priority |
| --- | --- | --- |
| S1 | Default listing is reverse chronological (newest first). | Must |
| S2 | Posts can carry labels/tags; readers can filter the listing by tag. | Must |
| S3 | Link to a question/find submission form. Baseline is an external Google Form; preferred is embedding the form in a page on the site so readers don't leave. | Must (embed: Should) |

---

## 7. Aggregated Reference Content (FAQ / Glossary / Hall of Fame)

Blog posts are narrative. Over time, they will collectively document many kinds of objects found in the data. We want a way to build up reference-style pages (an FAQ, a glossary of object types, a "hall of fame" of notable finds) that collect information from across posts, without duplicating content by hand.

| ID | Requirement | Priority |
| --- | --- | --- |
| R1 | One or more aggregate pages (FAQ, glossary, hall of fame — exact set TBD) that draw on content from the posts. | Must |
| R2 | A mechanism to share a piece of content between a post and an aggregate page — e.g. a short definition or a canonical image that appears in the narrative post and is also pulled into the glossary. Write once, render in multiple places. | Must |
| R3 | Posts can be associated with one or more object types / glossary entries (likely via tags or frontmatter), so the glossary can list the posts that feature each object. | Should |
| R4 | Adding a new glossary entry should be as low-effort as writing a post — no hand-editing of the aggregate page. | Should |

**Open questions**

- Which shared unit is right: reusable markdown snippets/includes, structured frontmatter fields on posts (e.g. `object_type`, `one_line_summary`) that aggregate pages read, or a separate glossary content collection that posts link to?
- Is the hall of fame curated by hand (a flagged frontmatter field) or derived (e.g. by tag)?
- Exact shape of these pages and the shared content unit are undecided — Ben to think this through further before framework selection.

---

## 8. Sharing & Discovery

| ID | Requirement | Priority |
| --- | --- | --- |
| D1 | Social media preview cards (Open Graph / Twitter card metadata) generated automatically from post content — title, summary, and an image from the post. | Must |
| D2 | Author can override the preview image via frontmatter; otherwise the first image in the post is used. | Should |
| D3 | Basic site analytics (page views, popular posts, referrers). Prefer a lightweight, privacy-respecting option that doesn't require a cookie banner. | Nice-to-have |
| D4 | Per-post comments via giscus (backed by GitHub Discussions on the repo). | Should |

---

## 9. Design & Theming

| ID | Requirement | Priority |
| --- | --- | --- |
| T1 | Custom visual identity — the site should not look like a default template of whatever framework is chosen. | Must |
| T2 | Theming is centralized; individual posts inherit it with no per-post configuration. | Must |

---

## 10. Hosting & Build

| ID | Requirement | Priority |
| --- | --- | --- |
| H1 | Static site, source in GitHub. | Must |
| H2 | Automated build and deploy on merge to main. | Must |
| H3 | GitHub Pages is the preferred host (team familiarity). Willing to use Netlify / Cloudflare Pages / similar if that is what it takes to get PR previews (C2) working well. | Should |

**Open questions**

- PR preview mechanism on GitHub Pages: a per-PR subdirectory deploy via Actions works but is fiddly (cleanup, base-path handling). Netlify and Cloudflare Pages provide this natively. Decide after the render spike, since it also determines where the image cache can live.

---

## 11. Ruled Out

Things explicitly not wanted, so they don't creep back in and don't influence framework choice.

- Notebook-executed content (Jupyter/R code cells run at build time). Never.
- Journal-strict citation styling (CSL-level fidelity). Consistency matters; exact style does not.

---

## 12. Next Steps Before Framework Selection

1. **Headless render spike:** confirm a Neuroglancer state can be rendered to an acceptable image on a standard GitHub Actions runner, and measure runtime. Outcome determines architecture for P3/P4 and N2/N3, and possibly hosting.
2. Settle the shared content unit for section 7.
3. Decide hosting / PR preview approach (H3).

---

## 13. Decided

- **Framework: Quarto** (decided 2026-09-23). Markdown-first authoring, native shared-`.bib` citations, listings with category filters, SCSS theming, Lua filters for Neuroglancer handling, and code execution can be disabled project-wide. The build plan is tracked as Backlog tasks in `backlog/` (run `backlog board`).

## 14. Deferred / Not Yet Decided

- Final name