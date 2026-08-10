import sqlite3

# Connect to SQLite
connection = sqlite3.connect("student.db")

# Create a cursor
cursor = connection.cursor()

# Create table
table_info = """
CREATE TABLE IF NOT EXISTS Student(
    Name VARCHAR(20),
    Class VARCHAR(25),
    Section VARCHAR(20),
    Marks INT
);
"""

cursor.execute(table_info)

# Insert records
cursor.execute(
    "INSERT INTO Student VALUES('John', '10th', 'A', 85)"
)

cursor.execute(
    "INSERT INTO Student VALUES('Alice', '10th', 'B', 90)"
)

cursor.execute(
    "INSERT INTO Student VALUES('Bob', '9th', 'A', 75)"
)

cursor.execute(
    "INSERT INTO Student VALUES('Eve', '9th', 'B', 80)"
)

cursor.execute(
    "INSERT INTO Student VALUES('Charlie', '10th', 'A', 95)"
)

# Print records
print("The inserted records are:")

data = cursor.execute(
    "SELECT * FROM Student"
)

for row in data:
    print(row)

# Save changes
connection.commit()

# Close connection
connection.close()