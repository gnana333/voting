# Online Voting System

A comprehensive online voting system built with Flask and MongoDB, featuring multiple elections, real-time timers, party logos, and enhanced admin/voter dashboards.

## 🚀 Features

### Admin Features
- **Multiple Elections Management**: Create and manage multiple voting events
- **Election Scheduling**: Set start and end dates/times for each election
- **Party Management**: Add parties with logos and descriptions
- **Real-time Monitoring**: Track election status and voter participation
- **Results Visualization**: View detailed election results with charts

### Voter Features
- **Multiple Elections**: View and participate in multiple elections
- **Real-time Timers**: Live countdown timers for election periods
- **Party Logos**: Visual party selection with uploaded logos
- **One Vote Per Election**: Secure voting with duplicate prevention
- **Voting History**: Track which elections you've participated in

### System Features
- **Secure Authentication**: Password hashing and session management
- **File Upload**: Party logo upload with validation
- **Real-time Updates**: Live results and status updates
- **Responsive Design**: Modern UI with Bootstrap and Font Awesome
- **MongoDB Integration**: Robust database with proper indexing

## 🛠️ Technology Stack

- **Backend**: Flask (Python)
- **Database**: MongoDB
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **File Handling**: Werkzeug
- **Charts**: Chart.js
- **Icons**: Font Awesome

## 📋 Prerequisites

- Python 3.7+
- MongoDB (local or cloud)
- pip (Python package manager)

## 🚀 Installation & Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd online-voting
```

### 2. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 3. Start MongoDB
Make sure MongoDB is running on your system.

**Local MongoDB:**
```bash
# Windows
mongod

# macOS/Linux
sudo systemctl start mongod
```

**Docker MongoDB:**
```bash
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

### 4. Create Admin User
```bash
cd backend
python create_admin.py
```

This creates an admin user with:
- **Email**: admin@example.com
- **Password**: admin123

### 5. Run the Application
```bash
cd backend
python app.py
```

The application will be available at `http://localhost:5000`

## 📖 Usage Guide

### Admin Workflow
1. **Login**: Use admin credentials to access admin dashboard
2. **Create Election**: Set election name, start/end dates and times
3. **Add Parties**: Upload party logos and descriptions
4. **Monitor**: Track election progress and voter participation
5. **View Results**: Analyze election results with charts

### Voter Workflow
1. **Register**: Create account with email and password
2. **Login**: Access voter dashboard
3. **View Elections**: See available elections with timers
4. **Vote**: Select party and cast vote (once per election)
5. **Track**: Monitor voting history and results

## 🗄️ Database Schema

### Collections
- **users**: Voter and admin accounts
- **elections**: Election details and scheduling
- **parties**: Party information and logos
- **votes**: Individual vote records

### Key Fields
- **users**: name, email, password_hash, student_id, is_admin
- **elections**: name, start_time, end_time, status, created_at
- **parties**: election_id, name, description, logo_filename, votes
- **votes**: voter_id, election_id, party_id, voted_at

## 🔧 Configuration

### Environment Variables
- `MONGO_URI`: MongoDB connection string (default: mongodb://localhost:27017/)

### File Upload Settings
- **Upload Folder**: `backend/uploads/`
- **Allowed Extensions**: PNG, JPG, JPEG, GIF
- **Max File Size**: 5MB

## 🛡️ Security Features

- Password hashing with Werkzeug
- Session-based authentication
- Input validation and sanitization
- File upload validation
- Unique constraints on critical fields
- Prevention of duplicate votes

## 📊 API Endpoints

### Public Routes
- `GET /` - Home page
- `GET /register` - Voter registration
- `GET /voter_login` - Voter login
- `GET /admin_login` - Admin login
- `GET /election_results/<id>` - View election results

### Admin Routes
- `GET /admin_dashboard` - Admin dashboard
- `GET/POST /create_election` - Create new election
- `GET/POST /manage_election/<id>` - Manage election parties
- `GET /delete_election/<id>` - Delete election
- `GET /delete_party/<id>` - Delete party

### Voter Routes
- `GET /voter_dashboard` - Voter dashboard
- `GET/POST /vote/<id>` - Cast vote
- `GET /logout` - Logout

### API Routes
- `GET /api/election_results/<id>` - JSON results API
- `GET /uploads/<filename>` - Serve uploaded files

## 🐛 Troubleshooting

### Common Issues

1. **MongoDB Connection Error**
   - Ensure MongoDB is running
   - Check connection string in environment variables

2. **File Upload Issues**
   - Verify uploads directory exists
   - Check file size and format restrictions

3. **Admin Login Problems**
   - Run `python create_admin.py` to create admin user
   - Verify admin credentials

4. **Database Index Errors**
   - Run `python cleanup_db.py` to clean duplicate data
   - Check MongoDB logs for specific errors

### Database Cleanup
```bash
cd backend
python cleanup_db.py
```

## 📝 License

This project is licensed under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For support and questions, please open an issue in the repository.

---

**Note**: This is a development system. For production use, implement additional security measures, SSL certificates, and proper error handling. 