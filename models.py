from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

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
