#!/usr/bin/env python3
"""
Online Voting System Startup Script
This script helps you set up and run the online voting system.
"""

import os
import sys
import subprocess
import time

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def check_mongodb():
    """Check if MongoDB is running"""
    print("\n🔍 Checking MongoDB connection...")
    try:
        import pymongo
        client = pymongo.MongoClient("mongodb+srv://hello:Gnana123@voting.8vt5bip.mongodb.net/?retryWrites=true&w=majority&appName=voting", serverSelectionTimeoutMS=5000)
        client.server_info()
        print("✅ MongoDB is running and accessible")
        return True
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        print("\n📋 To start MongoDB:")
        print("   Windows: Start MongoDB service or run 'mongod'")
        print("   macOS/Linux: sudo systemctl start mongod")
        print("   Docker: docker run -d -p 27017:27017 --name mongodb mongo:latest")
        return False

def main():
    """Main startup function"""
    print("🚀 Online Voting System Startup")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not os.path.exists("backend/app.py"):
        print("❌ Please run this script from the project root directory")
        sys.exit(1)
    
    # Check MongoDB
    if not check_mongodb():
        print("\n❌ Please start MongoDB and try again")
        sys.exit(1)
    
    # Install dependencies
    if not run_command("cd backend && pip install -r requirements.txt", "Installing dependencies"):
        print("\n❌ Failed to install dependencies")
        sys.exit(1)
    
    # Create admin user
    if not run_command("cd backend && python create_admin.py", "Creating admin user"):
        print("\n❌ Failed to create admin user")
        sys.exit(1)
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Admin Credentials:")
    print("   Email: admin@example.com")
    print("   Password: admin123")
    
    print("\n🚀 Starting the application...")
    print("   The application will be available at: http://localhost:5000")
    print("   Press Ctrl+C to stop the server")
    
    # Start the application
    try:
        os.chdir("backend")
        subprocess.run([sys.executable, "app.py"], check=True)
    except KeyboardInterrupt:
        print("\n\n👋 Application stopped by user")
    except Exception as e:
        print(f"\n❌ Failed to start application: {e}")

if __name__ == "__main__":
    main() 