# FOR MOCKUP PURPOSE ONLY
import os
import pandas as pd
import random
from datetime import datetime, timedelta
import functools

def generate_fake_data_for_x_days(date, dpts, days):
    return functools.reduce(
        lambda a, b: a + b,
        [
            generate_fake_data(
                (datetime.strptime(date, "%Y-%m-%d") - timedelta(days=delta)).strftime(
                    "%Y-%m-%d"
                ),
                dpts,
            )
            for delta in range(days)
        ],
    )


def generate_fake_data(date, dpts):
    return [
        {
            "date": date,
            "dpts": {
                dpts.split(" - ")[0]: {
                    "departement": dpts,
                    "data": {
                        "total": {
                            "cases": random.randint(1000, 10000),
                            "recoveries": random.randint(100, 300),
                            "deaths": random.randint(100, 300),
                        },
                        "new": {
                            "cases": random.randint(1, 100),
                            "recoveries": random.randint(10, 100),
                            "deaths": random.randint(10, 100),
                        },
                        "current": {
                            "cases": random.randint(1, 100),
                            "hospital": random.randint(1, 100),
                            "critical": random.randint(1, 100),
                        },
                    },
                }
            },
        }
    ]


def get_mockup_data(simu_data=False):
    if simu_data:
        return pd.read_csv(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'model_predictions.csv'), sep=';')
    else:
        return pd.read_csv(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'mockup_data.csv'), sep=';')