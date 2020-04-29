# Used to format JSON in get/data and get/until route
# DEPRECATED FORMAT
def format_v1(obj):
    dpts_data = {
        "total": {
            "recoveries": obj.get("total_returned_home"),
            "critical": obj.get("cumulative_critical"),
            "deaths": obj.get("total_death"),
            "hospital": obj.get("cumulative_hosp"),
        },
        "new": {
            "hospital": obj.get("new_hosp"),
            "critical": obj.get("new_critical"),
            "recoveries": obj.get("new_returned_home"),
            "deaths": obj.get("new_death"),
        },
        "current": {
            "hospital": obj.get("current_hosp"),
            "critical": obj.get("current_critical"),
        },
        "men": {
            "current": {
                "hospital": obj.get("current_men_hosp"),
                "critical": obj.get("current_men_critical"),
            },
            "total": {
                "recoveries": obj.get("total_men_returned_home"),
                "deaths": obj.get("total_men_death"),
            },
        },
        "women": {
            "current": {
                "hospital": obj.get("current_women_hosp"),
                "critical": obj.get("current_women_critical"),
            },
            "total": {
                "recoveries": obj.get("total_women_returned_home"),
                "deaths": obj.get("total_women_death"),
            },
        },
    }
    d = {
        "date": obj.get("jour"),
        "dpts": {obj.get("dep"): {"departement": obj.get("dep"), "data": dpts_data}},
    }
    return d

# Used to format JSON in get/data and get/until route
# Format expected in front application
def format_v2(obj):
    dpts_data = {
        "total": {
            "recoveries": obj.get("total_returned_home"),
            "critical": obj.get("cumulative_critical"),
            "deaths": obj.get("total_death"),
            "hospital": obj.get("cumulative_hosp"),
        },
        "new": {
            "hospital": obj.get("new_hosp"),
            "critical": obj.get("new_critical"),
            "recoveries": obj.get("new_returned_home"),
            "deaths": obj.get("new_death"),
        },
        "current": {
            "hospital": obj.get("current_hosp"),
            "critical": obj.get("current_critical"),
        },
        "men": {
            "current": {
                "hospital": obj.get("current_men_hosp"),
                "critical": obj.get("current_men_critical"),
            },
            "total": {
                "recoveries": obj.get("total_men_returned_home"),
                "deaths": obj.get("total_men_death"),
            },
        },
        "women": {
            "current": {
                "hospital": obj.get("current_women_hosp"),
                "critical": obj.get("current_women_critical"),
            },
            "total": {
                "recoveries": obj.get("total_women_returned_home"),
                "deaths": obj.get("total_women_death"),
            },
        },
    }
    d = {"date": obj.get("jour"), "area": obj.get("dep"), "data": dpts_data}
    return d


def format_simu(obj):
    date_data = obj.get('date')
    del obj["date"]

    return {"data": obj, "date": date_data}
