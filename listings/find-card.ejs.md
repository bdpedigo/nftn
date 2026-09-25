<%
// Custom listing template for Notes from the Neuropil "finds".
// Emits the .print cards from design/mockup-f-cover/index.html.
// Custom listings receive: items, metadataAttrs(item), templateParams.
// An item with no `image` emits Quarto's listing image placeholder, which
// Quarto replaces after rendering with the first image on that post.
const initials = (name) => {
  if (!name) return "?"
  return name.trim().split(/\s+/).map(w => w[0]).slice(0, 2).join("").toUpperCase()
}
%>
:::{.grid .find-grid}
<% for (const item of items) { %>
<% const cat = (item.categories && item.categories.length) ? item.categories[0] : "" %>
<% const author = item.author || "" %>
<article class="print" data-tag="<%= cat %>" <%= metadataAttrs(item) %>>
<% if (item.image) { %>
<a href="<%- item.path %>"><img src="<%= item.image %>" alt="<%= item['image-alt'] || 'Neuroglancer render of the find' %>"></a>
<% } else { %>
<a href="<%- item.path %>"><!-- img(9CEB782EFEE6)[progressive=false, height=]:<%- item.outputHref %> --></a>
<% } %>
<% if (item.question) { %><p class="q">“<%= item.question %>”</p><% } %>
<p class="asker"><% if (item.asker) { %>Asked by <%= item.asker %><% } else { %>Asked anonymously<% } %></p>
<h2><a href="<%- item.path %>"><%= item.title %></a></h2>
<p class="who"><% if (author) { %><span class="av"><%= initials(author) %></span><%= author %><% } %><% if (cat) { %><span class="tag"><span class="sw"></span><%= cat %></span><% } %></p>
</article>
<% } %>
:::
