from flask import Flask, render_template, url_for, request, redirect, jsonify

# from map.py import m

# import folium
# import os

# NJ_TRANSIT_API_URL = "https://testraildata.njtransit.com/api/GTFSRT/isValidToken'%20%5C%20-H%20'accept:%20text/plain"


import requests
from google.transit import gtfs_realtime_pb2
from google.protobuf.json_format import MessageToJson
import json
import zipfile
import io
import os

API_KEY = "Enter API KEY"


# Function to get and convert GTFS-RT data


# Function to get and convert GTFS-RT data
def get_trip_updates(token):
    url = "https://testraildata.njtransit.com/api/GTFSRT/getTripUpdates"
    files = {"token": (None, token)}
    response = requests.post(url, files=files)

    if response.status_code == 200:
        # Parse Protocol Buffer data
        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(response.content)

        # Convert FeedMessage to JSON
        feed_json = MessageToJson(feed)
        return json.loads(feed_json)  # Return JSON object
    else:
        print("Failed to fetch data:", response.status_code)
        print("Response content:", response.content.decode())
        return None


def download_gtfs_schedule_data(token):
    url = "https://testraildata.njtransit.com/api/GTFSRT/getGTFS"
    files = {"token": (None, token)}
    response = requests.post(url, files=files)

    if response.status_code == 200:
        # Open the ZIP file from the response content
        with zipfile.ZipFile(io.BytesIO(response.content)) as the_zip:
            # Extract each file to the current directory or a specific path
            the_zip.extractall("gtfs_schedule_data")
            print("GTFS data downloaded and extracted successfully.")
    else:
        print("Failed to download GTFS data:", response.status_code)


# Replace 'your_token_here' with the actual API token
# download_gtfs_schedule_data(API_KEY)

# Replace 'your_token_here' with your actual token
# trip_updates_json = get_trip_updates(API_KEY)  # Place your API token here


def getVehicleUpdates(token):
    url = "https://testraildata.njtransit.com/api/GTFSRT/getVehiclePositions"
    files = {"token": (None, token)}
    response = requests.post(url, files=files)

    if response.status_code == 200:
        # Parse Protocol Buffer data
        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(response.content)

        # Convert FeedMessage to JSON
        feed_json = MessageToJson(feed)
        return json.loads(feed_json)  # Return JSON object
    else:
        print("Failed to fetch data:", response.status_code)
        return None


# Replace 'your_token_here' with your actual token
# trip_updates_json = get_trip_updates("your_token_here")  # Place your API token here
# print(trip_updates_json)

# Replace 'your_token_here' with your actual token
