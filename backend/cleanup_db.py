from pymongo import MongoClient
import os

# MongoDB setup
MONGO_URI = os.environ.get('MONGO_URI', 'mongodb+srv://hello:Gnana123@voting.8vt5bip.mongodb.net/?retryWrites=true&w=majority&appName=voting')
client = MongoClient(MONGO_URI)
db = client['online_voting']

def cleanup_duplicates():
    """Clean up duplicate entries in the database"""
    users = db['users']
    
    print("Checking for duplicate student IDs...")
    
    # Find duplicate student IDs
    pipeline = [
        {"$group": {
            "_id": "$student_id",
            "count": {"$sum": 1},
            "docs": {"$push": "$_id"}
        }},
        {"$match": {"count": {"$gt": 1}}}
    ]
    
    duplicates = list(users.aggregate(pipeline))
    
    if duplicates:
        print(f"Found {len(duplicates)} duplicate student IDs:")
        for dup in duplicates:
            print(f"Student ID: {dup['_id']} - Count: {dup['count']}")
            
        # Keep the first document and remove others
        for dup in duplicates:
            docs_to_remove = dup['docs'][1:]  # Keep first, remove rest
            for doc_id in docs_to_remove:
                users.delete_one({"_id": doc_id})
                print(f"Removed duplicate document: {doc_id}")
    else:
        print("No duplicate student IDs found.")
    
    print("Checking for duplicate emails...")
    
    # Find duplicate emails
    pipeline = [
        {"$group": {
            "_id": "$email",
            "count": {"$sum": 1},
            "docs": {"$push": "$_id"}
        }},
        {"$match": {"count": {"$gt": 1}}}
    ]
    
    duplicates = list(users.aggregate(pipeline))
    
    if duplicates:
        print(f"Found {len(duplicates)} duplicate emails:")
        for dup in duplicates:
            print(f"Email: {dup['_id']} - Count: {dup['count']}")
            
        # Keep the first document and remove others
        for dup in duplicates:
            docs_to_remove = dup['docs'][1:]  # Keep first, remove rest
            for doc_id in docs_to_remove:
                users.delete_one({"_id": doc_id})
                print(f"Removed duplicate document: {doc_id}")
    else:
        print("No duplicate emails found.")

def reset_database():
    """Reset the entire database (WARNING: This will delete all data)"""
    response = input("This will delete ALL data. Are you sure? (yes/no): ")
    if response.lower() == 'yes':
        db.drop_collection('users')
        db.drop_collection('candidates')
        db.drop_collection('votes')
        print("Database reset complete.")
    else:
        print("Database reset cancelled.")

if __name__ == '__main__':
    print("Database cleanup utility")
    print("1. Clean up duplicates")
    print("2. Reset entire database")
    
    choice = input("Enter your choice (1 or 2): ")
    
    if choice == '1':
        cleanup_duplicates()
    elif choice == '2':
        reset_database()
    else:
        print("Invalid choice.") 