from flask import Flask, render_template_string, request, send_file, jsonify
import folium
import io
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

app = Flask(__name__)

points = []
mode = "add"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Map Instruction Tool</title>
    <style>
        body { display: flex; height: 100vh; margin: 0; }
        #map-container { width: 60vw; height: 100vh; position: relative; }
        #toolbar {
            position: absolute;
            top: 10px;
            left: 10px;
            display: flex;
            flex-direction: column;
            gap: 5px;
            background-color: rgba(255,255,255,0.9);
            padding: 0.5em;
            border: 1px solid #ccc;
            z-index: 1000;
        }
        #map { width: 100%; height: 100%; border: none; }
        #panel { width: 40vw; padding: 1em; overflow-y: auto; }
        textarea { width: 100%; height: 80%; }
        button { width: 100%; padding: 0.5em; }
    </style>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.3/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.3/dist/leaflet.js"></script>
</head>
<body>
    <div id="map-container">
        <div id="toolbar">
            <button onclick="setMode('add')">Add Marker</button>
            <button onclick="setMode('remove')">Remove Marker</button>
            <button onclick="setMode('none')">View Only</button>
        </div>
        <div id="map"></div>
    </div>
    <div id="panel">
        <form method="post" action="/save">
            <textarea name="instructions" id="instructions">{{ instructions }}</textarea>
            <button type="submit" name="format" value="txt">Export as TXT</button>
            <button type="submit" name="format" value="pdf">Export as PDF</button>
        </form>
    </div>

    <script>
        let mode = '{{ mode }}';

        function setMode(m) {
            mode = m;
        }

        const map = L.map('map').setView([45.0, 0.0], 4);

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19,
            attribution: '© OpenStreetMap contributors'
        }).addTo(map);

        let points = {{ points | safe }};
        const markers = [];

        function refreshMap() {
            markers.forEach(m => map.removeLayer(m));
            markers.length = 0;

            points.forEach((pt, i) => {
                const marker = L.marker(pt).addTo(map);
                marker.bindPopup(`Point ${i+1}`);
                markers.push(marker);
            });

            if (points.length > 1) {
                if (window.polyline) map.removeLayer(window.polyline);
                window.polyline = L.polyline(points, { color: 'blue' }).addTo(map);
            }
        }

        refreshMap();

        map.on('click', function(e) {
            if (mode === 'add') {
                fetch('/add_point', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                    body: 'lat=' + e.latlng.lat + '&lon=' + e.latlng.lng
                })
                .then(response => response.json())
                .then(data => {
                    points = data.points;
                    refreshMap();
                    document.getElementById("instructions").value = data.instructions;
                });
            } else if (mode === 'remove') {
                fetch(`/remove_point?lat=${e.latlng.lat}&lon=${e.latlng.lng}`)
                .then(response => response.json())
                .then(data => {
                    points = data.points;
                    refreshMap();
                    document.getElementById("instructions").value = data.instructions;
                });
            }
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    instructions = generate_instructions(points)
    return render_template_string(HTML_TEMPLATE, instructions=instructions, mode=mode, points=points)

def generate_instructions(pts):
    return "\n".join(
        f"{i+1}. From ({p[0]:.5f}, {p[1]:.5f}) to ({pts[i+1][0]:.5f}, {pts[i+1][1]:.5f})"
        for i, p in enumerate(pts[:-1])
    )

@app.route('/add_point', methods=['POST'])
def add_point():
    lat = float(request.form['lat'])
    lon = float(request.form['lon'])
    points.append((lat, lon))
    return jsonify(points=points, instructions=generate_instructions(points))

@app.route('/remove_point')
def remove_point():
    lat = float(request.args.get('lat'))
    lon = float(request.args.get('lon'))
    global points
    points = [pt for pt in points if not (abs(pt[0] - lat) < 1e-6 and abs(pt[1] - lon) < 1e-6)]
    return jsonify(points=points, instructions=generate_instructions(points))

@app.route('/save', methods=['POST'])
def save():
    data = request.form['instructions']
    file_format = request.form['format']

    if file_format == 'txt':
        buf = io.BytesIO()
        buf.write(data.encode('utf-8'))
        buf.seek(0)
        return send_file(buf, as_attachment=True, download_name='instructions.txt')

    elif file_format == 'pdf':
        buf = io.BytesIO()
        c = canvas.Canvas(buf, pagesize=A4)
        for i, line in enumerate(data.splitlines()):
            c.drawString(72, 800 - i * 15, line)
        c.save()
        buf.seek(0)
        return send_file(buf, as_attachment=True, download_name='instructions.pdf')

if __name__ == '__main__':
    app.run(debug=True)

