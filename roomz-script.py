# app.py
from flask import Flask, request, jsonify
from auth.roomz_login import login_to_roomz
from services.parking_reserver import reserve_parking

app = Flask(__name__)


@app.route("/reserve-parking", methods=["POST"])
def reserve():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    building = data.get("building", "BG - Plovdiv")
    subarea = data.get("subarea", "Parking Spaces Plovdiv")
    spot_prefix = data.get("spot_prefix", "PB")

    try:
        driver = login_to_roomz(email, password)
        result = reserve_parking(driver, building, subarea, spot_prefix)
        driver.quit()
        return jsonify({"status": "success", "details": result}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
