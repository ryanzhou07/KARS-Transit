import folium
from datetime import timedelta
import datetime as dt
import csv
import time
import copy
from threading import Lock
# from folium import plugins as p


# from p import ClickForMarker
from flask import (
    Flask,
    render_template,
    request,
    url_for,
    jsonify,
    Blueprint,
    redirect,
    redirect,
)


# from folium.plugins import ZoomControl
import os
import json
from info.main import getVehicleUpdates, get_trip_updates
import csv


# map boundaries (DO NOT CHANGE)
min_lat, max_lat = 39, 42
min_lon, max_lon = -76, -73.5


# zoom limit so users only see what they need to (DO NOT CHANGE)
min_zoom = 8
max_zoom = 0


# create a map focused on NJT routes, and previous parameters
m = folium.Map(
    max_bounds="True",
    location=(40.414893, -74.384644),
    tiles="cartodb positron",
    control_scale="True",
    min_lat=min_lat,
    max_lat=max_lat,
    min_lon=min_lon,
    max_lon=max_lon,
    min_zoom=min_zoom,
    max_zoom=max_zoom,
    # zoom_control=False,
)
# move zoom control to top right
# m.add_child(ZoomControl(position="topright"))
m.save("map.html")

# create time variable for later
change_time = 0

routeJSONMapping = {
    "1": ["gtfs_schedule_data/Atlantic City.geojson"],
    "2": ["gtfs_schedule_data/Meadowlands Line Geojson.geojson"],
    "3": ["gtfs_schedule_data/Montclair Boonton.geojson"],
    "4": ["gtfs_schedule_data/Montclair Boonton.geojson"],
    "5": ["gtfs_schedule_data/Light Rail.geojson"],
    "6": [
        "gtfs_schedule_data/Bergen County Line.geojson",
        "gtfs_schedule_data/Main Line NJTransit Rail.geojson",
    ],
    "7": [
        "gtfs_schedule_data/Bergen County Line.geojson",
        "gtfs_schedule_data/Main Line NJTransit Rail.geojson",
    ],
    "8": ["gtfs_schedule_data/Morristown.geojson"],
    "9": ["gtfs_schedule_data/Gladstone.geojson"],
    "10": [
        "gtfs_schedule_data/Northeast Corridor NJTransit Rail.geojson",
        "gtfs_schedule_data/Northeast Corridor South.geojson",
    ],
    "11": ["gtfs_schedule_data/North Jersey Coast Line.geojson"],
    "12": ["gtfs_schedule_data/North Jersey Coast Line.geojson"],
    "13": ["gtfs_schedule_data/Light Rail.geojson"],
    "14": ["gtfs_schedule_data/Pascack Valley.geojson"],
    "15": ["gtfs_schedule_data/Princeton Shuttle.geojson"],
    "16": ["gtfs_schedule_data/Raritan Valley.geojson"],
    "17": ["gtfs_schedule_data/Light Rail.geojson"],
}

lineCodes = {
    "1": ["AC"],
    "2": ["SL"],
    "3": ["MC"],
    "4": ["MC"],
    "5": ["HB"],
    "6": [
        "BC",
        "ML",
    ],
    "7": [
        "BC",
        "ML",
    ],
    "8": ["ME"],
    "9": ["GL"],
    "10": [
        "NE",
        "NE",
    ],
    "11": ["NC"],
    "12": ["NC"],
    "13": ["NS"],
    "14": ["PV"],
    "15": ["PRIN"],
    "16": ["RV"],
    "17": ["RL"],
}

def save_map():
    
        # Create a copy of the map before rendering
    map_copy = copy.deepcopy(m)
    return map_copy.get_root().render()


def displayRoute(route_id):
    """Displays trains and stops only for the specified route."""
    # Load vehicle updates
    train_data = getVehicleUpdates("638656265526235070")
    timeNow = dt.datetime.now()

    markedStations = []

    # Display train markers on the map for trains on the specified route
    for entity in train_data.get("entity", []):
        vehicle = entity.get("vehicle", {})
        trip = vehicle.get("trip", {})

        if trip.get("routeId") == route_id:
            position = vehicle.get("position", {})
            lat, lon = position.get("latitude"), position.get("longitude")
            train_id = vehicle.get("vehicle").get("id")
            occupancy = "Many Seats Available"

            # Add train marker
            folium.CircleMarker(
                location=[lat, lon],
                icon=folium.Icon(icon="train"),
                color="red",
                fill=True,
                popup=f"Route ID: {trip.get('routeId')}<br>Train ID: {train_id}<br>Occupancy: {occupancy}",
            ).add_to(m)

    line_code = lineCodes.get(route_id, [])
    if route_id == 5 or route_id == 13 or route_id == 17:
        with open(
            "gtfs_schedule_data/NJTransit_Light_Rail_Stations_7467717369539091415.csv",
            "r",
        ) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row["LINE_CODE"] == line_code:
                    lat = float(row["LATITUDE"])
                    lon = float(row["LONGITUDE"])
                    station_name = row["STATION"]
                    markedStations.append({"name": station_name, "lat": lat, "lon": lon})
                    
                folium.Marker(
                    location=[lat, lon],
                    icon=folium.Icon(color="blue", icon="info-sign"),
                    popup=f"Station: {station_name}",
                ).add_to(m)

    else:
        with open(
            "gtfs_schedule_data/NJTransit_Rail_Stations_-7781331129518987903.csv", "r"
        ) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                for code in line_code:
                    if code in row["RAIL_SERVICE"].split(", "):
                        # if code in row["LINE_CODE"]:
                        lat = float(row["LATITUDE"])
                        lon = float(row["LONGITUDE"])
                        station_name = row["STATION_ID"]
                        markedStations.append(
                            {"name": station_name, "lat": lat, "lon": lon}
                        )
                        
                        folium.Marker(
                            location=[lat, lon],
                            icon=folium.Icon(color="blue", icon="info-sign"),
                            popup=f"Station: {station_name}",
                        ).add_to(m)

    trip_update_data = get_trip_updates("638656265526235070")

    for station in markedStations:
        for entity in trip_update_data.get("entity", []):
            trip_update = entity.get("tripUpdate", {})
            if trip_update.get("trip", {}).get("routeId") == route_id:
                for stop_time_update in trip_update.get("stopTimeUpdate", []):
                    stop_id = stop_time_update.get("stopId")
                    departure_time = stop_time_update.get("departure", {}).get("time")

                    change_time = timedelta(
                        seconds=(float)(departure_time)
                        - time.time()
                        + stop_time_update.get("departure", {}).get("delay")
                    )
                    timeNow = timeNow + change_time

                    folium.Marker(
                        location=[
                            station.get("lat"),
                            station.get("lon"),
                        ],
                        icon=folium.Icon(color="blue", icon="info-sign"),
                        popup=f"Station: {station.get('name')}\nETA Next Train: "
                        + timeNow.strftime("%H:%M"),
                    ).add_to(m)


def drawRoute(route_id):
    jsonFiles = routeJSONMapping[route_id]
    for jsonFile in jsonFiles:
        with open(jsonFile, "r") as f:
            data = json.load(f)
        folium.GeoJson(data, tooltip=f"Route ID: {route_id}").add_to(m)

# clear the map to show a different route
def resetMap():
    global m
    m = folium.Map(
        max_bounds="True",
        location=(40.414893, -74.384644),
        tiles="cartodb positron",
        control_scale="True",
        min_lat=min_lat,
        max_lat=max_lat,
        min_lon=min_lon,
        max_lon=max_lon,
        min_zoom=min_zoom,
        max_zoom=max_zoom,
        # zoom_control=False,
    )
    
