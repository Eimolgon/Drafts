# app.py
from flask import Flask, request, send_file, render_template_string
from weasyprint import HTML
import tempfile
import os
import json

app = Flask(__name__)

@app.route('/')
def index():
    with open('frontend/index.html') as f:
        return render_template_string(f.read())

@app.route('/export', methods=['POST'])
def export():
    data = request.json
    html = f"""
    <html>
    <head>
    <style>
    body {{ font-family: sans-serif; padding: 2em; }}
    .instruction {{ margin-bottom: 1em; border-bottom: 1px solid #ccc; padding-bottom: 1em; }}
    </style>
    </head>
    <body>
    <h1>Rally Roadbook</h1>
    {data['html']}
    </body>
    </html>
    """
    
    tmp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    HTML(string=html).write_pdf(tmp_pdf.name)
    return send_file(tmp_pdf.name, as_attachment=True, download_name="roadbook.pdf")

if __name__ == '__main__':
    app.run(debug=True)


