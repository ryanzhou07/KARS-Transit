from flask import Flask, render_template, session, request
from flask_socketio import SocketIO
from map import save_map, drawRoute, displayRoute, resetMap

app = Flask(__name__)
app.secret_key = "super secret key"
socketio = SocketIO(app)

@app.route("/", methods=["GET", "POST"])
def displayMap():
    if request.method == "POST":
        resetMap()
        selected_option = request.form["route"]
        session['selected_option'] = selected_option
        socketio.emit('route_changed', {'route': selected_option})  # Notify the client about the change
        # Start background task to update the map
        socketio.start_background_task(updateMap, selected_option)
    else:
        selected_option = session.get('selected_option', "1")
    
    drawRoute(selected_option)
    displayRoute(selected_option)
    map_html = save_map()
    
    return render_template("base.html", map_html=map_html)

# client connects to the server 
@socketio.on('connect')
def handle_connect():
    print('connected')

#client disconnects from the server
@socketio.on('disconnect')
def handle_disconnect():
    print('disconnected')


@socketio.on('start_map_updates')
def handle_start_map_updates(selected_route):
    session['selected_option'] = selected_route
    print(f'Starting updates for route: {selected_route}')
    # Start background task with the selected route
    socketio.start_background_task(updateMap, selected_route)
    
def updateMap(selected_option):
    while True:
        socketio.sleep(10)
        # Emit the updated map
        drawRoute(selected_option)
        displayRoute(selected_option)
        map_html = save_map()  # Assuming this function returns the updated map
        socketio.emit('map', {'map': map_html})

if __name__ == "__main__":
    socketio.run(app, debug=True)
