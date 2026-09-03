#!/usr/bin/env python3
"""
Local web editor for the CV.

Left pane: YAML editor. Right pane: live PDF preview. Button: download PDF.

Usage:
    python app.py
    # then open http://localhost:5000
"""
import argparse
import io
import os

from flask import Flask, jsonify, render_template, request, send_file, send_from_directory

from cv_renderer import DEFAULT_DATA, FONTS_DIR, parse_yaml_string, render_pdf_bytes

app = Flask(__name__, template_folder="webapp/templates", static_folder="webapp/static")


@app.route("/fonts/<path:filename>")
def fonts(filename):
    """Serve the bundled Inter fonts so the editor UI matches the CV itself."""
    return send_from_directory(FONTS_DIR, filename)


@app.route("/")
def index():
    """Serve the editor, pre-filled with the YAML file from data/."""
    try:
        with open(DEFAULT_DATA, "r", encoding="utf-8") as f:
            initial_yaml = f.read()
    except FileNotFoundError:
        initial_yaml = "name: Your Name\nheadline: Your Title\n"
    return render_template("editor.html", initial_yaml=initial_yaml)


@app.route("/preview", methods=["POST"])
def preview():
    """Render the posted YAML to a PDF and stream it back for the preview pane."""
    yaml_text = request.get_data(as_text=True)
    try:
        cv_data = parse_yaml_string(yaml_text)
        if not isinstance(cv_data, dict):
            raise ValueError("The YAML must be a mapping of fields (name, headline, ...).")
        pdf_bytes = render_pdf_bytes(cv_data)
    except Exception as exc:  # surface the error in the UI instead of a 500 page
        return jsonify({"error": str(exc)}), 400

    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=False,
        download_name="cv_preview.pdf",
    )


@app.route("/download", methods=["POST"])
def download():
    """Render the posted YAML and send it as a file download."""
    yaml_text = request.get_data(as_text=True)
    try:
        cv_data = parse_yaml_string(yaml_text)
        pdf_bytes = render_pdf_bytes(cv_data)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400

    filename = "cv.pdf"
    name = cv_data.get("name") if isinstance(cv_data, dict) else None
    if name:
        filename = f"{str(name).replace(' ', '_')}_CV.pdf"

    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=True,
        download_name=filename,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the local CV editor.")
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("PORT", 5000)),
        help="Port (default: 5000, or $PORT if set)",
    )
    parser.add_argument("--host", default="127.0.0.1", help="Host (default: 127.0.0.1)")
    args = parser.parse_args()

    print(f"\n  CV editor running at http://localhost:{args.port}\n")
    app.run(host=args.host, port=args.port, debug=False)
