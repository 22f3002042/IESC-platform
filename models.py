# from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
# from flask_sqlalchemy import SQLAlchemy

# db = SQLAlchemy()
from db import db

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, autoincrement=True,primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # 'admin', 'sponsor', 'influencer'
    # created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Sponsor-specific fields
    company_name = db.Column(db.String(100), nullable=True)
    industry = db.Column(db.String(100), nullable=True)
    budget = db.Column(db.Float, nullable=True)

    # Influencer-specific fields
    category = db.Column(db.String(100), nullable=True)
    niche = db.Column(db.String(100), nullable=True)
    reach = db.Column(db.Integer, nullable=True)


class Campaign(db.Model):
    __tablename__ = 'campaigns'

    id = db.Column(db.Integer, primary_key=True)
    Title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(400), nullable=False)
    Niche = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    budget = db.Column(db.Float, nullable=False)
    visibility = db.Column(db.String(50), nullable=False)

