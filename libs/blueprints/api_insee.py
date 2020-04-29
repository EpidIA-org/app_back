from os import environ
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from libs.connectors import STORAGE_CONNECTOR
from libs.utils.mockup_data import get_mockup_data


# TO DO : populate labels and data in formated responses with new routes which fetch multiple days of data

# Formatting response. Each key for labels and data has a list as value, as used in most chart modules.
def format(obj):

    d = {"departement": obj.get("dep"), "labels": [obj.get("jour")], "datasets": [
        {"year_2018": [obj.get("death_2018_day")]},
        {"year_2019": [obj.get("death_2019_day")]},
        {"year_2020": [obj.get("death_2020_day")]}
    ]}

    return d


# Formatting response for multiple days request. Each key for labels and data has a list as value, as used in most chart modules.
def format_multiple_data(obj):

    d = {"departement": obj.get("dep"), "labels": obj.get("jour"), 
        "year_2018": obj.get("death_2018_day"),
        "year_2019": obj.get("death_2019_day"),
        "year_2020": obj.get("death_2020_day")
    }

    return d


api_insee_bp = Blueprint("api_insee_bp", __name__)

# BLUEPRINT FUNCTIONS
is_mockup_activated = bool(int(environ.get("ACTIVATE_MOCKUP", 0)))


def fetch_data(filename_format):
    # Fetch Data from Mockup/Storage
    if is_mockup_activated:
        df = get_mockup_data()
    else:
        file_to_retrieve = STORAGE_CONNECTOR.get_last_filename_version(
            filename_format)
        df = STORAGE_CONNECTOR.open_as_dataframe(file_to_retrieve, sep=";")
    return df


def filter_data(df, area, yyyy, mm, dd, date_query, area_query):
    # Check if Area Code is genuine
    endpoint_has_no_area = (area is None) or (
        area.isdigit() and int(area) == 0)
    if endpoint_has_no_area:
        # if no Area filled, filter only by date
        data = df.query(date_query)
    else:
        # Filter by date and area
        data = df.query(date_query).query(area_query)
    return data.to_dict(orient="records")


# Filter multiple days of data
def filter_multiple_data(df, date_query, area_query):
    data = df.query(date_query).query(area_query)
    data.dropna(inplace=True)  # Keep only rows with complete data
    return data.to_dict(orient="list")


# BLUEPRINT ROUTES

# Get One Day of Data for one or many departement
@api_insee_bp.route("/api/<version>/get/data_insee", methods=["GET"])
@api_insee_bp.route("/api/<version>/get/data_insee/<yyyy>/<mm>/<dd>", methods=["GET"])
@api_insee_bp.route("/api/<version>/get/data_insee/<yyyy>/<mm>/<dd>/<area>", methods=["GET"])
def get_data(yyyy=None, mm=None, dd=None, area=None, version="v1"):
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
    df = fetch_data(
        "formated-2020-04-17_deces_quotidiens_departements_csv.csv")
    # Filter Data with regard to filters
    data = filter_data(
        df,
        area,
        yyyy,
        mm,
        dd,
        date_query=f'jour == "{yyyy}-{mm}-{dd}"',
        area_query=f'dep == "{area}"',
    )
    # Map data
    data = list(map(lambda x: format(x), data))
    return jsonify(data), 200


@api_insee_bp.route("/api/<version>/get/data_insee/all", methods=["GET"])
def get_all_daily_data(area=None, jour=None, version="v1"):
    jour = request.args.get("jour")
    area = request.args.get("area", area)
    delta_day = datetime.fromisoformat(jour) - timedelta(8)

    df = fetch_data(
        "formated-2020-04-17_deces_quotidiens_departements_csv.csv")
    # Filter Data with regard to filters
    data = filter_multiple_data(
        df,
        date_query=f'jour <= "{jour}"',
        area_query=f'dep == "{area}"',
    )
    # Format data

    data = format_multiple_data(data)

    return data, 200

@api_insee_bp.route("/api/<version>/get/data_insee/previous_week", methods=["GET"])
def get_daily_data(area=None, jour=None, version="v1"):
    jour = request.args.get("jour")
    area = request.args.get("area", area)
    delta_day = datetime.fromisoformat(jour) - timedelta(8)

    df = fetch_data(
        "formated-deces-quotidiens-departements-")
    # Filter Data with regard to filters
    data = filter_multiple_data(
        df,
        date_query=f'jour >= "{delta_day}" and jour <= "{jour}"',
        area_query=f'dep == "{area}"',
    )
    # Format data

    data = format_multiple_data(data)

    return data, 200
