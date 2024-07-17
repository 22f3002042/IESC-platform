# # from flask import Blueprint,render_template


# # app = Blueprint('controllers', __name__)

# # @app.route('/')
# # def index():
# #     return render_template('index.html')

# # @app.route('/dashboard')
# # def dashboard():
# #     return render_template('dashboard.html')


# # @app.route('/login')
# # def login():
# #     return render_template('login.html')

# # @app.route('/signup')
# # def signup():
# #     return render_template('signup.html')



# from flask import Blueprint, render_template, redirect, url_for, request, session
# from .models import db, User

# bp = Blueprint('main', __name__)

# @bp.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#         user = User.query.filter_by(username=username).first()
#         if user and user.check_password(password):
#             session['user_id'] = user.id
#             session['role'] = user.role
#             return redirect(url_for('main.home'))
#     return render_template('login.html')

# @bp.route('/home')
# def dashboard():
#     if 'user_id' not in session:
#         return redirect(url_for('main.home'))
    
#     user = User.query.get(session['user_id'])
#     if user.role == 'admin':
#         return render_template('admin_dash.html')
#     elif user.role == 'sponsor':
#         return render_template('sponsor_dash.html')
#     elif user.role == 'influencer':
#         return render_template('influencer_dash.html')

#     return "Invalid role!"

# @bp.route("/")
# def home():
#     return render_template("home.html")
    
