from flask import Flask

app= None

def init_app():
    ICSE=Flask(__name__)
    ICSE.debug=True
    ICSE.app_context().push()
    print("ICSE is running ...")
    return ICSE

app =  init_app()

from backend.controllers import *

if __name__=="__main__":
    app.run()




# @app.route('/')
# def index():
#     return render_template("index.html")



# if __name__== "__main__":
#     app.run(host= "localhost", port=8000, debug=True)

# @app.route('/dashboard')
# def dashboard():
#     return render_template("dashboard.html")