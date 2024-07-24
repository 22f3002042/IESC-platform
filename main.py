from flask import Flask,render_template,request, redirect, url_for, session, flash
from db import db
from models import User, Campaign

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


# @app.route('/login', methods=['GET', 'POST'])
# def admin_login():
#     if request.method == 'GET':
#         return render_template("/users/login.html")
#     elif request.method == 'POST':
#         if request.form['email'] != 'admin@gmail.com' or \
#                 request.form['password'] != 'admin123':
#             flash('You were enter wrong details','warning')    
#             error = 'Invalid credentials'
#         else:
#             flash('You were successfully logged in','success')
#             return redirect(url_for('admin_dash'))
#     return render_template('users/login.html')

# def check_password(user_password, password):
#     return user_password == password


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

# Admin dashboard route
@app.route('/admin_dash')
def admin_dash():
    if 'user_role' in session and session['user_role'] == 'admin':
        username = session.get('username')
        flash(f'Welcome back Admin - {username} ','success')
        return render_template('/admin/admin_dash.html',username=username)
    else:
        flash('Please log in first!', 'danger')
        return redirect(url_for('homepage'))

# Sponsor dashboard route
@app.route('/sponsor_dash')
def sponsor_dash():
    if 'user_role' in session and session['user_role'] == 'sponsor':
        username = session.get('username')
        flash(f'Welcome back Sponsor - {username} ','success')
        return render_template('/sponsor/sponsor_dash.html')
    else:
        flash('Please log in first!', 'danger')
        return redirect(url_for('homepage'))

# Influencer dashboard route
@app.route('/influencer_dash')
def influencer_dash():
    if 'user_role' in session and session['user_role'] == 'influencer':
        username = session.get('username')
        flash(f'Welcome back Influencer - {username} ','success')
        return render_template('/influencer/influencer_dash.html')
    else:
        flash('Please log in first!', 'danger')
        return redirect(url_for('homepage'))





#######################################################################################################






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
    

