# Pinned to Debian bookworm so a future base-image bump doesn't rename packages
# out from under the build.
FROM python:3.12-slim-bookworm

# WeasyPrint 69 renders text through Pango + HarfBuzz + fontconfig.
# It no longer needs cairo or gdk-pixbuf (dropped in WeasyPrint 53+).
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libharfbuzz0b \
    libharfbuzz-subset0 \
    libfontconfig1 \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY cv_renderer.py generate_cv.py app.py ./
COPY template/ ./template/
COPY fonts/ ./fonts/
COPY webapp/ ./webapp/

EXPOSE 5000

# Default: run the web editor. For the CLI instead, see the README.
CMD ["python", "app.py", "--host", "0.0.0.0"]
