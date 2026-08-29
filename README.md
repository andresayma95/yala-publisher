# Publicador de Yala (prueba)

Prueba mínima para confirmar que se puede publicar en Instagram (@yalalatam) por API
desde GitHub Actions, antes de construir la automatización completa.

## Pasos (una vez)
1. Creá una cuenta de GitHub (gratis) y un repositorio **público** (ej. `yala-publisher`).
   Debe ser público para que la imagen tenga URL pública (la API de IG la necesita).
2. Subí estos archivos al repo (publish.py, README.md, la carpeta test/ con slide-01.jpg,
   y .github/workflows/test-publish.yml).
3. En el repo → **Settings → Secrets and variables → Actions → New repository secret**,
   creá DOS secrets:
   - `IG_TOKEN`  = tu token de Instagram (el que empieza con IGAA...).
   - `IG_USER_ID` = 7841436151715223
4. Andá a la pestaña **Actions** del repo → workflow **"Prueba publicar Yala"** →
   botón **Run workflow**.
5. Mirá el log: si dice "PUBLICADO. media_id: ..." → revisá @yalalatam, la foto está.
   Si da error, el log muestra el mensaje exacto de Meta (lo leemos y ajustamos).

## Si la prueba sale bien
Avisale a Claude y construye el resto: la máquina empuja la semana a este repo y un
workflow programado publica cada día solo. El token es SIEMPRE un Secret, nunca en el código.
