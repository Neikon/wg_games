"""Añade un juego a games.json a partir de un issue con label nuevo-juego.

Soporta imagen de 2 formas:
  1. URL externa en el campo "URL de imagen".
  2. Captura pegada con Ctrl+V en el campo "Captura / imagen" -> GitHub la convierte
     en markdown ![...](https://github.com/user-attachments/assets/...) y aquí
     la descargamos a assets/<slug>.<ext>.

Valida: nombre único, descripción <=140, url https válida.
Comenta en el issue el resultado y lo cierra si todo va bien, o etiqueta needs-fix si falla.
"""
import json
import os
import re
import sys
import unicodedata
import urllib.request

EVENT_PATH = os.environ["EVENT_PATH"]
ISSUE_NUMBER = os.environ["ISSUE_NUMBER"]
REPO = os.environ["REPO"]
TOKEN = os.environ["GH_TOKEN"]
API = "https://api.github.com"

ALLOWED_EXT = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg", "webp": "image/webp", "svg": "image/svg+xml", "gif": "image/gif"}


def gh_api(method, path, data=None):
    req = urllib.request.Request(
        API + path,
        data=json.dumps(data).encode() if data is not None else None,
        method=method,
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read().decode() or "{}")


def comment(body):
    gh_api("POST", f"/repos/{REPO}/issues/{ISSUE_NUMBER}/comments", {"body": body})


def set_labels(labels):
    gh_api("PUT", f"/repos/{REPO}/issues/{ISSUE_NUMBER}/labels", {"labels": labels})


def close_issue():
    gh_api("PATCH", f"/repos/{REPO}/issues/{ISSUE_NUMBER}", {"state": "closed"})


def slugify(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s.lower()).strip("-")
    return s[:60] or "juego"


def parse_section(body, heading):
    """Issue Forms renderiza como '### Heading\\n\\nvalor'. Extrae valor (puede ser '_No response_')."""
    m = re.search(rf"### {re.escape(heading)}\s*\n+(.*?)(?=\n### |\Z)", body, re.S)
    if not m:
        return ""
    v = m.group(1).strip()
    return "" if v == "_No response_" else v


def main():
    with open(EVENT_PATH) as f:
        event = json.load(f)
    body = event["issue"].get("body") or ""

    nombre = parse_section(body, "Nombre del juego *").strip()
    descripcion = parse_section(body, "Descripción corta *").strip()
    url = parse_section(body, "URL del juego *").strip()
    imagen_url = parse_section(body, "URL de imagen (opcional si pegas captura abajo)").strip()
    captura = parse_section(body, "Captura / imagen (pega aquí con Ctrl+V) 📸")

    errors = []
    if not nombre:
        errors.append("Falta el **nombre**.")
    if not descripcion:
        errors.append("Falta la **descripción**.")
    elif len(descripcion) > 140:
        errors.append(f"La descripción tiene {len(descripcion)} caracteres, máx 140.")
    if not url or not re.match(r"^https://\S+$", url):
        errors.append("La **URL del juego** debe empezar por `https://`.")

    # Buscar imágenes pegadas (Ctrl+V) en cualquier parte del body.
    # GitHub las renderiza como markdown ![...](url) o como <img src="url">.
    pasted = re.findall(r"!\[[^\]]*\]\((https://github\.com/user-attachments/assets/[^)\s]+)\)", body)
    pasted += re.findall(r'<img\b[^>]*\bsrc=["\'](https://github\.com/user-attachments/assets/[^"\')\s]+)["\']', body, re.I)
    pasted += re.findall(r'(https://github\.com/user-attachments/assets/[^\s)<>"\']+)', body)
    # dedup manteniendo orden
    pasted = list(dict.fromkeys(pasted))
    # También por si la URL externa viene como markdown
    if not imagen_url:
        m = re.search(r"https?://\S+\.(?:png|jpe?g|webp|svg|gif)(\?\S*)?", captura or "", re.I)
        if m:
            imagen_url = m.group(0)

    with open("games.json") as f:
        games = json.load(f)
    if any(g["nombre"].lower() == nombre.lower() for g in games):
        errors.append(f"Ya existe un juego llamado **{nombre}** (comparación insensible a mayúsculas).")

    if errors:
        set_labels(["nuevo-juego", "needs-fix"])
        comment("❌ No pude añadir el juego:\n\n" + "\n".join(f"- {e}" for e in errors) + "\n\nEdita el issue y lo reintento solo. 🤖")
        sys.exit(0)

    slug = slugify(nombre)
    imagen = imagen_url

    # Si hay captura pegada, descargarla a assets/
    if pasted:
        src = pasted[0]
        try:
            req = urllib.request.Request(src, headers={"Authorization": f"Bearer {TOKEN}"})
            with urllib.request.urlopen(req, timeout=30) as r:
                blob = r.read()
                ctype = r.headers.get_content_type() or ""
            if len(blob) > 5 * 1024 * 1024:
                raise ValueError("la imagen supera 5 MB")
            ext = None
            for e, ct in ALLOWED_EXT.items():
                if ct == ctype:
                    ext = "jpg" if e == "jpeg" else e
                    break
            # fallback por extensión en la URL
            if not ext:
                m = re.search(r"\.(png|jpe?g|webp|svg|gif)(\?|$)", src, re.I)
                ext = (m.group(1).lower() if m else "png").replace("jpeg", "jpg")
            if ext not in ALLOWED_EXT:
                ext = "png"
            os.makedirs("assets", exist_ok=True)
            # Evita colisiones
            dest = f"assets/{slug}.{ext}"
            i = 2
            while os.path.exists(dest):
                dest = f"assets/{slug}-{i}.{ext}"
                i += 1
            with open(dest, "wb") as f:
                f.write(blob)
            imagen = dest
        except Exception as e:
            set_labels(["nuevo-juego", "needs-fix"])
            comment(f"❌ No pude descargar la captura pegada ({e}). Revisa que el adjunto sea visible o pon una URL de imagen. 🤖")
            sys.exit(0)

    if not imagen:
        imagen = "assets/placeholder.svg"

    games.append({
        "id": slug,
        "nombre": nombre,
        "descripcion": descripcion,
        "url": url,
        "imagen": imagen,
    })
    games.sort(key=lambda g: g["nombre"].lower())
    with open("games.json", "w") as f:
        json.dump(games, f, ensure_ascii=False, indent=2)
        f.write("\n")

    # Limpia needs-fix si estaba, comenta éxito y cierra
    try:
        labels = [l["name"] for l in gh_api("GET", f"/repos/{REPO}/issues/{ISSUE_NUMBER}/labels")]
        labels = [l for l in labels if l != "needs-fix"]
        set_labels(labels)
    except Exception:
        pass
    comment(f"✅ **{nombre}** añadido al catálogo con imagen `{imagen}`. ¡Gracias! 🎉\n\nSe publicará solo con GitHub Pages en cuanto se fusione.")
    close_issue()


if __name__ == "__main__":
    main()
