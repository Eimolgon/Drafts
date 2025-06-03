import gpxpy
import gpxpy.gpx
from geopy.distance import geodesic

def load_gpx(filename):
    with open(filename, 'r') as f:
        gpx = gpxpy.parse(f)
    return gpx

def generate_instructions(gpx):
    instructions = []
    for track in gpx.tracks:
        for segment in track.segments:
            prev_point = None
            total_distance = 0.0
            for i, point in enumerate(segment.points):
                if prev_point:
                    dist = geodesic(
                        (prev_point.latitude, prev_point.longitude),
                        (point.latitude, point.longitude)
                    ).meters
                    total_distance += dist
                    instructions.append(f"Step {i}: Go {dist:.0f} meters to ({point.latitude:.5f}, {point.longitude:.5f})")
                else:
                    instructions.append(f"Start at ({point.latitude:.5f}, {point.longitude:.5f})")
                prev_point = point
    return instructions

if __name__ == "__main__":
    gpx = load_gpx("output.gpx")
    instructions = generate_instructions(gpx)
    print("\nRoute Instructions:\n")
    for instr in instructions:
        print(instr)

