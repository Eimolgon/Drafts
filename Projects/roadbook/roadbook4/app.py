from flask import Flask, render_template, request, jsonify, send_file
import requests
import svgwrite
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
import io
import json
import os

app = Flask(__name__)

# OpenRouteService API key (get yours at https://openrouteservice.org/)
ORS_API_KEY = os.getenv('ORS_API_KEY', 'your-api-key-here')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_route', methods=['POST'])
def generate_route():
    data = request.json
    profile = data.get('profile', 'driving-car')
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
    
    # Create PDF buffer
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    # Set up margins and column widths
    left_margin = 10 * mm
    col1_width = 30 * mm
    col2_width = 50 * mm
    col3_width = width - left_margin - col1_width - col2_width
    
    # Draw header
    c.setFont("Helvetica-Bold", 14)
    c.drawString(left_margin, height - 20 * mm, "Rally Roadbook")
    
    # Draw columns
    c.setFont("Helvetica", 10)
    col1_x = left_margin
    col2_x = col1_x + col1_width
    col3_x = col2_x + col2_width
    
    y_position = height - 30 * mm
    
    # Add route segments
    for i, segment in enumerate(route_data['segments']):
        distance = segment['distance'] / (1000 if distance_unit == 'km' else 1)
        
        # Column 1: Distance
        c.drawString(col1_x, y_position, f"{distance:.1f}{distance_unit}")
        
        # Column 2: Tulip diagram
        if i < len(tulips):
            tulip_svg = generate_tulip_svg(tulips[i])
            # In a real implementation, we'd convert SVG to PDF image
            # For now, just place a placeholder
            c.drawString(col2_x, y_position, "[Tulip Diagram]")
        
        # Column 3: Notes
        if i < len(notes):
            c.drawString(col3_x, y_position, notes[i])
        
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

def generate_tulip_svg(tulip_data):
    # Create SVG tulip diagram based on the data
    dwg = svgwrite.Drawing(size=("50mm", "20mm"))
    
    # Add basic elements based on tulip_data
    if tulip_data.get('direction') == 'left':
        dwg.add(dwg.polyline([(10, 10), (0, 20), (10, 30)]))
    elif tulip_data.get('direction') == 'right':
        dwg.add(dwg.polyline([(40, 10), (50, 20), (40, 30)]))
    else:  # straight
        dwg.add(dwg.line((10, 20), (40, 20)))
    
    # Add icons if specified
    if 'icons' in tulip_data:
        for icon in tulip_data['icons']:
            if icon == 'house':
                dwg.add(dwg.rect((25, 10), (15, 10)))
            elif icon == 'river':
                dwg.add(dwg.path(d="M 15,25 C 20,20 30,20 35,25"))
    
    return dwg.tostring()

if __name__ == '__main__':
    app.run(debug=True)
