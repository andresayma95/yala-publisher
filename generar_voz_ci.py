#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corre DENTRO de GitHub Actions (workflow generar-voz.yml). Lee un .txt del
repo, resuelve el voice_id por nombre contra tu cuenta de ElevenLabs (GET
/v1/voices), genera el audio (POST /v1/text-to-speech/{id}) y lo guarda.

Uso: python3 generar_voz_ci.py <archivo_texto> <nombre_voz> <archivo_salida>
Necesita ELEVENLABS_API_KEY en el entorno (viene del Secret del repo).
"""
import json
import os
import sys
import urllib.error
import urllib.request

API = "https://api.elevenlabs.io/v1"


def resolver_voice_id(nombre, key):
    req = urllib.request.Request(f"{API}/voices", headers={"xi-api-key": key})
    with urllib.request.urlopen(req) as r:
        data = json.load(r)
    nombre_l = nombre.strip().lower()
    for v in data.get("voices", []):
        if nombre_l in v.get("name", "").lower():
            return v["voice_id"], v["name"]
    disponibles = ", ".join(v.get("name", "?") for v in data.get("voices", []))
    sys.exit(f"No encontré una voz que contenga '{nombre}'. Disponibles: {disponibles}")


def main():
    if len(sys.argv) != 4:
        sys.exit("Uso: generar_voz_ci.py <archivo_texto> <nombre_voz> <archivo_salida>")
    archivo_texto, nombre_voz, archivo_salida = sys.argv[1:4]

    key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    if not key:
        sys.exit("Falta el Secret ELEVENLABS_API_KEY en el repo.")

    with open(archivo_texto, encoding="utf-8") as f:
        texto = f.read().strip()
    if not texto:
        sys.exit(f"{archivo_texto} está vacío.")

    voice_id, nombre_real = resolver_voice_id(nombre_voz, key)
    print(f"Usando voz: {nombre_real} ({voice_id})")

    req = urllib.request.Request(
        f"{API}/text-to-speech/{voice_id}",
        data=json.dumps({
            "text": texto,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
        }).encode(),
        headers={
            "xi-api-key": key,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        },
    )
    os.makedirs(os.path.dirname(archivo_salida) or ".", exist_ok=True)
    try:
        with urllib.request.urlopen(req) as r, open(archivo_salida, "wb") as f:
            f.write(r.read())
    except urllib.error.HTTPError as e:
        sys.exit(f"ElevenLabs devolvió error: {e.read().decode()}")

    print(f"OK -> {archivo_salida} ({os.path.getsize(archivo_salida)} bytes)")


if __name__ == "__main__":
    main()
