#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
import datetime
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import  join
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from datetime import datetime
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app,db)
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  value = str(value)
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  data = db.session.query(Artist).all()
  return render_template('pages/home.html', artists=data)

# -----------------------------------------------------------------
#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  cities = db.session.query(Venue.city, Venue.state).distinct(Venue.city, Venue.state).all()
  venues = []
  for city in cities: venues += db.session.query(Venue).filter(Venue.city == city[0]).filter(Venue.state == city[1]).all()
  return render_template('pages/venues.html', areas=cities, venues=venues)

@app.route('/venues/search', methods=['POST'])
def search_venues():

  search_term = request.form.get('search_term')
  data = db.session.query(Venue).filter(Venue.name.ilike(f'%{search_term}%'))
  count = []
  for d in data:
    count.append(d.name)
  response = {
    "count": len(count),
    "data": data,
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  data = db.session.query(Venue).filter(Venue.id == venue_id).all()
  shows = db.session.query(Show).filter(Show.venue_id == venue_id).all()
  upcoming_shows = db.session.query(Show).filter(Show.venue_id == venue_id).filter(Show.start_time >= str(datetime.now()).split('.',1)[0] ).all()
  past_shows = db.session.query(Show).filter(Show.venue_id == venue_id).filter(Show.start_time <= str(datetime.now()).split('.',1)[0] ).all()
  '''need artist name, and artist image link here'''
  venues = []
  for s in shows:
    print(s.venue_id)
    for u in upcoming_shows:
      u.venue_name=db.session.query(Venue.name).filter_by(id=u.venue_id).first()[0]
      u.venue_image_link=db.session.query(Venue.image_link).filter_by(id=u.venue_id).first()[0]
      u.artist_name = db.session.query(Artist.name).filter_by(id=u.artist_id).first()[0]
      u.artist_image_link = db.session.query(Artist.image_link).filter_by(id=u.artist_id).first()[0]
    for u in past_shows:
      u.venue_name=db.session.query(Venue.name).filter_by(id=u.venue_id).first()[0]
      u.venue_image_link=db.session.query(Venue.image_link).filter_by(id=u.venue_id).first()[0]
      u.artist_name = db.session.query(Artist.name).filter_by(id=u.artist_id).first()[0]
      u.artist_image_link = db.session.query(Artist.image_link).filter_by(id=u.artist_id).first()[0]

  for d in data:
    d.upcoming_shows=upcoming_shows
    d.past_shows=past_shows
    d.upcoming_shows_count=len(upcoming_shows)
    d.past_shows_count=len(past_shows)

  return render_template('pages/show_venue.html', venue=data[0])
# -----------------------------------------------------------------
#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():

  checked = ''
  form = VenueForm()
  if(request.form.get('seeking')=="yes"):
      checked = True
  else:
      checked = False
  try:
     new_venue = Venue(
      name=form.name.data,
      city=form.city.data,
      state=form.state.data,
      address=form.address.data,
      phone=form.phone.data,
      facebook_link=form.facebook_link.data,
      image_link=form.image_link.data,
      website=form.website.data,
      seeking_talent = checked,
      seeking_description = request.form.get('description')
    )
     db.session.add(new_venue);
     db.session.commit()
     flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback();
    flash('An error occurred. Venue ' + new_venue.name + ' could not be listed.')
  return render_template('pages/home.html')

@app.route('/venues/<int:venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO:
  try:
      venue = db.session.query(Venue).filter_by(Venue.id==venue_id).all()
      db.session.delete(venue)
      db.session.commit()
  except :
      db.session.rollback()
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = db.session.query(Artist).all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form.get('search_term')
  data = db.session.query(Artist).filter(Artist.name.ilike(f'%{search_term}%'))
  count = []
  for d in data:
    count.append(d.name)
  response = {
    "count": len(count),
    "data": data,
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  data = db.session.query(Artist).filter(Artist.id == artist_id).all()
  shows = db.session.query(Show).filter(Show.artist_id == artist_id).all()
  upcoming_shows = db.session.query(Show).filter(Show.artist_id == artist_id).filter(Show.start_time >= str(datetime.now()).split('.',1)[0] ).all()
  past_shows = db.session.query(Show).filter(Show.artist_id == artist_id).filter(Show.start_time <= str(datetime.now()).split('.',1)[0] ).all()

  venues = []
  for s in shows:
    print(s.venue_id)
    for u in upcoming_shows:
      u.venue_name=db.session.query(Venue.name).filter_by(id=u.venue_id).first()[0]
      u.venue_image_link=db.session.query(Venue.image_link).filter_by(id=u.venue_id).first()[0]
    for u in past_shows:
      u.venue_name=db.session.query(Venue.name).filter_by(id=u.venue_id).first()[0]
      u.venue_image_link=db.session.query(Venue.image_link).filter_by(id=u.venue_id).first()[0]

  for d in data:
    d.upcoming_shows=upcoming_shows
    d.past_shows=past_shows
    d.upcoming_shows_count=len(upcoming_shows)
    d.past_shows_count=len(past_shows)

  return render_template('pages/show_artist.html', artist=data[0])

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = db.session.query(Artist).filter_by(id=artist_id).first()
  return render_template('forms/edit_artist.html', form=form, artist=artist)
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  try:
    artist.name=form.name.data,
    artist.city=form.city.data,
    artist.state=form.state.data,
    artist.phone=form.phone.data,
    artist.genres=form.genres.data,
    artist.image_link=form.image_link.data,
    artist.facebook_link=form.facebook_link.data,
    artist.seeking_venue=form.seeking.data,
    artist.website=form.website.data,
    artist.seeking_description=form.description.data,

    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully updated!')
  except:
    flash('An error occurred. Venue ' + data.name + ' could not be updated.')
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = db.session.query(Venue).filter_by(id=venue_id).first()
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  try:
      venue.name=form.name.data,
      venue.city=form.city.data,
      venue.state=form.state.data,
      venue.phone=form.phone.data,
      venue.facebook_link=form.facebook_link.data,
      venue.image_link =form.image_link.data,
      venue.website=form.website.data,
      venue.seeking_talent=form.seeking.data,
      venue.description=form.description.data

      db.session.commit()

  except:
    flash('Venue could not be updated')
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  form = ArtistForm()
  try:
     new_artist = Artist(
      name=form.name.data,
      city=form.city.data,
      state=form.state.data,
      phone=form.phone.data,
      genres=form.genres.data,
      image_link=form.image_link.data,
      facebook_link=form.facebook_link.data,
      seeking_venue=form.seeking.data,
      seeking_description=form.description.data,
      website=form.website.data,
    )
     db.session.add(new_artist)
     db.session.commit()
     flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
     db.session.rollback()
     flash('An error occurred. Artist ' + new_artist.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  show_data = db.session.query(Show).all()
  venue_data = []
  for show in show_data:
    show.venue_name = db.session.query(Venue.name).filter_by(id=show.venue_id).first()[0]
    show.artist_name = db.session.query(Artist.name).filter_by(id=show.artist_id).first()[0]
    show.artist_image_link = db.session.query(Artist.image_link).filter_by(id=show.artist_id).first()[0]
    venue_data.append(show)
  return render_template('pages/shows.html', shows=venue_data)

@app.route('/shows/create')
def create_shows():
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  form = ShowForm()
  try:
      add_show = Show(
      start_time=form.start_time.data,
      artist_id=form.artist_id.data,
      venue_id=form.venue_id.data,
      )
      db.session.add(add_show)
      db.session.commit()
      flash('Show was successfully listed!')
  except:
      db.session.rollback()
      flash('An error occurred.'+ request.form['venue_id'] +'Show could not be listed.')
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
