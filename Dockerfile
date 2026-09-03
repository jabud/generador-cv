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
# Bakes in the example CV (data/cv_data.yaml) so the editor has something
# to show without a volume mount — needed for a public deploy (Render),
# where there's no local disk to mount. Local/Docker usage still works the
# same: `-v "$(pwd)/data:/app/data"` overrides this with your own file.
COPY data/ ./data/

EXPOSE 5000

# Default: run the web editor behind gunicorn (production-grade, unlike
# Flask's dev server) on $PORT if set (Render sets this), else 5000.
# --workers 1: free-tier hosts (e.g. Render's free plan) have very little
# RAM, and each worker loads its own copy of WeasyPrint/Pango — 2 workers
# was OOM-killing the process intermittently. One worker is plenty for a
# low-traffic personal tool.
# --timeout 60: WeasyPrint can take longer than gunicorn's 30s default,
# especially on a cold worker. For the CLI instead, see the README.
CMD ["sh", "-c", "gunicorn app:app --bind 0.0.0.0:${PORT:-5000} --workers 1 --timeout 60"]
