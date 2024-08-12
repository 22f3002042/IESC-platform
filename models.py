from datetime import datetime
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()
from db import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, autoincrement=True,primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # 'admin', 'sponsor', 'influencer'
    flagged = db.Column(db.Boolean, default=False)
    unflag_request = db.Column(db.String(500), nullable=False)                  
    
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
    status = db.Column(db.String(50), nullable=False)
    goals = db.Column(db.Text, nullable=True)
    sponsor_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    is_flagged = db.Column(db.Boolean, default=False)
    
    sponsor = db.relationship('User', backref=db.backref('campaigns', lazy=True, cascade='all, delete-orphan'))
    ad_requests = db.relationship('AdRequest', back_populates='campaign', lazy=True, cascade='all, delete-orphan')

    def progress(self):
        total_ads_required = sum(ad_request.ads_required for ad_request in self.ad_requests)
        total_ads_completed = sum(ad_request.ads_completed for ad_request in self.ad_requests)
        
        if total_ads_required == 0:
            return 0
        
        return int((total_ads_completed / total_ads_required) * 100)


class AdRequest(db.Model):
    __tablename__ = 'ad_requests'

    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.id', ondelete='CASCADE'), nullable=False)
    influencer_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    sponsor_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    details = db.Column(db.Text, nullable=True)
    payment_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), nullable=False, default='Pending')  # pending, accepted, rejected, completed
    ads_required = db.Column(db.Integer, nullable=False, default=1)
    ads_completed = db.Column(db.Integer, nullable=False, default=0)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    campaign = db.relationship('Campaign', back_populates='ad_requests')
    influencer = db.relationship('User', foreign_keys=[influencer_id])
    sponsor = db.relationship('User', foreign_keys=[sponsor_id])
