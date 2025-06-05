from flask import Flask, render_template, request, redirect
from math import radians, sin, cos, sqrt, atan2, degrees
import requests
import base64

app = Flask(__name__)

# Store points
points = []
current_location = {"lat": 40.7128, "lng": -74.0060}  # Default: New York
zoom = 12

def get_map_image(lat, lng, zoom, points=[]):
    """Get static map image from OpenStreetMap"""
    markers = "|".join([f"{p['lat']},{p['lng']}" for p in points])
    path = "|".join([f"{p['lat']},{p['lng']}" for p in points]) if len(points) > 1 else ""
    
    url = f"https://maps.geoapify.com/v1/staticmap?style=osm-carto"
    url += f"&center=lonlat:{lng},{lat}&zoom={zoom}&width=800&height=600"
    url += f"&marker=lonlat:{lng},{lat};color:red;size:large"  # Center marker
    
    if markers:
        url += f"&marker={markers};color:blue;size:small"
    if path:
        url += f"&path={path};color:green;width:3"
    
    # Add your Geoapify API key (free tier available)
    url += "&apiKey=YOUR_API_KEY"
    
    try:
        response = requests.get(url)
        return base64.b64encode(response.content).decode('utf-8')
    except:
        return None

def calculate_relative_position(p1, p2):
    # Haversine formula implementation here
    # (Same as previous examples)
    return {"distance": 100, "bearing": 45, "direction": "NE"}  # Simplified for example

@app.route('/', methods=['GET', 'POST'])
def index():
    global points, current_location, zoom
    
    if request.method == 'POST':
        if 'move_map' in request.form:
            dir = request.form['move_map']
            if dir == 'north': current_location['lat'] += 0.1
            elif dir == 'south': current_location['lat'] -= 0.1
            elif dir == 'east': current_location['lng'] += 0.1
            elif dir == 'west': current_location['lng'] -= 0.1
            elif dir == 'zoom_in': zoom = min(18, zoom + 1)
            elif dir == 'zoom_out': zoom = max(0, zoom - 1)
        
        elif 'add_point' in request.form:
            lat = float(request.form['lat'])
            lng = float(request.form['lng'])
            points.append({"lat": lat, "lng": lng})
            current_location = {"lat": lat, "lng": lng}
    
    map_img = get_map_image(current_location['lat'], current_location['lng'], zoom, points)
    return render_template('index.html', 
                         map_img=map_img,
                         points=points,
                         center=current_location,
                         zoom=zoom)

if __name__ == '__main__':
    app.run(debug=True)
