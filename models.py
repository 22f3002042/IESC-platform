# from werkzeug.security import generate_password_hash, check_password_hash
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
    flagged_notification = db.Column(db.Boolean, default=False)
    unflag_request = db.Column(db.String(500), nullable=False)                   # to uflag mesg
    
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
    goals = db.Column(db.Text, nullable=True)
    sponsor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_flagged = db.Column(db.Boolean, default=False)
    

    sponsor = db.relationship('User', backref=db.backref('campaigns', lazy=True))
    ad_requests = db.relationship('AdRequest', backref='campaigns', lazy=True)

    def progress(self):
        total_ads_required = sum(ad_request.ads_required for ad_request in self.ad_requests)
        total_ads_completed = sum(ad_request.ads_completed for ad_request in self.ad_requests)
        
        if total_ads_required == 0:
            return 0
        
        return int((total_ads_completed / total_ads_required) * 100)

   

class AdRequest(db.Model):
    __tablename__ = 'ad_requests'

    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.id'), nullable=False)
    influencer_id = db.Column(db.Integer, db.ForeignKey('users.id'),  nullable=False)
    sponsor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    details = db.Column(db.Text, nullable=True)
    ads_required = db.Column(db.Integer, nullable=False, default=1)
    ads_completed = db.Column(db.Integer, nullable=False, default=0)
    payment_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), nullable=False, default='pending')  # pending, approved, rejected, accepted, completed
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    campaign = db.relationship('Campaign', back_populates='ad_requests')
    influencer = db.relationship('User', foreign_keys=[influencer_id])
    sponsor = db.relationship('User', foreign_keys=[sponsor_id])



    


# class AdRequest(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)
#     influencer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
#     requirements = db.Column(db.String(500), nullable=False)
#     payment_amount = db.Column(db.Float, nullable=False)
#     status = db.Column(db.String(50), default='pending')
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)
#     updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

#     campaign = db.relationship('Campaign', back_populates='ad_requests')
#     influencer = db.relationship('User', back_populates='ad_requests')















# class Campaign(db.Model):
#     __tablename__ = 'campaigns'

#     id = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String(200), nullable=False)
#     description = db.Column(db.String(400), nullable=False)
#     niche = db.Column(db.String(100), nullable=True )
#     start_date = db.Column(db.Date, nullable=False)
#     end_date = db.Column(db.Date, nullable=False)
#     budget = db.Column(db.Float, nullable=False)
#     visibility = db.Column(db.String(50), nullable=False)  # public or private
#     status = db.Column(db.String(50), nullable=False, default='ongoing')  # ongoing, completed, etc.
#     goals = db.Column(db.Text, nullable=True)
#     sponsor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
#     is_flagged = db.Column(db.Boolean, default=False)

#     sponsor = db.relationship('User', backref=db.backref('sponsored_campaigns', lazy=True))
#     ad_requests = db.relationship('AdRequest', backref='campaign', lazy=True)

#     def progress(self):
#         total_requests = len(self.ad_requests)
#         if total_requests == 0:
#             return 0
#         completed_requests = len([ar for ar in self.ad_requests if ar.status == 'completed'])
#         return int((completed_requests / total_requests) * 100)

# class AdRequest(db.Model):
#     __tablename__ = 'ad_requests'

#     id = db.Column(db.Integer, primary_key=True)
#     campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.id'), nullable=False)
#     influencer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
#     messages = db.Column(db.Text, nullable=True)
#     requirements = db.Column(db.Text, nullable=False)
#     payment_amount = db.Column(db.Float, nullable=False)
#     status = db.Column(db.String(50), nullable=False, default='pending')  # pending, approved, rejected, accepted, completed
#     updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

#     influencer = db.relationship('User', backref=db.backref('influencer_ad_requests', lazy=True))

    
