#!/usr/bin/env python3
"""
Publica en Instagram (API con Instagram Login) una imagen simple o un carrusel.
Lee el token y el IG user id de variables de entorno (GitHub Secrets).
Uso: python publish.py URL_IMAGEN [URL2 URL3 ...]   (varias = carrusel)
Caption por env CAPTION (opcional).
"""
import os, sys, json, time, urllib.request, urllib.parse, urllib.error

BASE  = "https://graph.instagram.com/v21.0"
TOKEN = os.environ["IG_TOKEN"].strip()
IGID  = os.environ["IG_USER_ID"].strip()
CAP   = os.environ.get("CAPTION", "Prueba de publicación automática de Yala.")

def _call(method, path, data=None):
    url = BASE + path
    body = urllib.parse.urlencode(data).encode() if data else None
    req = urllib.request.Request(url, data=body, method=method)
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        print("ERROR de la API:", e.read().decode(), file=sys.stderr)
        raise

def main():
    imgs = sys.argv[1:]
    if not imgs:
        sys.exit("Faltan URLs de imagen.")

    # 0) validar token + ver quién soy
    me = _call("GET", f"/me?fields=user_id,username&access_token={TOKEN}")
    print("Token OK. Cuenta:", me)

    # 1) crear contenedor(es)
    if len(imgs) == 1:
        cont = _call("POST", f"/{IGID}/media",
                     {"image_url": imgs[0], "caption": CAP, "access_token": TOKEN})
        creation_id = cont["id"]
    else:
        kids = []
        for u in imgs:
            c = _call("POST", f"/{IGID}/media",
                      {"image_url": u, "is_carousel_item": "true", "access_token": TOKEN})
            kids.append(c["id"]); time.sleep(1)
        cont = _call("POST", f"/{IGID}/media",
                     {"media_type": "CAROUSEL", "children": ",".join(kids),
                      "caption": CAP, "access_token": TOKEN})
        creation_id = cont["id"]

    # 2) esperar procesamiento y publicar
    time.sleep(5)
    pub = _call("POST", f"/{IGID}/media_publish",
                {"creation_id": creation_id, "access_token": TOKEN})
    print("PUBLICADO. media_id:", pub.get("id"))

if __name__ == "__main__":
    main()
