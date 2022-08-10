
from flask import Flask
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
db = SQLAlchemy(app)



#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

# Show Model (Association table for the many to many relationship)
# The need for a separate id column for shows only come because if we use the venue_id and the artist_id as the primary keys,
# it will restrict one artist to have only one show at a particular venue. trying to add a show at a different time for the same
# artist at the same venue will cause an error.
class Show(db.Model):
  __tablename__ = "Show"
  id = db.Column(db.Integer, primary_key=True)
  venue_id= db.Column(db.Integer, db.ForeignKey('Venue.id', ondelete="CASCADE"), nullable=False)
  artist_id= db.Column(db.Integer, db.ForeignKey('Artist.id', ondelete="CASCADE"), nullable=False)
  start_time= db.Column(db.DateTime, nullable=False)
  
class Venue(db.Model):
    __tablename__ = "Venue"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500))
    genres = db.Column(db.String(), nullable=False)
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String())
    shows = db.relationship("Show", backref="venue", cascade="all, delete", lazy=True)


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String,  nullable=False)
    city = db.Column(db.String(120), nullable=False )
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_venues = db.Column(db.Boolean)
    seeking_description = db.Column(db.String())
    shows = db.relationship("Show", backref="artist", cascade="all, delete", lazy=True)