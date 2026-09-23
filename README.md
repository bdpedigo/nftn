# Notes from the Neuropil

People submit something weird they found in Neuroglancer. The team responds with
a short post that explains what it is.

## Live site

<https://bdpedigo.github.io/nftn/>

A push to `main` builds and deploys the site to GitHub Pages automatically.
Pull requests run the build as a status check but do not deploy.

## Local preview
(requires [`just`](https://github.com/casey/just) to be installed)
```bash
# Render the full site into _site/
just render

# Start a live-reloading preview server
just preview
```

You can also run the Quarto commands directly:

```bash
quarto render
quarto preview
```

## Neuroglancer links and figures

Paste a Neuroglancer link into a post as a plain markdown link or a bare URL. The
build turns every such link into a consistent badge, and some links into figures.

The rule:

- A Neuroglancer link **alone in its own paragraph** becomes a **figure**: an image
  rendered by [ngsnap](https://github.com/bdpedigo/ngsnap) with a badge caption that
  links to the live state.
- A Neuroglancer link **inside a sentence** stays a **badge** only.
- To override, add a class to a markdown link:
  - `[text](https://…){.ng-figure}` forces a figure. This works even for an inline link.
  - `[text](https://…){.ng-badge-only}` forces a badge. This overrides the paragraph-alone figure rule.

The host list that counts as "Neuroglancer" lives in one place, `neuroglancer.hosts`
in `_quarto.yml`. The figure house style is `ngsnap-style.toml`.

## Rendering figures locally

Figures render during `quarto render` through a pre-render script that calls ngsnap.
This needs [`uv`](https://docs.astral.sh/uv/) and a one-time browser install:

```bash
# Install the build tooling (ngsnap from git) into a local .venv
uv sync

# Install the pinned Chrome for Testing browser (one time)
uv run python -c "from ngsnap.render import install_browser; install_browser()"

# Now a normal render produces real figures
quarto render
```

Rendered images are written to `figures/` (gitignored) and are named by a content
key, so an unchanged link is not re-rendered.

Without the browser, the build still works: it substitutes a placeholder image for
each figure and prints a warning. To force placeholders (fast builds, no browser):

```bash
NFTN_NO_RENDER=1 quarto render
```
