# Publicador de Yala — semanal, automático

Publica en Instagram (@yalalatam) un post por día (lun-sáb) desde una cola,
usando GitHub Actions como backbone porque es el único lugar con internet
abierto a Meta (ni el contenedor de Claude ni el PC llegan a graph.instagram.com).

## Piezas

- **`cola.json`** — la cola de publicación. Una entrada por día: fecha, hora,
  `tipo` (`carrusel` o `reel`), imágenes o video (rutas relativas al repo),
  caption+hashtags ya combinados, y estado (`pendiente` → `publicado`). La
  arma `herramientas/preparar_cola.py` desde las piezas terminadas en
  `piezas/` — un carrusel necesita `caption.md` + `png/`, un reel necesita
  `caption.md` + un `.mp4` en `video/`.
- **`publish.py`** — habla con la API de Instagram. `publicar_post` publica
  una imagen o un carrusel; `publicar_reel` publica un Reel (sondea
  `status_code` hasta `FINISHED` antes de publicar, porque el video tarda en
  procesarse). Deriva el ID de la cuenta con `GET /me` usando el token —
  **nunca hardcodear ese ID a mano**, un ID equivocado da "Object does not
  exist".
- **`publicar_cola.py`** — corre dentro del workflow. Mira qué día es HOY en
  hora de Bogotá, busca la entrada `pendiente` de ese día en `cola.json`, la
  publica, y marca `publicado`.
- **`.github/workflows/publicar-diario.yml`** — el cron. Corre todos los días
  a las 19:00 hora Bogotá (lun-sáb) y llama a `publicar_cola.py`. También se
  puede disparar a mano (Actions → "Publicar diario Yala" → Run workflow),
  con un `fecha_forzada` opcional para probar sin esperar al cron.
- **`.github/workflows/test-publish.yml`** — la prueba original (una foto de
  test/), se deja para diagnóstico manual.

## Secrets necesarios (Settings → Secrets and variables → Actions)

- `IG_TOKEN` — el token largo (IGAA...) de la API de Instagram. Vence cada
  ~60 días, hay que renovarlo a mano por ahora.

(`IG_USER_ID` ya NO hace falta como secret: `publish.py` lo calcula solo.)

## Cómo se llena la cola cada semana

Desde el proyecto (`Maquina de contenido Yala/`), una vez que las piezas de
la semana están `revisada`/`aprobada` (carrusel + PNG + caption.md en
`piezas/YYYY-MM-DD-slug/`):

```
python3 herramientas/preparar_cola.py --fecha-inicio 2026-09-08 --hora 19:00
```

Esto convierte los PNG a JPEG 1080x1350, arma/actualiza `cola.json`, hace
commit local, y empuja a GitHub **si existe `config/github.pat`** (un Personal
Access Token clásico, scope `repo` + `workflow`, pegado en ese archivo — nunca
en el código ni en el repo). Sin ese archivo, deja todo commiteado localmente
y avisa que falta el push.

Es idempotente: correrlo de nuevo no toca fechas ya asignadas ni piezas ya
publicadas, solo agrega piezas nuevas después de la última fecha usada.

## Cómo se prueba sin esperar al cron

Actions → "Publicar diario Yala" → Run workflow → poné la fecha de una entrada
`pendiente` de `cola.json` en `fecha_forzada` → mirá el log.

## Historial

29-ago-2026: primera prueba real (una foto) confirmó que el camino funciona.
30-ago-2026: se construyó la cola semanal + el cron diario.
30-ago-2026: primer Reel real (`dom31-solo-tarjeta` — banco de videos + escenas
tipográficas + voz ElevenLabs) sumado a la cola. Se agregó soporte de Reels a
`publish.py`/`publicar_cola.py` (media_type REELS + espera de procesamiento),
antes solo publicaba carruseles de imagen.
