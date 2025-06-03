import time
import gpxpy
import gpxpy.gpx
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

def get_directions_from_google_maps(url):
    # Headless browser setup
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    driver.get(url)

    time.sleep(5)  # Wait for the page to load

    try:
        steps = driver.find_elements(By.CSS_SELECTOR, 'div[class*="directions-mode-step"]')
        coordinates = []

        for step in steps:
            try:
                el = step.find_element(By.TAG_NAME, 'img')
                latlng = el.get_attribute('src')
                if 'center=' in latlng:
                    coord_str = latlng.split('center=')[1].split('&')[0]
                    lat, lon = map(float, coord_str.split('%2C'))
                    coordinates.append((lat, lon))
            except Exception:
                continue

        driver.quit()
        return coordinates
    except Exception as e:
        driver.quit()
        raise e

def create_gpx(coordinates, output_path="output.gpx"):
    gpx = gpxpy.gpx.GPX()

    gpx_track = gpxpy.gpx.GPXTrack()
    gpx.tracks.append(gpx_track)
    gpx_segment = gpxpy.gpx.GPXTrackSegment()
    gpx_track.segments.append(gpx_segment)

    for lat, lon in coordinates:
        gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(lat, lon))

    with open(output_path, 'w') as f:
        f.write(gpx.to_xml())
    print(f"GPX file saved to {output_path}")

if __name__ == "__main__":
    gmaps_url = input("Paste your Google Maps route link: ")
    coords = get_directions_from_google_maps(gmaps_url)
    create_gpx(coords)

