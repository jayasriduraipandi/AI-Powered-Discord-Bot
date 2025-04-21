import mysql.connector

# Database Connection
db = mysql.connector.connect(
    host="localhost",        # Change to your MySQL host
    user="root",             # Your MySQL username
    password="@jayasri15D", # Your MySQL password
    database="discord_bot"   # Your database name
)

cursor = db.cursor()

def add_user(user_id, username, role, department, join_date, birthday):
    sql = "INSERT INTO Users (user_id, username, role, department, join_date, birthday) VALUES (%s, %s, %s, %s, %s, %s)"
    values = (user_id, username, role, department, join_date, birthday)
    cursor.execute(sql, values)
    db.commit()
    print(f"User {username} added successfully!")

# Example Usage
add_user(123456789, "Anu", "Employee", "IT", "2024-02-25", "1995-05-10")
