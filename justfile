quarto_version := "1.3.450"

# Install Quarto (macOS); see https://quarto.org/docs/get-started/ for other platforms
install:
    @echo "This project targets Quarto {{quarto_version}}"
    @echo "Install from https://quarto.org/docs/get-started/"

# Render the full site into _site/
render:
    quarto render

# Start a live-reloading preview server
preview:
    quarto preview

# Print the local Quarto version (compare with the pinned version)
check-quarto:
    @echo "Pinned version: {{quarto_version}}"
    @quarto --version
