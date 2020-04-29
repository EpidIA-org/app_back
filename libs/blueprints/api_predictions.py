from os import environ
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from libs.connectors import STORAGE_CONNECTOR
from libs.utils.formatter import format_v1, format_v2
from libs.utils.mockup_data import get_mockup_data

predictor_bp = Blueprint("predictor_bp", __name__)
filename_base = "formated-covid-predictions-"

# BLUEPRINT FUNCTIONS
is_mockup_activated = bool(int(environ.get("ACTIVATE_MOCKUP", 0)))

def fetch_data(filename_format):
    # Fetch Data from Mockup/Storage
    if is_mockup_activated:
        df = get_mockup_data()
    else:
        file_to_retrieve = STORAGE_CONNECTOR.get_last_filename_version(filename_format)
        df = STORAGE_CONNECTOR.open_as_dataframe(file_to_retrieve, sep=";")
    return df


def filter_data(df, area, date_query, area_query):
    # Check if Area Code is genuine
    endpoint_has_no_area = (area is None) or (area.isdigit() and int(area) == 0)
    if endpoint_has_no_area:
        # if no Area filled, filter only by date
        data = df.query(date_query)
    else:
        # Filter by date and area
        data = df.query(date_query).query(area_query)
    return data.to_dict(orient="records")


@predictor_bp.route("/api/get/from/predictor/<yyyy>/<mm>/<dd>/<area>", methods=["GET"])
def get_from_predictor(yyyy=None, mm=None, dd=None, area=None):
    # Get the request arguments
    yyyy = request.args.get("yyyy", yyyy)
    mm = request.args.get("mm", mm)
    dd = request.args.get("dd", dd)
    area = request.args.get("area", area)
    # Check if date is not sampled genuinely
    endpoint_has_no_date = (yyyy is None) or (mm is None) or (dd is None)
    if endpoint_has_no_date:
        # Return Error 400 BAD REQUEST
        return jsonify({"message": "error", "type": "bad_request"}), 400

    # Fetch Data from Mockup/Storage
    df = fetch_data(filename_format=filename_base)
    df['jour'] = df['ds']
    df['new_death'] = df['new_death_yhat']
    df['new_hosp'] = df['new_hosp_yhat']
    df = df[['jour', 'new_death', 'new_hosp', 'area']]
    df['new_death'] = df['new_death'].apply(lambda x: int(x)).apply(lambda x: x if x >= 0 else 0)
    df['new_hosp'] = df['new_hosp'].apply(lambda x: int(x)).apply(lambda x: x if x >=    0 else 0)
    # Compute Start Date
    N_DAYS = 8
    to_date = (
        datetime.strptime(f"{yyyy}-{mm}-{dd}", "%Y-%m-%d") + timedelta(days=N_DAYS)
    ).strftime("%Y-%m-%d")
    # Filter Data with regard to filters
    data = filter_data(
        df,
        area,
        date_query=f'"{yyyy}-{mm}-{dd}" <= jour <= "{to_date}"',
        area_query=f'area == "{area}"',
    )
    return jsonify(data), 200


# Get Last Update from data sources
@predictor_bp.route("/get/last_updated/predictor", methods=["GET"])
def get_last_updated_predictor():
    df = fetch_data(filename_format=filename_base)
    last_updated = df['ds'].max()
    return jsonify({"last_updated": last_updated}), 200