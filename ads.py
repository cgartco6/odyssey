# Ad sequence management
class AdManager:
    def __init__(self):
        self.ad_providers = ['google_ads', 'unity_ads', 'applovin']
        self.ad_metrics = {}
    
    def trigger_ad_sequence(self, mission_result):
        # Show 3 ads after mission completion
        for i in range(3):
            ad_provider = self.select_optimal_provider()
            self.display_ad(ad_provider)
            self.track_ad_performance(ad_provider)
        
        # Award bonus tokens based on ad performance
        bonus = self.calculate_bonus_tokens()
        return bonus
    
    def select_optimal_provider(self):
        # Simple rotation - will be enhanced with AI later
        return random.choice(self.ad_providers)
