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

#function to get start and end dates and tmin, tmax, and tavg for laste two api routns
def calc_temps(start_date, end_date):
    """Tmax, Tmin, and Tavg for list of dates
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
    
    Returns: Tmzx, Tmin, Tavg
    """
    return session.query(func.max(Measurement.tobs), func.min(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()


@app.route("/")
def welcome():
    """List all available api routes."""
    return(
        f"Hawaii Weather API<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"Enter start date at end of address to get temps for range:<br/>"
        f"/api/v1.0/startlast/<start><br/>"
        f"Enter start and end date at end of address to get temps for range:<br/>"
        f"/api/v1.0/startend/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Precitpitation Data for the Last Year"""
    last_day = session.query(Measurement.date, Measurement.prcp).order_by(Measurement.date.desc()).first()[0]
    last_year = str(dt.datetime.strptime(last_day, "%Y-%m-%d") - dt.timedelta(days=366))

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

@app.route("/api/v1.0/tobs")
def tobs():
    """Temperature Observations for the Last Year"""
    last_day = session.query(Measurement.date, Measurement.prcp).order_by(Measurement.date.desc()).first()[0]
    last_year = str(dt.datetime.strptime(last_day, "%Y-%m-%d") - dt.timedelta(days=366))

    tobs_query = session.query(Measurement.date, Measurement.station, Measurement.tobs).\
        filter(Measurement.date >= last_year, Measurement.date <= last_day).\
        order_by(Measurement.date).all()

    tobs_list = []
    for tlist in tobs_query:
        tobs_dict = {}
        tobs_dict['date'] = tlist.date
        tobs_dict['station'] = tlist.station
        tobs_dict['tobs'] = tlist.tobs
        tobs_list.append(tobs_dict)
    
    return jsonify(tobs_list)

@app.route("/api/v1.0/startlast/<start>")

def start(start):
    """Calculates Tmin Tmax and Tavg for dates after start date"""
    last_date_query = session.query(func.max(func.strftime("%Y-%m-%d", Measurement.date))).all()
    last_date = last_date_query[0][0]

    temps = calc_temps(start, last_date)

    temp_list = []
    date_dict = {'start_date': start, 'end_date': last_date}
    temp_list.append(date_dict)
    temp_list.append({'Tmax': temps[0][0]})
    temp_list.append({'Tmin': temps[0][1]})
    temp_list.append({'Tavg': temps[0][2]})

    return jsonify(temp_list)

@app.route("/api/v1.0/startend/<start>/<end>")
def start_end(start, end):
    """Calculates Tmax, Tmin, and Tavg between two dates"""
    temps = calc_temps(start, end)

    temp_list = []
    date_dict = {'start_date': start, 'end_date': end}
    temp_list.append(date_dict)
    temp_list.append({'Tmax': temps[0][0]})
    temp_list.append({'Tmin': temps[0][1]})
    temp_list.append({'Tavg': temps[0][2]})

    return jsonify(temp_list)

if __name__ == '__main__':
    app.run(debug=True)
