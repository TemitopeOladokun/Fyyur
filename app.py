#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from sqlalchemy import ARRAY
from forms import *
from flask_migrate import Migrate
from datetime import datetime
from model import db, Venue, Artist, Show


#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)

# TODO: connect to a local postgresql database
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
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  venues = Venue.query.all()

    # Get the state and city and remove duplicates
  unique_venues = Venue.query.distinct(Venue.city, Venue.state).all()

  data = [] # An array where the data that will be passed to the view is stored

  current_time = datetime.now()

  for unique_venue in unique_venues:

    venue_data = [] # An array that stores all the venues in each city
    
    for venue in venues:

      if unique_venue.city == venue.city:
        venue_data.append({
          "id": venue.id,
          "name": venue.name,
          "num_upcoming_shows": len([Show.query.filter(Show.start_time > current_time)])
        })
    data.append({
      "city": unique_venue.city,
      "state": unique_venue.state,
      "venues": venue_data
    })
  
  return render_template('pages/venues.html', areas=data)
  

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  
  search_term=request.form.get('search_term', '')

  venues = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()

  response={
      "count": len(venues),
      "data": []
  }

  for venue in venues:
    response['data'].append({
      "id": venue.id,
      "name": venue.name,
    })
  
  return render_template('pages/search_venues.html', results=response)


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  
  venues = Venue.query.get(venue_id)

    # Get the current time
  current_time = datetime.today()


    # Get all the venues where a show has been performed
  shows = Show.query.filter(Show.venue_id == venue_id)


  past_show = [] # An array that hold all the past shows
  upcoming_show = [] # An array that hold all upcoming shows

    # Loop Through every row in the Show Model table
  for show in shows:
    
    if show.start_time > current_time:

      # put the shows that are upcoming to the upcoming_show array
      upcoming_show.append({
        "artist_id": show.artist.id,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time": format_datetime(str(show.start_time))
      })
    else:
      # put the show that already took place in the past_shows array
      past_show.append({
        "artist_id": show.artist.id,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time": format_datetime(str(show.start_time))
      })


    Data= {
    "id": venues.id,
    "name": venues.name,
    "genres": venues.genres,
    "address": venues.address,
    "city": venues.city,
    "state": venues.state,
    "phone": venues.phone,
    "website": venues.website,
    "facebook_link": venues.facebook_link,
    "seeking_talent": venues.seeking_talent,
    "seeking_description": venues.seeking_description,
    "image_link": venues.image_link,
    "past_shows": past_show,
    "upcoming_shows": upcoming_show,
    "past_shows_count": len(past_show),
    "upcoming_shows_count": len(upcoming_show),
    }

  return render_template('pages/show_venue.html', venue=Data)
  
  

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = VenueForm()
  
  try:
      venue = Venue()
      form.populate_obj(venue)

      db.session.add(venue)
      db.session.commit()

      # on successful db insert, flash success
      flash('Venue ' + form.name.data + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + form.name.data + ' could not be listed.')

  finally:
    db.session.close()

  return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    venue = Venue.query.get(venue_id)

    db.session.delete(venue)
    db.session.commit()
    
    flash('Venue: ' + venue.name + ' was DELETED successfully!')
  except:
    db.session.rollback()

    flash('Venue: ' + venue.name + ' was NOT DELETED an Error Occured!')
  finally:
    db.session.close()


  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return jsonify({"success": True})
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  
  data = Artist.query.all()

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term=request.form.get('search_term', '')
  artists = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()

  response={
    "count": len(artists),
    "data": []
    }

  for artist in artists:
    response['data'].append({
      "id": artist.id,
      "name": artist.name,
    })
  
  return render_template('pages/search_artists.html', results=response)

  
@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id

  artist = Artist.query.get(artist_id)

    # Get the current time
  current_date = datetime.now()

    # Get the shows the artist have performed in and the venues
  artist_shows = Show.query.filter(Show.artist_id == artist_id)
    

  past_shows = [] # An array that hold past_shows
  upcoming_shows = [] # An array that hold upcoming_shows

    # loop through all the shows the artist has performed in
  for show in artist_shows:
        
    if show.start_time < current_date:
            # added past shows to p_show list
      past_shows.append({
        "venue_id": show.id,
        "venue_name": show.venue.name,
        "venue_image_link": show.venue.image_link,
        "start_time": format_datetime(str(show.start_time))
      })
    else:
            # Add upcoming show to u_show list
      upcoming_shows.append({
        "venue_id": show.id,
        "venue_name": show.venue.name,
        "venue_image_link": show.venue.image_link,
        "start_time": format_datetime(str(show.start_time))
        })

    Data= {
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
    }
    
  
  return render_template('pages/show_artist.html', artist=Data)

  

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.get(artist_id)
  
  form = ArtistForm(obj=artist)
  
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)



@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  form = ArtistForm()
  
  try:
    
    
    artist = Artist.query.get(artist_id)
  
    form.populate_obj(artist)
    db.session.commit()

    flash(f'Artist: {form.name.data} was updated successfully')

  except:

    db.session.rollback()
    flash(f'Artist {form.name.data} was not updated an Error Occurred')

  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.get(venue_id)
  form = VenueForm(obj=venue)
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  form = VenueForm()
  
  try:
    venue = Venue.query.get(venue_id)
    form.populate_obj(venue)
    db.session.commit()

    flash(f'Venue: {form.name.data} was updated successfully')

  except:

    db.session.rollback()
    flash(f'Venue {form.name.data} was not updated an Error Occurred')

  finally:
    db.session.close()

  # venue record with ID <venue_id> using the new attributes
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
    artist = Artist()
    form.populate_obj(artist)

    db.session.add(artist)
    db.session.commit()

    # on successful db insert, flash success
    flash('Artist ' + form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + form.name.data + ' could not be listed.')

  finally:
    db.session.close()


  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  shows = Show.query.all()

  data = []

  for show in shows:

    data.append({
      "venue_id": show.venue.id,
      "venue_name":show.venue.name,
      "artist_id": show.artist.id,
      "artist_name": show.artist.name,
      "artist_image_link": show. artist.image_link,
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
  form = ShowForm()
  try:
    show = Show()
    form.populate_obj(show)
    db.session.add(show)
    db.session.commit()

    # on successful db insert, flash success
    flash('Show was successfully listed!')
  except:

    db.session.rollback()

    # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Show could not be listed.')
  
  finally:
    db.session.close()

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
