#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import os
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from flask_wtf.csrf import CSRFProtect
from forms import *
from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')


db = SQLAlchemy(app)
migrate = Migrate(app, db)
# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.


# Define two many-to-many relationship tables: ArtistGenre, VenueGenre
ArtistGenre = db.Table('ArtistGenre',
    db.Column('genre_id' , db.Integer, db.ForeignKey('Genre.id') , primary_key=True),
    db.Column('artist_id', db.Integer, db.ForeignKey('Artist.id', ondelete='CASCADE'), primary_key=True)
)

VenueGenre = db.Table('VenueGenre',
    db.Column('genre_id', db.Integer, db.ForeignKey('Genre.id'), primary_key=True),
    db.Column('venue_id', db.Integer, db.ForeignKey('Venue.id', ondelete='CASCADE'), primary_key=True)
)


# Define the Venue class
class Venue(db.Model):
    __tablename__ = 'Venue'

    # Define the columns of the Venue table
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(120))
    image_link = db.Column(db.String(500))

    # Define the relationship with the Genre table through the VenueGenre table
    genres = db.relationship('Genre',\
                              secondary=VenueGenre,\
                              passive_deletes=True,\
                              backref=db.backref('venues'))

    # Define the relationship with the Show table
    shows = db.relationship('Show', backref='venue', lazy=True)

    # Define the string representation of a Venue object
    def __repr__(self):
        return f'<Venue {self.id} {self.name}>'

# Define the Artist class
class Artist(db.Model):
    __tablename__ = 'Artist'

    # Define the columns of the Artist table
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(120))

    # Define the relationship with the Show table
    shows = db.relationship('Show', backref='artist', lazy=True)
    
    # Define the relationship with the Genre table through the ArtistGenre table 
    genres = db.relationship('Genre',\
                              secondary=ArtistGenre,\
                              passive_deletes=True,\
                              backref=db.backref('artists'))
    
    # Define the string representation of an Artist object
    def __repr__(self):
        return f'<Artist {self.id} {self.name}>'
    
# Define the Genre class
class Genre(db.Model):
    __tablename__ = 'Genre'

    # Define the columns of the Genre table
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))

    
# Define the Show class
class Show(db.Model):
    __tablename__ = 'Show'

    # Define the columns of the Show table
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime)
    
    # Define the relationship with the Artist table 
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    
    # Define the relationship with the Venue table 
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)

    # Define the string representation of a Show object
    def __repr__(self):
        return f'<Show {self.id} artist_id={self.artist_id} venue_id={self.venue_id}>'




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

# Query the Venue table and join with the Show table to count the number of upcoming shows
  venues = Venue.query.with_entities(
        Venue.city,
        Venue.state,
        Venue.id,
        Venue.name,
        db.func.count(Show.id).label('num_upcoming_shows')
    )\
  .outerjoin(Show, Venue.id == Show.venue_id)\
  .group_by(Venue.id, Venue.name, Venue.city, Venue.state)\
  .all()
    
# Create a dictionary to store the formatted data
  response_data = []

# Iterate over the venues and format the data
  for venue in venues:
        venue_data = {
            'city': venue.city,
            'state': venue.state,
            'venues': []
        }

    # Check if the city and state combination already exists in the formatted data
        existing_data = next((data for data in response_data if data['city'] == venue.city and data['state'] == venue.state), None)

        if existing_data:
            existing_data['venues'].append({
                'id': venue.id,
                'name': venue.name,
                'num_upcoming_shows': venue.num_upcoming_shows
            })
        else:
            venue_data['venues'].append({
                'id': venue.id,
                'name': venue.name,
                'num_upcoming_shows': venue.num_upcoming_shows
            })
            response_data.append(venue_data)


  return render_template('pages/venues.html', areas=response_data);




@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

# Get the search term from the form data
  search_term = request.form.get('search_term', '').strip()

# Get the current datetime
  now = datetime.now()

# Perform a case-insensitive partial string search on the Venue name column
  venues = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()

# Initialize an empty list to store the venue data
  response_data = []

# Iterate over the venues and retrieve the number of upcoming shows for each venue
  for venue in venues:
      # Count the number of upcoming shows for the venue
      num_upcoming_shows = len([show for show in venue.shows if show.start_time > now])
      
      # Create a dictionary with the venue data and the number of upcoming shows
      venue_data = {
          "id": venue.id,
          "name": venue.name,
          "num_upcoming_shows": num_upcoming_shows
      }

      # Add the venue data to the response_data
      response_data.append(venue_data)

# Create a response dictionary with the count of venues and the response_data
  response = {
      "count": len(venues),
      "data": response_data
  }

# Render the search_venues.html template with the response and search_term variables
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))




@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

# Get the venue by ID from the database. If not found return 404
  venue = Venue.query.get_or_404(venue_id)
    
# Separate past and upcoming shows
  now = datetime.now()
  upcoming_shows = []
  past_shows = []
  
  for show in venue.shows:
      show_info = {
          "artist_id": show.artist_id,
          "artist_name": show.artist.name,
          "artist_image_link": show.artist.image_link,
          "start_time": format_datetime(str(show.start_time))
      }
      if show.start_time > now:
          upcoming_shows.append(show_info)
      else:
          past_shows.append(show_info)

  response_data = {
      "id": venue_id,
      "name": venue.name,
      "genres": [genre.name for genre in venue.genres],
      "address": venue.address,
      "city": venue.city,
      "state": venue.state,
      # Using f-string for phone number formatting
      "phone": f"{venue.phone[:3]}-{venue.phone[3:6]}-{venue.phone[6:]}",  
      "website": venue.website,
      "facebook_link": venue.facebook_link,
      "seeking_talent": venue.seeking_talent,
      "seeking_description": venue.seeking_description,
      "image_link": venue.image_link,
      "past_shows": past_shows,
      "past_shows_count": len(past_shows),
      "upcoming_shows": upcoming_shows,
      "upcoming_shows_count": len(upcoming_shows)
  }

  return render_template('pages/show_venue.html', venue=response_data)
  
    


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
  form = VenueForm(request.form)
  
  # Set default value for seeking_talent if it's not found in the form data
  if 'seeking_talent' not in request.form:
      form.seeking_talent.data = False
    

  if form.validate():
      try:
          # Create a new Venue object with the form data
          # Retrieve the maximum ID value from the database table
          max_id = db.session.query(db.func.max(Venue.id)).scalar()

          # Increment the maximum ID value by 1 to generate the ID for the new venue
          new_id = max_id + 1 if max_id is not None else 1
            
          venue = Venue(
              id=new_id,
              name=form.name.data,
              city=form.city.data,
              state=form.state.data,
              address=form.address.data,
              phone=form.phone.data,
              website=form.website_link.data,
              facebook_link=form.facebook_link.data,
              seeking_talent=form.seeking_talent.data,
              seeking_description=form.seeking_description.data,
              image_link=form.image_link.data
          )
        

          # Add the genres for the venue
          genre_names = form.genres.data
          genres = Genre.query.filter(Genre.name.in_(genre_names)).all()
          venue.genres = genres

          # Add the venue to the database
          db.session.add(venue)
          db.session.commit()

          # on successful db insert, flash success
          flash('Venue ' + form.name.data + ' was successfully listed!')
          
          return redirect(url_for('index'))
        
      except Exception as e:
          # Rollback the changes if an error occurs
          db.session.rollback()
          # Print the exception error
          print(str(e))
          # Flash error message
          flash('An error occurred. Venue ' + form.name.data + ' could not be listed.')
  else:
      for field, errors in form.errors.items():
          for error in errors:
              flash(f'Validate error: {field} {error}')

  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    
  try:
      # Find the venue by venue_id
      venue = Venue.query.get(venue_id)

      if not venue:
          flash('Venue not found.')
          return redirect(url_for('index'))
        
      # Delete the venue from the database
      db.session.delete(venue_id)
      db.session.commit()

      flash('Venue ' + venue.name + ' was successfully deleted.')
        
      return redirect(url_for('show_venue', venue_id=venue_id))
    
  except Exception as e:
      # Rollback the changes if an error occurs
      db.session.rollback()
      # Print the exception error
      print(str(e))
      # Flash error message
      flash('An error occurred. Venue with id ' + venue_id + ' could not be deleted.')
      
      return redirect(url_for('show_venue', venue_id=venue_id))

  return redirect(url_for('index'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database

  response_data = Artist.query.with_entities(
                  Artist.id,
                  Artist.name).all()

  return render_template('pages/artists.html', artists=response_data)




@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  
# Get the search term from the form data
  search_term = request.form.get('search_term', '').strip()

# Get the current datetime
  now = datetime.now()

# Perform a case-insensitive partial string search on the Artist name column
  artists = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()

# Initialize an empty list to store the artist data
  response_data = []

# Iterate over the artist and retrieve the number of upcoming shows for each artist
  for artist in artists:
      # Count the number of upcoming shows for the artist
      num_upcoming_shows = len([show for show in artist.shows if show.start_time > now])
      
      # Create a dictionary with the artist data and the number of upcoming shows
      artist_data = {
          "id": artist.id,
          "name": artist.name,
          "num_upcoming_shows": num_upcoming_shows
      }

      # Add the artist data to the response_data
      response_data.append(artist_data)

# Create a response dictionary with the count of artists and the response_data
  response = {
      "count": len(artists),
      "data": response_data
  }

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))




@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id

# Get the artist by ID from the database. If not found reeturn 404
  artist = Artist.query.get_or_404(artist_id)
    
# Separate past and upcoming shows
  now = datetime.now()
  upcoming_shows = []
  past_shows = []
  
  for show in artist.shows:
      show_info = {
          "venue_id": show.venue_id,
          "venue_name": show.venue.name,
          "venue_image_link": show.venue.image_link,
          "start_time": format_datetime(str(show.start_time))
      }
      if show.start_time > now:
          upcoming_shows.append(show_info)
      else:
          past_shows.append(show_info)
       
  response_data = {
      "id": artist_id,
      "name": artist.name,
      "genres": [genre.name for genre in artist.genres],
      "city": artist.city,
      "state": artist.state,
      "phone": artist.phone,  
      "website": artist.website,
      "facebook_link": artist.facebook_link,
      "seeking_venue": artist.seeking_venue,
      "seeking_description": artist.seeking_description,
      "image_link": artist.image_link,
      "past_shows": past_shows,
      "past_shows_count": len(past_shows),
      "upcoming_shows": upcoming_shows,
      "upcoming_shows_count": len(upcoming_shows)
  }

  return render_template('pages/show_artist.html', artist=response_data)




#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  # TODO: populate form with fields from artist with ID <artist_id>
  
  # Get the artist record with the specified artist_id from the database. If not found return 404
  artist = Artist.query.get_or_404(artist_id)

  # Extract the genres as a list of genre names
  genres = [genre.name for genre in artist.genres]

  # Create a dictionary with the necessary artist data
  response_data = {
      "id": artist.id,
      "name": artist.name,
      "city": artist.city,
      "state": artist.state,
      "phone": artist.phone,
      "image_link": artist.image_link,
      "genres": genres,
      "facebook_link": artist.facebook_link,
      "website_link": artist.website,
      "seeking_venue": artist.seeking_venue,
      "seeking_description": artist.seeking_description
  }
  
  # Create an instance of the form and populate it with response_data 
  form = ArtistForm(data=response_data)

  
  return render_template('forms/edit_artist.html', form=form, artist=response_data)




@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
    
  # Find the artist with the given ID
  artist = Artist.query.get(artist_id)

  if artist:

      # Create an instance of the form and populate it with the submitted data
      form = ArtistForm(request.form)

      # Set default value for seeking_venue if it's not found in the form data
      if 'seeking_venue' not in request.form:
          form.seeking_venue.data = False
      
      if form.validate():
          try:
              # Update the artist record with the new attributes
              artist.name = form.name.data
              artist.city = form.city.data
              artist.state = form.state.data
              artist.phone = form.phone.data
              artist.seeking_venue = form.seeking_venue.data
              artist.seeking_description = form.seeking_description.data
              artist.image_link = form.image_link.data
              artist.website = form.website_link.data
              artist.facebook_link = form.facebook_link.data
            
              # Update the genres for the artist
              genre_names = form.genres.data
              genres = Genre.query.filter(Genre.name.in_(genre_names)).all()
              artist.genres = genres
              
                
              # Commit the changes to the database
              db.session.commit()
    
              # Flash a success message
              flash('Artist successfully updated.')
            
              # Redirect to the artist's detail page
              return redirect(url_for('show_artist', artist_id=artist_id))
        
          except Exception as e:
              # Rollback the changes if an error occurs
              db.session.rollback()
              # Print the exception error
              print(str(e))
              # Flash error message
              flash('An error occurred. Artist ' + artist.name + ' could not be updated.')

      else:
          # Handle the case when the form validation fails
          flash('Form validation failed. Please check your input.')
          return redirect(url_for('edit_artist_submission', artist_id=artist_id, form=form))
  else:
      # Handle the case when the artist with the given ID is not found
      flash('Artist not found.')
      return redirect(url_for('index'))
        
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  # TODO: populate form with values from venue with ID <venue_id>

  # Get the venue record with the specified venue_id from the database. If not found return 404
  venue = Venue.query.get_or_404(venue_id)

  # Extract the genres as a list of genre names
  genres = [genre.name for genre in venue.genres]

  # Create a dictionary with the necessary venue data
  response_data = {
      "id": venue.id,
      "name": venue.name,
      "genres": genres,
      "address": venue.address,
      "city": venue.city,
      "state": venue.state,
      "phone": venue.phone,
      "website_link": venue.website,
      "facebook_link": venue.facebook_link,
      "seeking_talent": venue.seeking_talent,
      "seeking_description": venue.seeking_description,
      "image_link": venue.image_link
  }
  
  # Create an instance of the form and populate it with response_data 
  form = VenueForm(data=response_data)

  return render_template('forms/edit_venue.html', form=form, venue=response_data)




@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  # Find the venue with the given ID
  venue = Venue.query.get(venue_id)

  if venue:
      # Create an instance of the form and populate it with the submitted data
      form = VenueForm(request.form)
    
      # Set default value for seeking_venue if it's not found in the form data
      if 'seeking_talent' not in request.form:
          form.seeking_talent.data = False
    
      if form.validate():
          try:
              # Update the venue record with the new attributes
              venue.name = form.name.data
              venue.city = form.city.data
              venue.state = form.state.data
              venue.phone = form.phone.data
              venue.seeking_talent  = form.seeking_talent.data 
              venue.seeking_description = form.seeking_description.data
              venue.image_link = form.image_link.data
              venue.website = form.website_link.data
              venue.facebook_link = form.facebook_link.data
            
              # Update the genres for the venue
              genre_names = form.genres.data
              genres = Genre.query.filter(Genre.name.in_(genre_names)).all()
              venue.genres = genres
              
                
              # Commit the changes to the database
              db.session.commit()
    
              # Flash a success message
              flash('Venue successfully updated.')
            
              # Redirect to the venue's detail page
              return redirect(url_for('show_venue', venue_id=venue_id))
        
          except Exception as e:
              # Rollback the changes if an error occurs
              db.session.rollback()
              # Print the exception error
              print(str(e))
              # Flash error message
              flash('An error occurred. Venue ' + venue.name + ' could not be updated.')

      else:
          # Handle the case when the form validation fails
          flash('Form validation failed. Please check your input.')
          return redirect(url_for('edit_venue_submission', venue_id=venue_id, form=form))
  else:
      # Handle the case when the venue with the given ID is not found
      flash('Venue not found.')
      return redirect(url_for('index'))
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Artist record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  form = ArtistForm(request.form)
  
  # Set default value for seeking_venue if it's not found in the form data
  if 'seeking_venue' not in request.form:
      form.seeking_venue.data = False

  if form.validate():
      try:
          # Create a new Artist object with the form data
          # Retrieve the maximum ID value from the database table
          max_id = db.session.query(db.func.max(Artist.id)).scalar()

          # Increment the maximum ID value by 1 to generate the ID for the new venue
          new_id = max_id + 1 if max_id is not None else 1
        
          
        
          # Create a new Artist object with the form data
          artist = Artist(
              id=new_id,
              name=form.name.data,
              city=form.city.data,
              state=form.state.data,
              phone=form.phone.data,
              website=form.website_link.data,
              facebook_link=form.facebook_link.data,
              seeking_venue=form.seeking_venue.data,
              seeking_description=form.seeking_description.data,
              image_link=form.image_link.data
          )

          # Add the genres for the artist
          genre_names = form.genres.data
          genres = Genre.query.filter(Genre.name.in_(genre_names)).all()
          artist.genres = genres

          # Add the artist to the database
          db.session.add(artist)
          db.session.commit()

          # on successful db insert, flash success
          flash('Artist ' + form.name.data + ' was successfully listed!')
          
          return redirect(url_for('index'))
      except Exception as e:
          # Rollback the changes if an error occurs
          db.session.rollback()
          # Print the exception error
          print(str(e))
          # Flash error message
          flash('An error occurred. Artist ' + form.name.data + ' could not be listed.')
  else:
      for field, errors in form.errors.items():
          for error in errors:
              flash(f'Validate error: {field} {error}')

  return render_template('forms/new_artist.html', form=form)


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.

  # Retrieve all Show records from the database
  shows = Show.query.all()

  # Create an empty list to store the formatted show data
  response_data = []

  for show in shows:
        show_data = {
            "venue_id"         : show.venue_id,
            "venue_name"       : show.venue.name,
            "artist_id"        : show.artist_id,
            "artist_name"      : show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time"       : format_datetime(str(show.start_time))
        }
        response_data.append(show_data)

  return render_template('pages/shows.html', shows=response_data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  form = ShowForm(request.form)

  if form.validate():
      try:
          # Create a new Show object with the form data
          # Retrieve the maximum ID value from the database table
          max_id = db.session.query(db.func.max(Show.id)).scalar()

          # Increment the maximum ID value by 1 to generate the ID for the new venue
          new_id = max_id + 1 if max_id is not None else 1
        
        
          # Create a new Show object with the form data
          show = Show(
              id=new_id,
              artist_id =form.artist_id.data,
              venue_id =form.venue_id.data,
              start_time =form.start_time.data
          )

          # Add the show to the database
          db.session.add(show)
          db.session.commit()

          # on successful db insert, flash success
          flash('Form id' + str(new_id) + ' was successfully listed!')
        
          return render_template('pages/home.html')
      except Exception as e:
          # Rollback the changes if an error occurs
          db.session.rollback()
          # Print the exception error
          print(str(e))
          # Flash error message
          flash('An error occurred. Form id ' + str(new_id) + ' could not be listed.')
  else:
      for field, errors in form.errors.items():
          for error in errors:
              flash(f'Validate error: {field} {error}')

  return render_template('forms/new_show.html', form=form)

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
# if __name__ == '__main__':
#     app.run()

# Or specify port manually:
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port)
