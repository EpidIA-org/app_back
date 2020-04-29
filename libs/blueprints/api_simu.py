from flask import Blueprint, jsonify
from libs.utils.formatter import format_simu
from libs.blueprints.api import fetch_data

api_simu = Blueprint("api_simu", __name__)

# BLUEPRINT ROUTES

# Get simulation
@api_simu.route("/api/<version>/simu", methods=["GET"])
def get_data(version="v1"):
    df = fetch_data(filename_format="formated-simu-", simu=True)
    # Map data accordingly
    list_by_area = []
    for area in df['area'].unique():
        data = (
            df.query(f'area == "{area}"')
            .drop(columns=["area"])
            .to_dict(orient="records")        
        )
        list_by_area.append({"area": str(area),"series": list(map(format_simu, data))})
    return jsonify(list_by_area), 200
