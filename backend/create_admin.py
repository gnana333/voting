from pymongo import MongoClient
from werkzeug.security import generate_password_hash
import os

# MongoDB setup
MONGO_URI = os.environ.get('MONGO_URI', 'mongodb+srv://hello:Gnana123@voting.8vt5bip.mongodb.net/?retryWrites=true&w=majority&appName=voting')
client = MongoClient(MONGO_URI)
db = client['online_voting']

def create_admin_user():
    """Create an admin user for testing"""
    users = db['users']
    
    # Check if admin already exists
    admin = users.find_one({'email': 'admin@example.com'})
    if admin:
        print("Admin user already exists!")
        return
    
    # Create admin user
    admin_data = {
        'name': 'Administrator',
        'email': 'admin@example.com',
        'password_hash': generate_password_hash('admin123'),
        'student_id': 'ADMIN001',
        'has_voted': False,
        'is_admin': True
    }
    
    result = users.insert_one(admin_data)
    if result.inserted_id:
        print("Admin user created successfully!")
        print("Email: admin@example.com")
        print("Password: admin123")
    else:
        print("Failed to create admin user!")

if __name__ == '__main__':
    create_admin_user() 