// Reference snippet — copy inline into each widget (do not load as a module).
// loadState(defaults) → Promise<{ data, source, updatedAt }>
// Precedence for fields is applied in each widget: URL param > state.json > defaults (example).
function loadState(defaults) {
  var q = new URLSearchParams(location.search);
  var src = q.get('src') || 'data/state.json';
  return fetch(src, { cache: 'no-store' })
    .then(function (res) { if (!res.ok) throw new Error(String(res.status)); return res.json(); })
    .then(function (json) {
      return { data: json, source: 'state', updatedAt: json.updatedAt || null };
    })
    .catch(function () {
      return { data: defaults, source: 'example', updatedAt: null };
    });
}
