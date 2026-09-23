# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

**Primary reader: the curious general public.** Someone who saw a strange image from a brain dataset, often through a shared link or a social card, and wants to know what it is. They have never opened Neuroglancer and do not know the vocabulary. A post must explain everything it uses and lean on story to hold them. Confirmed by Ben on 2026-09-23.

**Submitters.** People who found something odd while looking at data in Neuroglancer and sent it in through the submission form. Many are researchers or students who already use the viewer. Their job is to hand over a link and a question with as little effort as possible.

**Contributors (post authors).** Scientists who work in the data and answer a submission. Most contribute exactly once. They write markdown and open a pull request, and nothing else. They must never need to touch rendering, layout, theming, citation formatting, or image generation.

**Secondary readers.** Connectomics researchers who use the same datasets. They are welcome, and the glossary and citations serve them, but the writing is not pitched at them.

## Product Purpose

Notes from the Neuropil (working name) is a blog. A reader submits something weird that they found in Neuroglancer, and a scientist on the team replies with a short, story-style post that explains, or openly speculates about, what it is.

Success looks like:

- A reader outside the field understands what the object is and why it is interesting after one read.
- A one-time contributor publishes a post without a local setup and without learning the site's tooling.
- Every post shows the find as a figure and links straight back to the live data.
- Over time the posts add up to reference pages (glossary, FAQ, hall of fame) without anyone hand-copying content.

Expected scale is about ten posts per year. Build speed does not matter. Contributor friction and reader comprehension do.

## Positioning

The site answers reader-submitted mysteries with the scientists who actually work in the data, and every answer is anchored to the real thing: a figure rendered from the exact Neuroglancer state, plus a badge that opens that state in the viewer. A lab news blog, a documentation site, or a general science explainer cannot truthfully offer that loop from "what is this?" to "here is the object, go look at it yourself."

## Operating Context

- **Neuroglancer** is a browser-based viewer for large volumetric microscopy data (electron microscopy images, segmentations, meshes, annotations). A Neuroglancer link encodes the full view state after `#!`, so a link is a reproducible pointer to one view of one object.
- **Finds** arrive as Neuroglancer links plus a question. The baseline submission channel is an external Google Form. An embedded form on the site is preferred.
- **Authoring** happens in markdown files in a GitHub repository. Each post is a folder under `posts/` with an `index.qmd`. Contributions are pull requests. Each pull request must get a rendered preview so the contributor can see their post without a local install (not built yet, TASK-3).
- **Figures** come from ngsnap, a sibling Python package at `../ngsnap`. It renders a Neuroglancer state to a PNG in one house style, headless, on a standard CI runner, with a deterministic cache key. The site build will call it for every Neuroglancer link in a post (TASK-7, TASK-8). Authors never render or commit images by hand.
- **Build and hosting.** Quarto renders the site on GitHub Actions. A push to `main` deploys to GitHub Pages at https://bdpedigo.github.io/nftn/. Pull requests run the build as a status check only.
- **Reading scene.** Readers often arrive from a shared link on a phone. Long-form reading with figures must work at narrow widths.
- **Reference pages.** Glossary, FAQ, and hall of fame pages will aggregate content from posts. The shared content unit is undecided (TASK-14).

## Capabilities and Constraints

**Decided**

- Framework is Quarto (decided 2026-09-23), pinned to version 1.3.450 in `justfile` and the publish workflow. Bootstrap stays underneath because Quarto requires it, but nothing visually recognizable as Bootstrap or a stock Quarto theme can remain (requirement T1).
- Theming is centralized in one project-level theme. Posts inherit it and set no theme, layout, or style options (T2).
- Code execution is disabled project-wide. Notebook-executed content is ruled out permanently.
- Posts are markdown with inline links, images, and citations. Citations come from one shared `.bib` file and cite with `[@key]`. A reference list is generated per post. Formatting must be identical across pages, but journal-strict styling is ruled out.
- Author metadata lives in one central authors file. Posts reference authors by a short ID. An unknown ID must still render something reasonable and must not break the build.
- Every Neuroglancer link renders as one consistent badge with an icon, identical on every page.
- The listing is reverse chronological and filterable by tag.
- Social preview cards are generated from post content, with a frontmatter override for the image.
- Comments through giscus are planned (Should). Analytics are planned only if they need no cookie banner (Nice-to-have).

**Undecided, do not invent**

- Final site name.
- Where the rendered figure cache lives (repo, CI cache, or object storage).
- Whether a failed render blocks the build or degrades to a placeholder with a warning.
- The shared content unit for glossary, FAQ, and hall of fame, and whether the hall of fame is curated or derived.
- The pull request preview mechanism, and whether hosting moves off GitHub Pages to get it.
- Whether the live Neuroglancer viewer or an interactive 3D mesh viewer is embedded in posts (both are low priority).

**Terminology**

- *Find*: the weird thing a reader submitted.
- *Post*: the team's answer to a find.
- *State link* or *Neuroglancer link*: a URL that encodes a full viewer state.
- *Badge*: the consistent button that represents a Neuroglancer link to readers.
- *Segmentation*, *mesh*, *EM* (electron microscopy), *cross-section*: viewer and dataset terms that posts must define on first use for the primary reader.

## Brand Commitments

- **Name.** "Notes from the Neuropil" is the working name. The final name is deferred. Do not treat the working name as fixed in permanent assets such as logos.
- **Identity.** An independent community site run by scientists. There is no institute logo, no institutional brand rules, and no dataset or consortium branding. The name and the voice are the whole brand. Confirmed by Ben on 2026-09-23.
- **Voice.** Field-notes storytelling. First person, curious, a little playful. Speculation is allowed and is labeled as speculation. Citations back the factual claims. Confirmed by Ben on 2026-09-23.
- **Visual constraint volunteered by Ben (binding, not expanded here).** The site uses colors from Neuroglancer's own UI as theming elements and must be prettier than Neuroglancer. It must not look like default Quarto or Bootstrap. Direction chosen 2026-09-23: mockup F in `design/mockup-f-cover/`, recorded with tokens and fonts in `design/theme-direction.md` section 7. Light only. The reader's question leads every post and the author card comes last.

## Evidence on Hand

- `vision.md`: the full requirements document with IDs (A, N, C, S, R, D, T, H) that Backlog tasks reference.
- `design/theme-direction.md`: an audit of Neuroglancer UI colors with source file references, two proposed token palettes with WCAG AA checks, and a typography proposal. Status: awaiting Ben's review.
- `design/mockup-a-dark/` and `design/mockup-b-light/`: static HTML mockups of the home listing and a post page for each palette option.
- `design/sample-figure.png` and `../ngsnap/assets/default-style-example.png`: a real ngsnap render of public FIB-25 data in the default house style. This is the only real figure so far.
- `posts/2026-09-23-placeholder/`: a placeholder post with a placeholder image. There are no real posts, finds, or submitter quotes yet.
- Backlog: 18 tasks in one linear chain in `backlog/`, run `backlog board`.

**Absent, do not fabricate:** real finds, real post text, author entries, bibliography entries, reader or submitter testimonials, traffic numbers, and any institutional endorsement.

## Product Principles

1. **Write for the person who has never opened Neuroglancer.** Every term is defined where it first appears, and the glossary is the bridge for readers who want more. A researcher can skim past a definition. An outsider cannot skip one that is missing.
2. **Story first, evidence attached.** A post reads like a field note, not a report. Speculation is welcome when it is labeled. Claims that matter carry a citation.
3. **The author writes markdown and nothing else.** Figures, citations, author blocks, badges, and theming come from the infrastructure. If a feature needs a contributor to learn a tool, it is the wrong feature.
4. **Every figure points back to the real object.** A rendered figure always sits beside a badge that opens the same state in Neuroglancer. The reader can go look.
5. **One source of truth, rendered identically everywhere.** Theme, authors, bibliography, badges, and shared glossary content are each defined once and appear the same on every page.

## Accessibility & Inclusion

The primary reader is a member of the public, often on a phone. Body text and accent colors must meet WCAG AA contrast, pages must read at narrow widths with no horizontal scroll, and figures must carry descriptive alt text because the image is the whole point of a post. No further product-specific standard has been established.
