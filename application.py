# packages
from flask import Flask, render_template, request
import requests
import csv
import base64
import os
from datetime import datetime

# web app instance
application = Flask(__name__)

# Directory to save images
UPLOAD_FOLDER = "captured_images"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# function to check IP information


def get_ip_based_geolocation(ip):
    response = requests.get(f'https://ipinfo.io/{ip}/json')
    data = response.json()
    print(data)

    return {
        "ip": data.get("ip"),
        "city": data.get("city"),
        "region": data.get("region"),
        "country": data.get("country"),
        "loc": data.get("loc"),  # Latitude and Longitude in "lat,lon" format
        "organization": data.get("org"),
        "postal": data.get("postal"),
        "timezone": data.get("timezone"),
        "privacy": data.get("privacy")
    }

# root route


@application.route("/")
def index_html():
    location_info = {}
    for i in range(len(request.access_route)):
        location_info[i] = get_ip_based_geolocation(request.access_route[i])
        i += 1

    # Append a new line
    for i in range(len(location_info)):
        with open('ip_visitors.csv', mode='a', newline='') as file:
            writer = csv.writer(file)
            # Additional data row
            writer.writerow(location_info[i].items())

    return render_template("index.html")


@application.route("/camera")
def camera_html():
    location_info = {}
    for i in range(len(request.access_route)):
        location_info[i] = get_ip_based_geolocation(request.access_route[i])
        i += 1

    # Append a new line
    for i in range(len(location_info)):
        with open('ip_visitors.csv', mode='a', newline='') as file:
            writer = csv.writer(file)
            # Additional data row
            writer.writerow(location_info[i].items())
    return render_template("camera.html")


@application.route('/upload', methods=['POST'])
def upload_image():
    try:
        # Get the base64-encoded image data from the request
        data = request.json.get("image_data")
        if not data:
            return {"error": "No image data provided"}, 400

        # Decode the base64 image
        image_data = base64.b64decode(data.split(",")[1])

        # Generate a unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = f"image_{timestamp}.png"
        filepath = os.path.join(UPLOAD_FOLDER, filename)

        # Save the image to the server
        with open(filepath, "wb") as f:
            f.write(image_data)

        return {"message": f"Image saved as {filename}"}, 200
    except Exception as e:
        return {"error": str(e)}, 500


# main loop
# if __name__ == "__main__":
    # start web server localhost
    # application.run(host="192.168.0.164", port=5000, debug=True)
    # application.run(host="127.0.0.1", port=8080, debug=True)
    # start web server aws
    # application.run(host="0.0.0.0", port=8000)
