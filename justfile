quarto_version := "1.3.450"

# Install Quarto (macOS); see https://quarto.org/docs/get-started/ for other platforms
install:
    @echo "This project targets Quarto {{quarto_version}}"
    @echo "Install from https://quarto.org/docs/get-started/"

# One-time setup for real figure renders: install ngsnap and the pinned browser
setup:
    uv sync
    uv run python -c "from ngsnap.render import install_browser; install_browser()"

# Render the full site into _site/ (renders Neuroglancer figures via ngsnap)
render:
    quarto render

# Render only the Neuroglancer figures (fast; no full site build)
figures:
    uv run python scripts/render_figures.py

# Force a re-render of every figure (clears the figures/ cache first)
figures-force:
    rm -f figures/*.png figures/manifest.json
    uv run python scripts/render_figures.py

# Start a live-reloading preview server
preview:
    quarto preview

# Print the local Quarto version (compare with the pinned version)
check-quarto:
    @echo "Pinned version: {{quarto_version}}"
    @quarto --version
