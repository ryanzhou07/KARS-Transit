from flask import Flask, render_template, session, url_for, request, redirect, jsonify
from map import save_map, drawRoute, displayRoute, resetMap


app = Flask(__name__)
app.secret_key = "super secret key"



@app.route("/", methods=["GET", "POST"])
def displayMap():
    if request.method == "POST":
        resetMap()
        selected_option = request.form["route"]
        session['selected_option'] = selected_option
    else:
        try:
            selected_option = session['selected_option']
        except KeyError:
            selected_option = "1"
        
    drawRoute(selected_option)
    displayRoute(selected_option)


    map_html = save_map()
    return render_template("base.html", map_html=map_html)

if __name__ == "__main__":
    app.run(debug=True)
