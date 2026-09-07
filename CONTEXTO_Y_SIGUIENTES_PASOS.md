# WG Party Games — Contexto y siguientes pasos

Fecha: 2026-09-07. Repo local: carpeta `wg_games/` (este mismo directorio).

## Qué es
Portal web a modo de **catálogo de juegos** para fiestas. Los juegos son
**solo links a otras webs** (no se alojan aquí). Un **solo link compartible**
(GitHub Pages) que siempre es el mismo aunque se añadan juegos.

Stack v1: **estático puro, sin build** — `index.html` + `style.css` + `app.js`
+ `games.json` + `assets/`. Sin framework, sin backend, sin dependencias.

## Qué hay ya hecho (verificado en local)
- `index.html` — layout fiestero (oscuro + acentos), buscador, grid, footer.
  OJO: contiene `OWNER` en 2 enlaces "añadir juego" → sustituir por usuario/org real.
- `style.css` — responsive `auto-fill minmax(260px,1fr)`, cards 16:9.
- `app.js` — fetch de `games.json`, render de cards, filtro por texto,
  fallback a `assets/placeholder.svg`, links con `target=_blank rel=noopener`.
- `games.json` — 1 entrada de ejemplo `Quiz Fiesta (ejemplo)` → borrar al añadir
  el primer juego real.
- `assets/placeholder.svg` — placeholder + fallback.
- `.github/ISSUE_TEMPLATE/añadir-juego.yml` — Issue Form con label `nuevo-juego`.
  Campos: nombre*, descripción* (máx 140), URL* (https), URL imagen opcional,
  campo "Captura / imagen (pega aquí con Ctrl+V) 📸".
- `.github/scripts/add_game.py` + `.github/workflows/add-game.yml` — bot:
  en issues con label `nuevo-juego` (opened/edited/reopened) valida
  (nombre único case-insensitive, desc ≤140, URL `https://`), detecta capturas
  pegadas (`github.com/user-attachments/assets/...`), las descarga a
  `assets/<slug>.<ext>` (png/jpg/webp/svg/gif, <5 MB), añade entrada ordenada
  a `games.json`, commit+push, comenta ✅ y cierra. Si falla: comenta error +
  label `needs-fix`; editar el issue reintenta.
- `.github/workflows/pages.yml` — deploy a GitHub Pages en cada push a `main`.
- `.devcontainer/devcontainer.json` — base bookworm + Python 3.12 + gh CLI,
  puerto 8000.
- `README.md` — instrucciones de uso. `.gitignore` mínimo.
- Verificación hecha: `json.tool` OK, `py_compile` OK, servidor local 200 en
  index/games.json/app.js, regex de adjuntos OK.

## Decisiones tomadas con el usuario
1. Nombre del portal: **WG Party Games** (aprobado).
2. Imagen: **las dos vías** — URL externa o captura pegada con Ctrl+V en el
   issue (el bot la guarda en `assets/`).
3. Deploy: **GitHub Pages** (`https://<user>.github.io/wg_games/`).

## Siguientes pasos (en orden)
1. `git init && git add -A && git commit -m "feat: catálogo WG Party Games v1"`
   y subir a GitHub como `wg_games`.
2. Sustituir `OWNER` en `index.html` (2 enlaces) por el usuario/org real.
3. GitHub → Settings → Pages → Source: **GitHub Actions**.
4. Probar el flujo: Issues → New → "Añadir juego 🎮" → rellenar + pegar una
   captura con Ctrl+V → crear → comprobar que el Action añade el juego,
   commitea y cierra el issue.
5. Borrar la entrada de ejemplo de `games.json` (a mano o con otro issue).
6. Compartir el link de Pages: ya no cambia nunca.
7. (Opcional, post-v1): filtros por nº jugadores/etiquetas, analytics,
   thumbnails auto, dominio propio.

## Comandos útiles
```bash
python3 -m http.server 8000        # ver en local → http://localhost:8000
python3 -m json.tool games.json    # validar catálogo
```
