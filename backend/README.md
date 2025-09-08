# Online Voting System - Backend

A Flask-based backend for an online voting system with MongoDB integration.

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start MongoDB
Make sure MongoDB is running on your system. If using Docker:
```bash
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

### 3. Create Admin User
```bash
python create_admin.py
```
This creates an admin user with:
- Email: admin@example.com
- Password: admin123

### 4. Run the Application
```bash
python app.py
```

**Note:** Make sure you're in the `backend` directory when running the application.

The application will be available at `http://localhost:5000`

## Features

- **User Registration**: Students can register with email and student ID
- **Voter Login**: Secure authentication for voters
- **Admin Login**: Administrative access for managing candidates
- **Voting System**: One vote per user with validation
- **Real-time Results**: Live vote counting and results display
- **Candidate Management**: Add/remove candidates (admin only)

## Database Collections

- **users**: Voter and admin user accounts
- **candidates**: Election candidates with vote counts
- **votes**: Individual vote records for audit trail

## Security Features

- Password hashing using Werkzeug
- Session-based authentication
- Input validation and sanitization
- Unique constraints on email and student ID
- Prevention of duplicate votes

## API Endpoints

- `GET /` - Home page
- `GET/POST /register` - User registration
- `GET/POST /voter_login` - Voter authentication
- `GET/POST /admin_login` - Admin authentication
- `GET /voter_dashboard` - Voting interface
- `GET /admin_dashboard` - Admin management panel
- `GET /results` - Election results
- `GET /api/results` - JSON API for results
- `POST /add_candidate` - Add new candidate (admin)
- `GET /delete_candidate/<id>` - Remove candidate (admin)
- `GET /logout` - Logout user

## Environment Variables

- `MONGO_URI`: MongoDB connection string (default: mongodb://localhost:27017/) 