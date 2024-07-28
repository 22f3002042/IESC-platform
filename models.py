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
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(400), nullable=False)
    niche = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    budget = db.Column(db.Float, nullable=False)
    visibility = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), nullable=False, default='ongoing')
    sponsor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    sponsor = db.relationship('User', backref='sponsored_campaigns', foreign_keys=[sponsor_id])
    ad_requests = db.relationship('AdRequest', backref='related_campaign', lazy=True)

    def __repr__(self):
        return f'<Campaign {self.title}>'

class AdRequest(db.Model):
    __tablename__ = 'ad_requests'

    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.id'), nullable=False)
    influencer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(50), nullable=False, default='pending')  # pending, approved, rejected
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    campaign = db.relationship('Campaign', backref=db.backref('all_ad_requests', lazy=True))
    influencer = db.relationship('User', backref=db.backref('influencer_ad_requests', lazy=True), foreign_keys=[influencer_id])

    def __repr__(self):
        return f'<AdRequest {self.id} - Campaign: {self.campaign.title}, Influencer: {self.influencer.username}>'
