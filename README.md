# 🎉 WG Party Games — catálogo

Un solo link para todos tus juegos web multijugador de fiesta. Aunque añadas juegos, el link siempre es el mismo (GitHub Pages).

## Ver en local

```bash
python3 -m http.server 8000
# abre http://localhost:8000
```

## Añadir un juego (30 segundos, sin tocar código)

1. Ve a **Issues → New → Añadir juego 🎮**.
2. Rellena nombre, descripción (máx 140), URL (`https://…`).
3. Imagen, elige una:
   - **Pega una captura con Ctrl+V** en el campo "Captura / imagen" (recomendado), o
   - Pega una URL de imagen.
4. Crea el issue. El Action `Add game from issue` valida, guarda la imagen en `assets/`, añade la entrada a `games.json`, commitea, comenta y cierra solo.
5. Si algo falla, comenta el error y pone label `needs-fix`: edita el issue y se reintenta.

## Estructura

- `index.html` / `style.css` / `app.js` — web estática, sin build.
- `games.json` — `[{id, nombre, descripcion, url, imagen}]`, ordenado por nombre.
- `assets/` — capturas guardadas por el bot + `placeholder.svg`.
- `.github/ISSUE_TEMPLATE/añadir-juego.yml` — formulario.
- `.github/scripts/add_game.py` + `workflows/add-game.yml` — el bot.
- `.github/workflows/pages.yml` — deploy a Pages en cada push a `main`.

## Deploy

1. Sube el repo a GitHub.
2. Settings → Pages → Source: **GitHub Actions**.
3. Cada push a `main` publica. Tu link será `https://<user>.github.io/wg_games/`.
4. Recuerda sustituir `OWNER` en `index.html` (2 enlaces "añadir juego") por tu usuario/org.
