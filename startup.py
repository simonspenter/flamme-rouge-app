# startup.py - Azure App Service entry point
import os
from app import app

if __name__ == "__main__":
    # Azure expects the app to run on the port specified by the PORT environment variable
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)