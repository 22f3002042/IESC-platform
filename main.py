from flask import Flask,render_template,request, redirect, url_for, session, flash , jsonify
from models import db
from datetime import datetime
from models import User, Campaign,AdRequest
from sqlalchemy import func

app = Flask(__name__)

app.config['SECRET_KEY'] = 'this_is_personal_project.'
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





@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        
        if user and user.password == password: 
        
            session['user_id'] = user.id
            session['username'] = user.username 
            session['user_role'] = user.role
            session['email'] = user.email  
            

            if user.role == 'admin':
                username = session['username']
                flash(f'Welcome back Admin- {username}', 'success')
                return redirect(url_for('admin_dash'))
                
            elif user.role == 'sponsor':
                username = session['username']
                flash(f'Welcome back Sponsor- {username}', 'success')
                return redirect(url_for('sponsor_profile'))
                
            elif user.role == 'influencer':
                username =  session['username']
                flash(f'Welcome back Influencer- {username}', 'success')
                return redirect(url_for('influencer_profile'))
                
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

@app.route('/logout')
def logout():
    username = session.get('username')
    session.clear()
    flash(f'{username} - you have been logged out', 'danger')
    return redirect(url_for('homepage'))



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
    if 'user_id' not in session or session['user_role'] != 'admin':
        flash('You need to be logged in as an admin to see the dashboard.', 'danger')
        return redirect(url_for('login'))

    try:
        username = session.get('username')

        total_users = User.query.count()
        total_influencers = User.query.filter_by(role='influencer').count()
        total_sponsors = User.query.filter_by(role='sponsor').count()

        public_campaigns = Campaign.query.filter_by(visibility='public').count()
        private_campaigns = Campaign.query.filter_by(visibility='private').count()

        ad_requests_per_campaign = db.session.query(
            Campaign.title, func.count(AdRequest.id)
        ).join(AdRequest, Campaign.id == AdRequest.campaign_id).group_by(Campaign.title).all()

        campaign_names = [campaign[0] for campaign in ad_requests_per_campaign]
        ad_requests_counts = [campaign[1] for campaign in ad_requests_per_campaign]

        all_campaigns = Campaign.query.all()
        campaign_progress = [campaign.progress() for campaign in all_campaigns]

        flagged_users = User.query.filter_by(flagged=True).count()
        flagged_campaigns = Campaign.query.filter_by(is_flagged=True).count()

        ad_requests = AdRequest.query.all()
        ad_requests_status_count = {
            'Pending': AdRequest.query.filter_by(status='Pending').count(),
            'Accepted': AdRequest.query.filter_by(status='Accepted').count(),
            'Rejected': AdRequest.query.filter_by(status='Rejected').count(),
            'Completed': AdRequest.query.filter_by(status='Completed').count()
        }

        ad_requests_list = [{
            'id': ad_request.id,
            'campaign_id': ad_request.campaign_id,
            'influencer_id': ad_request.influencer_id,
            'status': ad_request.status,
            'ads_required': ad_request.ads_required,
            'ads_completed': ad_request.ads_completed
        } for ad_request in ad_requests]

        data = {
            'total_users': total_users,
            'total_influencers': total_influencers,
            'total_sponsors': total_sponsors,
            'campaign_status': {
                'public': public_campaigns,
                'private': private_campaigns,
            },
            'campaign_names': campaign_names,
            'ad_requests_per_campaign': ad_requests_counts,
            'campaign_progress': campaign_progress,
            'flagged_users': flagged_users,
            'flagged_campaigns': flagged_campaigns,
            'ad_requests_status': ad_requests_status_count,
            'ad_requests': ad_requests_list
        }

        return render_template('/admin/admin_dash.html', username=username, data=data)
    except Exception as e:
        flash(f'An error occurred:', 'danger')
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



##########################################  admin campaign    ####################

@app.route('/admin/campaigns', methods=['GET'])
def manage_campaigns():
    if 'user_id' not in session or session['user_role'] != 'admin':
        flash('You need to be logged in as an admin to flag the campaigns.', 'danger')
        return redirect(url_for('login'))

    campaigns = Campaign.query.all()
    flagged_campaigns = Campaign.query.filter_by(is_flagged=True).all()
    return render_template('/campaigns/admin_cam/admin_campaigns.html', campaigns=campaigns, flagged_campaigns=flagged_campaigns)

@app.route('/admin/campaign/<int:campaign_id>/view')
def ad_view_campaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    return render_template('/campaigns/admin_cam/ad_view_campaigns.html', campaign=campaign)

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
    AdRequest.query.filter_by(campaign_id=campaign_id).delete()
    
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
    if 'user_id' not in session or session['user_role'] != 'sponsor':
        flash('You need to be logged in as a sponsor to see this dashboard.', 'danger')
        return redirect(url_for('homepage'))

    username = session.get('username')
    sponsor_id = session.get('user_id')
    
    # Fetch the sponsor
    sponsor = User.query.get(sponsor_id)
    if not sponsor:
        flash('Sponsor not found.', 'danger')
        return redirect(url_for('homepage'))
    
    # Public and Private Campaigns
    public_campaigns = Campaign.query.filter_by(sponsor_id=sponsor_id, visibility='public').all()
    private_campaigns = Campaign.query.filter_by(sponsor_id=sponsor_id, visibility='private').all()

    # Ad Requests Status
    ad_requests_status = {
        'Pending': AdRequest.query.filter_by(sponsor_id=sponsor_id, status='Pending').count(),
        'Accepted': AdRequest.query.filter_by(sponsor_id=sponsor_id, status='Accepted').count(),
        'Rejected': AdRequest.query.filter_by(sponsor_id=sponsor_id, status='Rejected').count(),
        'Completed': AdRequest.query.filter_by(sponsor_id=sponsor_id, status='Completed').count()
    }
    
    # Progress of Campaigns
    public_campaign_progress = {campaign.title: campaign.progress() for campaign in public_campaigns}
    private_campaign_progress = {campaign.title: campaign.progress() for campaign in private_campaigns}

    # Active Influencers
    active_influencers = [
        {'id': influencer.id, 'username': influencer.username} 
        for influencer in User.query.filter_by(role='influencer').all()
    ]

    data = {
        'public_campaigns': [campaign.title for campaign in public_campaigns],  # You might want to simplify this if needed
        'private_campaigns': [campaign.title for campaign in private_campaigns],  # You might want to simplify this if needed
        'ad_requests_status': ad_requests_status,
        'public_campaign_progress': public_campaign_progress,
        'private_campaign_progress': private_campaign_progress,
        'active_influencers': active_influencers
    }

    return render_template('/sponsor/sponsor_dash.html', username=username, data=data)

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
        campaign.status = request.form['status']
        db.session.commit()

        flash(f'Campaign {campaign.title}  updated successfully!', 'success')
        return redirect(url_for('sponsor_campaigns'))
    
    return render_template('/campaigns/sponsor_cam/sponsor_campaigns.html', campaign=campaign)

@app.route('/sponsor/campaigns/<int:campaign_id>/delete', methods=['POST'])
def delete_campaign(campaign_id):
    if 'user_id' not in session or session['user_role'] != 'sponsor':
        flash('You need to be logged in as a sponsor to create a campaign.', 'danger')
        return redirect(url_for('login'))

    campaign = Campaign.query.get_or_404(campaign_id)
    AdRequest.query.filter_by(campaign_id=campaign_id).delete()

    db.session.delete(campaign)
    db.session.commit()
    flash(f'Campaign {campaign.title} deleted successfully!', 'success')
    return redirect(url_for('sponsor_campaigns'))

@app.route('/sponsor/influencers')
def sponsor_influencer():
    influencers = User.query.filter_by(role='influencer').all()
    return render_template('/sponsor/search_influencer.html', influencers=influencers)

@app.route('/search_influencers', methods=['GET'])
def search_influencers():
    username = request.args.get('username', '').strip()
    niche = request.args.get('niche', '').strip()
    min_reach = request.args.get('min_reach', '').strip()
    max_reach = request.args.get('max_reach', '').strip()

    query = User.query.filter(User.role == 'influencer')

    # Apply filters based on search criteria
    if username:
        query = query.filter(User.username.ilike(f"%{username}%"))

    if niche:
        query = query.filter(User.niche.ilike(f"%{niche}%"))

    if min_reach:
        query = query.filter(User.reach >= int(min_reach))

    if max_reach:
        query = query.filter(User.reach <= int(max_reach))

    influencers = query.all()

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

@app.route('/sponsor/ad_request/<int:ad_request_id>', methods=['GET'])
def sponsor_view_ad_request(ad_request_id):
    ad_request = AdRequest.query.get_or_404(ad_request_id)
    return render_template('/sponsor/sponsor_view_ad_request.html', ad_request=ad_request)

@app.route('/sponsor/ad_requests/update/<int:ad_request_id>', methods=['POST'])
def update_ad_request(ad_request_id):
    if 'user_id' not in session or session['user_role'] != 'sponsor':
        flash('You need to be logged in as a sponsor to update ad requests.', 'danger')
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
        
        if ad_request.status == 'Completed':
            ad_request.ads_completed = ad_request.ads_required

        elif ad_request.status == 'Accepted':
            ad_request.ads_completed = request.form.get('ads_completed')

        elif ad_request.status == 'Pending' or ad_request.status == 'Rejected':
            ad_request.ads_completed = 0
    
        db.session.commit()
        flash('Ad request status updated successfully!', 'success')
        return redirect(url_for('sponsor_ad_requests',campaign_id=ad_request.campaign_id))

@app.route('/sponsor/ad_requests/<int:ad_request_id>/status', methods=['POST'])
def update_request_status(ad_request_id):
    ad_request = AdRequest.query.get_or_404(ad_request_id)
    status = request.form['status']
    ad_request.status = status

    if status == 'Completed':
        ad_request.ads_completed = ad_request.ads_required
    else:
        ad_request.ads_completed = 0

    db.session.commit()
    flash(f'Ad request is {status}!', 'success')
    return redirect(url_for('sponsor_ad_requests'))


@app.route('/sponsor/ad_request/<int:ad_request_id>/delete', methods=['POST'])
def delete_ad_request(ad_request_id):
    ad_request = AdRequest.query.get_or_404(ad_request_id)

    if 'user_id' not in session or session['user_role'] != 'sponsor' or ad_request.sponsor_id != session['user_id']:
        flash('You need to be logged in as a sponsor to delete ad requests.', 'danger')
        return redirect(url_for('login'))

    db.session.delete(ad_request)
    db.session.commit()
    flash('Ad request deleted successfully!', 'success')
    return redirect(url_for('sponsor_ad_requests', campaign_id=ad_request.campaign_id))


# #####################                               Influencer  route          ###########

@app.route('/influencer_dash')
def influencer_dash():
    if 'user_id' not in session or session['user_role'] != 'influencer':
        flash('You need to be logged in as an influencer to view Dashboard .', 'danger')
        return redirect(url_for('login'))

    influencer = User.query.get(session['user_id'])
    ad_requests = AdRequest.query.filter_by(influencer_id=influencer.id).all()
    public_campaigns = Campaign.query.filter_by(visibility='public').all()

    username = session.get('username')
    influencer_id = session.get('user_id')
    
    # Public Campaigns
    public_campaigns = Campaign.query.filter_by(visibility='public').all()

    # Ad Requests Status
    ad_requests_status = {
        'Pending': AdRequest.query.filter_by(influencer_id=influencer_id, status='Pending').count(),
        'Accepted': AdRequest.query.filter_by(influencer_id=influencer_id, status='Accepted').count(),
        'Rejected': AdRequest.query.filter_by(influencer_id=influencer_id, status='Rejected').count(),
        'Completed': AdRequest.query.filter_by(influencer_id=influencer_id, status='Completed').count()
    }
    
    # Active Sponsors
    active_sponsors = [
        {'id': sponsor.id, 'username': sponsor.username} 
        for sponsor in User.query.filter_by(role='sponsor').all()
    ]

    data = {
        'public_campaigns': [campaign.title for campaign in public_campaigns],  
        'ad_requests': len(ad_requests),
        'ad_requests_status': ad_requests_status,
        'active_sponsors': active_sponsors
    }

    return render_template('/influencer/influencer_dash.html', username=username, data=data, influencer=influencer, ad_requests=ad_requests, public_campaigns=public_campaigns)

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

@app.route('/influencer/public_campaigns', methods=['GET'])
def inf_public_campaigns():
    if 'user_id' not in session or session['user_role'] != 'influencer':
        flash('You need to be logged in as an influencer to view public campaigns.', 'danger')
        return redirect(url_for('login'))

    campaigns = Campaign.query.filter_by(visibility='public').all()

    return render_template('campaigns/influencer_cam/influencer_campaigns.html', campaigns=campaigns)

@app.route('/search_campaigns', methods=['GET'])
def search_campaigns():
    title = request.args.get('title', '').strip()
    niche = request.args.get('niche', '').strip()

    # Start with a base query for public campaigns
    query = Campaign.query.filter(Campaign.visibility == 'public')

    # Apply filters based on search criteria
    if title:
        query = query.filter(Campaign.title.ilike(f"%{title}%"))

    if niche:
        query = query.filter(Campaign.niche.ilike(f"%{niche}%"))

    campaigns = query.all()

    return render_template('/campaigns/influencer_cam/influencer_campaigns.html', campaigns=campaigns)

@app.route('/influencer/campaign/<int:campaign_id>', methods=['GET'])
def view_campaign_details(campaign_id):
    if session['user_role'] != 'influencer':
        return redirect(url_for('homepage'))
    
    campaign = Campaign.query.get_or_404(campaign_id)
    return render_template('/campaigns/influencer_cam/campaign_details.html', campaign=campaign)



#####################                                         influencer   #ads requests

@app.route('/influencer/ad-requests', methods=['GET'])
def influencer_ad_requests():
    influencer_id = session['user_id']   

   
    sent_ad_requests = AdRequest.query.join(Campaign).filter(AdRequest.influencer_id == influencer_id, 
        Campaign.id == AdRequest.campaign_id, Campaign.visibility == 'public').all()

    received_ad_requests = AdRequest.query.join(Campaign).filter(AdRequest.influencer_id == influencer_id,
        Campaign.id == AdRequest.campaign_id, Campaign.visibility == 'private').all()

    public_campaigns = Campaign.query.filter_by(visibility='public').all()

    return render_template(
        '/influencer/inf_ad_request.html',
        sent_ad_requests=sent_ad_requests,
        received_ad_requests=received_ad_requests,
        public_campaigns=public_campaigns
    )

@app.route('/influencer/ad_request/create', methods=['POST'])
def create_public_request():
    if 'user_id' not in session or session['user_role'] != 'influencer':
        flash('You need to be logged in as a influencer to create ad requests.', 'danger')
        return redirect(url_for('login'))
    
    influencer_id = session['user_id']
    campaign_id = request.form['campaign_id']
    
    details = request.form['details']
    payment_amount = float(request.form['payment_amount'])
    ads_required = int(request.form['ads_required'])

    
    campaign = Campaign.query.get(campaign_id)
    new_public_request = AdRequest(
        campaign_id=campaign_id,
        influencer_id=influencer_id, 
        sponsor_id=campaign.sponsor_id ,        
        details=details,
        payment_amount=payment_amount,
        ads_required=ads_required,
        status='Pending', 
        updated_at=datetime.utcnow()
    )

    db.session.add(new_public_request)
    db.session.commit()
    flash('Ad request created successfully!', 'success')
    return redirect(url_for('influencer_ad_requests'))

@app.route('/influencer/ad-requests/view/<int:ad_request_id>', methods=['GET'])
def inf_view_ad_request(ad_request_id):
    if 'user_id' not in session or session['user_role'] != 'influencer':
        flash('You need to be logged in as a influencer to view ad requests.', 'danger')
        return redirect(url_for('login'))

    ad_request = AdRequest.query.get_or_404(ad_request_id)
    
    if ad_request.influencer_id != session['user_id'] or session['user_role'] != 'influencer' :
        flash('You are not authorized to view this request!', 'danger')
        return redirect(url_for('influencer_ad_requests'))
    
    return render_template('/influencer/inf_view_ad_request.html', ad_request=ad_request )

@app.route('/influencer/ad_request/<int:ad_request_id>/update', methods=['POST'])
def influencer_update_ad_request(ad_request_id):
    if 'user_id' not in session or session['user_role'] != 'influencer':
        flash('You need to be logged in as a influencer to update ad requests.', 'danger')
        return redirect(url_for('login'))
    
    ad_request = AdRequest.query.get_or_404(ad_request_id)
    
    if ad_request.influencer_id != session['user_id']:
        return redirect(url_for('login'))
    
    ad_request.details = request.form.get('details')
    ad_request.payment_amount = request.form.get('payment_amount')
    ad_request.ads_required = request.form.get('ads_required')
    ad_request.ads_completed = request.form.get('ads_completed')
    ad_request.status = request.form.get('status')

    if ad_request.status == 'Completed':
        ad_request.ads_completed = ad_request.ads_required

    elif ad_request.status == 'Accepted':
        ad_request.ads_completed = request.form.get('ads_completed')

    elif ad_request.status == 'Pending' or ad_request.status == 'Rejected':
        ad_request.ads_completed = 0
    
    db.session.commit()
    flash('Ad request updated successfully!', 'success')
    return redirect(url_for('influencer_ad_requests'))

@app.route('/influencer/ad_requests/<int:ad_request_id>/status', methods=['POST'])
def inf_update_request_status(ad_request_id):
    if session['user_role'] != 'influencer':
        flash('You need to be logged in as a influencer to update ad requests.', 'danger')
        return redirect(url_for('login'))

    ad_request = AdRequest.query.get_or_404(ad_request_id)

    status = request.form['status']
    ad_request.status = status

    if status == 'Completed':
        ad_request.ads_completed = ad_request.ads_required
    else:
        ad_request.ads_completed = 0

    db.session.commit()
    flash(f'Ad request is {status}!', 'success')
    return redirect(url_for('influencer_ad_requests'))

@app.route('/influencer/ad_request/<int:ad_request_id>/delete', methods=['POST'])
def influencer_delete_ad_request(ad_request_id):
    if session['user_role'] != 'influencer':
        flash('You need to be logged in as a influencer to delete ad requests.', 'danger')
        return redirect(url_for('login'))
    
    ad_request = AdRequest.query.get_or_404(ad_request_id)
    
    if ad_request.influencer_id != session['user_id']:
        return redirect(url_for('login'))
    
    db.session.delete(ad_request)
    db.session.commit()
    flash('Ad request deleted successfully!', 'danger')
    return redirect(url_for('influencer_ad_requests'))






                    









    

################################################################################################################################################
        
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
    


    
