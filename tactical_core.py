# tactical_core.py
# Enhanced backend with MySQL and ad system hooks

import mysql.connector
import json
import random
import logging
from datetime import datetime
from flask import Flask, request, jsonify

# Configure logging
logging.basicConfig(filename='tactical.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

class TacticalCore:
    def __init__(self):
        self.setup_database()
        self.ad_providers = ['google_ads', 'unity_ads', 'applovin']
        logging.info("Tactical Core Initialized. Database connected.")

    def setup_database(self):
        """Connect to MySQL on AfriHost"""
        try:
            self.conn = mysql.connector.connect(
                host='localhost',
                user='YOUR_MYSQL_USERNAME',      # Replace with your MySQL username
                password='YOUR_MYSQL_PASSWORD',  # Replace with your MySQL password
                database='YOUR_DATABASE_NAME'    # Replace with your database name
            )
            self.cursor = self.conn.cursor()
            
            # Create players table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS players (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(255) UNIQUE,
                    token_count INT DEFAULT 100,
                    current_mission INT DEFAULT 0,
                    referral_code VARCHAR(50),
                    referrals INT DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create missions table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS missions (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    title VARCHAR(255),
                    description TEXT,
                    difficulty INT,
                    duration_min INT,
                    token_reward INT,
                    ai_generated BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create ads table for tracking
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS ad_events (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    player_id INT,
                    ad_provider VARCHAR(50),
                    revenue DECIMAL(10,4),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            self.conn.commit()
            logging.info("MySQL database setup complete.")
            
        except mysql.connector.Error as err:
            logging.error(f"Database connection failed: {err}")
            raise

    def load_missions(self):
        """Load initial missions"""
        base_missions = [
            ("Operation: BLACK ICE", "Infiltrate the data fortress 'Iceberg'. Expect heavy drone resistance.", 3, 15, 250),
            ("Operation: SANDSTORM", "Provide overwatch for a high-value convoy crossing the arid zone.", 2, 10, 150),
            ("Operation: PHANTOM SIGHT", "Locate and secure a captured intelligence agent.", 4, 20, 400)
        ]
        
        try:
            self.cursor.executemany('''
                INSERT IGNORE INTO missions (title, description, difficulty, duration_min, token_reward)
                VALUES (%s, %s, %s, %s, %s)
            ''', base_missions)
            self.conn.commit()
        except mysql.connector.Error as err:
            logging.error(f"Failed to load missions: {err}")

    def generate_referral_code(self, username):
        """Generate unique referral code"""
        code = f"TL-{username[:3]}-{random.randint(1000,9999)}"
        try:
            self.cursor.execute(
                'UPDATE players SET referral_code = %s WHERE username = %s',
                (code, username)
            )
            self.conn.commit()
            return code
        except mysql.connector.Error as err:
            logging.error(f"Referral code generation failed: {err}")
            return None

    def track_ad_event(self, player_id, provider, revenue=0.01):
        """Track ad views for future optimization"""
        try:
            self.cursor.execute(
                'INSERT INTO ad_events (player_id, ad_provider, revenue) VALUES (%s, %s, %s)',
                (player_id, provider, revenue)
            )
            self.conn.commit()
        except mysql.connector.Error as err:
            logging.error(f"Ad tracking failed: {err}")

    def complete_mission(self, username, mission_success=True):
        """Complete mission and trigger ads"""
        try:
            # Get player and mission data
            self.cursor.execute('SELECT id, token_count FROM players WHERE username = %s', (username,))
            player = self.cursor.fetchone()
            if not player:
                return {"status": "error", "message": "Player not found"}
            
            player_id, current_tokens = player
            
            # Calculate reward
            reward = 250 if mission_success else 50  # Base rewards
            
            # Simulate ad sequence - THIS IS WHERE ADS WILL PLAY
            ad_revenue = 0
            for i in range(3):  # 3 ads per mission completion
                provider = random.choice(self.ad_providers)
                self.track_ad_event(player_id, provider)
                ad_revenue += 0.03  # Simulated revenue per ad
            
            total_reward = reward + int(ad_revenue * 1000)  # Convert to tokens
            
            # Update player tokens
            new_balance = current_tokens + total_reward
            self.cursor.execute(
                'UPDATE players SET token_count = %s WHERE id = %s',
                (new_balance, player_id)
            )
            self.conn.commit()
            
            return {
                "status": "success", 
                "message": f"Mission complete. Earned {total_reward} tokens (incl. ad bonus).",
                "tokens": new_balance
            }
            
        except mysql.connector.Error as err:
            logging.error(f"Mission completion failed: {err}")
            return {"status": "error", "message": "Database error"}

# Flask App Setup
app = Flask(__name__)
core = TacticalCore()

@app.route('/api/player/add', methods=['POST'])
def api_add_player():
    data = request.get_json()
    username = data.get('username')
    
    try:
        core.cursor.execute('INSERT INTO players (username) VALUES (%s)', (username,))
        core.conn.commit()
        
        # Generate referral code
        referral_code = core.generate_referral_code(username)
        
        return jsonify({
            "status": "success", 
            "message": f"Welcome to Tactical Legends, {username}",
            "referral_code": referral_code
        })
        
    except mysql.connector.Error as err:
        return jsonify({"status": "error", "message": "Username already exists"})

@app.route('/api/mission/complete', methods=['POST'])
def api_complete_mission():
    data = request.get_json()
    username = data.get('username')
    success = data.get('success', True)
    
    result = core.complete_mission(username, success)
    return jsonify(result)

@app.route('/api/player/stats', methods=['GET'])
def api_player_stats():
    username = request.args.get('username')
    
    try:
        core.cursor.execute('''
            SELECT username, token_count, referral_code, referrals 
            FROM players WHERE username = %s
        ''', (username,))
        player = core.cursor.fetchone()
        
        if player:
            return jsonify({
                "username": player[0],
                "tokens": player[1],
                "referral_code": player[2],
                "referrals": player[3]
            })
        else:
            return jsonify({"status": "error", "message": "Player not found"})
            
    except mysql.connector.Error as err:
        return jsonify({"status": "error", "message": "Database error"})

if __name__ == '__main__':
    # Load initial data
    core.load_missions()
    
    # Start server
    logging.info("Starting Tactical Legends Server...")
    app.run(host='0.0.0.0', port=5000, debug=True)
