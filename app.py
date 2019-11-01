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

session = Session(engine)

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
    last_day = session.query(Measurement.date, Measurement.prcp).order_by(Measurement.date.desc()).first()[0]
    last_year = str(dt.datetime.strptime(last_day, "%Y-%m-%d") - dt.timedelta(days=365))

    precipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= last_year, Measurement.date <= last_day).\
        order_by(Measurement.date).all()
    prcp_dict = {date: prcp for date, prcp in precipitation}
    return jsonify(prcp_dict)

@app.route("/api/v1.0/stations")
def stations():
    """List of Weather Stations in Hawaii"""
    station_query = session.query(Station).all()
    station_list = []
    for station in station_query:
        station_dict = {}
        station_dict['id'] = station.id
        station_dict['station'] = station.station
        station_dict['name'] = station.name
        station_dict['latitude'] = station.latitude
        station_dict['longitude'] = station.longitude
        station_dict['elevation'] = station.elevation
        station_list.append(station_dict)
    
    return jsonify(station_list)





if __name__ == '__main__':
    app.run(debug=True)
