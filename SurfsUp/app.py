# Import dependencies.
#################################################

import datetime as dt
import numpy as np

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
#################################################


# Database Setup
#################################################
engine = create_engine('sqlite:///C:/Users/tgruh/OneDrive/BOOTCamp/GitHub/sqlalchemy-challenge/SurfsUp/Resources/hawaii.sqlite')

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
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

# welcome route
@app.route("/")
def welcome():
    base_url = "http://127.0.0.1:5000"
    return (
        f"<html>"
        f"<head><title>Hawaii Climate Analysis API</title></head>"
        f"<body>"
        f"<h1>Welcome to the Hawaii Climate Analysis API</h1>"
        f"<h2>Available Routes:</h2>"
        f"<ul>"
        f"<li><a href='{base_url}/api/v1.0/precipitation'>Precipitation</a></li>"
        f"<li><a href='{base_url}/api/v1.0/stations'>Stations</a></li>"
        f"<li><a href='{base_url}/api/v1.0/tobs'>Temperature Observations (Tobs)</a></li>"
        f"</ul>"
        f"<h2>Temperature Analysis:</h2>"
        f"<p>Check temperature by a specific date:<br/>"
        f"Format: /api/v1.0/temp/[replace with start date]</p>"
        f"<p>Check temperature by a date range:<br/>"
        f"Format: /api/v1.0/temp/[replace with start date]/[replace with end date]</p>"
        f"<p>Note: 'start' and 'end' dates should be in the format MMDDYYYY. Copy the format above and paste in the URL bar after the main URL.</p>"
        f"</body>"
        f"</html>"
    )



# precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the precipitation data for the last year"""
    
    # Calculate the date 1 year ago from last date in database
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Query for the date and precipitation for the last year
    precipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= prev_year).all()

    session.close()
    # Dict with date as the key and prcp as the value
    precip = {date: prcp for date, prcp in precipitation}
    return jsonify(precip)

# stations route
@app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations."""
    results = session.query(Station.station).all()

    session.close()

    # Unravel results into a 1D array and convert to a list
    stations = list(np.ravel(results))
    return jsonify(stations=stations)


# temperature route
@app.route("/api/v1.0/tobs")
def temp_monthly():
    """Return the temperature observations (tobs) for previous year."""
    # Calculate the date 1 year ago from last date in database
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Query the primary station for all tobs from the last year
    results = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= prev_year).all()

    session.close()
    # Unravel results into a 1D array and convert to a list
    temps = list(np.ravel(results))

    # Return the results
    return jsonify(temps=temps)

# statistics route
@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    """Return TMIN, TAVG, TMAX."""

    # Select statement
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end:
        # start = dt.datetime.strptime(start, "%m/%d/%Y")
        # # calculate TMIN, TAVG, TMAX for dates greater than start
        # results = session.query(*sel).\
        #     filter(Measurement.date >= start).all()
        # # Unravel results into a 1D array and convert to a list
        # temps = list(np.ravel(results))
        # return jsonify(temps)

        start = dt.datetime.strptime(start, "%m%d%Y")
        results = session.query(*sel).\
            filter(Measurement.date >= start).all()

        session.close()

        temps = list(np.ravel(results))
        return jsonify(temps)

    # calculate TMIN, TAVG, TMAX with start and stop
    start = dt.datetime.strptime(start, "%m%d%Y")
    end = dt.datetime.strptime(end, "%m%d%Y")

    results = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()

    session.close()

    # Unravel results into a 1D array and convert to a list
    temps = list(np.ravel(results))
    return jsonify(temps=temps)


if __name__ == '__main__':
    app.run()
