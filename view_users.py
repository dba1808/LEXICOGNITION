"""
ORION - View Database Users
"""
import sqlite3
from pathlib import Path

db_path = Path(__file__).parent / "data" / "lexicognition.db"
output_file = Path(__file__).parent / "users_report.txt"

lines = []
lines.append("=" * 80)
lines.append("ORION DATABASE - REGISTERED USERS")
lines.append("=" * 80)

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, name, email, role, class_name, created_at 
        FROM users 
        ORDER BY id
    ''')
    rows = cursor.fetchall()
    
    if rows:
        lines.append("")
        lines.append(f"{'ID':<5} {'Name':<25} {'Email':<35} {'Role':<10} {'Class'}")
        lines.append("-" * 80)
        for row in rows:
            user_id, name, email, role, class_name, created_at = row
            lines.append(f"{user_id:<5} {name:<25} {email:<35} {role:<10} {class_name or '-'}")
        lines.append("-" * 80)
        lines.append(f"Total users: {len(rows)}")
    else:
        lines.append("No users found in database")
    
    conn.close()

except Exception as e:
    lines.append(f"Error: {e}")

lines.append("=" * 80)

# Write to file
with open(output_file, "w") as f:
    f.write("\n".join(lines))

print(f"Report saved to: {output_file}")
print("\n".join(lines))
