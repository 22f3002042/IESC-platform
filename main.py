from flask import Flask,render_template,request, redirect, url_for, session, flash
from db import db
from datetime import datetime
from models import User, Campaign,AdRequest


app = Flask(__name__)

app.config['SECRET_KEY'] = 'this_is_person_project.'
app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///iesc.db"
db.init_app(app)



@app.route("/homepage")
def homepage():
    if 'user_role' in session and session['user_role'] == 'admin':
        return redirect(url_for('admin_dash'))

    elif 'user_role' in session and session['user_role'] == 'sponsor':
        return redirect(url_for('sponsor_dash'))

    elif 'user_role' in session and session['user_role'] == 'influencer':
        return redirect(url_for('sponsor_dash'))
    else:
        return render_template("home.html")

@app.route("/")
def index():
    return redirect(url_for('homepage'))

@app.route("/base")
def base():
    return render_template("base.html")






#new login framwork
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        
        if user and user.password == password: 
            # User authenticated, store user info in session
            session['user_id'] = user.id
            session['username'] = user.username 
            session['user_role'] = user.role
            session['email'] = user.email  
            
            if user.flagged and user.flagged_notification:
                flash("You have been flagged by the admin. Please contact support for more information.", "warning")
                user.flagged_notification = False  # Reset notification flag
                db.session.commit()


            if user.role == 'admin':
                return redirect(url_for('admin_dash'))
                flash(f'Welcome back Admin- {username}', 'success')
            elif user.role == 'sponsor':
                return redirect(url_for('sponsor_dash'))
                flash(f'Welcome back Sponsor- {username}', 'success')
            elif user.role == 'influencer':
                return redirect(url_for('influencer_dash'))
                flash(f'Welcome back Influencer- {username}', 'success')
        else:
            flash('Please Enter correct Email and Passsword', 'danger')

    return render_template('login.html')

@app.route('/sponsor_signup', methods=['GET', 'POST'])
def sponsor_signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        company_name = request.form['company_name']
        industry = request.form['industry']
        budget = float(request.form['budget'])

        # Check for email exist
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('This Email account already exist! Try different email.', 'danger')
            return redirect(url_for('sponsor_signup'))
        
        user = User(username=username, email=email, password=password, role='sponsor', company_name=company_name, industry=industry, budget=budget)
        db.session.add(user)
        db.session.commit()
        flash(f'Hey {username}  your account created successfully. Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('/sponsor/sponsor_signup.html')

@app.route('/influencer_signup', methods=['GET', 'POST'])
def influencer_signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        category = request.form['category']
        niche = request.form['niche']
        reach = int(request.form['reach'])

        # Check for email exist
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('This Emails account already exist! Try different email.', 'danger')
            return redirect(url_for('/influencer/influencer_signup'))
        
        user = User(username=username, email=email, password=password, role='influencer', category=category, niche=niche, reach=reach)
        db.session.add(user)
        db.session.commit()
        flash(f'Hey {username}  your account created successfully. Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('/influencer/influencer_signup.html')

#session Logout
@app.route('/logout')
def logout():
    username = session.get('username')
    session.clear()
    flash(f'{username} - you have been logged out', 'danger')
    return redirect(url_for('homepage'))





#                                   #########                   Admin  route            ############
@app.route('/admin_dash')
def admin_dash():
    if 'user_role' in session and session['user_role'] == 'admin':
        username = session.get('username')
        flash(f'Welcome back Admin - {username} ','success')
        return render_template('/admin/admin_dash.html',username=username)
    else:
        flash('Please log in first!', 'danger')
        return redirect(url_for('homepage'))


@app.route('/admin_profile')
def admin_profile():
    if 'user_id' not in session or session['user_role'] != 'admin':
        flash('You need to be logged in as an admin to view this page.', 'danger')
        return redirect(url_for('login'))

    admin = User.query.get(session['user_id'])
    return render_template('admin/admin_profile.html', admin=admin)

@app.route('/admin/edit_admin_profile', methods=['POST'])
def edit_admin_profile():
    if 'user_id' not in session or session['user_role'] != 'admin':
        flash('You need to be logged in as an admin to edit this profile.', 'danger')
        return redirect(url_for('login'))

    admin = User.query.get(session['user_id'])

    username = request.form['username']
    email = request.form['email']
    password = request.form['password']

    admin.username = username
    admin.email = email

    if password:
        admin.password = password

    db.session.commit()

    flash('Profile updated successfully!', 'success')
    return redirect(url_for('admin_profile'))

@app.route('/admin/manage_users')
def manage_users():
    influencers = User.query.filter_by(role='influencer').all()
    sponsors = User.query.filter_by(role='sponsor').all()
    flagged_users = User.query.filter_by(flagged=True).all()
    unflag_requests = User.query.filter(User.unflag_request.isnot(None)).all()

    return render_template('/admin/manage_users.html', influencers=influencers, sponsors=sponsors, flagged_users=flagged_users, unflag_requests=unflag_requests)





@app.route('/admin/users/flag/<user_id>', methods=['POST'])
def flag_user(user_id):
    user = User.query.get(user_id)
    if user:
        user.flagged = True
        # user.flagged_notification = True
        db.session.commit()
        flash(f'{user.username} has been flagged.', 'warning')
    else:
        flash('User not found.', 'danger')

    return redirect(url_for('manage_users'))

@app.route('/admin/users/unflag/<user_id>', methods=['POST'])
def unflag_user(user_id):
    user = User.query.get(user_id)
    unflag_requests = User.query.filter(User.unflag_request.isnot(None)).all()
    if user.flagged:
        user.flagged = False
        user.unflag_request = None
        db.session.commit()
        flash(f"User {user.username} has been unflagged.", "success")
    else:
        flash(f"User {user.username} is not flagged.", "info")

    return redirect(url_for('manage_users'))

@app.route('/admin/users/delete/<user_id>', methods=['POST'])
def delete_user(user_id):
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        flash(f'{user.username} has been deleted.', 'success')
    else:
        flash('User not found.', 'danger')

    return redirect(url_for('manage_users'))

@app.route('/request_unflag', methods=['GET', 'POST'])
def request_unflag():

    user = User.query.get(session['user_id'])

    if request.method == 'POST':
        user.unflag_request = request.form['unflag_request']
        
        db.session.commit()
        flash('Your unflag request has been submitted.', 'success')
        return redirect(url_for('sponsor_profile'))

    return render_template('request_unflag.html', user=user)

@app.route('/admin/unflag_requests')
def admin_unflag_requests():
    if 'user_id' not in session or session['user_role'] != 'admin':
        return redirect(url_for('homepage'))

    requests = User.query.filter(User.unflag_request.isnot(None)).all()
    influencers = User.query.filter_by(role='influencer').all()
    sponsors = User.query.filter_by(role='sponsor').all()
    flagged_users = User.query.filter_by(flagged=True).all()
    return render_template('admin/manage_users.html', requests=requests, influencers=influencers, sponsors=sponsors, flagged_users=flagged_users)

@app.route('/admin/approve_unflag/<int:user_id>', methods=['POST'])
def approve_unflag(user_id):
    if 'user_id' not in session or session['user_role'] != 'admin':
        return redirect(url_for('homepage'))

    user = User.query.get_or_404(user_id)
    user.flagged = False
    user.unflag_request = None
    db.session.commit()

    flash(f'User {user.username} has been unflagged successfully!', 'success')
    return redirect(url_for('admin_unflag_requests'))

########################################## campaigns  ####################

@app.route('/admin/campaigns', methods=['GET'])
def manage_campaigns():
    campaigns = Campaign.query.all()
    flagged_campaigns = Campaign.query.filter_by(is_flagged=True).all()
    return render_template('/admin/admin_campaigns.html', campaigns=campaigns, flagged_campaigns=flagged_campaigns)


@app.route('/admin/campaigns/flag/<campaign_id>', methods=['POST'])
def flag_campaign(campaign_id):
    if 'user_id' not in session or session['user_role'] != 'admin':
        flash('You need to be logged in as an admin to flag the campaigns.', 'danger')
        return redirect(url_for('login'))

    campaign = Campaign.query.get(campaign_id)
    campaign.is_flagged = True
    db.session.commit()
    flash(f"Campaign '{campaign.title}' has been flagged.", "warning")
    return redirect(url_for('manage_campaigns'))

# @app.route('/admin/flagged_campaigns', methods=['GET'])
# def manage_flagged_campaigns():
#     if 'user_id' not in session or session['user_role'] != 'admin':
#         flash('You need to be logged in as an admin to access this page.', 'danger')
#         return redirect(url_for('login'))
    
#     flagged_campaigns = Campaign.query.filter_by(is_flagged=True).all()
#     return render_template('manage_campaigns', flagged_campaigns=flagged_campaigns)

@app.route('/admin/flagged_campaigns/unflag/<int:campaign_id>', methods=['POST'])
def unflag_campaign(campaign_id):
    if 'user_id' not in session or session['user_role'] != 'admin':
        flash('You need to be logged in as an admin to perform this action.', 'danger')
        return redirect(url_for('login'))

    campaign = Campaign.query.get_or_404(campaign_id)
    campaign.is_flagged = False
    db.session.commit()
    flash(f"Campaign '{campaign.title}' has been unflagged.", "success")
    return redirect(url_for('manage_campaigns'))


@app.route('/admin/flagged_campaigns/delete/<int:campaign_id>', methods=['POST'])
def delete_flagged_campaign(campaign_id):
    if 'user_id' not in session or session['user_role'] != 'admin':
        flash('You need to be logged in as an admin to perform this action.', 'danger')
        return redirect(url_for('login'))

    campaign = Campaign.query.get_or_404(campaign_id)
    db.session.delete(campaign)
    db.session.commit()
    flash(f"Campaign '{campaign.title}' has been deleted.", "danger")
    return redirect(url_for('manage_campaigns'))
########################################################################################################################






# Sponsor  route
@app.route('/sponsor_dash')
def sponsor_dash():
    if 'user_role' in session and session['user_role'] == 'sponsor':
        username = session.get('username')
        flash(f'Welcome back Sponsor - {username} ','success')
        return render_template('/sponsor/sponsor_dash.html')
    else:
        flash('Please log in first!', 'danger')
        return redirect(url_for('homepage'))

@app.route("/sponsor_profile")
def sponsor_profile():
    sponsor = User.query.get(session['user_id'])

    session['username'] = sponsor.username
    session['email'] = sponsor.email
    session['company_name'] = sponsor.company_name
    session['industry'] = sponsor.industry
    session['budget'] = sponsor.budget
    session['unflag_request'] = sponsor.unflag_request

    return render_template('/sponsor/sponsor_profile.html', sponsor=sponsor)

@app.route('/edit_profile', methods=['POST'])
def edit_profile():
    sponsor = User.query.get(session['user_id'])
    
    sponsor.username = request.form['username']
    sponsor.email = request.form['email']
    sponsor.company_name = request.form['company_name']
    sponsor.industry = request.form['industry']
    sponsor.budget = request.form['budget']
    
    db.session.commit()

    session['username'] = sponsor.username
    session['email'] = sponsor.email
    session['company_name'] = sponsor.company_name
    session['industry'] = sponsor.industry
    session['budget'] = sponsor.budget

    flash('Profile updated successfully!', 'success')
    return redirect(url_for('sponsor_profile'))


@app.route('/sponsor/campaigns', methods=['GET', 'POST'])
def sponsor_campaigns():
    if 'user_id' not in session or session['user_role'] != 'sponsor':
        flash('You need to be logged in as a sponsor to create a campaign.', 'danger')
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        niche = request.form['niche']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        budget = request.form['budget']
        visibility = request.form['visibility']
        status = request.form['status']
        goals = request.form['goals']


        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()        

        new_campaign = Campaign(
            title=title,
            description=description,
            niche=niche,
            start_date=start_date,
            end_date=end_date,
            budget=budget,
            visibility=visibility,
            status=status,
            goals=goals,
            sponsor_id=session['user_id']
        )
        db.session.add(new_campaign)
        db.session.commit()
        flash('Campaign created successfully!', 'success')
        return redirect(url_for('sponsor_campaigns'))

    # Fetch campaigns for the sponsor
    public_campaigns = Campaign.query.filter_by(visibility='public').all()
    private_campaigns = Campaign.query.filter_by(visibility='private').all()
    return render_template('/sponsor/sponsor_campaigns.html', public_campaigns=public_campaigns, private_campaigns=private_campaigns)

@app.route('/campaign/<int:campaign_id>/view')
def view_campaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    return render_template('sponsor/view_campaign.html', campaign=campaign)

@app.route('/sponsor/campaigns/<int:campaign_id>/edit', methods=['GET', 'POST'])
def edit_campaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    if campaign.sponsor_id != session['user_id']:
        flash('Access denied', 'danger')
        return redirect(url_for('sponsor_campaigns'))

    if request.method == 'POST':
        campaign.title = request.form['title']
        campaign.description = request.form['description']
        campaign.niche = request.form['niche']
        campaign.start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d').date()
        campaign.end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d').date()
        campaign.budget = request.form['budget']
        campaign.visibility = request.form['visibility']
        db.session.commit()

        flash('Campaign updated successfully!', 'success')
        return redirect(url_for('sponsor_campaigns'))
    
    return render_template('/sponsor/edit_campaign.html', campaign=campaign)

@app.route('/sponsor/campaigns/<int:campaign_id>/delete', methods=['POST'])
def delete_campaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    db.session.delete(campaign)
    db.session.commit()
    flash('Campaign deleted successfully!', 'success')
    return redirect(url_for('sponsor_campaigns'))

@app.route('/sponsor/campaigns/<int:campaign_id>/ad_requests', methods=['GET', 'POST'])
def manage_ad_requests(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    if request.method == 'POST':
        # Create a new ad request
        influencer_id = request.form['influencer_id']
        requirements = request.form['requirements']
        payment_amount = request.form['payment_amount']
        new_ad_request = AdRequest(
            campaign_id=campaign_id,
            influencer_id=influencer_id,
            requirements=requirements,
            payment_amount=payment_amount
        )
        db.session.add(new_ad_request)
        db.session.commit()
        flash('Ad request created successfully!', 'success')
        return redirect(url_for('manage_ad_requests', campaign_id=campaign_id))
    
    # Fetch ad requests for the campaign
    ad_requests = AdRequest.query.filter_by(campaign_id=campaign_id).all()
    return render_template('manage_ad_requests.html', campaign=campaign, ad_requests=ad_requests)



@app.route("/sponsor_stats")
def sponsor_stats():
    return render_template("sponsor/sponsor_stats.html")

@app.route('/sponsor/influencers')
def sponsor_influencer():
    influencers = User.query.filter_by(role='influencer').all()
    return render_template('/sponsor/search_influencer.html', influencers=influencers)





# @app.route('/campaign/<campaign_id>/submit_ad_request', methods=['GET','POST'])
# def submit_ad_request(campaign_id):
#     if 'user_id' not in session or session['user_role'] != 'influencer':
#         flash('You need to be logged in as an influencer to submit an ad request.', 'danger')
#         return redirect(url_for('login'))

#     if request.method == 'POST':
#         submission = request.form['submission']
#         new_ad_request = AdRequest(
#             campaign_id=campaign_id,
#             influencer_id=session['user_id'],
#             status='pending'
#         )

#         db.session.add(new_ad_request)
#         db.session.commit()

#         flash('Ad request submitted successfully!', 'success')
#         return redirect(url_for('view_campaign', campaign_id=campaign_id))

#     campaign = Campaign.query.get_or_404(campaign_id)
#     return render_template('submit_ad_request.html', campaign=campaign)

# @app.route('/campaign/<int:campaign_id>/view')
# def view_campaign(campaign_id):
#     campaign = Campaign.query.get_or_404(campaign_id)
#     return render_template('view_campaign.html', campaign=campaign)

# @app.route('/campaign/<int:campaign_id>/submit_ad_request', methods=['POST'])
# def submit_ad_request(campaign_id):
#     if 'user_id' not in session or session['user_role'] != 'influencer':
#         flash('You need to be logged in as an influencer to submit an ad request.', 'danger')
#         return redirect(url_for('login'))

#     ad_request = AdRequest(
#         campaign_id=campaign_id,
#         influencer_id=session['user_id'],
#         status='pending'
#     )

#     db.session.add(ad_request)
#     db.session.commit()

#     flash('Ad request submitted successfully!', 'success')
#     return redirect(url_for('influencer_dashboard'))

















# #####################                               Influencer  route          ###########
# @app.route('/influencer_dash')
# def influencer_dash():
#     if 'user_role' in session and session['user_role'] == 'influencer':
#         username = session.get('username')
#         flash(f'Welcome back Influencer - {username} ','success')

#         if 'user_id' in session :
#             influencer = User.query.get(session['user_id'])
#             ad_requests = AdRequest.query.filter_by(influencer_id=influencer.id).all()
#             public_campaigns = Campaign.query.filter_by(visibility='public').all()

#             return render_template('/influencer/influencer_dash.html', influencer=influencer, ad_requests=ad_requests, public_campaigns=public_campaigns)
#     else:
#         flash('Please log in first!', 'danger')
#         return redirect(url_for('homepage'))

@app.route('/influencer_dash')
def influencer_dash():
    if 'user_id' not in session or session['user_role'] != 'influencer':
        flash('You need to be logged in as an influencer .', 'danger')
        return redirect(url_for('homepage'))

    influencer = User.query.get(session['user_id'])
    ad_requests = AdRequest.query.filter_by(influencer_id=influencer.id).all()
    public_campaigns = Campaign.query.filter_by(visibility='public').all()

    return render_template('/influencer/influencer_dash.html', influencer=influencer, ad_requests=ad_requests, public_campaigns=public_campaigns)



@app.route('/influencer_profile')
def influencer_profile():
    if 'user_id' not in session or session['user_role'] != 'influencer':
        flash('You need to be logged in as an influencer to view your profile.', 'danger')
        return redirect(url_for('login'))

    influencer = User.query.get(session['user_id'])

    return render_template('influencer/influencer_profile.html', influencer=influencer)



@app.route('/edit_influencer_profile', methods=['GET', 'POST'])
def edit_influencer_profile():
    if 'user_id' not in session or session['user_role'] != 'influencer':
        flash('You need to be logged in as an influencer to edit your profile.', 'danger')
        return redirect(url_for('login'))

    influencer = User.query.get(session['user_id'])

    if request.method == 'POST':
        influencer.username = request.form['username']
        influencer.email = request.form['email']
        influencer.category = request.form['category']
        influencer.niche = request.form['niche']
        influencer.reach = request.form['reach']

        db.session.commit()

        # session['username'] = influencer.username
        # session['email'] = influencer.email

        flash('Profile updated successfully!', 'success')
        return redirect(url_for('influencer_profile'))

    return render_template('edit_influencer_profile.html', influencer=influencer)

@app.route('/public_campaigns', methods=['GET', 'POST'])
def public_campaigns():
    if 'user_id' not in session or session['user_role'] != 'influencer':
        flash('You need to be logged in as an influencer to view public campaigns.', 'danger')
        return redirect(url_for('login'))

    campaigns = Campaign.query.filter_by(visibility='public').all()

    return render_template('influencer/public_campaigns.html', campaigns=campaigns)

@app.route('/ad_requests')
def ad_requests():
    if 'user_id' not in session or session['user_role'] != 'influencer':
        flash('You need to be logged in as an influencer to view ad requests.', 'danger')
        return redirect(url_for('login'))

    ad_requests = AdRequest.query.filter_by(influencer_id=session['user_id']).all()

    return render_template('influencer/ad_requests.html', ad_requests=ad_requests)

@app.route('/ad_request/<int:ad_request_id>/accept', methods=['POST'])
def accept_ad_request(ad_request_id):
    if 'user_id' not in session or session['user_role'] != 'influencer':
        flash('You need to be logged in as an influencer to accept an ad request.', 'danger')
        return redirect(url_for('login'))

    ad_request = AdRequest.query.get(ad_request_id)
    ad_request.status = 'approved'
    db.session.commit()

    flash('Ad request accepted successfully!', 'success')
    return redirect(url_for('ad_requests'))

@app.route('/ad_request/<int:ad_request_id>/reject', methods=['POST'])
def reject_ad_request(ad_request_id):
    if 'user_id' not in session or session['user_role'] != 'influencer':
        flash('You need to be logged in as an influencer to reject an ad request.', 'danger')
        return redirect(url_for('login'))

    ad_request = AdRequest.query.get(ad_request_id)
    ad_request.status = 'rejected'
    db.session.commit()

    flash('Ad request rejected successfully!', 'success')
    return redirect(url_for('ad_requests'))

@app.route('/ad_request/<int:ad_request_id>/negotiate', methods=['POST'])
def negotiate_ad_request(ad_request_id):
    if 'user_id' not in session or session['user_role'] != 'influencer':
        flash('You need to be logged in as an influencer to negotiate an ad request.', 'danger')
        return redirect(url_for('login'))

    new_payment_amount = request.form['new_payment_amount']
    ad_request = AdRequest.query.get(ad_request_id)
    ad_request.payment_amount = new_payment_amount
    ad_request.status = 'negotiation'
    db.session.commit()

    flash('Ad request negotiation submitted successfully!', 'success')
    return redirect(url_for('ad_requests'))




#######################################################################################################









# @app.route('/camapaigns')
# def campaigns():
#     return render_template('campaigns.html')



#list (we are getting an http GET request at this endpoint)
@app.route("/users" ,  methods=['GET','POST'])
def list_user():
    if request.method == "GET":
        users =User.query.all()
        return render_template("user_list.html", users=users)
    elif request.method == "POST":
        # validate and get request data 
        username = request.form.get("username") #none of not key names 'username'
        email = request.form.get("email")
        password= request.form.get("password")
        print("password",password)
        print(f"username:{username} , password:{password}")
        role = "admsdcsin"
        # #create an entryh to the users table
        new_user = User(username=username, email=email, password=password, role=role)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('list_user'))
        

        # send appropriate response
        


#create-- we will send HTTP request with the formto create data anew entity
# @app.post("/users")
# def create_user(request):
#     pass


# #Retrieve
# @app.route("/users/<user_id>")
# def get_user(user_id):
#     pass

# #Update
# @app.route("/users/<user_id>")
# def update_user(user_id):
#     pass


# #delete
# @app.route("/user/<user_id>")
# def delete_usser(user_id):
#     pass


@app.route("/create_table")
def create_table():
    db.create_all()
    print("db is created")
    return "<h1> table created successfully</h1>"



if __name__ == '__main__':
    with app.app_context():
        
    
        app.run(debug=True,port=8000)
    


    
