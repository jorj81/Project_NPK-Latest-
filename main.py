from init_db import initialize_database
from webserver import app

if __name__ == "__main__":
    # Check and initialize the database on startup
    initialize_database()
    
    # Start the Flask web server
    app.run(host="0.0.0.0", debug=True)
