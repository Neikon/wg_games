const grid = document.getElementById('grid');
const search = document.getElementById('search');
const count = document.getElementById('count');
const tpl = document.getElementById('card-template');

let games = [];

async function load() {
  try {
    const res = await fetch('games.json', { cache: 'no-store' });
    if (!res.ok) throw new Error('no games.json');
    games = await res.json();
  } catch (e) {
    console.error(e);
    games = [];
  }
  render('');
}

function render(q) {
  const query = q.trim().toLowerCase();
  const filtered = games.filter(g =>
    !query ||
    g.nombre.toLowerCase().includes(query) ||
    (g.descripcion || '').toLowerCase().includes(query)
  );
  grid.innerHTML = '';
  count.textContent = filtered.length === 0
    ? 'Sin resultados 😅'
    : `${filtered.length} juego${filtered.length === 1 ? '' : 's'} 🎮`;

  if (filtered.length === 0) {
    const p = document.createElement('p');
    p.className = 'empty';
    p.textContent = 'No hay juegos todavía (o ninguno coincide). ¡Añade el primero con un issue! 🥳';
    grid.appendChild(p);
    return;
  }

  for (const g of filtered) {
    const node = tpl.content.cloneNode(true);
    const a = node.querySelector('.card-link');
    const img = node.querySelector('.card-img');
    a.href = g.url;
    a.setAttribute('aria-label', `${g.nombre} — jugar`);
    img.src = g.imagen || 'assets/placeholder.svg';
    img.alt = `Portada de ${g.nombre}`;
    img.onerror = () => { img.onerror = null; img.src = 'assets/placeholder.svg'; };
    node.querySelector('.card-title').textContent = g.nombre;
    node.querySelector('.card-desc').textContent = g.descripcion || '';
    grid.appendChild(node);
  }
}

search.addEventListener('input', e => render(e.target.value));
load();
