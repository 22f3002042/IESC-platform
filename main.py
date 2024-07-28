from flask import Flask,render_template,request, redirect, url_for, session, flash
from db import db
from datetime import datetime
from models import User, Campaign,AdRequest

app = Flask(__name__)

app.config['SECRET_KEY'] = 'this_is_person_project.'
app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///iesc.db"
db.init_app(app)



@app.route("/")
def homepage():
    return render_template("home.html")

@app.route("/base")
def base():
    return render_template("base.html")






#new login framwork
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        
        email = request.form['email']
        password = request.form['password']

        # print(f'email:{email},password:{password}')

        user = User.query.filter_by(email=email).first()
        
        if user and user.password == password: 
            # User authenticated, store user info in session
            session['user_id'] = user.id
            session['username'] = user.username 
            session['user_role'] = user.role
            session['email'] = user.email  
            
            # Redirect based on role
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

# Admin  route
@app.route('/admin_dash')
def admin_dash():
    if 'user_role' in session and session['user_role'] == 'admin':
        username = session.get('username')
        flash(f'Welcome back Admin - {username} ','success')
        return render_template('/admin/admin_dash.html',username=username)
    else:
        flash('Please log in first!', 'danger')
        return redirect(url_for('homepage'))

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

@app.route("/sponsor_campaigns")
def sponsor_campaigns():
    return render_template("campaigns.html")


@app.route("/sponsor_stats")
def sponsor_stats():
    return render_template("sponsor/sponsor_stats.html")

@app.route("/search_infl")
def search_influencer():
    return "this is the searching for influencers"




### campaigns routes
@app.route('/create_campaign', methods=['GET', 'POST'])
def create_campaign():
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

        # Convert string dates to Python date objects
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
            sponsor_id=session['user_id']
        )

        db.session.add(new_campaign)
        db.session.commit()

        flash('Campaign created successfully!', 'success')
        return redirect(url_for('sponsor_profile'))

    return render_template('/campaigns/create_campaign.html')

@app.route('/campaign/<campaign_id>/submit_ad_request', methods=['GET','POST'])
def submit_ad_request(campaign_id):
    if 'user_id' not in session or session['user_role'] != 'influencer':
        flash('You need to be logged in as an influencer to submit an ad request.', 'danger')
        return redirect(url_for('login'))

    if request.method == 'POST':
        submission = request.form['submission']
        new_ad_request = AdRequest(
            campaign_id=campaign_id,
            influencer_id=session['user_id'],
            status='pending'
        )

        db.session.add(new_ad_request)
        db.session.commit()

        flash('Ad request submitted successfully!', 'success')
        return redirect(url_for('view_campaign', campaign_id=campaign_id))

    campaign = Campaign.query.get_or_404(campaign_id)
    return render_template('submit_ad_request.html', campaign=campaign)




















# #####################                               Influencer  route          ###########
@app.route('/influencer_dash')
def influencer_dash():
    if 'user_role' in session and session['user_role'] == 'influencer':
        username = session.get('username')
        flash(f'Welcome back Influencer - {username} ','success')
        return render_template('/influencer/influencer_dash.html')
    else:
        flash('Please log in first!', 'danger')
        return redirect(url_for('homepage'))

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
@app.post("/users")
def create_user(request):
    pass


#Retrieve
@app.route("/users/<user_id>")
def get_user(user_id):
    pass

#Update
@app.route("/users/<user_id>")
def update_user(user_id):
    pass


#delete
@app.route("/user/<user_id>")
def delete_user(user_id):
    pass



if __name__ == '__main__':
    with app.app_context():
        # db.create_all()
        # print("db is created")
    
        app.run(debug=True,port=8000)
    


    
