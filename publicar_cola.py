#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corre DENTRO de GitHub Actions. Lee cola.json, busca el post de HOY (hora de
Bogotá) que siga 'pendiente', lo publica en Instagram, y marca la cola.
Si no hay nada para hoy, no hace nada (exit 0) — el cron corre igual todos los
días lun-sáb y la mayoría de las veces no encuentra nada si la cola está vacía.
"""
import json, os, sys
from datetime import datetime
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from publish import publicar_post, publicar_reel

COLA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cola.json")


def raw_url(repo, ref, path):
    return f"https://raw.githubusercontent.com/{repo}/{ref}/{path}"


def main():
    token = os.environ["IG_TOKEN"].strip()
    repo = os.environ["GITHUB_REPOSITORY"]
    ref = os.environ.get("GITHUB_REF_NAME", "main")
    fecha_forzada = os.environ.get("FECHA_FORZADA", "").strip()

    with open(COLA_PATH, encoding="utf-8") as f:
        cola = json.load(f)

    tz = ZoneInfo(cola.get("zona_horaria", "America/Bogota"))
    hoy = fecha_forzada or datetime.now(tz).date().isoformat()
    print(f"Fecha de hoy (Bogotá): {hoy}")

    objetivo = None
    for post in cola["posts"]:
        if post["fecha"] == hoy and post.get("estado") == "pendiente":
            objetivo = post
            break

    if not objetivo:
        print("Nada pendiente para hoy. No se publica nada.")
        return

    if objetivo.get("tipo") == "reel":
        video_url = raw_url(repo, ref, objetivo["video"])
        print(f"Publicando reel '{objetivo['slug']}' ({video_url})...")
        media_id = publicar_reel(video_url, objetivo["caption"], token)
    else:
        urls = [raw_url(repo, ref, img) for img in objetivo["imagenes"]]
        print(f"Publicando '{objetivo['slug']}' con {len(urls)} imagen(es)...")
        media_id = publicar_post(urls, objetivo["caption"], token)

    objetivo["estado"] = "publicado"
    objetivo["media_id"] = media_id
    objetivo["publicado_en"] = datetime.now(tz).isoformat()

    with open(COLA_PATH, "w", encoding="utf-8") as f:
        json.dump(cola, f, ensure_ascii=False, indent=2)
    print("Cola actualizada.")


if __name__ == "__main__":
    main()
