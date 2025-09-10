class ReferralSystem:
    def __init__(self):
        self.referral_codes = {}
        self.rewards = {
            '5_referrals': {'tokens': 500, 'weapon': 'Tactical SMG'},
            '25_referrals': {'tokens': 2000, 'weapon': 'Advanced Rifle'},
            '100_referrals': {'tokens': 10000, 'weapon': 'Legendary Sniper'}
        }
    
    def generate_referral_code(self, username):
        code = f"TL-{username[:3]}-{random.randint(1000,9999)}"
        self.referral_codes[code] = {'user': username, 'count': 0}
        return code
    
    def apply_referral(self, code, new_user):
        if code in self.referral_codes:
            self.referral_codes[code]['count'] += 1
            self.grant_rewards(code, new_user)
            return True
        return False
