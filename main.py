from flask import Flask,render_template,request, redirect, url_for, session, flash
from db import db
from datetime import datetime
from models import User, Campaign,AdRequest

app = Flask(__name__)

app.config['SECRET_KEY'] = 'this_is_person_project.'
app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///iesc.db"
db.init_app(app)




@app.route("/home")
def homepage():
    if 'user_role' in session and session['user_role'] == 'admin':
        return redirect(url_for('admin_profile'))

    elif 'user_role' in session and session['user_role'] == 'sponsor':
        return redirect(url_for('sponsor_profile'))

    elif 'user_role' in session and session['user_role'] == 'influencer':
        return redirect(url_for('influencer_profile'))
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
            

            if user.role == 'admin':
                return redirect(url_for('admin_dash'))
                flash(f'Welcome back Admin- {username}', 'success')
            elif user.role == 'sponsor':
                return redirect(url_for('sponsor_profile'))
                flash(f'Welcome back Sponsor- {username}', 'success')
            elif user.role == 'influencer':
                return redirect(url_for('influencer_profile'))
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

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '').strip()  # Retrieve and trim the query string

    if not query:  # Check if query is empty or whitespace
        flash('No Result for this query!', 'warning')
        return render_template('search_results.html', sponsors=[], influencers=[], campaigns=[], query=query)
    
    # Perform search logic and fetch results
    sponsors = User.query.filter(User.role == 'sponsor', User.username.contains(query)).all()
    influencers = User.query.filter(User.role == 'influencer', User.username.contains(query)).all()
    campaigns = Campaign.query.filter(Campaign.title.contains(query)).all()

    return render_template('search_results.html', 
                           sponsors=sponsors, 
                           influencers=influencers, 
                           campaigns=campaigns,
                           query=query)



#                                   #########                   Admin  route            ############

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

@app.route('/admin_dash')
def admin_dash():
    if 'user_role' in session and session['user_role'] == 'admin':
        username = session.get('username')
        flash(f'Welcome back Admin - {username} ','success')
        return render_template('/admin/admin_dash.html',username=username)
    else:
        flash('Please log in first!', 'danger')
        return redirect(url_for('homepage'))

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


















##########################################  admin campaign CRUD   ####################

@app.route('/admin/campaigns', methods=['GET'])
def manage_campaigns():
    campaigns = Campaign.query.all()
    flagged_campaigns = Campaign.query.filter_by(is_flagged=True).all()
    return render_template('/campaigns/admin_cam/admin_campaigns.html', campaigns=campaigns, flagged_campaigns=flagged_campaigns)

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

@app.route('/sponsor_dash')
def sponsor_dash():
    if 'user_role' in session and session['user_role'] == 'sponsor':
        username = session.get('username')
        
        flash(f'Welcome back Sponsor - {username} ','success')
        return render_template('/sponsor/sponsor_dash.html')
    else:
        flash('Please log in first!', 'danger')
        return redirect(url_for('homepage'))



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
    sponsor_id = session['user_id']
    public_campaigns = Campaign.query.filter_by(visibility='public', sponsor_id=sponsor_id).all()
    private_campaigns = Campaign.query.filter_by(visibility='private', sponsor_id=sponsor_id).all()
    return render_template('campaigns/sponsor_cam/sponsor_campaigns.html', public_campaigns=public_campaigns, private_campaigns=private_campaigns)

@app.route('/campaign/<int:campaign_id>/view')
def view_campaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    return render_template('/campaigns/sponsor_cam/view_campaign.html', campaign=campaign)

@app.route('/sponsor/campaigns/<int:campaign_id>/update', methods=['GET', 'POST'])
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

        flash(f'Campaign {campaign.title}  updated successfully!', 'success')
        return redirect(url_for('sponsor_campaigns'))
    
    return render_template('/campaigns/sponsor_cam/sponsor_campaigns.html', campaign=campaign)

@app.route('/sponsor/campaigns/<int:campaign_id>/delete', methods=['POST'])
def delete_campaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    db.session.delete(campaign)
    db.session.commit()
    flash(f'Campaign {campaign.title} deleted successfully!', 'success')
    return redirect(url_for('sponsor_campaigns'))



@app.route("/sponsor_stats")
def sponsor_stats():
    return render_template("sponsor/sponsor_stats.html")

@app.route('/sponsor/influencers')
def sponsor_influencer():
    influencers = User.query.filter_by(role='influencer').all()
    return render_template('/sponsor/search_influencer.html', influencers=influencers)




@app.route('/sponsor/ad_requests')
def sponsor_ad_requests():
    if 'user_id' not in session or session['user_role'] != 'sponsor':
        flash('You need to be logged in as a sponsor to view ad requests.', 'danger')
        return redirect(url_for('login'))

    sponsor_id = session['user_id']
    public_ad_requests = AdRequest.query.join(Campaign).filter(
        AdRequest.influencer_id.isnot(None),
        Campaign.sponsor_id == sponsor_id,
        Campaign.visibility == 'public'
    ).all()  # Public received requests

    private_ad_requests = AdRequest.query.join(Campaign).filter(
        AdRequest.sponsor_id == sponsor_id,
        Campaign.visibility == 'private'
    ).all()  # Private sent requests

    # Fetch the campaigns created by the sponsor for private ad requests
    private_campaigns = Campaign.query.filter_by(sponsor_id=sponsor_id, visibility='private').all()
    public_campaigns = Campaign.query.filter_by(sponsor_id=sponsor_id, visibility='public').all()

    # Fetch all influencers for the create ad request form
    influencers = User.query.filter_by(role='influencer').all()

    return render_template(
        'sponsor/sponsor_ad_requests.html',
        public_ad_requests=public_ad_requests,
        private_ad_requests=private_ad_requests,
        private_campaigns=private_campaigns,
        public_campaigns=public_campaigns,
        influencers=influencers
    )

@app.route('/sponsor/ad_requests/create', methods=['POST'])
def create_private_ad_request():
    if 'user_id' not in session or session['user_role'] != 'sponsor':
        flash('You need to be logged in as a sponsor to create ad requests.', 'danger')
        return redirect(url_for('login'))

    sponsor_id = session['user_id']
    campaign_id = request.form['campaign_id']
    influencer_id = request.form['influencer_id']
    details = request.form['details']
    payment_amount = float(request.form['payment_amount'])
    ads_required = int(request.form['ads_required'])

    campaign = Campaign.query.get_or_404(campaign_id)
    if campaign.sponsor_id != sponsor_id:
        flash('You can only create ad requests for your own campaigns.', 'danger')
        return redirect(url_for('sponsor_ad_requests'))

    new_ad_request = AdRequest(
        campaign_id=campaign_id,
        influencer_id=influencer_id,
        sponsor_id=sponsor_id,
        details=details,
        payment_amount=payment_amount,
        ads_required=ads_required
    )

    db.session.add(new_ad_request)
    db.session.commit()
    flash('Ad request created successfully!', 'success')
    return redirect(url_for('sponsor_ad_requests'))

@app.route('/sponsor/ad_requests/update_status/<int:ad_request_id>', methods=['POST'])
def update_ad_request(ad_request_id):
    if 'user_id' not in session or session['user_role'] != 'sponsor':
        flash('You need to be logged in as a sponsor to manage ad requests.', 'danger')
        return redirect(url_for('login'))

    ad_request = AdRequest.query.get_or_404(ad_request_id)
    campaign = Campaign.query.get_or_404(ad_request.campaign_id)
    sponsor_id = session['user_id']

    if request.method == 'POST':
        ad_request.status = request.form['status']
        ad_request.details = request.form['details']
        ad_request.payment_amount = request.form['payment_amount']
        ad_request.ads_required = int(request.form['ads_required'])
        ad_request.ads_completed = int(request.form['ads_completed'])
        
        
        db.session.commit()
        flash('Ad request status updated successfully!', 'success')
        return redirect(url_for('sponsor_ad_requests',campaign_id=ad_request.campaign_id))
               
@app.route('/sponsor/ad_request/<int:ad_request_id>', methods=['GET'])
def sponsor_view_ad_request(ad_request_id):
    ad_request = AdRequest.query.get_or_404(ad_request_id)
    return render_template('/sponsor/sponsor_view_ad_request.html', ad_request=ad_request)



# #####################                               Influencer  route          ###########

@app.route('/influencer_dash')
def influencer_dash():
    if 'user_id' not in session or session['user_role'] != 'influencer':
        flash('You need to be logged in as an influencer .', 'danger')
        return redirect(url_for('login'))

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








@app.route('/influencer/campaigns', methods=['GET', 'POST'])
def search_public_campaigns():
    if session['user_role'] != 'influencer':
        return redirect(url_for('login'))
    
    campaigns = Campaign.query.filter_by(visibility='public').all()

    if request.method == 'POST':
        niche = request.form.get('niche')
        min_budget = request.form.get('min_budget', type=float)
        max_budget = request.form.get('max_budget', type=float)
        
        if niche:
            campaigns = campaigns.filter(Campaign.niche.ilike(f'%{niche}%'))
        if min_budget is not None:
            campaigns = campaigns.filter(Campaign.budget >= min_budget)
        if max_budget is not None:
            campaigns = campaigns.filter(Campaign.budget <= max_budget)

    return render_template('/campaigns/influencer_cam/influencer_campaigns.html', campaigns=campaigns)

@app.route('/influencer/campaign/<int:campaign_id>/apply', methods=['POST'])
def apply_for_campaign(campaign_id):
    if session['user_role'] != 'influencer':
        return redirect(url_for('homepage'))
    
    campaign = Campaign.query.get_or_404(campaign_id)
    ad_request = AdRequest(
        campaign_id=campaign.id,
        influencer_id=session['user_id'],
        sponsor_id=campaign.sponsor_id,
        details=request.form.get('details'),
        payment_amount=request.form.get('payment_amount'),
        ads_required=request.form.get('ads_required'),
        status='pending'
    )
    db.session.add(ad_request)
    db.session.commit()
    return redirect(url_for('search_public_campaigns', campaign_id=campaign.id))

@app.route('/influencer/campaign/<int:campaign_id>', methods=['GET'])
def view_campaign_details(campaign_id):
    if session['user_role'] != 'influencer':
        return redirect(url_for('homepage'))
    
    campaign = Campaign.query.get_or_404(campaign_id)
    return render_template('/campaigns/influencer_cam/campaign_details.html', campaign=campaign)





#####################                                            #ads requests

@app.route('/influencer/ad-requests', methods=['GET'])
def influencer_ad_requests():
    influencer_id = session['user_id']   # Fetch sent ad requests (for public campaigns)

    # Sent ad requests are those where the influencer is sending the request
    sent_ad_requests = AdRequest.query.join(Campaign).filter(AdRequest.influencer_id == influencer_id, 
        Campaign.id == AdRequest.campaign_id, Campaign.visibility == 'public').all()

    # Received ad requests are those where the influencer is receiving the request
    received_ad_requests = AdRequest.query.join(Campaign).filter(AdRequest.influencer_id == influencer_id,
        Campaign.id == AdRequest.campaign_id, Campaign.visibility == 'private').all()

    public_campaigns = Campaign.query.filter_by(visibility='public').all()

    return render_template(
        '/influencer/inf_ad_request.html',
        sent_ad_requests=sent_ad_requests,
        received_ad_requests=received_ad_requests,
        public_campaigns=public_campaigns
    )


@app.route('/influencer/create_ad_request', methods=['POST'])
def create_ad_request():
    if 'user_id' not in session or session['user_role'] != 'influecner':
        flash('You need to be logged in as a sponsor to create ad requests.', 'danger')
        return redirect(url_for('login'))
    
    influencer_id = session['user_id']
    campaign_id = request.form['campaign_id']
    sponsor_id = request.form['sponsor_id']
    details = request.form['details']
    payment_amount = float(request.form['payment_amount'])
    ads_required = int(request.form['ads_required'])

    
    campaign = Campaign.query.get(campaign_id)
    if not campaign:
        flash('Selected campaign does not exist.', 'danger')
        return redirect(url_for('influencer_ad_requests'))

    new_ad_request = AdRequest(
        campaign_id=campaign_id,
        influencer_id=influencer_id, 
        sponsor_id=sponsor_id,        
        details=details,
        payment_amount=payment_amount,
        ads_required=ads_required,
        status='pending', 
        updated_at=datetime.utcnow()
    )

    db.session.add(new_ad_request)
    db.session.commit()
    flash('Ad request created successfully!', 'success')
    
    return redirect(url_for('influencer_ad_requests'))


@app.route('/influencer/ad-requests/view/<int:ad_request_id>', methods=['GET'])
def inf_view_ad_request(ad_request_id):
    ad_request = AdRequest.query.get_or_404(ad_request_id)
    current_user=session['user_id']

    if ad_request.influencer_id != current_user:
        flash('You are not authorized to view this request!', 'danger')
        return redirect(url_for('influencer_sent_ad_requests'))
    
    return render_template('/influencer/inf_view_ad_request.html', ad_request=ad_request)


@app.route('/influencer/ad_request/<int:ad_request_id>/update', methods=['POST'])
def influencer_update_ad_request(ad_request_id):
    if session['user_role'] != 'influencer':
        return redirect(url_for('login'))
    
    ad_request = AdRequest.query.get_or_404(ad_request_id)
    
    if ad_request.influencer_id != session['user_id']:
        return redirect(url_for('login'))
    
    ad_request.details = request.form.get('details')
    ad_request.payment_amount = request.form.get('payment_amount')
    ad_request.ads_required = request.form.get('ads_required')
    ad_request.ads_completed = request.form.get('ads_completed')
    ad_request.status = request.form.get('status')
    
    db.session.commit()
    flash('Ad request updated successfully!', 'info')
    return redirect(url_for('influencer_ad_requests'))

@app.route('/influencer/ad_request/<int:ad_request_id>/delete', methods=['POST'])
def influencer_delete_ad_request(ad_request_id):
    if session['user_role'] != 'influencer':
        return redirect(url_for('login'))
    
    ad_request = AdRequest.query.get_or_404(ad_request_id)
    
    if ad_request.influencer_id != session['user_id']:
        return redirect(url_for('login'))
    
    db.session.delete(ad_request)
    db.session.commit()
    flash('Ad request deleted successfully!', 'danger')
    return redirect(url_for('influencer_ad_requests'))






                                                 

















#### these preivous adrequest for infl no using now delete them

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




###################################################################################################























@app.route('/sponsor/ad_request/<int:ad_request_id>/edit', methods=['GET', 'POST'])
def edit_ad_request(ad_request_id):
    ad_request = AdRequest.query.get_or_404(ad_request_id)

    if request.method == 'POST':
        ad_request.influencer_id = request.form['influencer_id']
        ad_request.details = request.form['details']
        ad_request.ads_required = int(request.form['ads_required'])
        ad_request.ads_completed = int(request.form['ads_completed'])
        ad_request.payment_amount = float(request.form['payment_amount'])
        ad_request.status = request.form['status']

        db.session.commit()
        flash('Ad request updated successfully!', 'success')
        return redirect(url_for('sponsor_ad_requests', campaign_id=ad_request.campaign_id))

    influencers = User.query.filter_by(role='influencer').all()
    return render_template('sponsor/edit_ad_request.html', ad_request=ad_request, influencers=influencers)

@app.route('/sponsor/ad_request/<int:ad_request_id>/delete', methods=['POST'])
def delete_ad_request(ad_request_id):
    ad_request = AdRequest.query.get_or_404(ad_request_id)

    if 'user_id' not in session or session['user_role'] != 'sponsor' or ad_request.sponsor_id != current_user.id:
        flash('You need to be logged in as a sponsor to delete ad requests.', 'danger')
        return redirect(url_for('login'))

    db.session.delete(ad_request)
    db.session.commit()
    flash('Ad request deleted successfully!', 'success')
    return redirect(url_for('sponsor_ad_requests', campaign_id=ad_request.campaign_id))


# @app.route('/influencer/campaign/<int:campaign_id>/ad_requests', methods=['GET', 'POST'])
# def influencer_ad_requests(campaign_id):
#     if 'user_id' not in session or session['user_role'] != 'sponsor' or ad_request.sponsor_id != current_user.id:
#         flash('You need to be logged in as a influencer to view ad requests.', 'danger')
#         return redirect(url_for('login'))

#     campaign = Campaign.query.get_or_404(campaign_id)

#     if campaign.visibility != 'public':
#         flash('You cannot request ads for private campaigns.', 'danger')
#         return redirect(url_for('influencer_campaigns'))

#     if request.method == 'POST':
#         details = request.form['details']
#         ads_required = int(request.form['ads_required'])
#         payment_amount = float(request.form['payment_amount'])

#         new_ad_request = AdRequest(
#             campaign_id=campaign.id,
#             influencer_id=current_user.id,
#             sponsor_id=campaign.sponsor_id,
#             details=details,
#             ads_required=ads_required,
#             payment_amount=payment_amount
#         )

#         db.session.add(new_ad_request)
#         db.session.commit()
#         flash('Ad request created successfully!', 'success')
#         return redirect(url_for('influencer_ad_requests', campaign_id=campaign.id))

#     ad_requests = AdRequest.query.filter_by(campaign_id=campaign.id).all()
#     return render_template('influencer/influencer_ad_requests.html', campaign=campaign, ad_requests=ad_requests)
















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
        
@app.context_processor
def inject_user():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
    else:
        user = None
    return dict(current_user=user)




@app.route("/create_table")
def create_table():
    db.create_all()
    print("db is created")
    return "<h1> table created successfully</h1>"



if __name__ == '__main__':
    with app.app_context():
        app.run(debug=True,port=8000)
    


    
