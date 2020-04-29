from os import environ
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from libs.utils.formatter import format_v1, format_v2
from libs.utils.mockup_data import get_mockup_data

api_bp = Blueprint("api_bp", __name__)

# BLUEPRINT FUNCTIONS
is_mockup_activated = bool(int(environ.get("ACTIVATE_MOCKUP", 0)))
if not(is_mockup_activated):
    from libs.connectors import STORAGE_CONNECTOR


def fetch_data(filename_format,simu=False):
    # Fetch Data from Mockup/Storage
    if is_mockup_activated:
        df = get_mockup_data(simu)
    else:
        file_to_retrieve = STORAGE_CONNECTOR.get_last_filename_version(filename_format)
        df = STORAGE_CONNECTOR.open_as_dataframe(file_to_retrieve, sep=";")
    return df


def filter_data(df, area, yyyy, mm, dd, date_query, area_query):
    # Check if Area Code is genuine
    endpoint_has_no_area = (area is None) or (area.isdigit() and int(area) == 0)
    if endpoint_has_no_area:
        # if no Area filled, filter only by date
        data = df.query(date_query)
    else:
        # Filter by date and area
        data = df.query(date_query).query(area_query)
    return data.to_dict(orient="records")


# BLUEPRINT ROUTES

# Get One Day of Data for one departement
@api_bp.route("/api/<version>/get/data", methods=["GET"])
@api_bp.route("/api/<version>/get/data/<yyyy>/<mm>/<dd>", methods=["GET"])
@api_bp.route("/api/<version>/get/data/<yyyy>/<mm>/<dd>/<area>", methods=["GET"])
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
    df = fetch_data(filename_format="formated-covid-data-from-datagouvfr-")
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
    # Map data accordingly
    data = list(map(lambda x: (format_v1 if version == "v1" else format_v2)(x), data))
    return jsonify(data), 200


# Get X Days of Data for one departement
@api_bp.route("/api/<version>/get/until", methods=["GET"])
@api_bp.route("/api/<version>/get/until/<yyyy>/<mm>/<dd>", methods=["GET"])
@api_bp.route("/api/<version>/get/until/<yyyy>/<mm>/<dd>/<area>", methods=["GET"])
def get_until(yyyy=None, mm=None, dd=None, area=None, version="v1"):
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
    df = fetch_data(filename_format="formated-covid-data-from-datagouvfr-")
    # Compute Start Date
    N_DAYS = 20
    from_date = (
        datetime.strptime(f"{yyyy}-{mm}-{dd}", "%Y-%m-%d") - timedelta(days=N_DAYS)
    ).strftime("%Y-%m-%d")
    # Filter Data with regard to filters
    data = filter_data(
        df,
        area,
        yyyy,
        mm,
        dd,
        date_query=f'"{from_date}" < jour <= "{yyyy}-{mm}-{dd}"',
        area_query=f'dep == "{area}"',
    )
    # Map data accordingly
    data = list(map(lambda x: (format_v1 if version == "v1" else format_v2)(x), data))
    return jsonify(data), 200


@api_bp.route("/api/<version>/get/country/until", methods=["GET"])
@api_bp.route("/api/<version>/get/country/until/<yyyy>/<mm>/<dd>", methods=["GET"])
def get_country_until(yyyy=None, mm=None, dd=None, version="v1"):
    # Get the request arguments
    yyyy = request.args.get("yyyy", yyyy)
    mm = request.args.get("mm", mm)
    dd = request.args.get("dd", dd)
    # Check if date is not sampled genuinely
    endpoint_has_no_date = (yyyy is None) or (mm is None) or (dd is None)
    if endpoint_has_no_date:
        # Return Error 400 BAD REQUEST
        return jsonify({"message": "error", "type": "bad_request"}), 400
    # Fetch Data from Mockup/Storage
    df = fetch_data(filename_format="formated-covid-data-from-datagouvfr-")
    # Compute Start Date
    N_DAYS = 20
    from_date = (
        datetime.strptime(f"{yyyy}-{mm}-{dd}", "%Y-%m-%d") - timedelta(days=N_DAYS)
    ).strftime("%Y-%m-%d")
    # Filter Data with regard to filters
    data = (
        df.query(f'"{from_date}" < jour <= "{yyyy}-{mm}-{dd}"')
        .drop(columns=["dep"])
        .groupby(["jour"])
        .sum()
        .reset_index()
        .assign(dep="00")
        .to_dict(orient="records")
    )
    # Map data accordingly
    data = list(map(lambda x: (format_v1 if version == "v1" else format_v2)(x), data))
    return jsonify(data), 200


# Get Last Update from data sources
@api_bp.route("/get/last_updated", methods=["GET"])
def get_last_updated():
    df = fetch_data(filename_format="formated-covid-data-from-datagouvfr-")
    last_updated = df.jour.max()
    return jsonify({"last_updated": last_updated}), 200

# Get hospital capacity
@api_bp.route("/get/<version>/capacity", methods=["get"])
@api_bp.route("/get/<version>/capacity/<yyyy>", methods=["get"])
def get_capacity(yyyy="2018", version="v1"):
    # Get the request arguments
    yyyy = request.args.get("yyyy", yyyy)

    file_to_retrieve = STORAGE_CONNECTOR.get_last_filename_version("capacite_hopitaux")
    df = STORAGE_CONNECTOR.open_as_dataframe(file_to_retrieve)
    # HotFix for global country
    df.code = df.code.str.replace('FR', '00')
    cols = ["code", "libelle"]
    cols += [c for c in df.columns if c.endswith(f"{yyyy}")]

    df = df[cols]
    df = df.rename(columns={c: c.strip(f"_{yyyy}") for c in df.columns})

    return jsonify(df.to_dict(orient="records")), 200