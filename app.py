#Dependencies
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

from flask import Flask, jsonify

import datetime as dt
import numpy as np
import pandas as pd

# Set up engine
engine = create_engine("sqlite:///hawaii.sqlite")

Base = automap_base()
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

# Flask Routes and code

app = Flask(__name__)

@app.route("/")
def welcome():
    """List all available api routes."""
    return(
        f"Hawaii Weather API<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Precitpitation Data for the Last Year"""
    session = Session(engine)
    last_day = session.query(Measurement.date, Measurement.prcp).order_by(Measurement.date.desc()).first()[0]
    last_year = str(dt.datetime.strptime(last_day, "%Y-%m-%d") - dt.timedelta(days=365))

    precipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= last_year, Measurement.date <= last_day).\
        order_by(Measurement.date).all()
    prcp_dict = {date: prcp for date, prcp in precipitation}
    return jsonify(prcp_dict)




if __name__ == '__main__':
    app.run(debug=True)
