# packages
from flask import Flask, render_template, request
import requests
import csv
from user_agents import parse
from datetime import datetime
import base64
import os


# web app instance
application = Flask(__name__)

# Directory to save images
UPLOAD_FOLDER = "captured_images"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# function to check IP information


def get_ip_based_geolocation(ip):
    response = requests.get(f'https://ipinfo.io/{ip}/json')
    data = response.json()
    # print(data)

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


def parse_user_agent(user_agent):
    ua = parse(user_agent)
    return [f"{ua.device.family}", f"{ua.os.family} {ua.os.version_string}", f"{ua.browser.family} {ua.browser.version_string}"]


def client_info():
    user_agent = request.headers.get("User-Agent", "Unknown User-Agent")
    parsed_info = parse_user_agent(user_agent)
    return parsed_info


def client_ip():
    return f"Device IP: {request.remote_addr}"


def show_environ():
    return f"Server environment: {request.environ}"

# root route


@application.route("/")
def index_html():
    location_info = {}
    for i in range(len(request.access_route)):
        location_info[i] = get_ip_based_geolocation(request.access_route[i])
        i += 1

    # Append a new line with IP info
    for i in range(len(location_info)):
        with open('ip_visitors.csv', mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Session start", datetime.now()])
            # Additional data row
            writer.writerow(location_info[i].items())

    # Append a new line with device os info
    device_os_browser = client_info()
    with open('ip_visitors.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([
            f"Device : {device_os_browser[0]}",
            f"Operating System : {device_os_browser[1]}",
            f"Browser : {device_os_browser[2]}",
            f"request.remote_addr: {client_ip()}",
        ])

    user_environment = show_environ()
    with open('ip_visitors.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        # Additional data row
        writer.writerow([user_environment])
        writer.writerow(["Session end", datetime.now()])

    return render_template("index.html")


@application.route("/camera")
def camera_html():
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
    # application.run(host="192.168.0.164", port=8080,
    #                ssl_context='adhoc', debug=True)
    # application.run(host="127.0.0.1", port=8080, debug=True)
    # start web server aws
    # application.run(host="0.0.0.0")
