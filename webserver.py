from flask import Flask

from routes.public import public
from routes.auth import auth
from routes.admin.admin_dashboard import admin_dashboard
from routes.user.user_dashboard import user_dashboard
from routes.farmer.farmer_dashboard import farmer_dashboard
from routes.technologist.technologist_dashboard import technologist_dashboard

app = Flask(__name__)
app.secret_key = "Heinrich14"

app.register_blueprint(public)
app.register_blueprint(auth)
app.register_blueprint(admin_dashboard)
app.register_blueprint(user_dashboard)
app.register_blueprint(farmer_dashboard)
app.register_blueprint(technologist_dashboard)



if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)