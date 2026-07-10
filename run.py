from app import create_app
from app.models import db

app = create_app()

# Ensure tables are created when starting the app in development
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
