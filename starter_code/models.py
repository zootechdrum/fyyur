import os

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, DateTime
from flask_migrate import Migrate
from sqlalchemy.orm import relationship, backref

database_name = "fyurr"
database_path = "postgres://{}@{}/{}".format('zootechdrum','localhost:5432', database_name)

db = SQLAlchemy()
#'postgres://zootechdrum@localhost:5432/fyurr'
def setup_db(app, database_path=database_path):
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = database_path
    db.init_app(app)
    migrate = Migrate(app, db)
    

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    city = db.Column(db.String(100))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(100))
    seeking_talent = db.Column(db.BOOLEAN)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    seeking_description = db.Column(db.String(120))
    shows = db.relationship('Shows', backref='Venue', passive_deletes=True, lazy=True)

    def __repr__(self):
      return f'<Venue {self.id} {self.name} {self.address}>'

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_description = db.Column(db.String(120))
    seeking_venue = db.Column(db.BOOLEAN)
    website = db.Column(db.String(120))
    shows = db.relationship('Shows', backref='Artist', passive_deletes=True, lazy=True)


class Shows(db.Model):
    __tablename__ = 'Show'

      # Foreign Keys
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id', ondelete="CASCADE"))
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id', ondelete="CASCADE"))
    start_time = db.Column(db.DateTime)
                