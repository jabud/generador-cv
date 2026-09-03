# Roadmap

Plan de trabajo para llevar el generador de CV de "herramienta local" a "app
pública" y agregarle un par de features. Cada sección es independiente; no
hay que hacerlas en orden salvo donde se indique una dependencia.

## 1. Preparar el repo para desplegar en Render ✅ Hecho

Implementado: `.dockerignore`, `PORT` leído del entorno con fallback a
5000, `gunicorn` como servidor de producción (Dockerfile), `data/` ahora
se copia a la imagen (antes solo llegaba por volumen — sin eso, un deploy
sin volumen mostraba el editor vacío en vez del ejemplo de Bartleby),
botón/ruta `/save` eliminados, y un `render.yaml` mínimo. Falta lo que no
se puede probar desde acá: crear el Web Service en el dashboard de Render,
conectar el repo y verificar el deploy real (pasos 4 y 5 de abajo siguen
pendientes, son manuales).


El objetivo es que el **mismo** `Dockerfile`/`app.py` sirvan para dos
públicos distintos, sin mantener dos versiones del proyecto:

- alguien con Docker que clona el repo y corre `docker run` en su máquina
  (como hoy, ver el README), y
- alguien no técnico que solo entra al link de Render y usa el editor en
  el navegador, sin saber que existe un Dockerfile.

Render construye directamente desde el `Dockerfile`, así que la mayoría del
trabajo es hacer que el contenedor se comporte como un servicio de
producción en vez de un editor local.

1. **Agregar `.dockerignore`** en la raíz para no copiar basura a la imagen:
   `output/`, `.git/`, `__pycache__/`, `.DS_Store`, `*.pyc`.
2. **Escuchar en el puerto que Render asigna.** Render inyecta la variable
   de entorno `PORT` (no siempre es 5000) y espera que el proceso escuche
   ahí. Hoy `app.py` solo acepta `--port` por CLI (default 5000). Hay que
   leer `PORT` del entorno como fallback:
   ```python
   import os
   parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", 5000)))
   ```
3. **Cambiar el servidor de dev por uno de producción.** `app.run(...)` es
   el servidor de desarrollo de Flask — no está pensado para tráfico real
   ni para manejar el tiempo que tarda WeasyPrint en renderizar un PDF sin
   bloquear otras requests. Agregar `gunicorn` a `requirements.txt` y
   cambiar el `CMD` del Dockerfile a algo como:
   ```dockerfile
   CMD ["sh", "-c", "gunicorn app:app --bind 0.0.0.0:${PORT:-5000} --workers 2 --timeout 60"]
   ```
   (el `--timeout 60` importa: renderizar PDF con fuentes + Pango puede
   tardar más que el timeout default de 30s en la primera request fría).
4. **Subir el repo a GitHub** (o GitLab) — Render despliega conectándose a
   un repo remoto, no aceptando un `git push` directo tipo Heroku.
5. **Crear el Web Service en Render:**
   - New → Web Service → conectar el repo.
   - Environment: Docker (lo detecta solo por el `Dockerfile`).
   - Instance Type: Free.
   - Verifica en el momento si Render te pide método de pago para el
     free tier — esa política ha cambiado con el tiempo.
6. **Quitar el botón "Save to file" y la ruta `/save` por completo** — más
   simple que apagarlo condicionalmente, y sirve igual de bien para los
   dos públicos:
   - Local/Docker: quien clonó el repo ya tiene `data/cv_data.yaml` en su
     editor de texto de siempre; el UI web pasa a ser solo para escribir
     cómodo con syntax highlighting, ver el preview en vivo y descargar el
     PDF. No pierde nada, solo deja de duplicar la edición del archivo.
   - Link público: nunca hubo un archivo de servidor que tuviera sentido
     compartir entre desconocidos, así que no hay nada que perder.
   - Quitar en `app.py` la ruta `@app.route("/save", ...)`, en
     `webapp/templates/editor.html` el botón `#save` y su listener, y
     actualizar la tabla de botones del `README.md`.
   - La sección 4 (autoguardado en `localStorage`) cubre el "no quiero
     perder lo que escribí" para todo el mundo, sin tocar disco del
     servidor en ningún caso.
7. **Deploy y verificación:**
   - Revisar logs de build (que las libs de sistema de Pango/HarfBuzz se
     instalen bien — ya están en el `Dockerfile` actual).
   - Probar `/`, `/preview` y `/download` en la URL pública.
   - Confirmar el comportamiento de "cold start": el free tier duerme el
     servicio tras inactividad: la primera request tras dormir tarda más.
8. **Opcional:** agregar un `render.yaml` en la raíz para infra-as-code
   (que el servicio quede definido en el repo y no solo en la UI de
   Render), útil si luego quieres reproducir el setup o migrarlo.

## 2. ~~Reemplazar los datos personales por un ejemplo~~ ✅ Hecho

`data/cv_data.yaml` ahora tiene un perfil ficticio ("Juan Bartleby", Data
Scientist) con casos de promoción (varios `roles` bajo una misma empresa,
con ascenso de puesto) y casos sin promoción (una sola posición, o cambios
de empresa sin cambio de nivel), sirviendo de ejemplo para quien clone el
repo y quiera armar su propio CV.

## 3. Elegir entre distintos templates de PDF

1. **Reestructurar `template/`** en una carpeta por diseño, por ejemplo:
   ```
   template/
     classic/cv_template.html.j2   # el diseño actual
     modern/cv_template.html.j2    # un segundo diseño nuevo
   ```
2. **Agregar un registro de templates en `cv_renderer.py`**, algo como:
   ```python
   TEMPLATES = {
       "classic": TEMPLATE_DIR / "classic",
       "modern": TEMPLATE_DIR / "modern",
   }
   ```
3. **Parametrizar el render.** `render_html()`, `render_pdf_bytes()` y
   `render_pdf_file()` reciben un `template_id: str = "classic"` y arman el
   `FileSystemLoader` apuntando a `TEMPLATES[template_id]` en vez de al
   `TEMPLATE_DIR` fijo.
4. **Exponer el parámetro en `app.py`.** Como `/preview` y `/download` hoy
   reciben el YAML crudo como body (`Content-Type: text/plain`), la forma
   más simple es agregar un query param: `POST /preview?template=modern`.
5. **Exponer el flag en `generate_cv.py`** (`--template modern`) para el
   modo CLI.
6. **Agregar el selector en `webapp/templates/editor.html`:** un `<select>`
   junto a los botones del header, con las opciones hardcodeadas (o
   servidas por un endpoint `/templates` si prefieres no tocar el HTML
   cada vez que agregues un diseño). Su evento `change` debe disparar
   `refreshPreview()` pasando el template elegido.
7. **Guardar el template elegido junto con el borrador** del YAML (ver
   sección 4), para que al volver a abrir la página se mantenga la
   selección, no solo el contenido.
8. **Diseñar al menos un segundo template** de verdad distinto (layout de
   dos columnas, otra tipografía/paleta, etc.) — si no, el selector queda
   de adorno con una sola opción real.

## 4. No perder el YAML al refrescar o cerrar la pestaña ✅ Hecho


Objetivo: un autoguardado en el navegador (`localStorage`) que reemplaza
por completo lo que hacía el botón "Save to file" (ver sección 1, donde se
quita) — sin escribir nada a disco del servidor, y sirviendo igual para el
uso local que para el link público.

1. **Definir una clave de storage** en `editor.html`, ej.
   `const DRAFT_KEY = 'cv_editor_draft_v1'`.
2. **Guardar en cada cambio.** Dentro del listener de `input` que ya existe
   (el mismo que dispara `paintHighlight()` y `scheduleRefresh()`), agregar
   un `try { localStorage.setItem(DRAFT_KEY, yamlEl.value) } catch {}` — el
   `try/catch` cubre modo privado de Safari o storage deshabilitado.
3. **Restaurar al cargar la página.** Antes de pintar el editor con
   `initial_yaml` (el valor que manda el servidor), revisar si existe un
   draft en `localStorage`. Si existe y es distinto al de servidor, usarlo
   en vez de `initial_yaml` — con un aviso chico tipo "Se restauró tu
   borrador local" y un botón para descartarlo y volver al valor del
   servidor.
4. **Botón "Descartar borrador"** que haga
   `localStorage.removeItem(DRAFT_KEY)` y recargue el textarea con
   `initial_yaml`.
5. **Ya no hay un "Save to file" con el que coordinarse** (se quita en la
   sección 1) — el draft en `localStorage` es la única copia intermedia;
   `Download PDF` sigue siendo el paso explícito para llevarte el
   resultado final.
6. **Nota de alcance:** `localStorage` es por navegador/dispositivo, no se
   sincroniza entre pestañas de más de una persona ni entre dispositivos —
   es exactamente lo que se busca aquí (una copia de seguridad personal,
   no un guardado compartido).
