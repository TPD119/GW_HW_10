import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station
# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/stations"
    )


@app.route("/api/v1.0/precipitation")
def precips():

    session = Session(engine)

    results = session.query(Measurement).all()
    
    all_precip = []
    for precipitation in results:
        precip_dict = {}
        precip_dict["date"] = precipitation.date
        precip_dict["precip"] = precipitation.prcp
        all_precip.append(precip_dict)

    return jsonify(all_precip)

@app.route("/api/v1.0/stations")
def stations():

    results = session.query(Station.name).all()
    all_stations = list(np.ravel(results))
    
    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
     import datetime as dt
     session = Session(engine)

     """Return a total observations from last year"""
     query_date = session.query(Measurement.date). \
        order_by(Measurement.date.desc()).first()
     prior_year = dt.datetime.strptime(query_date[0],'%Y-%m-%d').date() \
        - (dt.timedelta(days=365))
     results = session.query(Measurement.date,Measurement.tobs). \
     filter(Measurement.date >= prior_year).all()
     #all_stations = list(np.ravel(results))
    
     return jsonify(results)
 
@app.route("/api/v1.0/<start>")
def starter(start):
     """Return a lcount of total observations"""
     import datetime as dt
     session = Session(engine)
     
     results = session.query(func.min(Measurement.tobs), \
                             func.max(Measurement.tobs), \
                             func.avg(Measurement.tobs)). \
                             filter(Measurement.date >= start).all()
       
     return jsonify(results)
 
    
@app.route("/api/v1.0/<start>/<end>")
def start_end(start,end):
     """Return a lcount of total observations"""
     import datetime as dt
     session = Session(engine)
     
     results = session.query(func.min(Measurement.tobs), \
                             func.max(Measurement.tobs), \
                             func.avg(Measurement.tobs)). \
                             filter(Measurement.date >= start). \
                             filter(Measurement.date <= end).all()
       
     return jsonify(results)    
# Stopping flask can be a pain, so I recommend this ONLY in dev
# Avoid using this in production
from flask import request

def shutdown_server():
    function = request.environ.get('werkzeug.server.shutdown')
    if function is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    function()

@app.route('/shutdown')
def shutdown():
    shutdown_server()
    return 'Server shutting down...'

if __name__ == '__main__':
    app.run(debug=True)