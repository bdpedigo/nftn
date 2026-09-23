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
