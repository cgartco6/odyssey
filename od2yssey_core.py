# odyssey_core.py
# The Brain of your Operation - Running on your AfriHost Server

import sqlite3  # Use your MySQL later, SQLite for simplicity now
import json
import random
import logging
from datetime import datetime

# Configure logging to see what your AI pack is doing
logging.basicConfig(filename='odyssey.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class OdysseyCore:
    """The central nervous system for your synthetic intelligence pack."""

    def __init__(self):
        self.setup_database()
        self.players = {}
        self.missions = self.load_missions()
        logging.info("Odyssey Core Initialized. Awaiting orders.")

    def setup_database(self):
        """Initialize the database. We'll use SQLite now, easy to switch to your MySQL later."""
        self.conn = sqlite3.connect('odyssey.db', check_same_thread=False)
        self.cursor = self.conn.cursor()
        # Create players table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS players (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE,
                token_count INTEGER DEFAULT 100,
                current_mission INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # Create missions table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS missions (
                id INTEGER PRIMARY KEY,
                title TEXT,
                description TEXT,
                difficulty INTEGER,
                duration_min INTEGER,
                token_reward INTEGER,
                ai_generated BOOLEAN DEFAULT 0
            )
        ''')
        self.conn.commit()
        logging.info("Database setup complete.")

    def load_missions(self):
        """Load mission templates. Later, this will call your AI Narrative Agent."""
        base_missions = [
            (1, "Operation: BLACK ICE", "Infiltrate the data fortress 'Iceberg' and extract the AI core. Expect heavy drone resistance.", 3, 15, 250),
            (2, "Operation: SANDSTORM", "Provide overwatch for a high-value convoy crossing the arid zone. Eliminate ambush threats.", 2, 10, 150),
            (3, "Operation: PHANTOM SIGHT", "Locate and secure a captured intelligence agent before the enemy extracts them.", 4, 20, 400)
        ]
        self.cursor.executemany('INSERT OR IGNORE INTO missions (id, title, description, difficulty, duration_min, token_reward) VALUES (?, ?, ?, ?, ?, ?)', base_missions)
        self.conn.commit()
        return base_missions

    def generate_ai_mission(self):
        """This function will be the bridge to your AI Helper (e.g., OpenAI API).
        For now, it creates a simple random mission. You will connect this to GPT-4 later."""
        locations = ["Neo-Kyoto", "Cairo Desolation Zone", "Orbital Platform X-12", "Arctic Bio-Lab"]
        objectives = ["Sabotage", "Recover", "Assassinate", "Escort"]
        targets = ["Communications Array", "Prototype Weapon", "Defector", "AI Core"]

        location = random.choice(locations)
        objective = random.choice(objectives)
        target = random.choice(targets)
        difficulty = random.randint(1, 5)
        reward = difficulty * 125

        ai_mission = {
            'title': f"Operation: {random.choice(['GHOST', 'IRON', 'SHADOW', 'BLADE'])} {random.choice(['WALTZ', 'HAMMER', 'EYE', 'STRIKE'])}",
            'description': f"{objective} the {target} in {location}. AI-Generated Mission.",
            'difficulty': difficulty,
            'duration_min': difficulty * 5,
            'token_reward': reward,
            'ai_generated': True
        }
        logging.info(f"AI Mission Generated: {ai_mission['title']}")
        return ai_mission

    def add_player(self, username):
        """Your Recruitment Agent will use this."""
        try:
            self.cursor.execute('INSERT INTO players (username) VALUES (?)', (username,))
            self.conn.commit()
            logging.info(f"New player recruited: {username}")
            return {"status": "success", "message": f"Welcome to the squad, {username}. You have been issued 100 tokens."}
        except sqlite3.IntegrityError:
            return {"status": "error", "message": "Call sign already in use."}

    def get_player_data(self, username):
        """Check a player's status."""
        self.cursor.execute('SELECT * FROM players WHERE username = ?', (username,))
        player = self.cursor.fetchone()
        if player:
            return {"id": player[0], "username": player[1], "tokens": player[2], "mission": player[3]}
        else:
            return {"status": "error", "message": "Player not found."}

    def complete_mission(self, username, mission_success=True):
        """This is called when a mission ends. Awards tokens and triggers the Ad Sequence."""
        player_data = self.get_player_data(username)
        if "status" in player_data and player_data["status"] == "error":
            return player_data

        mission_id = player_data['mission']
        self.cursor.execute('SELECT token_reward FROM missions WHERE id = ?', (mission_id,))
        reward = self.cursor.fetchone()[0]

        if not mission_success:
            reward = reward // 4  # Quarter tokens for failure

        new_token_count = player_data['tokens'] + reward
        self.cursor.execute('UPDATE players SET token_count = ? WHERE username = ?', (new_token_count, username))
        self.conn.commit()

        # !!! This is where you will trigger your 3-ad sequence before awarding rewards !!!
        logging.info(f"PLAYER {username} COMPLETED MISSION. {reward} tokens awarded. Total: {new_token_count}. ***TRIGGER AD SEQUENCE HERE***")

        return {"status": "success", "message": f"Mission debrief complete. {reward} tokens awarded.", "tokens": new_token_count}

# This is a simple Flask web server to make an API for your game to talk to.
# Install flask first: `pip install flask`
from flask import Flask, request, jsonify

app = Flask(__name__)
core = OdysseyCore()

@app.route('/api/player/add', methods=['POST'])
def api_add_player():
    data = request.get_json()
    username = data.get('username')
    result = core.add_player(username)
    return jsonify(result)

@app.route('/api/player/<username>', methods=['GET'])
def api_get_player(username):
    result = core.get_player_data(username)
    return jsonify(result)

@app.route('/api/mission/complete', methods=['POST'])
def api_complete_mission():
    data = request.get_json()
    username = data.get('username')
    success = data.get('success', True)
    result = core.complete_mission(username, success)
    return jsonify(result)

@app.route('/api/mission/ai_generate', methods=['GET'])
def api_generate_mission():
    result = core.generate_ai_mission()
    return jsonify(result)

if __name__ == '__main__':
    logging.info("Starting Odyssey Core Web Server...")
    app.run(host='0.0.0.0', port=5000, debug=True)
