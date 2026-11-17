"""SQL for the members table. No HTTP, no library rules.

Only get_member exists so far (loans and fines need it). The rest of the member
queries move here when the members domain is refactored.
"""
import db


def get_member(member_id):
    conn = db.connect()
    member = conn.execute("SELECT * FROM members WHERE id = ?", (member_id,)).fetchone()
    conn.close()
    return member
