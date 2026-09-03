# CV Generator

Un editor local para tu CV: escribes tus datos en YAML del lado izquierdo y ves
el PDF actualizarse en vivo del lado derecho. Cuando te gusta, lo descargas.

También puede correr como comando de terminal, sin interfaz, si solo quieres
regenerar el PDF a partir del archivo de datos.

El diseño vive en una plantilla HTML/CSS (`template/cv_template.html.j2`) y se
convierte a PDF con [WeasyPrint](https://weasyprint.org/).

## Editor web (localhost)

### Con Docker (recomendado — no necesitas instalar nada más)

```bash
docker build -t cv-generator .
docker run --rm -p 8080:5000 -v "$(pwd)/data:/app/data" cv-generator
```

Abre http://localhost:8080

El volumen de `data/` es lo que hace que el editor arranque pre-cargado con
tu `cv_data.yaml`. Para guardar cambios de forma permanente, edita ese
archivo directamente (con tu editor de texto de siempre, o en modo comando
con `generate_cv.py`) — el editor web es solo para escribir con
syntax-highlighting, ver el preview en vivo y descargar el PDF; no escribe
nada al disco. Mientras escribes, tu borrador se guarda automáticamente en
el navegador (no en el servidor) así que un refresh o cerrar la pestaña no
te hace perder el trabajo.

### Sin Docker

Necesitas Python 3.10+ y las librerías de sistema de WeasyPrint:

- **Mac**: `brew install pango`
- **Linux (Debian/Ubuntu)**: `sudo apt-get install libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0`
- **Windows**: usa Docker o WSL.

```bash
pip install -r requirements.txt
python app.py
```

Abre http://localhost:5000 (o usa `--port 8080` para otro puerto).

### Qué hace cada botón

| Botón | Qué hace |
|---|---|
| *(automático)* | El preview se actualiza solo, ~0.7s después de que dejas de escribir |
| *(automático)* | Tu borrador se guarda solo en el navegador (`localStorage`), para no perderlo con un refresh |
| **Discard local draft** | Solo aparece si hay un borrador restaurado; lo descarta y vuelve al `cv_data.yaml` que cargó el servidor |
| **Download PDF** | Descarga el PDF con el nombre `TuNombre_CV.pdf` |

Si el YAML tiene un error de sintaxis, aparece un mensaje abajo del preview con
la línea y columna del problema; el preview conserva la última versión válida.

## Modo comando (sin interfaz)

Con Docker:

```bash
docker run --rm \
  -v "$(pwd)/data:/app/data" -v "$(pwd)/output:/app/output" \
  --entrypoint python cv-generator generate_cv.py
```

Sin Docker:

```bash
python generate_cv.py
python generate_cv.py --data data/cv_data.yaml --output output/mi_cv.pdf
```

## Estructura del repo

```
cv-generator/
├── data/cv_data.yaml          # Tus datos — edita esto para actualizar el CV
├── template/
│   └── cv_template.html.j2    # El diseño (HTML/CSS con Jinja2)
├── webapp/templates/
│   └── editor.html            # La interfaz del editor
├── fonts/                     # Inter, empaquetada para que el diseño
│                              # se vea igual en cualquier máquina
├── cv_renderer.py             # Lógica compartida: YAML -> HTML -> PDF
├── app.py                     # Servidor del editor web
├── generate_cv.py             # Versión de línea de comandos
├── output/                    # Aquí cae el PDF en modo comando
├── requirements.txt
└── Dockerfile
```

## Cómo agregar un puesto nuevo o una promoción

En `data/cv_data.yaml`, cada empresa es un elemento de `experience`, con una
lista `roles` debajo. Si tuviste más de un puesto en la misma empresa, agrega
otro elemento a `roles` — el diseño dibuja automáticamente la línea que conecta
los puestos, y la corta después del último. Pon el puesto más reciente primero.

```yaml
- company: "Nombre de la empresa"
  url: "https://ejemplo.com/"      # o null si no quieres que sea un link
  roles:
    - title: "Puesto más reciente"
      dates: "Mon YYYY - Present"
      bullets:
        - "Logro o responsabilidad. Puedes usar <strong>negritas</strong> con HTML."
    - title: "Puesto anterior en la misma empresa"
      dates: "Mon YYYY - Mon YYYY"
      bullets:
        - "..."
```

## Cómo cambiar las skills

Cada categoría en `skills` es un bloque con `category` y una lista de `items`.
Puedes agregar, quitar o renombrar categorías — la plantilla acomoda las
columnas automáticamente.

## Cómo usarlo para otro CV

Borra el contenido de `data/cv_data.yaml` y escribe el tuyo siguiendo la misma
estructura. Nada del diseño está atado a un nombre o empresa en particular.
