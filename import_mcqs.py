import sqlite3
import json

# Load MCQs from JSON file
with open("mcqs.json", "r", encoding="utf-8") as f:
    mcqs = json.load(f)

# Connect to the SQLite database
conn = sqlite3.connect("mcq.db")
cursor = conn.cursor()

# Insert each MCQ into the database
for mcq in mcqs:
    cursor.execute('''
        INSERT INTO mcqs (question, option1, option2, option3, option4, correct_answer)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        mcq['question'],
        mcq['options'][0],
        mcq['options'][1],
        mcq['options'][2],
        mcq['options'][3],
        mcq['answer']
    ))

conn.commit()
conn.close()

print("✅ MCQs imported successfully!")
