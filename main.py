from flask import Flask,render_template,request,redirect,url_for
from db import db
from models import User

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///iesc.db"
db.init_app(app)



@app.route("/")
def index():
    return render_template("home.html")

# @app.route("login")
# def login():
#     return render_template("login.html")

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
    # with app.app_context():
    #     db.create_all()
    
    app.run(debug=True,port=8000)
    

