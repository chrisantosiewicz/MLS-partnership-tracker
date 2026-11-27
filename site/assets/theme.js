// Site behaviour: the club picker, the directory filter, and smaller chart
// labels on narrow screens.
(function () {
  "use strict";

  function plots() { return document.querySelectorAll(".js-plotly-plot"); }

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
        count.textContent = shown + " of " + rows.length + " " + (count.dataset.noun || "clubs");
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

  // Club profiles: show the chosen club's block.
  function wireProfiles() {
    var select = document.getElementById("profile-select");
    if (!select) return;
    select.addEventListener("change", function () {
      document.querySelectorAll(".profile").forEach(function (el) {
        el.hidden = el.dataset.club !== select.value;
      });
      try { history.replaceState(null, "", "#" + select.value); } catch (e) { /* file:// */ }
    });
    var wanted = (location.hash || "").slice(1).toUpperCase();
    if (wanted && select.querySelector("option[value='" + wanted + "']")) {
      select.value = wanted;
      select.dispatchEvent(new Event("change"));
    }
  }

  function init() {
    wireProfiles();
    compact();
    wireClubSelect();
    wireDirectory();
  }

  if (document.readyState === "complete") init();
  else window.addEventListener("load", init);
})();
