#!/usr/bin/env python3
"""
Publica en Instagram (API con Instagram Login) una imagen simple o un carrusel.
Lee el token de una variable de entorno (GitHub Secret) y deriva el IG user id
de GET /me con ese mismo token (no depende de un ID hardcodeado en un secret).

Uso como CLI:
  IG_TOKEN=... python publish.py URL_IMAGEN [URL2 URL3 ...]   (varias = carrusel)
  CAPTION="..." (env, opcional)

También se puede importar: from publish import publicar_post
"""
import os, sys, json, time, urllib.request, urllib.parse, urllib.error

# OJO: SIN /vXX.0 en la ruta. Con versión, graph.instagram.com devuelve 400.
# Confirmado a mano el 29-ago-2026 (ver memoria: publicar-instagram).
BASE = "https://graph.instagram.com"


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


def obtener_ig_user_id(token):
    """Deriva el ID que realmente publica desde /me (campo 'id'). Nunca hardcodear
    este ID a mano: el ID de perfil público NO es el mismo que este, y usar el
    equivocado da 'Object does not exist'."""
    me = _call("GET", f"/me?fields=id,username&access_token={token}")
    print("Token OK. Cuenta:", me)
    return me["id"]


def publicar_post(imgs, caption, token, igid=None):
    """Publica una imagen o un carrusel (si imgs tiene más de una URL). Devuelve el media_id."""
    if not imgs:
        raise ValueError("Faltan URLs de imagen.")
    if igid is None:
        igid = obtener_ig_user_id(token)

    if len(imgs) == 1:
        cont = _call("POST", f"/{igid}/media",
                     {"image_url": imgs[0], "caption": caption, "access_token": token})
        creation_id = cont["id"]
    else:
        kids = []
        for u in imgs:
            c = _call("POST", f"/{igid}/media",
                      {"image_url": u, "is_carousel_item": "true", "access_token": token})
            kids.append(c["id"]); time.sleep(1)
        cont = _call("POST", f"/{igid}/media",
                     {"media_type": "CAROUSEL", "children": ",".join(kids),
                      "caption": caption, "access_token": token})
        creation_id = cont["id"]

    # esperar procesamiento y publicar
    time.sleep(5)
    pub = _call("POST", f"/{igid}/media_publish",
                {"creation_id": creation_id, "access_token": token})
    print("PUBLICADO. media_id:", pub.get("id"))
    return pub.get("id")


def publicar_reel(video_url, caption, token, igid=None, timeout_seg=180):
    """Publica un Reel de video. A diferencia de una imagen, IG tarda en procesar
    el video: hay que sondear /{creation_id}?fields=status_code hasta FINISHED
    antes de poder publicar (ERROR ahí = video_url inaccesible o formato inválido)."""
    if igid is None:
        igid = obtener_ig_user_id(token)

    cont = _call("POST", f"/{igid}/media",
                 {"media_type": "REELS", "video_url": video_url,
                  "caption": caption, "access_token": token})
    creation_id = cont["id"]

    esperado = 0
    while esperado < timeout_seg:
        time.sleep(5)
        esperado += 5
        estado = _call("GET", f"/{creation_id}?fields=status_code&access_token={token}")
        code = estado.get("status_code")
        print(f"  procesando video... status_code={code} ({esperado}s)")
        if code == "FINISHED":
            break
        if code == "ERROR":
            raise RuntimeError(f"IG no pudo procesar el video: {estado}")
    else:
        raise TimeoutError(f"El video no terminó de procesar en {timeout_seg}s.")

    pub = _call("POST", f"/{igid}/media_publish",
                {"creation_id": creation_id, "access_token": token})
    print("PUBLICADO (reel). media_id:", pub.get("id"))
    return pub.get("id")


def main():
    imgs = sys.argv[1:]
    token = os.environ["IG_TOKEN"].strip()
    caption = os.environ.get("CAPTION", "Prueba de publicación automática de Yala.")
    publicar_post(imgs, caption, token)


if __name__ == "__main__":
    main()
