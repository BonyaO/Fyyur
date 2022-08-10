#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
from lib2to3.pgen2.pgen import DFAState
import sys
from this import d
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from datetime import datetime
from sqlalchemy import func
from models import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

moment = Moment(app)
app.config.from_object('config')
migrate = Migrate(app, db)


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  
  venues = Venue.query.group_by(Venue.id, Venue.state, Venue.city).all()
  data = []
  venue_city_and_state = ''

  for venue in venues: 
    num_upcoming_shows = Show.query.filter(venue.id == Show.venue_id).filter(Show.start_time > datetime.now()).count()
    if venue_city_and_state == venue.city + venue.state:
      data[len(data) - 1]["venues"].append({
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": num_upcoming_shows
      })
    else: 
      venue_city_and_state == venue.city + venue.state
      data.append({
        "city": venue.city,
        "state": venue.state,
        "venues": [{
          "id": venue.id,
          "name": venue.name,
          "num_upcoming_shows": num_upcoming_shows,
        }]
      })


  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():

  search_term = request.form['search_term'].casefold()
  venues = Venue.query.filter(func.lower(Venue.name).contains(search_term.lower())).all()

  venue_data = []

  for venue in venues:
    num_upcoming_shows = Show.query.filter(venue.id == Show.venue_id).filter(Show.start_time > datetime.now()).count()
    venue_info = {
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows": num_upcoming_shows
    }
    venue_data.append(venue_info)


  response={
    "count": len(venue_data),
    "data": venue_data
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  past_shows = []
  upcoming_shows = []
  venue = Venue.query.get(venue_id)
  shows = venue.shows
  for show in shows:
    show_info = {
      "artist_id": show.venue_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": str(show.start_time)
    }
    if (show.start_time < datetime.now()):
      past_shows.append(show_info)
    else: 
      upcoming_shows.append(show_info)
  data ={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres.split(','),
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }
  
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  error=False
  data={}
  venueform = VenueForm()
  try:
    venue = Venue(
      name = venueform.name.data,
      city = venueform.city.data,
      state = venueform.state.data,
      address = venueform.address.data,
      phone = venueform.phone.data,
      genres = venueform.genres.data,
      image_link = venueform.image_link.data,
      facebook_link = venueform.facebook_link.data,
      website_link = venueform.website_link.data,
      seeking_talent = venueform.seeking_talent.data,
      seeking_description = venueform.seeking_description.data
    )
    db.session.add(venue)
    db.session.commit()
    data['name'] = venue.name
  except: 
    error = True
    db.session.rollback()
    print(sys.exc_info())

  finally:
    db.session.close()
    if error: 
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    else: 
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
    return render_template('pages/home.html')
  
# Route to delete a venue Item
# At the moment feedback on success or failure can't be displayed even though I use flash()
# I guess it's because of my little understand of how the ajax requests communicates and responds to this route.
@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  error = False
  try:  
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
  except:
    error = True 
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
    if not error: 
      flash('Venue with ID: ' + venue_id + ' was successfully deleted!')
    else: 
      flash('An error occurred. Venue ID: ' + venue_id + ' could not be be deleted.')
  return render_template('pages/home.html')
  

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data=Artist.query.with_entities(Artist.id, Artist.name).all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form['search_term']

  artists = Artist.query.filter(func.lower(Artist.name).contains(search_term.lower())).all()
  
  artist_data = []
  for artist in artists:
    shows = artist.shows
    num_upcoming_shows = 0
    for show in shows:
      if (show.start_time > datetime.now()):
        num_upcoming_shows += 1
    response_info = {
      "id": artist.id,
      "name": artist.name,
      "num_upcoming_shows": num_upcoming_shows
    }
    artist_data.append(response_info)


  response={
    "count": len(artist_data),
    "data": artist_data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id

  upcoming_shows = []
  past_shows = []
  artist = Artist.query.get(artist_id)
  shows = artist.shows
  for show in shows:
    show_info = {
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "venue_image_link": show.venue.image_link,
      "start_time": str(show.start_time)
    }
    if (show.start_time < datetime.now()):
      past_shows.append(show_info)
    else: 
      upcoming_shows.append(show_info)
  data={
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres.split(','),
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website_link,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venues,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  
  try:
    artist = Artist.query.filter_by(id=artist_id).first()
    form = ArtistForm(obj=artist)
    form.populate_obj(artist)
    db.session.commit()

  except:
    db.session.rollback()
  finally:
    return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  form = ArtistForm()
  try: 
    artist = Artist.query.filter_by(id=artist_id).first()
    artist.name=form.name.data,
    artist.city=form.city.data,
    artist.state=form.state.data,
    artist.phone=form.phone.data,
    artist.genres=form.genres.data,
    artist.image_link=form.image_link.data,
    artist.facebook_link=form.facebook_link.data,
    artist.website_link=form.website_link.data,
    artist.looking_for_venues=form.seeking_venue.data,
    artist.seeking_description=form.seeking_description.data
    db.session.commit()
  except: 
    db.session.rollback()
  finally: 
    db.session.close()
    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  error = False
  try: 
    venue = Venue.query.filter_by(id=venue_id).first()
    form = VenueForm(obj=venue)
    form.populate_obj(venue)
    db.session.commit()
  except: 
    error = True
    print(sys.exc_info())
    db.sesssion.rollback()

  finally:
    return render_template('forms/edit_venue.html', form=form, venue=venue)
  

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  venueform = VenueForm()
  try: 
    venue = Venue.query.filter_by(id=venue_id).first()
    venue.name = venueform.name.data,
    venue.city = venueform.city.data,
    venue.state = venueform.state.data,
    venue.address = venueform.address.data,
    venue.phone = venueform.phone.data,
    venue.genres = venueform.genres.data,
    venue.image_link = venueform.image_link.data,
    venue.facebook_link = venueform.facebook_link.data,
    venue.website_link = venueform.website_link.data,
    venue.looking_for_talent = venueform.seeking_talent.data,
    venue.seeking_description = venueform.seeking_description.data
    db.session.commit()

  except:
    db.session.rollback() 
  finally:
    db.session.close()
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  data={}
  error = False
  form = ArtistForm()
  try: 
    artist = Artist(
      name=form.name.data,
      city=form.city.data,
      state=form.state.data,
      phone=form.phone.data,
      genres=form.genres.data,
      image_link=form.image_link.data,
      facebook_link=form.facebook_link.data,
      website_link=form.website_link.data,
      seeking_venues=form.seeking_venue.data,
      seeking_description=form.seeking_description.data
    )
    db.session.add(artist)
    db.session.commit()
  except:
    error = True
    db.session.rollback 
    print(sys.exc_info())
  finally:
    db.session.close()
    if error: 
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
    else: 
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
    return render_template('pages/home.html')



#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  shows = Show.query.all()
  data = []

  for show in shows:
    data.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": str(show.start_time)
    })
 
  return render_template('pages/shows.html', shows=data)
  
 
@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  showform = ShowForm()
  error = False
  # I was forced to devise a way to enter the id for shows as the id could not autoincrement eventhough I set the id Column similar to the other models
  # But I still get a NotNullViolation when I try to create a show with Show(artist_id, venue_id, start_time)
  # So I use some logic to combine artist_id, venue_id and time that will be unique for each show
  # Basically, show id = artist_id + venue_id + hour of start_time
  hour = showform.start_time.data.hour
  show_id = int(showform.artist_id.data) + int(showform.venue_id.data) + hour
  try: 

    show = Show(id=show_id, artist_id=showform.artist_id.data, venue_id=showform.venue_id.data, start_time = showform.start_time.data)
    db.session.add(show)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info()) 
  finally: 
    db.session.close()
    if error:
      flash('An error occurred. Show could not be listed.')
    else: 
      flash('Show was successfully listed!')
    return render_template('pages/home.html')
  

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
