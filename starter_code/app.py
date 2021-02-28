#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, DateTime
import datetime
from models import setup_db, Venue, Shows, Artist, db

import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')

setup_db(app)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
  # date = dateutil.parser.parse(value)
  if isinstance(value, str):
        date = dateutil.parser.parse(value)
  else:
        date = value
  if format == 'full':
      format = "EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format = "EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)


app.jinja_env.filters['datetime'] = format_datetime


def format_genres(genres):
    genres_formatted = ''.join(
        list(filter(lambda x: x != '{' and x != '}', genres))).split(',')
    return genres_formatted


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

  all_areas = Venue.query.with_entities(func.count(
      Venue.id), Venue.city, Venue.state).group_by(Venue.city, Venue.state).all()
  venues_info = []
  for area in all_areas:
    area_venues = Venue.query.filter_by(
        state=area.state).filter_by(city=area.city).all()

    local_venue_info = []

    for venue in area_venues:
      local_venue_info.append({
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": len(Shows.query.filter_by(venue_id=venue.id).filter(Shows.start_time > datetime.now()).all())
      })
    venues_info.append({
      "city": area.city,
      "state": area.state,
      "venues": local_venue_info
    })

  return render_template('pages/venues.html',
  areas=venues_info)


@app.route('/venues/search', methods=['POST'])
def search_venues():
  name_venue = request.form.get('search_term')

  venues = Venue.query.filter(Venue.name.ilike("%" + name_venue + "%")).all()
  number_of_venues = len(venues)

  data = []

  for venue in venues:
    data.append(venue)

  response = {
    "count": number_of_venues,
    "data": data
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue_query = db.session.query(Venue).filter(Venue.id == venue_id).first()
  future_shows = db.session.query(Artist, Shows).join(Shows).join(Venue).filter(
        Shows.venue_id == venue_id,
        Shows.artist_id == Artist.id,
        Shows.start_time > datetime.now()
    ).all()

  count_of_future_shows = len(future_shows)
  past_shows = db.session.query(Artist, Shows).join(Shows).join(Venue).filter(
        Shows.venue_id == venue_id,
        Shows.artist_id == Artist.id,
        Shows.start_time < datetime.now()
    ).all()
    
  count_of_past_shows = len(past_shows)

  data = {
    "id": venue_query.id,
    "name": venue_query.name,
    "genres": format_genres(venue_query.genres),
    "address": venue_query.address,
    "city": venue_query.city,
    "state": venue_query.state,
    "phone": venue_query.phone,
    "website": venue_query.website,
    "facebook_link": venue_query.facebook_link,
    "seeking_talent": venue_query.seeking_talent,
    "seeking_description": venue_query.seeking_description,
    "image_link": venue_query.image_link,
    "past_shows": [],
    "upcoming_shows": [],
    "past_shows_count": count_of_past_shows,
    "upcoming_shows_count": count_of_future_shows
  } 

  for artist, show in future_shows:
    show_to_add = {
      "venue_id":show.id,
      "artist_name":artist.name,
      "artist_image_link":artist.image_link,
      "start_time": show.start_time

    }
    data["upcoming_shows"].append(show_to_add)

  for artist, show in past_shows:
    shows_to_add = {
      "venue_id":show.id,
      "artist_name":artist.name,
      "artist_image_link":artist.image_link,
      "start_time": show.start_time
    }
    data["past_shows"].append(shows_to_add)

  # TODO: replace with real venue data from the venues table, using venue_id

  return render_template('pages/show_venue.html', venue=data)



#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm(request.form)
  return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm(request.form, csrf_enabled=False)
  if form.validate():

    if form.seeking_talent.data == 'True':
      form.seeking_talent.data = True
    else:
      form.seeking_talent.data = False

    body = {}
    error = False
    try:
      name = form.name.data
      address = form.address.data
      city = form.city.data
      state = form.state.data
      phone = form.phone.data
      genres = form.genres.data
      image_link = form.image_link.data
      website = form.website.data
      seeking_description = form.seeking_description.data
      seeking_talent = form.seeking_talent.data
      facebook_link = form.facebook_link.data

      venue_to_add = Venue(name=name, seeking_talent=seeking_talent, address=address, city=city, state=state, phone=phone,
                          genres=genres, image_link=image_link, website=website, seeking_description=seeking_description, facebook_link=facebook_link)
      db.session.add(venue_to_add)
      db.session.commit()

    except:
      error = True
      db.session.rollback()
    finally:
      db.session.close()
    if error:
      flash('An error occurred. Venue  could not be listed.')
      abort(500)
    else:
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
  else: flash(form.errors)

  return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:
    x = Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return jsonify({'success': True})
  return None

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
  artists = Artist.query.all()


  data = []

  for artist in artists:
    artist_dic = {
      "id": artist.id,
      "name": artist.name
    }
    data.append(artist_dic)

  return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
  artist_name = request.form.get('search_term')
  artists = Artist.query.filter(
      Artist.name.ilike("%" + artist_name + "%")).all()
  number_of_results = len(artists)

  data = []

  for artist in artists:
    artist = {
        "id": artist.id,
        "name": artist.name,
        "num_upcoming_shows": 0,
        }
    data.append(artist)

  response = {
    "count": number_of_results,
    "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  artist_query = db.session.query(Artist).filter(Artist.id == artist_id).first()

  future_shows = db.session.query(Venue,Shows).join(Artist).filter(
        Shows.artist_id == artist_id,
        Shows.venue_id == Venue.id,
        Shows.start_time > datetime.now()
    ).all()

  count_of_future_shows = len(future_shows)

  past_shows = db.session.query(Venue,Shows).join(Artist).filter(
        Shows.artist_id == artist_id,
        Shows.venue_id == Venue.id,
        Shows.start_time < datetime.now()
    ).all()

  count_of_past_shows = len(past_shows)


  data = {
    "id":artist_query.id,
    "name":artist_query.name,
    "genres":format_genres(artist_query.genres),
    "city":artist_query.city,
    "state":artist_query.state,
    "phone":artist_query.phone,
    "website":artist_query.website,
    "seeking_description":artist_query.seeking_description,
    "seeking_venue":artist_query.seeking_venue,
    "facebook_link":artist_query.facebook_link,
    "image_link":artist_query.image_link,
    "past_shows":[],
    "upcoming_shows":[],
    "past_shows_count": count_of_past_shows,
    "upcoming_shows_count": count_of_future_shows,
  }

  for venue, show in future_shows:

    show_to_add = {
      "venue_id":venue.id,
      "venue_name":venue.name,
      "venue_image_link":venue.image_link,
      "start_time":show.start_time
    }
    data["upcoming_shows"].append(show_to_add)

  for venue, show in past_shows:
    show_to_add = {
      "venue_id":venue.id,
      "venue_name":venue.name,
      "venue_image_link":venue.image_link,
      "start_time":show.start_time
    }
    data["upcoming_shows"].append(show_to_add)
  return render_template('pages/show_artist.html', artist=data)


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.first_or_404(artist_id)

  artist_query = db.session.query(Artist).filter(
      Artist.id == artist_id).first()
  artist_query.genres = format_genres(artist_query.genres)

  form = ArtistForm(obj=artist_query)
  template_object = {"name": artist_query.name, "id": artist_query.id}

  artist = db.session.query(Artist.name).filter(Artist.id == artist_id).all()

  return render_template('forms/edit_artist.html', form=form, artist=template_object)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  form = VenueForm(request.form)
  artist = Artist.query.first_or_404(artist_id)

  artist_query = db.session.query(Artist).filter(Artist.id == artist_id).first()


  try:
    error=False

    name = form.name.data
    city = form.city.data
    state = form.state.data
    phone = form.phone.data
    genres = form.genres.data
    image_link = form.image_link.data
    facebook_link = form.facebook_link.data

    artist_to_update = db.session.query(Artist).filter(Artist.id == artist_id).update({
      Artist.name:form.name.data,
      Artist.city:form.city.data,
      Artist.state:form.state.data,
      Artist.phone:form.phone.data,
      Artist.genres:form.genres.data,
      Artist.image_link:form.image_link.data,
      Artist.facebook_link:form.facebook_link.data
      })

    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Artist  could not be edited')
    abort(500)
  else:
    flash('Artist ' + request.form['name'] + ' was successfully updated')
  return render_template('pages/home.html')


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue_query = db.session.query(Venue).filter(Venue.id==venue_id).first()

  
  venue = Venue.query.first_or_404(venue_id) 
  venue_query.genres = format_genres( venue_query.genres)

  template_object = {"name":venue_query.name , "id": venue_query.id}
  
  form = VenueForm(obj=venue_query)
 

  return render_template('forms/edit_venue.html', form=form, venue=template_object)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  form = VenueForm(request.form)
  


  if form.seeking_talent.data == 'True':
    form.seeking_talent.data = True
  else:
    form.seeking_talent.data = False
  body = {}
  error = False
  try:
    name = form.name.data
    address = form.address.data
    city = form.city.data
    state = form.state.data
    phone = form.phone.data
    genres = form.genres.data
    image_link = form.image_link.data
    seeking_description = form.seeking_description.data
    seeking_talent = form.seeking_talent.data
    facebook_link = form.facebook_link.data

    venue_to_update = db.session.query(Venue).filter(Venue.id==venue_id).update({
      Venue.name:form.name.data,
      Venue.address:form.address.data,
      Venue.city:form.city.data,
      Venue.state:form.state.data,
      Venue.state:form.state.data,
      Venue.phone:form.phone.data,
      Venue.genres:form.genres.data,
      Venue.image_link:form.image_link.data,
      Venue.seeking_description:form.seeking_description.data,
      Venue.seeking_talent:form.seeking_talent.data,
      Venue.facebook_link:form.facebook_link.data
      })
      
    db.session.commit()
  
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Venue  could not be edited')
    abort(500)
  else:
    flash('Venue ' + request.form['name'] + ' was successfully updated')
  return render_template('pages/home.html')

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():

  form = ArtistForm(request.form)

  if form.seeking_venue.data == 'True':
    form.seeking_venue.data = True
  else:
    form.seeking_venue.data = False

  error = False
  try:
    name = form.name.data
    city = form.city.data
    state = form.state.data
    phone = form.phone.data
    genres = form.genres.data
    image_link = form.image_link.data
    facebook_link = form.facebook_link.data
    seeking_venue = form.seeking_venue.data
    seeking_description = form.seeking_description.data
    website = form.website.data
    artist_to_add = Artist(name=name,city=city,state=state,phone=phone,genres=genres,
      image_link=image_link,seeking_venue=seeking_venue,seeking_description=seeking_description, 
      facebook_link=facebook_link, website=website)


    db.session.add(artist_to_add)
    db.session.commit()
  
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Artist could not be listed.')
    abort(400)
  else:
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():

  shows = db.session.query(Artist,Venue,Shows).all()

  
  show_data = []

  for artist,venue,show in shows:

    show_data.append({
      "venue_id":venue.id,
      "venue_name": venue.name,
      "artist_id": artist.id,
      "artist_name":artist.name,
      "artist_image_link": artist.image_link,
      "start_time":show.start_time
    })


  return render_template('pages/shows.html', shows=show_data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  form = ShowForm(request.form)
  error = False

  show = Shows( 
     artist_id = form.artist_id.data,
     venue_id = form.venue_id.data,
     start_time = form.start_time.data
  )
  try:
    db.session.add(show)
    db.session.commit()
    flash('Show was succesfully listed!')
  except:

    error = True
    flash('Show could not be listed!')
    db.session.rollback()
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

