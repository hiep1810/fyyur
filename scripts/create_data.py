from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Table, ForeignKey, Boolean, DateTime, MetaData
from sqlalchemy.orm import sessionmaker, relationship, backref
from sqlalchemy.ext.declarative import declarative_base

# Define the database engine
SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:abc@localhost:5432/fyyur'
engine = create_engine(SQLALCHEMY_DATABASE_URI)

# Create a MetaData object and reflect the existing database tables
metadata = MetaData(bind=engine)
metadata.reflect()

# Drop all tables
metadata.drop_all()

# Create the base class
Base = declarative_base()

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

# Define two many-to-many relationship tables: ArtistGenre, VenueGenre
ArtistGenre =  Table('ArtistGenre',
     Base.metadata,
     Column('genre_id' ,  Integer,  ForeignKey('Genre.id') , primary_key=True),
     Column('artist_id',  Integer,  ForeignKey('Artist.id', ondelete="CASCADE"), primary_key=True)
)

VenueGenre =  Table('VenueGenre',
     Base.metadata,
     Column('genre_id',  Integer,  ForeignKey('Genre.id'), primary_key=True),
     Column('venue_id',  Integer,  ForeignKey("Venue.id", ondelete="CASCADE"), primary_key=True)
)

# Define the Venue class
class Venue(Base):
    __tablename__ = 'Venue'

    # Define the columns of the Venue table
    id =  Column( Integer, primary_key=True)
    name =  Column( String)
    city =  Column( String(120))
    state =  Column( String(120))
    address =  Column( String(120))
    phone =  Column( String(120))
    website =  Column( String(120))
    facebook_link =  Column( String(120))
    seeking_talent =  Column( Boolean)
    seeking_description =  Column( String(120))
    image_link =  Column( String(500))

    # Define the relationship with the Genre table through the VenueGenre table
    genres =  relationship('Genre',\
                              secondary=VenueGenre,\
                              passive_deletes=True,\
                              backref= backref('venues'))
    # Define the relationship with the Show table
    shows = relationship('Show', backref='venue', lazy=True)

    # Define the string representation of a Venue object
    def __repr__(self):
        return f'<Venue {self.id} {self.name}>'
    

# Define the Artist class
class Artist(Base):
    __tablename__ = 'Artist'

    # Define the columns of the Artist table
    id =  Column( Integer, primary_key=True)
    name =  Column( String)
    city =  Column( String(120))
    state =  Column( String(120))
    phone =  Column( String(120))
    image_link =  Column( String(500))
    facebook_link =  Column( String(120))
    website =  Column( String(120))
    seeking_venue =  Column( Boolean, default=False)
    seeking_description =  Column( String(120))

    # Define the relationship with the Show table
    shows = relationship('Show', backref='artist', lazy=True)
    
    # Define the relationship with the Genre table through the ArtistGenre table 
    genres =  relationship('Genre',\
                              secondary=ArtistGenre,\
                              passive_deletes=True,\
                              backref= backref('artists'))
    
    # Define the string representation of an Artist object
    def __repr__(self):
        return f'<Artist {self.id} {self.name}>'
    
# Define the Genre class
class Genre(Base):
    __tablename__ = 'Genre'

    # Define the columns of the Genre table
    id =  Column( Integer, primary_key=True)
    name =  Column( String(120))

    
# Define the Show class
class Show(Base):
    __tablename__ = 'Show'

    # Define the columns of the Show table
    id =  Column( Integer, primary_key=True)
    start_time =  Column( DateTime)
    
    # Define the relationship with the Artist table 
    artist_id =  Column( Integer,  ForeignKey('Artist.id'), nullable=False)
    
    # Define the relationship with the Venue table 
    venue_id =  Column( Integer,  ForeignKey('Venue.id'), nullable=False)


    # Define the string representation of a Show object
    def __repr__(self):
        return f'<Show {self.id} artist_id={self.artist_id} venue_id={self.venue_id}>'


    
    

#----------------------------------------------------------------------------#
# Data.
#----------------------------------------------------------------------------#

# Create the tables
Base.metadata.create_all(engine)   


# Create a session factory and open a session
Session = sessionmaker(bind=engine)
session = Session()


#---------------------*
# Genre
#---------------------*

# The genres list contains a collection of different music genres.   
genres = [
    'Alternative',
    'Blues',
    'Classical',
    'Country',
    'Electronic',
    'Folk',
    'Funk',
    'Hip-Hop',
    'Heavy Metal',
    'Instrumental',
    'Jazz',
    'Musical Theatre',
    'Pop',
    'Punk',
    'R&B',
    'Reggae',
    'Rock n Roll',
    'Soul',
    'Other'
]

# Insert genre into the table Genres
for genre_name in genres:
    genre = Genre(name=genre_name)
    session.add(genre)


    
#---------------------*
# Venue
#---------------------*

venue_1_data={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
    "past_shows": [{
      "artist_id": 4,
      "artist_name": "Guns N Petals",
      "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
      "start_time": "2019-05-21T21:30:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }
venue_2_data={
    "id": 2,
    "name": "The Dueling Pianos Bar",
    "genres": ["Classical", "R&B", "Hip-Hop"],
    "address": "335 Delancey Street",
    "city": "New York",
    "state": "NY",
    "phone": "914-003-1132",
    "website": "https://www.theduelingpianos.com",
    "facebook_link": "https://www.facebook.com/theduelingpianos",
    "seeking_talent": False,
    "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
    "past_shows": [],
    "upcoming_shows": [],
    "past_shows_count": 0,
    "upcoming_shows_count": 0,
  }
venue_3_data={
    "id": 3,
    "name": "Park Square Live Music & Coffee",
    "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
    "address": "34 Whiskey Moore Ave",
    "city": "San Francisco",
    "state": "CA",
    "phone": "415-000-1234",
    "website": "https://www.parksquarelivemusicandcoffee.com",
    "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
    "seeking_talent": False,
    "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    "past_shows": [{
      "artist_id": 5,
      "artist_name": "Matt Quevedo",
      "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
      "start_time": "2019-06-15T23:00:00.000Z"
    }],
    "upcoming_shows": [{
      "artist_id": 6,
      "artist_name": "The Wild Sax Band",
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": "2035-04-01T20:00:00.000Z"
    }, {
      "artist_id": 6,
      "artist_name": "The Wild Sax Band",
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": "2035-04-08T20:00:00.000Z"
    }, {
      "artist_id": 6,
      "artist_name": "The Wild Sax Band",
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": "2035-04-15T20:00:00.000Z"
    }],
    "past_shows_count": 1,
    "upcoming_shows_count": 1,
  }


# Create a new Venue instance and populate its attributes with venue_1 data
venue_1 = Venue(
    id=venue_1_data['id'],
    name=venue_1_data['name'],
    address=venue_1_data['address'],
    city=venue_1_data['city'],
    state=venue_1_data['state'],
    phone=venue_1_data['phone'],
    website=venue_1_data['website'],
    facebook_link=venue_1_data['facebook_link'],
    seeking_talent=venue_1_data['seeking_talent'],
    seeking_description=venue_1_data['seeking_description'],
    image_link=venue_1_data['image_link']
)

# Match the genres for the venue_1
for genre_name in venue_1_data['genres']:
    genre = session.query(Genre).filter_by(name=genre_name).first()
    if genre:
        venue_1.genres.append(genre)
        

# Create a new Venue instance and populate its attributes with venue_2 data
venue_2 = Venue(
    id=venue_2_data['id'],
    name=venue_2_data['name'],
    address=venue_2_data['address'],
    city=venue_2_data['city'],
    state=venue_2_data['state'],
    phone=venue_2_data['phone'],
    website=venue_2_data['website'],
    facebook_link=venue_2_data['facebook_link'],
    seeking_talent=venue_2_data['seeking_talent'],
    image_link=venue_2_data['image_link']
)

# Match the genres for the venue_2
for genre_name in venue_2_data['genres']:
    genre = session.query(Genre).filter_by(name=genre_name).first()
    if genre:
        venue_2.genres.append(genre)
        

# Create a new Venue instance and populate its attributes with venue_3 data
venue_3= Venue(
    id=venue_3_data['id'],
    name=venue_3_data['name'],
    city=venue_3_data['city'],
    state=venue_3_data['state'],
    address=venue_3_data['address'],
    phone=venue_3_data['phone'],
    website=venue_3_data['website'],
    facebook_link=venue_3_data['facebook_link'],
    seeking_talent=venue_3_data['seeking_talent'],
    image_link=venue_3_data['image_link']
)
# Match the genres for the venue_3
for genre_name in venue_3_data['genres']:
    genre = session.query(Genre).filter_by(name=genre_name).first()
    if genre:
        venue_3.genres.append(genre)


# Add the Venue instances to the session and commit the changes
session.add(venue_1)
session.add(venue_2)
session.add(venue_3)
session.commit()

    
    
    
    
#---------------------*
# Artist
#---------------------*
    
artist_1_data={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "past_shows": [{
      "venue_id": 1,
      "venue_name": "The Musical Hop",
      "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
      "start_time": "2019-05-21T21:30:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }
artist_2_data = {
    "id": 5,
    "name": "Matt Quevedo",
    "genres": ["Jazz"],
    "city": "New York",
    "state": "NY",
    "phone": "300-400-5000",
    "facebook_link": "https://www.facebook.com/mattquevedo923251523",
    "seeking_venue": False,
    "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    "past_shows": [{
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2019-06-15T23:00:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }
artist_3_data = {
    "id": 6,
    "name": "The Wild Sax Band",
    "genres": ["Jazz", "Classical"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "432-325-5432",
    "seeking_venue": False,
    "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "past_shows": [],
    "upcoming_shows": [{
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-01T20:00:00.000Z"
    }, {
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-08T20:00:00.000Z"
    }, {
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-15T20:00:00.000Z"
    }],
    "past_shows_count": 0,
    "upcoming_shows_count": 3,
  }

# Create a new Artist instance and populate its attributes with artist_1 data
artist_1 = Artist(
    id=artist_1_data["id"],
    name=artist_1_data["name"],
    city=artist_1_data["city"],
    state=artist_1_data["state"],
    phone=artist_1_data["phone"],
    image_link=artist_1_data["image_link"],
    facebook_link=artist_1_data["facebook_link"],
    seeking_venue=artist_1_data["seeking_venue"],
    seeking_description=artist_1_data["seeking_description"]
)

# Match the genres for the artist_1
for genre_name in artist_1_data['genres']:
    genre = session.query(Genre).filter_by(name=genre_name).first()
    if genre:
        artist_1.genres.append(genre)

        
# Create a new Artist instance and populate its attributes with artist_2 data
artist_2 = Artist(
    id=artist_2_data["id"],
    name=artist_2_data["name"],
    city=artist_2_data["city"],
    state=artist_2_data["state"],
    phone=artist_2_data["phone"],
    image_link=artist_2_data["image_link"],
    facebook_link=artist_2_data["facebook_link"],
    seeking_venue=artist_2_data["seeking_venue"]
)

# Match the genres for the artist_2
for genre_name in artist_2_data['genres']:
    genre = session.query(Genre).filter_by(name=genre_name).first()
    if genre:
        artist_2.genres.append(genre)
        
        
# Create a new Artist instance and populate its attributes with artist_3 data
artist_3 = Artist(
    id=artist_3_data["id"],
    name=artist_3_data["name"],
    city=artist_3_data["city"],
    state=artist_3_data["state"],
    phone=artist_3_data["phone"],
    image_link=artist_3_data["image_link"],
    seeking_venue=artist_3_data["seeking_venue"]
)

# Match the genres for the artist_3
for genre_name in artist_3_data['genres']:
    genre = session.query(Genre).filter_by(name=genre_name).first()
    if genre:
        artist_3.genres.append(genre)
        

# Add the Artist instances to the session and commit the changes
session.add(artist_1)
session.add(artist_2)
session.add(artist_3)
session.commit()




#---------------------*
# Show
#---------------------*

shows=[{
    "venue_id": 1,
    "venue_name": "The Musical Hop",
    "artist_id": 4,
    "artist_name": "Guns N Petals",
    "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "start_time": "2019-05-21T21:30:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 5,
    "artist_name": "Matt Quevedo",
    "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    "start_time": "2019-06-15T23:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-01T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-08T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-15T20:00:00.000Z"
  }]    

# Loop through the data and insert into the Show table
for show_data in shows:
    show = Show(
        venue_id=show_data['venue_id'],
        artist_id=show_data['artist_id'],
        start_time=datetime.strptime(show_data['start_time'], '%Y-%m-%dT%H:%M:%S.%fZ')
    )
    # Add the Show instances to the session
    session.add(show)

# Commit the changes to the database
session.commit()    


