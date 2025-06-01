from flask import Flask, render_template, request, jsonify, send_file
import requests
import svgwrite
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
import io
import os

app = Flask(__name__)

# Configuration
ORS_API_KEY = os.getenv('ORS_API_KEY', 'your-api-key-here')
MAP_CENTER = [51.505, -0.09]  # Default map center (London)
MAP_ZOOM = 13

@app.route('/')
def index():
    return render_template('index.html', 
                         center=MAP_CENTER, 
                         zoom=MAP_ZOOM,
                         ors_api_key=ORS_API_KEY)

@app.route('/generate_route', methods=['POST'])
def generate_route():
    data = request.json
    profile_map = {
        'motorcycle': 'driving-car',
        'bicycle-road': 'cycling-regular',
        'bicycle-mountain': 'cycling-mountain'
    }
    profile = profile_map.get(data.get('profile', 'motorcycle'))
    coordinates = data['coordinates']
    
    # Call OpenRouteService API
    url = f"https://api.openrouteservice.org/v2/directions/{profile}"
    headers = {
        'Authorization': ORS_API_KEY,
        'Content-Type': 'application/json'
    }
    body = {
        "coordinates": coordinates,
        "instructions": "false",
        "geometry": "true"
    }
    
    response = requests.post(url, json=body, headers=headers)
    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({"error": "Route generation failed"}), 400

@app.route('/generate_pdf', methods=['POST'])
def generate_pdf():
    data = request.json
    route_data = data['route']
    tulips = data['tulips']
    notes = data['notes']
    distance_unit = data.get('unit', 'km')
    
    # Create PDF
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    # Set up layout
    left_margin = 10 * mm
    col1_width = 30 * mm
    col2_width = 50 * mm
    col3_width = width - left_margin - col1_width - col2_width
    
    # Header
    c.setFont("Helvetica-Bold", 14)
    c.drawString(left_margin, height - 20 * mm, "Rally Roadbook")
    
    # Content
    y_position = height - 30 * mm
    
    for i, segment in enumerate(route_data['segments']):
        distance = segment['distance'] / (1000 if distance_unit == 'km' else 1)
        
        # Column 1: Distance
        c.setFont("Helvetica", 10)
        c.drawString(left_margin, y_position, f"{distance:.1f}{distance_unit}")
        
        # Column 2: Tulip diagram
        if i < len(tulips):
            c.drawString(left_margin + col1_width, y_position, f"[Tulip: {tulips[i]['direction']}]")
        
        # Column 3: Notes
        if i < len(notes):
            c.drawString(left_margin + col1_width + col2_width, y_position, notes[i])
        
        y_position -= 5 * mm
        if y_position < 20 * mm:
            c.showPage()
            y_position = height - 20 * mm
    
    c.save()
    buffer.seek(0)
    return send_file(
        buffer,
        as_attachment=True,
        download_name='roadbook.pdf',
        mimetype='application/pdf'
    )

if __name__ == '__main__':
    app.run(debug=True)
