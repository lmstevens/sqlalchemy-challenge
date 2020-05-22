# 1. import Flask
from flask import Flask, jsonify

import numpy as np
import pandas as pd

import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station
# 2. Create an app, being sure to pass __name__
app = Flask(__name__)


# 3. Define what to do when a user hits the index route
@app.route("/")
def home():
    return (
        "Welcome to the SQLAlchemy Climate App API!<br/>"
        "Available Routes:<br/>"
        "/api/v1.0/precipitation<br/>"
        "/api/v1.0/stations<br/>"
        "/api/v1.0/tobs<br/>"
        "/api/v1.0/<start><br/>"
        "/api/v1.0/<start>/<end>"
    )


# 4. Define what to do when a user hits the /about route
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(bind=engine)
    newest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    newest_date_string=newest_date[0] 
    date_time_obj = dt.datetime.strptime(newest_date_string, '%Y-%m-%d')
    year_ago = date_time_obj - dt.timedelta(days=365)
    year_ago_string = year_ago.strftime('%Y-%m-%d')
    precip_data=session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date > year_ago_string).\
    order_by(Measurement.date).all()
    dates = [result[0] for result in precip_data]
    precipitation = [result[1] for result in precip_data]

    precip_dictionary = dict(zip(dates,precipitation))
    session.close()
    return jsonify(precip_dictionary)

@app.route("/api/v1.0/stations")
def stations():
    session=Session(bind=engine)

    active_stations = session.query(Measurement.station,func.count(Measurement.station)).\
    group_by(Measurement.station).\
    order_by(func.count(Measurement.station).desc()).all()

    active_stations_list = []
    for station in active_stations:
        active_stations_list.append(station[0])
    
    session.close()

    return jsonify(active_stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    session=Session(bind=engine)

    newest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    newest_date_string=newest_date[0]

    date_time_obj = dt.datetime.strptime(newest_date_string, '%Y-%m-%d')

    year_ago = date_time_obj - dt.timedelta(days=365)

    year_ago_string = year_ago.strftime('%Y-%m-%d')

    active_stations = session.query(Measurement.station,func.count(Measurement.station)).\
    group_by(Measurement.station).\
    order_by(func.count(Measurement.station).desc()).all()
    
    most_active_station=active_stations[0][0]
    
    tobs_route= session.query(Measurement.tobs).filter(Measurement.station == most_active_station).filter(Measurement.date > year_ago_string).all()

    tobs_route_list =[]
    for tob in tobs_route:
        tobs_route_list.append(tob[0])
    
    session.close()

    return jsonify(tobs_route_list)

@app.route("/api/v1.0/<start>")
def startstats(start):
    session = Session(bind=engine)
    #lowest_temp = session.query(Measurement.station,Measurement.tobs).filter(Measurement.station == most_active_station).order_by(Measurement.tobs).first()

    #highest_temp = session.query(Measurement.station,Measurement.tobs).filter(Measurement.station == most_active_station).order_by(Measurement.tobs.desc()).first()

    #avg_temp = session.query(Measurement.station,func.avg(Measurement.tobs)).filter(Measurement.station == most_active_station).all()

    lowest_temp = session.query(Measurement.tobs).filter(Measurement.date >= start).order_by(Measurement.tobs).first()

    avg_temp = session.query(func.avg(Measurement.tobs)).filter(Measurement.date >= start).all()

    highest_temp = session.query(Measurement.tobs).filter(Measurement.date >= start).order_by(Measurement.tobs.desc()).first()

    temp_dict = {}
    temp_dict["TMIN"]=lowest_temp[0]
    temp_dict["TAVG"]=avg_temp[0]
    temp_dict["TMAX"]=highest_temp[0]
    
    session.close()

    return jsonify(temp_dict)

@app.route("/api/v1.0/<start>/<end>")
def start_end_stats(start,end):
    session = Session(bind=engine)

    lowest_temp2 = session.query(Measurement.tobs).filter(Measurement.date >= start).filter(Measurement.date <= end).order_by(Measurement.tobs).first()

    avg_temp2 = session.query(func.avg(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    highest_temp2 = session.query(Measurement.tobs).filter(Measurement.date >= start).filter(Measurement.date <= end).order_by(Measurement.tobs.desc()).first()
   
    temp_dict2 = {}
    temp_dict2["TMIN"]=lowest_temp2[0]
    temp_dict2["TAVG"]=avg_temp2[0]
    temp_dict2["TMAX"]=highest_temp2[0]
    
    session.close()
    
    return jsonify(temp_dict2)


if __name__ == "__main__":
    app.run(debug=True)

