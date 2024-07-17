from flask_sqlalchemy import SQLAlchemy

db= SQLAlchemy()


# from app import create_app, db
# from app.models import User

# app = create_app()

# with app.app_context():
#     db.create_all()

#     # Admin credentials
#     admin_username = 'admin'
#     admin_email = 'admin@gmail.com'
#     admin_password = 'admin@123'

#     # Check if the admin already exists
#     existing_admin = User.query.filter_by(role='admin').first()
#     if not existing_admin:
#         # Create superuser admin
#         admin = User(username=admin_username, email=admin_email, role='admin')
#         admin.set_password(admin_password)
#         db.session.add(admin)
#         db.session.commit()
#         print("Admin user created successfully.")
#     else:
#         print("Admin user already exists.")

#     # # Sponsor credentials
#     # sponsor_username = 'sponsor1'
#     # sponsor_email = 'sponsor1@gmail.com'
#     # sponsor_password = 'sp@123'

#     # company_name = 'Sponsor Company'
#     # industry = 'Technology'
#     # budget = 10000.00

#     sponsor = User(
#         username=sponsor_username,
#         email=sponsor_email,
#         role='sponsor',
#         company_name=company_name,
#         industry=industry,
#         budget=budget
#     )
#     sponsor.set_password(sponsor_password)
#     db.session.add(sponsor)
#     db.session.commit()
#     print("Sponsor user created successfully.")

#     # # Influencer credentials
#     # influencer_username = 'influencer1'
#     # influencer_email = 'influencer1@gmail.com'
#     # influencer_password = 'inf@123'
#     # category = 'Lifestyle'
#     # niche = 'Health and Fitness'
#     # reach = 50000

#     influencer = User(
#         username=influencer_username,
#         email=influencer_email,
#         role='influencer',
#         category=category,
#         niche=niche,
#         reach=reach
#     )
#     influencer.set_password(influencer_password)
#     db.session.add(influencer)
#     db.session.commit()
#     print("Influencer user created successfully.")
