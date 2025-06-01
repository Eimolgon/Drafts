import requests

url = "https://api.openrouteservice.org/v2/directions/cycling-regular/geojson"
headers = {
    "Authorization": "5b3ce3597851110001cf6248b820b778a0974d0e8430fc6d7c921bf9",
    "Content-Type": "application/json"
}
body = {
    "coordinates": [[8.681495,49.41461], [8.687872,49.420318]]
}

response = requests.post(url, json=body, headers=headers)
print(response.status_code)
print(response.text)

