// Site behaviour: chart colors per theme, the club picker, the directory filter.
// Charts are drawn in Python with the light palette; this swaps every light
// value for its dark step (same hue, validated for the dark surface) when the
// page is in dark mode, and back again. Keep the map in sync with charts.py.
(function () {
  "use strict";

  var LIGHT_TO_DARK = {
    "#257de0": "#338ced",   // series 1 blue
    "#f47230": "#e76624",   // series 2 orange
    "#00b894": "#00a888",   // series 3 aqua
    "#ec4647": "#eb6263",   // negative red
    "#191919": "#efefef",   // text
    "#666666": "#9c9c9c",   // secondary text
    "#8c8c8c": "#7a7a7a",   // muted lines
    "#e6e6e3": "#2e2e2e",   // grid
    "#ffffff": "#191919"    // card surface (gaps, rings, hover label)
  };
  var DARK_TO_LIGHT = {};
  Object.keys(LIGHT_TO_DARK).forEach(function (k) { DARK_TO_LIGHT[LIGHT_TO_DARK[k]] = k; });

  function isDark() { return document.body.classList.contains("quarto-dark"); }

  function remap(value, map) {
    if (typeof value === "string") {
      var hit = map[value.toLowerCase()];
      return hit === undefined ? value : hit;
    }
    if (Array.isArray(value)) return value.map(function (v) { return remap(v, map); });
    if (value && typeof value === "object" && !(value instanceof Date) &&
        !ArrayBuffer.isView(value)) {
      var out = {};
      Object.keys(value).forEach(function (k) {
        out[k] = k === "customdata" || k === "x" || k === "y" ? value[k] : remap(value[k], map);
      });
      return out;
    }
    return value;
  }

  function plots() { return document.querySelectorAll(".js-plotly-plot"); }

  function applyTheme() {
    if (!window.Plotly) return;
    var dark = isDark();
    plots().forEach(function (gd) {
      if (gd.dataset.theme === (dark ? "dark" : "light")) return;
      if (!gd.dataset.theme && !dark) { gd.dataset.theme = "light"; return; }
      var map = dark ? LIGHT_TO_DARK : DARK_TO_LIGHT;
      var data = gd.data.map(function (t) { return remap(t, map); });
      var layout = remap(gd.layout, map);
      window.Plotly.react(gd, data, layout, gd._context);
      gd.dataset.theme = dark ? "dark" : "light";
    });
  }

  // Club picker: show the three traces whose meta is the chosen club.
  function wireClubSelect() {
    var select = document.getElementById("club-select");
    if (!select) return;
    var titles = {};
    try { titles = JSON.parse(select.dataset.titles || "{}"); } catch (e) { /* keep defaults */ }
    select.addEventListener("change", function () {
      var gd = document.getElementById(select.dataset.target);
      if (!gd || !window.Plotly) return;
      var club = select.value;
      var visible = gd.data.map(function (t) { return t.meta === club; });
      window.Plotly.restyle(gd, { visible: visible });
      window.Plotly.relayout(gd, { "xaxis.autorange": true, "yaxis.autorange": true });
      var title = document.getElementById(select.dataset.target + "-title");
      if (title && titles[club]) title.textContent = titles[club];
    });
  }

  // Directory: free-text search plus a conference toggle.
  function wireDirectory() {
    document.querySelectorAll(".directory").forEach(function (root) {
      var input = root.querySelector(".dir-search");
      var buttons = root.querySelectorAll(".seg-btn");
      var rows = root.querySelectorAll("tbody tr");
      var count = root.querySelector(".dir-count");
      var conf = "";
      function update() {
        var q = (input.value || "").trim().toLowerCase();
        var shown = 0;
        rows.forEach(function (tr) {
          var ok = (!conf || tr.dataset.conf === conf) &&
                   (!q || tr.dataset.search.indexOf(q) !== -1);
          tr.hidden = !ok;
          if (ok) shown += 1;
        });
        count.textContent = shown + " of " + rows.length + " clubs";
      }
      input.addEventListener("input", update);
      buttons.forEach(function (b) {
        b.addEventListener("click", function () {
          buttons.forEach(function (x) { x.classList.remove("active"); x.setAttribute("aria-pressed", "false"); });
          b.classList.add("active"); b.setAttribute("aria-pressed", "true");
          conf = b.dataset.conf; update();
        });
      });
      update();
    });
  }

  // Narrow screens: smaller tick labels so long category names leave room for bars.
  function compact() {
    if (!window.Plotly || window.innerWidth > 600) return;
    plots().forEach(function (gd) {
      window.Plotly.relayout(gd, { "yaxis.tickfont.size": 10, "xaxis.tickfont.size": 10,
                                   "legend.font.size": 11 });
    });
  }

  function init() {
    compact();
    wireClubSelect();
    wireDirectory();
    applyTheme();
    new MutationObserver(applyTheme).observe(document.body, { attributes: true, attributeFilter: ["class"] });
  }

  if (document.readyState === "complete") init();
  else window.addEventListener("load", init);
})();
