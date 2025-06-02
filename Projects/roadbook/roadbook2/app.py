from flask import Flask, render_template, request, jsonify, send_file
import requests
import io
from fpdf import FPDF
import svgwrite

app = Flask(__name__)

ORS_API_KEY = "API HERE"  # <-- Replace here

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/route', methods=['POST'])
def route():
    data = request.json
    waypoints = data.get('waypoints')
    profile = data.get('profile', 'cycling-regular')  # cycling-regular or driving-motorcycle
    
    if not waypoints or len(waypoints) < 2:
        return jsonify({"error": "At least two waypoints required"}), 400
    
    # Prepare coordinates for OpenRouteService
    coords = [[pt['lng'], pt['lat']] for pt in waypoints]
    
    url = f'https://api.openrouteservice.org/v2/directions/{profile}/geojson'
    headers = {
        'Authorization': ORS_API_KEY,
        'Content-Type': 'application/json'
    }
    body = {"coordinates": coords, "instructions": True}
    
    resp = requests.post(url, json=body, headers=headers)
    if resp.status_code != 200:
        return jsonify({"error": "Routing API failed", "details": resp.text}), 500
    
    route_data = resp.json()
    # Extract needed info: geometry, instructions, distances
    features = route_data['features'][0]
    geometry = features['geometry']
    segments = features['properties']['segments'][0]
    steps = segments['steps']

    # Prepare simplified instructions + tulip info
    instructions = []
    cumulative = 0
    for step in steps:
        dist_km = step['distance'] / 1000
        cumulative += dist_km
        instr = {
            "distance": round(dist_km, 2),
            "cumulative": round(cumulative, 2),
            "instruction": step['instruction'],
            "type": step['maneuver']['type'],
            "modifier": step['maneuver'].get('modifier', None)
        }
        instructions.append(instr)
    
    return jsonify({
        "geometry": geometry,
        "instructions": instructions
    })

def generate_tulip_svg(instruction_type, modifier=None):
    dwg = svgwrite.Drawing(size=(60,60))
    center = (30, 30)
    
    # Draw base tulip shapes for common maneuvers
    # (simplified example - you can expand with detailed paths)
    if instruction_type == 'turn':
        if modifier == 'left':
            dwg.add(dwg.polyline([(50, 55), (30, 30), (50, 5)], stroke='black', fill='none', stroke_width=4))
        elif modifier == 'right':
            dwg.add(dwg.polyline([(10, 55), (30, 30), (10, 5)], stroke='black', fill='none', stroke_width=4))
        else:
            dwg.add(dwg.line((30, 55), (30, 5), stroke='black', stroke_width=4))
    elif instruction_type == 'roundabout':
        dwg.add(dwg.circle(center=center, r=20, stroke='black', fill='none', stroke_width=4))
        dwg.add(dwg.line((30,50), (30,10), stroke='black', stroke_width=4))
    elif instruction_type == 'depart':
        dwg.add(dwg.line((30, 55), (30, 5), stroke='black', stroke_width=4))
        dwg.add(dwg.polygon([(30,5),(25,15),(35,15)], fill='black'))
    else:
        dwg.add(dwg.line((30, 55), (30, 5), stroke='black', stroke_width=4))
    
    return dwg.tostring()

@app.route('/generate_pdf', methods=['POST'])
def generate_pdf():
    data = request.json
    instructions = data.get('instructions', [])
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)

    # Title
    pdf.cell(0, 10, "Rally Roadbook", ln=True, align='C')

    col_widths = [40, 60, 80]
    row_height = 20
    
    # Header
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(col_widths[0], row_height, "Distance (km)", border=1)
    pdf.cell(col_widths[1], row_height, "Tulip", border=1)
    pdf.cell(col_widths[2], row_height, "Notes", border=1)
    pdf.ln(row_height)
    pdf.set_font("Arial", '', 10)

    for instr in instructions:
        dist_text = f"{instr['distance']} km\nTotal: {instr['cumulative']} km"
        pdf.multi_cell(col_widths[0], 10, dist_text, border=1, ln=3, max_line_height=pdf.font_size)
        
        # Tulip SVG to PNG conversion is complex; simplified here: draw text placeholder
        pdf.set_xy(pdf.get_x() + col_widths[0], pdf.get_y() - 10)
        pdf.cell(col_widths[1], 10, f"[{instr['instruction'][:15]}]", border=1)
        
        pdf.set_xy(pdf.get_x() + col_widths[1], pdf.get_y() - 10)
        pdf.cell(col_widths[2], 10, instr.get('note', ''), border=1)
        pdf.ln(row_height)
    
    # Output PDF to bytes
    pdf_bytes = pdf.output(dest='S').encode('latin1')
    return send_file(io.BytesIO(pdf_bytes), mimetype='application/pdf', as_attachment=True, download_name='roadbook.pdf')

if __name__ == '__main__':
    app.run(debug=True)

