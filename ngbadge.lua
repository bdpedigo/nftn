-- ngbadge.lua
-- Render links to configured Neuroglancer deployments as one consistent badge.
-- Authors write plain markdown links or bare URLs and do nothing else.
--
-- The host list comes from project metadata (neuroglancer.hosts in _quarto.yml),
-- so there is one source of truth and no per-post configuration.
--
-- This filter is structured so TASK-7 (build-time figure generation) can extend
-- the same detection: reuse url_host / is_ng and add a Para/figure pass.

local hosts = {}

local function normalize_host(h)
  if not h then return nil end
  h = h:gsub("^[^@]*@", "") -- strip userinfo
  h = h:gsub(":%d+$", "")   -- strip port
  return h:lower()
end

-- Authority between "://" and the first / ? or #. This deliberately ignores
-- "#!" encoded state and "#!middleauth+https://..." fragments, which appear
-- after the host and must not be mistaken for a second URL.
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

local function badge(url)
  return pandoc.RawInline("html",
    '<a class="ng-badge" href="' .. attr_escape(url) .. '" target="_blank" rel="noopener">'
    .. ICON .. 'Open in Neuroglancer</a>')
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

return {
  { Meta = function(m) hosts = read_hosts(m); return m end },
  {
    -- Markdown links and autolinked bare URLs arrive as Link.
    Link = function(el)
      if is_ng(el.target) then return badge(el.target) end
      return nil
    end,
    -- A bare URL the reader did not autolink stays a single Str token (a URL
    -- has no spaces). Trailing sentence punctuation is kept out of the href.
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
