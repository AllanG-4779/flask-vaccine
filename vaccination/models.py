from datetime import date
from vaccination import db, login_manager
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from vaccination import app


@login_manager.user_loader
def load_user(id):
    return User.query.get(id)


class User(db.Model, UserMixin):
    id = db.Column(db.String(20), primary_key=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    phone = db.Column(db.String(15), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    first_name = db.Column(db.String(30), nullable=True)
    last_name = db.Column(db.String(30), nullable=True)
    dob = db.Column(db.DATE, nullable=True)
    county = db.Column(db.String(20), nullable=True)
    profile_image = db.Column(db.String(100), default="provided.jpg")
    detail_id = db.relationship('Vaccination_Detail', backref="detail", uselist=False)
    is_admin = db.Column(db.Boolean, default=False)
    email_confirmed = db.Column(db.Boolean, default=False)

    # incharge of issuing security tokens once request sent
    def request_token(self, expiry=3600 * 24):
        serializer = Serializer(app.config['SECRET_KEY'], expiry)
        return serializer.dumps({'user_id': self.id}).decode('utf-8')

    def verify_token(token):
        try:
            serializer = Serializer(app.config['SECRET_KEY'])
            id = serializer.loads(token).get('user_id')
        except:
            return None
        return User.query.get(id)

    #     To make the object readable and show its class, we'll use the __repr__ method
    #     However to make the object readable, make use of the __str__ but it won't show the origin class
    def __repr__(self):
        return f'{self.id} email of {self.email}'


class Vaccine(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    origin = db.Column(db.String(40), nullable=False)
    doses_req = db.Column(db.Integer, nullable=False)
    dose_time = db.Column(db.Integer, nullable=False, comment="Days taken before the next dose")
    # the backref parameter in the relationship will create a fake column that will not be visible
    #  in the database that will hold all the details containing the said vaccine
    administered_to = db.relationship("Vaccination_Detail", backref="users", lazy=True)


class Vaccination_Detail(db.Model):
    detail_id = db.Column(db.Integer, autoincrement=True, nullable=False, primary_key=True)
    vaccine_id = db.Column(db.Integer, db.ForeignKey('vaccine.id'), nullable=False)
    user_id = db.Column(db.String(20), db.ForeignKey('user.id'), nullable=False, unique=True)
    dose_date = db.Column(db.DATE(), default=date.today(), nullable=False)
    dose_count = db.Column(db.Integer, default=0, nullable=False)

    def __repr__(self):
        return f'{self.user_id} {self.vaccine_id} on {self.dose_date}'
