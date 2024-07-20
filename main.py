from flask import Flask,render_template,\
request,redirect,url_for,flash
from sqlalchemy.exc import NoResultFound
from db import db
from models import User, Campaign

app = Flask(__name__)

app.config['SECRET_KEY'] = 'this_is_person_project.'
app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///iesc.db"
db.init_app(app)



@app.route("/")
def index():
    return render_template("home.html")

# @app.route("/base")
# def base():
#     return render_template("base.html")


@app.route('/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'GET':
        return render_template("/users/login.html")
    # error = None
    elif request.method == 'POST':
        if request.form['email'] != 'admin@gmail.com' or \
                request.form['password'] != 'admin123':
            flash('You were enter wrong details','warning')    
            error = 'Invalid credentials'
        else:
            flash('You were successfully logged in','success')
            return redirect(url_for('admin_dash'))
    return render_template('users/login.html')

def check_password(user_password, password):
    return user_password == password

# @app.route("/login" , methods=['GET','POST']) 
# def login():
#     if request.method == 'GET':
#         return render_template("/users/login.html")
#     elif request.method =='POST':
#         email = request.form.get("email")
#         password = request.form.get("password")
#         print(f'email:{email},password:{password}')

#         try:
#             user= User.query.filter_by(email=email).one()
#         except NoResultFound as n:
#             flash("enter the correct email.", "error")
            
#             return redirect(url_for("index"))
#         authenticated = check_password(user.password ,password)
#         if authenticated:
#             return redirect(url_for("index"))
#         else:
#             flash("enter correct password.", "error")
#             return redirect(url_for("login"))

@app.route("/sponsor_signup")
def sponsor_signup():
    return render_template("users/sponsor_signup.html")

@app.route("/influencer_signup")
def influencer_signup():
    return render_template("users/influencer_signup.html")

@app.route("/sponsor_dash")
def sponsor_dash():
    return render_template("sponsor_dash.html")


@app.route("/influencer_dash")
def influencer_dash():
    return render_template("influencer_dash.html")

@app.route("/admin_dash")
def admin_dash():
    return render_template("admin_dash.html")





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
        # print(" db is created")
    
        app.run(debug=True,port=8000)
    

