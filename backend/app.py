from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_from_directory
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import datetime
import time
from datetime import datetime, timedelta

app = Flask(__name__, template_folder='../frontend/templates', static_folder='../frontend/static')
app.secret_key = 'supersecretkey'  # Change this in production
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create uploads directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# MongoDB setup
MONGO_URI = os.environ.get('MONGO_URI', 'mongodb+srv://hello:Gnana123@voting.8vt5bip.mongodb.net/?retryWrites=true&w=majority&appName=voting')
client = MongoClient(MONGO_URI)
db = client['online_voting']

# Helper functions
def hash_password(password):
    return generate_password_hash(password)

def verify_password(password, password_hash):
    return check_password_hash(password_hash, password)

def get_user_collection():
    return db['users']

def get_election_collection():
    return db['elections']

def get_party_collection():
    return db['parties']

def get_vote_collection():
    return db['votes']

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_file(file):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Add timestamp to make filename unique
        timestamp = str(int(time.time()))
        filename = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return filename
    return None

def get_election_status(election):
    """Determine election status based on current time"""
    now = datetime.now()
    start_time = election.get('start_time')
    end_time = election.get('end_time')
    
    if not start_time or not end_time:
        return 'unknown'
    
    # Convert string to datetime if needed
    if isinstance(start_time, str):
        try:
            start_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        except:
            return 'unknown'
    
    if isinstance(end_time, str):
        try:
            end_time = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
        except:
            return 'unknown'
    
    # Determine status
    if now < start_time:
        return 'upcoming'
    elif start_time <= now <= end_time:
        return 'active'
    else:
        return 'ended'

def is_election_active(election):
    """Check if election is currently active based on start and end times"""
    return get_election_status(election) == 'active'

def format_time_remaining(election):
    """Calculate and format time remaining for election"""
    now = datetime.now()
    status = get_election_status(election)
    
    if status == 'ended':
        return "Election ended"
    
    # For upcoming elections, show time until start
    if status == 'upcoming':
        start_time = election.get('start_time')
        if isinstance(start_time, str):
            try:
                start_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            except:
                return "Invalid start time"
        
        time_diff = start_time - now
        days = time_diff.days
        hours, remainder = divmod(time_diff.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if days > 0:
            return f"Starts in {days}d {hours}h {minutes}m"
        elif hours > 0:
            return f"Starts in {hours}h {minutes}m"
        else:
            return f"Starts in {minutes}m {seconds}s"
    
    # For active elections, show time until end
    elif status == 'active':
        end_time = election.get('end_time')
        if isinstance(end_time, str):
            try:
                end_time = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            except:
                return "Invalid end time"
        
        time_diff = end_time - now
        days = time_diff.days
        hours, remainder = divmod(time_diff.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if days > 0:
            return f"Ends in {days}d {hours}h {minutes}m"
        elif hours > 0:
            return f"Ends in {hours}h {minutes}m"
        else:
            return f"Ends in {minutes}m {seconds}s"
    
    return "Unknown status"

# Initialize database collections
def init_db():
    # Create indexes for better performance
    users = get_user_collection()
    elections = get_election_collection()
    parties = get_party_collection()
    votes = get_vote_collection()
    
    # Create unique indexes with error handling
    try:
        users.create_index('email', unique=True)
    except Exception as e:
        print(f"Email index creation warning: {e}")
    
    try:
        votes.create_index([('voter_id', 1), ('election_id', 1)], unique=True)
    except Exception as e:
        print(f"Votes index creation warning: {e}")

# --- ROUTES ---

@app.route('/')
def index():
    return render_template('index.html')

# Voter Registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '')
            student_id = request.form.get('student_id', '').strip()
            
            # Validate input
            if not all([name, email, password]):
                flash('Name, email, and password are required.')
                return redirect(url_for('register'))
            
            users = get_user_collection()
            
            # Check if email already exists
            if users.find_one({'email': email}):
                flash('Email already registered.')
                return redirect(url_for('register'))
            
            # Check if student_id already exists (if provided)
            if student_id and users.find_one({'student_id': student_id}):
                flash('Student ID already registered.')
                return redirect(url_for('register'))
            
            # Create new user
            user_data = {
                'name': name,
                'email': email,
                'password_hash': hash_password(password),
                'student_id': student_id or f"USER_{int(time.time())}",
                'is_admin': False,
                'created_at': datetime.now()
            }
            
            result = users.insert_one(user_data)
            if result.inserted_id:
                flash('Registration successful! Please login.')
                return redirect(url_for('voter_login'))
            else:
                flash('Registration failed. Please try again.')
                return redirect(url_for('register'))
                
        except Exception as e:
            print(f"Registration error: {e}")
            flash('An error occurred during registration. Please try again.')
            return redirect(url_for('register'))
            
    return render_template('register.html')

# Voter Login
@app.route('/voter_login', methods=['GET', 'POST'])
def voter_login():
    if request.method == 'POST':
        try:
            email = request.form['email']
            password = request.form['password']
            
            if not email or not password:
                flash('Email and password are required.')
                return redirect(url_for('voter_login'))
            
            users = get_user_collection()
            user = users.find_one({'email': email, 'is_admin': False})
            
            if user and verify_password(password, user['password_hash']):
                session['user_id'] = str(user['_id'])
                session['user_name'] = user['name']
                session['is_admin'] = False
                return redirect(url_for('voter_dashboard'))
            else:
                flash('Invalid credentials.')
                return redirect(url_for('voter_login'))
                
        except Exception as e:
            print(f"Login error: {e}")
            flash('An error occurred during login. Please try again.')
            return redirect(url_for('voter_login'))
            
    return render_template('voter_login.html')

# Admin Login
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        try:
            email = request.form['email']
            password = request.form['password']
            
            if not email or not password:
                flash('Email and password are required.')
                return redirect(url_for('admin_login'))
            
            users = get_user_collection()
            user = users.find_one({'email': email, 'is_admin': True})
            
            if user and verify_password(password, user['password_hash']):
                session['user_id'] = str(user['_id'])
                session['user_name'] = user['name']
                session['is_admin'] = True
                return redirect(url_for('admin_dashboard'))
            else:
                flash('Invalid admin credentials.')
                return redirect(url_for('admin_login'))
                
        except Exception as e:
            print(f"Admin login error: {e}")
            flash('An error occurred during login. Please try again.')
            return redirect(url_for('admin_login'))
            
    return render_template('admin_login.html')

# Admin Dashboard
@app.route('/admin_dashboard')
def admin_dashboard():
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    
    try:
        elections = list(get_election_collection().find().sort('created_at', -1))
        
        # Add status to each election
        for election in elections:
            election['_id'] = str(election['_id'])
            election['status'] = get_election_status(election)
            election['time_remaining'] = format_time_remaining(election)
        
        voters = list(get_user_collection().find({'is_admin': False}))
        return render_template('admin_dashboard.html', elections=elections, voters=voters)
    except Exception as e:
        print(f"Admin dashboard error: {e}")
        flash('Error loading dashboard data.')
        return render_template('admin_dashboard.html', elections=[], voters=[])

# Create Election
@app.route('/create_election', methods=['GET', 'POST'])
def create_election():
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    
    if request.method == 'POST':
        try:
            election_name = request.form['election_name']
            start_date = request.form['start_date']
            start_time = request.form['start_time']
            end_date = request.form['end_date']
            end_time = request.form['end_time']
            
            if not all([election_name, start_date, start_time, end_date, end_time]):
                flash('All fields are required.')
                return redirect(url_for('create_election'))
            
            # Combine date and time
            start_datetime = datetime.strptime(f"{start_date} {start_time}", "%Y-%m-%d %H:%M")
            end_datetime = datetime.strptime(f"{end_date} {end_time}", "%Y-%m-%d %H:%M")
            
            if start_datetime >= end_datetime:
                flash('End time must be after start time.')
                return redirect(url_for('create_election'))
            
            elections = get_election_collection()
            election_data = {
                'name': election_name,
                'start_time': start_datetime,
                'end_time': end_datetime,
                'created_at': datetime.now(),
                'created_by': ObjectId(session['user_id'])
            }
            
            result = elections.insert_one(election_data)
            if result.inserted_id:
                flash('Election created successfully!')
                return redirect(url_for('manage_election', election_id=str(result.inserted_id)))
            else:
                flash('Failed to create election.')
                
        except Exception as e:
            print(f"Create election error: {e}")
            flash('Error creating election.')
            
    return render_template('create_election.html')

# Manage Election (Add Parties)
@app.route('/manage_election/<election_id>', methods=['GET', 'POST'])
def manage_election(election_id):
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    
    try:
        election = get_election_collection().find_one({'_id': ObjectId(election_id)})
        if not election:
            flash('Election not found.')
            return redirect(url_for('admin_dashboard'))
        
        parties = list(get_party_collection().find({'election_id': ObjectId(election_id)}))
        
        if request.method == 'POST':
            party_name = request.form['party_name']
            party_description = request.form.get('party_description', '')
            logo_file = request.files.get('logo')
            
            if not party_name:
                flash('Party name is required.')
                return redirect(url_for('manage_election', election_id=election_id))
            
            logo_filename = None
            if logo_file:
                logo_filename = save_file(logo_file)
            
            parties_col = get_party_collection()
            party_data = {
                'election_id': ObjectId(election_id),
                'name': party_name,
                'description': party_description,
                'logo_filename': logo_filename,
                'votes': 0,
                'created_at': datetime.now()
            }
            
            result = parties_col.insert_one(party_data)
            if result.inserted_id:
                flash('Party added successfully!')
            else:
                flash('Failed to add party.')
            
            return redirect(url_for('manage_election', election_id=election_id))
        
        return render_template('manage_election.html', election=election, parties=parties)
        
    except Exception as e:
        print(f"Manage election error: {e}")
        flash('Error managing election.')
        return redirect(url_for('admin_dashboard'))

# Delete Party
@app.route('/delete_party/<party_id>')
def delete_party(party_id):
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    
    try:
        parties = get_party_collection()
        party = parties.find_one({'_id': ObjectId(party_id)})
        
        if party:
            # Delete logo file if exists
            if party.get('logo_filename'):
                logo_path = os.path.join(app.config['UPLOAD_FOLDER'], party['logo_filename'])
                if os.path.exists(logo_path):
                    os.remove(logo_path)
            
            # Delete party
            parties.delete_one({'_id': ObjectId(party_id)})
            flash('Party deleted successfully.')
        else:
            flash('Party not found.')
            
    except Exception as e:
        print(f"Delete party error: {e}")
        flash('Error deleting party.')
    
    # Redirect back to manage election page
    if party:
        return redirect(url_for('manage_election', election_id=str(party['election_id'])))
    return redirect(url_for('admin_dashboard'))

# Delete Election
@app.route('/delete_election/<election_id>')
def delete_election(election_id):
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    
    try:
        elections = get_election_collection()
        parties = get_party_collection()
        votes = get_vote_collection()
        
        # Delete all parties and their logos
        election_parties = list(parties.find({'election_id': ObjectId(election_id)}))
        for party in election_parties:
            if party.get('logo_filename'):
                logo_path = os.path.join(app.config['UPLOAD_FOLDER'], party['logo_filename'])
                if os.path.exists(logo_path):
                    os.remove(logo_path)
        
        # Delete parties, votes, and election
        parties.delete_many({'election_id': ObjectId(election_id)})
        votes.delete_many({'election_id': ObjectId(election_id)})
        elections.delete_one({'_id': ObjectId(election_id)})
        
        flash('Election deleted successfully.')
        
    except Exception as e:
        print(f"Delete election error: {e}")
        flash('Error deleting election.')
        
    return redirect(url_for('admin_dashboard'))

# Voter Dashboard
@app.route('/voter_dashboard')
def voter_dashboard():
    if session.get('is_admin') or not session.get('user_id'):
        return redirect(url_for('voter_login'))
    
    try:
        users = get_user_collection()
        user = users.find_one({'_id': ObjectId(session['user_id'])})
        
        if not user:
            session.clear()
            flash('User not found. Please login again.')
            return redirect(url_for('voter_login'))
        
        # Get all elections with their status
        elections = list(get_election_collection().find().sort('start_time', -1))
        
        # Check which elections user has voted in
        votes = get_vote_collection()
        user_votes = list(votes.find({'voter_id': ObjectId(session['user_id'])}))
        voted_election_ids = [str(vote.get('election_id', '')) for vote in user_votes if vote.get('election_id')]
        
        # Add status and time remaining to each election
        for election in elections:
            election['_id'] = str(election['_id'])
            election['status'] = get_election_status(election)
            election['is_active'] = is_election_active(election)
            election['time_remaining'] = format_time_remaining(election)
            election['has_voted'] = str(election['_id']) in voted_election_ids
        
        return render_template('voter_dashboard.html', elections=elections, user=user)
        
    except Exception as e:
        print(f"Voter dashboard error: {e}")
        flash('Error loading dashboard.')
        return redirect(url_for('voter_login'))

# Vote in Election
@app.route('/vote/<election_id>', methods=['GET', 'POST'])
def vote(election_id):
    if session.get('is_admin') or not session.get('user_id'):
        return redirect(url_for('voter_login'))
    
    try:
        users = get_user_collection()
        user = users.find_one({'_id': ObjectId(session['user_id'])})
        
        if not user:
            session.clear()
            flash('User not found. Please login again.')
            return redirect(url_for('voter_login'))
        
        election = get_election_collection().find_one({'_id': ObjectId(election_id)})
        if not election:
            flash('Election not found.')
            return redirect(url_for('voter_dashboard'))
        
        # Check if user already voted
        votes = get_vote_collection()
        existing_vote = votes.find_one({
            'voter_id': ObjectId(session['user_id']),
            'election_id': ObjectId(election_id)
        })
        
        if existing_vote:
            flash('You have already voted in this election.')
            return redirect(url_for('voter_dashboard'))
        
        # Check if election is active
        if not is_election_active(election):
            flash('This election is not currently active.')
            return redirect(url_for('voter_dashboard'))
        
        parties = list(get_party_collection().find({'election_id': ObjectId(election_id)}))
        
        if request.method == 'POST':
            party_id = request.form.get('party_id')
            
            if not party_id:
                flash('Please select a party to vote for.')
                return render_template('vote.html', election=election, parties=parties, user=user)
            
            # Validate party exists
            party = get_party_collection().find_one({'_id': ObjectId(party_id)})
            if not party:
                flash('Invalid party selected.')
                return render_template('vote.html', election=election, parties=parties, user=user)
            
            # Record vote
            vote_data = {
                'voter_id': ObjectId(session['user_id']),
                'election_id': ObjectId(election_id),
                'party_id': ObjectId(party_id),
                'voted_at': datetime.now()
            }
            votes.insert_one(vote_data)
            
            # Update party vote count
            parties_col = get_party_collection()
            parties_col.update_one(
                {'_id': ObjectId(party_id)},
                {'$inc': {'votes': 1}}
            )
            
            flash('Vote recorded successfully!')
            return redirect(url_for('voter_dashboard'))
        
        return render_template('vote.html', election=election, parties=parties, user=user)
        
    except Exception as e:
        print(f"Vote error: {e}")
        flash('Error processing vote.')
        return redirect(url_for('voter_dashboard'))

# View Election Results
@app.route('/election_results/<election_id>')
def election_results(election_id):
    try:
        election = get_election_collection().find_one({'_id': ObjectId(election_id)})
        if not election:
            flash('Election not found.')
            return redirect(url_for('index'))
        # Add this two lines
        election['status'] = get_election_status(election)
        election['time_remaining'] = format_time_remaining(election)
        
        parties = list(get_party_collection().find({'election_id': ObjectId(election_id)}).sort('votes', -1))
        
        # Calculate total votes
        total_votes = sum(party['votes'] for party in parties)
        
        # Add percentage to each party
        for party in parties:
            party['percentage'] = (party['votes'] / total_votes * 100) if total_votes > 0 else 0
        
        return render_template('election_results.html', election=election, parties=parties, total_votes=total_votes)
        
    except Exception as e:
        print(f"Election results error: {e}")
        flash('Error loading results.')
        return redirect(url_for('index'))

# Serve uploaded files
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# API for live results
@app.route('/api/election_results/<election_id>')
def api_election_results(election_id):
    try:
        parties = list(get_party_collection().find({'election_id': ObjectId(election_id)}).sort('votes', -1))
        for party in parties:
            party['_id'] = str(party['_id'])
            party['election_id'] = str(party['election_id'])
        return jsonify(parties)
    except Exception as e:
        print(f"API results error: {e}")
        return jsonify([])

# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('index.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('index.html'), 500

if __name__ == '__main__':
    # Initialize database on startup
    try:
        init_db()
        print("Database initialized successfully")
    except Exception as e:
        print(f"Database initialization error: {e}")
    
    app.run(debug=True, host='0.0.0.0', port=5000) 