# tactical_legends_client.py
# Text-Based Terminal Frontend for TACTICAL LEGENDS: BLACK OPS

import requests
import json
import time
import random
import os
from datetime import datetime

# Configuration - UPDATE THIS WITH YOUR AFRIHOST IP
BASE_API_URL = "http://YOUR_AFRIHOST_IP:5000/api"

class TacticalLegendsClient:
    def __init__(self):
        self.username = None
        self.player_data = None
        self.current_mission = None
        self.available_weapons = {
            "Pistol": {"cost": 0, "damage": 10},
            "Assault Rifle": {"cost": 200, "damage": 25},
            "Sniper Rifle": {"cost": 500, "damage": 50},
            "Shotgun": {"cost": 300, "damage": 35},
            "Tactical SMG": {"cost": 400, "damage": 30}
        }
        self.player_weapon = "Pistol"
        self.team_members = ["Raven", "Ghost", "Viper", "Hunter"]  # AI squad members

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_header(self):
        print("=" * 70)
        print("          TACTICAL LEGENDS: BLACK OPS - COMMAND TERMINAL")
        print("=" * 70)
        if self.username:
            print(f"OPERATOR: {self.username} | TOKENS: {self.player_data.get('tokens', 0)}")
            print(f"EQUIPPED: {self.player_weapon} | AI SQUAD: {', '.join(self.team_members)}")
        print("=" * 70)

    def api_request(self, endpoint, method="GET", data=None):
        url = f"{BASE_API_URL}/{endpoint}"
        try:
            if method == "GET":
                response = requests.get(url)
            else:
                response = requests.post(url, json=data)
            
            return response.json()
        except requests.exceptions.ConnectionError:
            print("Cannot connect to Tactical Command. Is the server running?")
            return {"status": "error", "message": "Connection failed"}
        except Exception as e:
            print(f"COMMS ERROR: {e}")
            return {"status": "error", "message": str(e)}

    def login(self):
        self.clear_screen()
        self.print_header()
        print("\n[SECURE ACCESS - TACTICAL LEGENDS NETWORK]")
        print("-" * 55)
        
        username = input("ENTER YOUR TACTICAL CALL SIGN: ").strip()
        if not username:
            print("Invalid call sign. Authorization failed.")
            time.sleep(2)
            return False
        
        # Try to add player (will fail if already exists, which is fine)
        result = self.api_request("player/add", "POST", {"username": username})
        
        if result.get("status") == "error" and "already in use" in result.get("message", ""):
            print(f"Call sign {username} already active. Authenticating...")
        elif result.get("status") == "success":
            print(result.get("message", "Authorization successful!"))
        else:
            print("Security protocol violation. Try again.")
            time.sleep(2)
            return False
        
        # Get player data
        self.username = username
        self.player_data = self.api_request(f"player/{username}")
        time.sleep(2)
        return True

    def main_menu(self):
        while True:
            self.clear_screen()
            self.print_header()
            
            print("\nTACTICAL COMMAND MENU")
            print("-" * 40)
            print("1. Mission Operations")
            print("2. Armory & Equipment")
            print("3. Agent Dossier")
            print("4. AI Mission Generation")
            print("5. Squad Management")
            print("6. Exit to Safe Mode")
            
            choice = input("\nSELECT OPTION: ").strip()
            
            if choice == "1":
                self.mission_operations()
            elif choice == "2":
                self.armory()
            elif choice == "3":
                self.agent_dossier()
            elif choice == "4":
                self.generate_ai_mission()
            elif choice == "5":
                self.squad_management()
            elif choice == "6":
                print("Logging out. Stay vigilant, agent.")
                break
            else:
                print("Invalid option. Try again.")
                time.sleep(1)

    def mission_operations(self):
        self.clear_screen()
        self.print_header()
        
        print("\nMISSION OPERATIONS CENTER")
        print("-" * 45)
        print("Available Operations:")
        print("1. Operation: BLACK ICE (Difficulty: 3/5 - Urban Assault)")
        print("2. Operation: SANDSTORM (Difficulty: 2/5 - Desert Recon)")
        print("3. Operation: PHANTOM SIGHT (Difficulty: 4/5 - Stealth Infil)")
        print("4. Back to Command Menu")
        
        choice = input("\nSELECT OPERATION: ").strip()
        
        if choice == "1":
            self.play_mission(1, "Operation: BLACK ICE", 3, "Urban")
        elif choice == "2":
            self.play_mission(2, "Operation: SANDSTORM", 2, "Desert")
        elif choice == "3":
            self.play_mission(3, "Operation: PHANTOM SIGHT", 4, "Stealth")
        elif choice == "4":
            return
        else:
            print("Invalid operation selection.")
            time.sleep(1)

    def play_mission(self, mission_id, mission_name, difficulty, mission_type):
        self.clear_screen()
        self.print_header()
        
        print(f"\nMISSION: {mission_name}")
        print(f"TYPE: {mission_type} | DIFFICULTY: {difficulty}/5")
        print("-" * 50)
        
        # Mission briefing
        print("MISSION BRIEFING:")
        if mission_id == 1:
            print("Infiltrate the data fortress 'Iceberg' and extract the AI core.")
            print("Expect heavy drone resistance and enhanced security measures.")
        elif mission_id == 2:
            print("Provide overwatch for a high-value convoy crossing the arid zone.")
            print("Eliminate ambush threats and ensure safe passage.")
        elif mission_id == 3:
            print("Locate and secure a captured intelligence agent.")
            print("Maximum stealth required - avoid detection at all costs.")
        
        input("\nPress Enter to deploy...")
        
        # Simulate mission progress with text-based gameplay
        mission_phases = [
            "Inserting into mission zone...",
            "Establishing comms with squad...",
            f"{random.choice(self.team_members)}: Visual on target...",
            "Engaging hostiles...",
            f"{random.choice(self.team_members)}: Objective secured...",
            "Extracting with assets..."
        ]
        
        success_chance = 0.7 - (difficulty * 0.1) + (self.available_weapons[self.player_weapon]["damage"] * 0.01)
        success = random.random() <= success_chance
        
        for phase in mission_phases:
            print(f"\n{phase}")
            time.sleep(1.5)
            
            # Random event during mission
            if random.random() < 0.3:
                event = random.choice([
                    "Enemy patrol spotted!",
                    "Comms jammed temporarily...",
                    f"{random.choice(self.team_members)} provides covering fire!",
                    "Equipment functioning normally."
                ])
                print(f"   > {event}")
                time.sleep(1)
        
        print("\nMISSION STATUS: " + ("SUCCESS" if success else "FAILED"))
        
        # Complete mission via API
        result = self.api_request("mission/complete", "POST", {
            "username": self.username,
            "success": success
        })
        
        if result.get("status") == "success":
            print(f"\nMission complete! {result.get('message')}")
            self.player_data['tokens'] = result.get('tokens', self.player_data.get('tokens', 0))
        else:
            print(f"Error reporting mission status: {result.get('message')}")
        
        print("\n*** MISSION DEBRIEFING ***")
        print("Ad sequence would play here in the full game")
        input("\nPress Enter to return to command menu...")

    def armory(self):
        self.clear_screen()
        self.print_header()
        
        print("\nTACTICAL ARMORY")
        print("-" * 40)
        print("Available Weapons:")
        
        for i, (weapon, stats) in enumerate(self.available_weapons.items(), 1):
            owned = "(EQUIPPED)" if weapon == self.player_weapon else ""
            print(f"{i}. {weapon} - Damage: {stats['damage']} - Cost: {stats['cost']} tokens {owned}")
        
        print(f"\nYour tokens: {self.player_data.get('tokens', 0)}")
        print("0. Back to Command Menu")
        
        choice = input("\nSELECT WEAPON TO PURCHASE/EQUIP: ").strip()
        
        if choice == "0":
            return
        
        try:
            choice_idx = int(choice) - 1
            weapons = list(self.available_weapons.keys())
            if 0 <= choice_idx < len(weapons):
                selected_weapon = weapons[choice_idx]
                weapon_data = self.available_weapons[selected_weapon]
                
                if selected_weapon == self.player_weapon:
                    print(f"\n{selected_weapon} is already equipped.")
                elif self.player_data.get('tokens', 0) >= weapon_data['cost']:
                    # Deduct cost and equip weapon
                    self.player_data['tokens'] -= weapon_data['cost']
                    self.player_weapon = selected_weapon
                    print(f"\nWeapon equipped: {selected_weapon}")
                else:
                    print("\nInsufficient tokens for this weapon.")
            else:
                print("\nInvalid weapon selection.")
        except ValueError:
            print("\nPlease enter a valid number.")
        
        input("\nPress Enter to continue...")

    def agent_dossier(self):
        self.clear_screen()
        self.print_header()
        
        print("\nAGENT DOSSIER - TOP SECRET")
        print("-" * 45)
        print(f"Call Sign: {self.username}")
        print(f"Security Clearance: LEVEL 4")
        print(f"Token Balance: {self.player_data.get('tokens', 0)}")
        print(f"Primary Weapon: {self.player_weapon}")
        print(f"Damage Output: {self.available_weapons[self.player_weapon]['damage']}")
        print(f"Active Squad: {', '.join(self.team_members)}")
        print("\nMission Statistics:")
        print("Completed: Classified")
        print("Success Rate: Classified")
        print("Threats Neutralized: Classified")
        
        input("\nPress Enter to return to command menu...")

    def generate_ai_mission(self):
        self.clear_screen()
        self.print_header()
        
        print("\nAI MISSION GENERATION PROTOCOL")
        print("-" * 45)
        print("Accessing tactical AI network...")
        time.sleep(2)
        
        result = self.api_request("mission/ai_generate")
        
        if "title" in result:
            print(f"\nAI MISSION GENERATED: {result['title']}")
            print(f"INTEL: {result['description']}")
            print(f"DIFFICULTY: {result['difficulty']}/5")
            print(f"ESTIMATED DURATION: {result['duration_min']} minutes")
            print(f"POTENTIAL REWARD: {result['token_reward']} tokens")
            
            play = input("\nExecute this mission? (y/n): ").lower()
            if play == 'y':
                mission_types = ["Assault", "Recon", "Stealth", "Extraction"]
                self.play_mission(99, result['title'], result['difficulty'], random.choice(mission_types))
        else:
            print("Failed to generate AI mission. Network issue.")
        
        input("\nPress Enter to return to command menu...")

    def squad_management(self):
        self.clear_screen()
        self.print_header()
        
        print("\nAI SQUAD MANAGEMENT")
        print("-" * 40)
        print("Current Squad Members:")
        for i, member in enumerate(self.team_members, 1):
            print(f"{i}. {member} - Status: READY")
        
        print("\nSquad functions are currently in development.")
        print("Future versions will allow squad customization and upgrades.")
        
        input("\nPress Enter to return to command menu...")

def main():
    client = TacticalLegendsClient()
    
    # Login sequence
    print("Initializing Tactical Legends: Black Ops...")
    time.sleep(1)
    print("Security protocols engaged...")
    time.sleep(1)
    
    # Login loop
    while not client.login():
        pass
    
    # Main game loop
    client.main_menu()

if __name__ == "__main__":
    main()
