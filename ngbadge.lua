-- ngbadge.lua
-- Render links to configured Neuroglancer deployments as one consistent badge,
-- and links that should be figures as a .sheet figure with a badge caption.
-- Authors write plain markdown links or bare URLs and do nothing else.
--
-- Figure vs badge rule (kept in sync with scripts/render_figures.py):
--   * A Neuroglancer link alone in its own paragraph becomes a figure.
--   * A link inside prose stays a badge.
--   * Override on a markdown link: {.ng-figure} forces a figure even inline;
--     {.ng-badge-only} forces a badge even when alone in a paragraph.
--
-- The host list comes from project metadata (neuroglancer.hosts in _quarto.yml),
-- one source of truth. Figure images and their paths come from the pre-render
-- manifest (figures/manifest.json), so this filter never shells out.

local hosts = {}
local figures = {} -- url -> path (project-relative), from the manifest

local function normalize_host(h)
  if not h then return nil end
  h = h:gsub("^[^@]*@", "")
  h = h:gsub(":%d+$", "")
  return h:lower()
end

-- Authority between "://" and the first / ? or #. Ignores "#!" encoded state
-- and "#!middleauth+https://..." fragments after the host.
local function url_host(url)
  local host = url:match("^%a[%w%+%-.]*://([^/?#]+)")
  return normalize_host(host)
end

local function is_ng(url)
  local h = url_host(url)
  return h ~= nil and hosts[h] == true
end

local ICON = '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><rect x="1.5" y="1.5" width="13" height="13"/><path d="M8 1.5v13M1.5 8h13"/><rect x="1.5" y="8" width="6.5" height="6.5" fill="currentColor" stroke="none"/></svg>'

local function attr_escape(s)
  return (s:gsub("&", "&amp;"):gsub('"', "&quot;"):gsub("<", "&lt;"):gsub(">", "&gt;"))
end

local function badge_html(url, label)
  return '<a class="ng-badge" href="' .. attr_escape(url) .. '" target="_blank" rel="noopener">'
    .. ICON .. (label or "Open in Neuroglancer") .. "</a>"
end

local function badge(url)
  return pandoc.RawInline("html", badge_html(url))
end

-- A figure: the pre-rendered image on a .sheet with the badge as its caption.
-- The image path is site-root-relative ("/figures/..."); Quarto rewrites it to
-- the correct relative path per page, so it is safe under the Pages base path.
local function figure(url)
  local path = figures[url]
  if not path then return nil end
  local html = '<div class="sheet"><figure>'
    .. '<img src="/' .. attr_escape(path) .. '" alt="Neuroglancer render of the find">'
    .. '<figcaption><span>Rendered from the Neuroglancer link they sent.</span>'
    .. badge_html(url, "Open the link they sent")
    .. "</figcaption></figure></div>"
  return pandoc.RawBlock("html", html)
end

local function read_hosts(meta)
  local set = {}
  local ng = meta.neuroglancer
  if ng and ng.hosts then
    for _, item in ipairs(ng.hosts) do
      local h = normalize_host(pandoc.utils.stringify(item))
      if h and h ~= "" then set[h] = true end
    end
  end
  return set
end

-- Quarto runs pandoc with the input file's directory as the working directory,
-- so find the project root (holds _quarto.yml) to load the shared manifest.
local function project_dir()
  local d = os.getenv("QUARTO_PROJECT_DIR")
  if d and d ~= "" then return d end
  local dir = pandoc.system.get_working_directory()
  for _ = 1, 8 do
    local probe = io.open(dir .. "/_quarto.yml", "r")
    if probe then probe:close(); return dir end
    local parent = dir:gsub("/[^/]+$", "")
    if parent == dir or parent == "" then break end
    dir = parent
  end
  return pandoc.system.get_working_directory()
end

local function read_manifest()
  local f = io.open(project_dir() .. "/figures/manifest.json", "r")
  if not f then return {} end
  local content = f:read("*a")
  f:close()
  local ok, data = pcall(pandoc.json.decode, content)
  if not ok or type(data) ~= "table" then return {} end
  local map = {}
  for url, entry in pairs(data) do
    -- Include placeholders (ok == false) too, so a browser-less local build
    -- shows the placeholder image rather than falling back to a badge.
    if type(entry) == "table" and entry.path then
      map[url] = entry.path
    end
  end
  return map
end

-- Is this block a single Neuroglancer link on its own? Returns url, attr.
local function sole_link(inlines)
  local link, count = nil, 0
  for _, il in ipairs(inlines) do
    local t = il.t
    if t == "Space" or t == "SoftBreak" or t == "LineBreak" then
      -- ignore surrounding whitespace
    elseif t == "Link" then
      count = count + 1
      link = il
    elseif t == "Str" and il.text:match("^https?://%S+$") then
      count = count + 1
      link = il
    else
      return nil
    end
  end
  if count ~= 1 then return nil end
  if link.t == "Link" then return link.target, link.attr end
  return link.text, nil
end

local function has_class(attr, cls)
  if not attr then return false end
  for _, c in ipairs(attr.classes or {}) do
    if c == cls then return true end
  end
  return false
end

return {
  { Meta = function(m)
      hosts = read_hosts(m)
      figures = read_manifest()
      return m
    end },

  -- Figure pass first, so a paragraph-sole link becomes a figure before the
  -- badge pass would turn it into a badge.
  { Para = function(el)
      local url, attr = sole_link(el.content)
      if url and is_ng(url) and not has_class(attr, "ng-badge-only") then
        local fig = figure(url)
        if fig then return fig end
      end
      return nil
    end },

  -- Badge pass: remaining Neuroglancer links and bare URLs become badges.
  {
    Link = function(el)
      if not is_ng(el.target) then return nil end
      if has_class(el.attr, "ng-figure") then
        local fig = figure(el.target)
        if fig then return pandoc.utils.blocks_to_inlines({ fig }) end
      end
      return badge(el.target)
    end,
    Str = function(el)
      local core, trail = el.text:match("^(.-)([%.,;:!%?%)%]]*)$")
      local url = core or el.text
      if url:match("^https?://") and is_ng(url) then
        if trail and trail ~= "" then
          return { badge(url), pandoc.Str(trail) }
        end
        return badge(url)
      end
      return nil
    end,
  },
}
