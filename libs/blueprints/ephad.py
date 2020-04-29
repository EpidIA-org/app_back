from os import environ
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from libs.connectors import STORAGE_CONNECTOR
from libs.utils.formatter import format_v1, format_v2
from libs.utils.mockup_data import get_mockup_data

ephad_bp = Blueprint("ephad_bp", __name__)

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


def filter_data(df, date_query):
    # Filter by date and area
    data = df.query(date_query)
    return data.to_dict(orient="records")


@ephad_bp.route("/api/get/data/ehpad/<yyyy>/<mm>/<dd>", methods=["GET"])
def get_data_ehpad(yyyy=None, mm=None, dd=None):
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
    df = fetch_data(filename_format="covid-19-with-ephad_")
    df['jour'] = df['jour'].apply(lambda x: '-'.join(x.split('/')[::-1]))
    df = df[df['dc ehpad'].notnull()][['jour', 'dc ehpad', 'dc ehpad quot']]
    df.columns = ['jour', 'total_deaths_ehpad', 'new_deaths_ehpad']
    # Filter Data with regard to filters
    data = filter_data(
        df,
        date_query=f'jour == "{yyyy}-{mm}-{dd}"'
    )
    return jsonify(data), 200

@ephad_bp.route("/api/get/until/data/ehpad/<yyyy>/<mm>/<dd>", methods=["GET"])
def get_until_ehpad(yyyy=None, mm=None, dd=None):
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
    df = fetch_data(filename_format="covid-19-with-ephad_")
    df['jour'] = df['jour'].apply(lambda x: '-'.join(x.split('/')[::-1]))
    df = df[df['dc ehpad'].notnull()][['jour', 'dc ehpad', 'dc ehpad quot']]
    df.columns = ['jour', 'total_deaths_ehpad', 'new_deaths_ehpad']
    # Compute Start Date
    N_DAYS = 8
    from_date = (
        datetime.strptime(f"{yyyy}-{mm}-{dd}", "%Y-%m-%d") - timedelta(days=N_DAYS)
    ).strftime("%Y-%m-%d")
    # Filter Data with regard to filters
    data = filter_data(
        df,
        date_query=f'"{from_date}" < jour <= "{yyyy}-{mm}-{dd}"',
    )
    return jsonify(data), 200


# Get Last Update from data sources
@ephad_bp.route("/get/last_updated/ehpad", methods=["GET"])
def get_last_updated_ehpad():
    df = fetch_data(filename_format="covid-19-with-ephad_")
    last_updated = df['jour'].apply(lambda x: '-'.join(x.split('/')[::-1])).max()
    return jsonify({"last_updated": last_updated}), 200