import os
import psycopg2


# ==================================================
# DATABASE CONNECTION
# ==================================================

DATABASE_URL = "postgres://postgres:jmoE3IDR2J8CM9mzF4CMEThhLPtWEhYLEzLdmwgcHOb45nV3oQijO2zULWmpqPmT@gtvyt3z2scwjupafsh1xqz78:5432/postgres"


def get_connection():

    if not DATABASE_URL:
        raise Exception("DATABASE_URL environment variable is not set")

    return psycopg2.connect(DATABASE_URL)


# ==================================================
# INITIALIZE DATABASE
# ==================================================

def init():

    conn = get_connection()
    cursor = conn.cursor()

    # Create table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS devices (
            id TEXT PRIMARY KEY,
            command TEXT DEFAULT 'none'
        )
    """)

    # Add timer_seconds if it doesn't exist
    cursor.execute("""
        ALTER TABLE devices
        ADD COLUMN IF NOT EXISTS timer_seconds INTEGER DEFAULT 0
    """)

    conn.commit()

    cursor.close()
    conn.close()

    print("PostgreSQL database connected")


# ==================================================
# CHECK ID
# ==================================================

def check_id(bot_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id
        FROM devices
        WHERE id=%s
        """,
        (bot_id,)
    )

    result = cursor.fetchone()

    cursor.close()
    conn.close()

    return result is not None


# ==================================================
# ADD DEVICE
# ==================================================

def add_device(bot_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO devices
        (id, command, timer_seconds)
        VALUES (%s, %s, %s)
        ON CONFLICT (id) DO NOTHING
        """,
        (bot_id, "none", 0)
    )

    conn.commit()

    cursor.close()
    conn.close()

    print("Added device:", bot_id)


# ==================================================
# SET COMMAND
# ==================================================

def set_command(bot_id, command):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE devices
        SET command=%s
        WHERE id=%s
        """,
        (command, bot_id)
    )

    conn.commit()

    cursor.close()
    conn.close()


# ==================================================
# GET COMMAND
# ==================================================

def get_command(bot_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT command
        FROM devices
        WHERE id=%s
        """,
        (bot_id,)
    )

    result = cursor.fetchone()

    cursor.close()
    conn.close()

    if result:
        return result[0]

    return "none"


# ==================================================
# CLEAR COMMAND
# ==================================================

def clear_command(bot_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE devices
        SET command='none'
        WHERE id=%s
        """,
        (bot_id,)
    )

    conn.commit()

    cursor.close()
    conn.close()


# ==================================================
# SET TIMER
# ==================================================

def set_timer(bot_id, seconds):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE devices
        SET timer_seconds=%s
        WHERE id=%s
        """,
        (seconds, bot_id)
    )

    conn.commit()

    cursor.close()
    conn.close()

    print("Database timer set:", bot_id, seconds)


# ==================================================
# GET TIMER
# ==================================================

def get_timer(bot_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT timer_seconds
        FROM devices
        WHERE id=%s
        """,
        (bot_id,)
    )

    result = cursor.fetchone()

    cursor.close()
    conn.close()

    if result:
        return result[0]

    return 0


# ==================================================
# CLEAR TIMER
# ==================================================

def clear_timer(bot_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE devices
        SET timer_seconds=0
        WHERE id=%s
        """,
        (bot_id,)
    )

    conn.commit()

    cursor.close()
    conn.close()

    print("Database timer cleared:", bot_id)


# ==================================================
# CLEAR DATABASE
# ==================================================

def clear_database():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM devices"
    )

    conn.commit()

    cursor.close()
    conn.close()

    print("Database cleared")


# ==================================================
# REMOVE DEVICE
# ==================================================

def remove_device(bot_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM devices
        WHERE id=%s
        """,
        (bot_id,)
    )

    conn.commit()

    cursor.close()
    conn.close()