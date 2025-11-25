"""
IoT Telemetry Simulator
Generates realistic maritime environmental data
"""

import random
import time
from datetime import datetime
from typing import Dict

class TelemetrySimulator:
    """
    Simulates maritime environmental telemetry data
    """
    
    def __init__(self, seed: int = None):
        if seed:
            random.seed(seed)
        
        self.base_wave = 2.5
        self.base_wind = 20.0
        self.base_current = 1.0
        self.base_visibility = 10.0
        self.base_temp = 25.0
    
    def generate_sample(self) -> Dict:
        """Generate a single telemetry sample"""
        # Add random variations
        wave_height = max(0.5, self.base_wave + random.gauss(0, 1.0))
        wind_speed = max(5, self.base_wind + random.gauss(0, 5))
        current = max(0, self.base_current + random.gauss(0, 0.5))
        visibility = max(1, self.base_visibility + random.gauss(0, 3))
        temperature = self.base_temp + random.gauss(0, 2)
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "wave_height": round(wave_height, 2),
            "wind_speed": round(wind_speed, 2),
            "current_speed": round(current, 2),
            "visibility": round(visibility, 2),
            "temperature": round(temperature, 2)
        }
    
    def simulate_storm(self):
        """Simulate storm conditions"""
        self.base_wave = 6.0
        self.base_wind = 45.0
        self.base_current = 2.5
        self.base_visibility = 3.0
    
    def reset_normal(self):
        """Reset to normal conditions"""
        self.base_wave = 2.5
        self.base_wind = 20.0
        self.base_current = 1.0
        self.base_visibility = 10.0
    
    def generate_voyage_data(self, duration_minutes: int = 60, interval_seconds: int = 10):
        """Generate data for entire voyage simulation"""
        samples = []
        num_samples = (duration_minutes * 60) // interval_seconds
        
        for i in range(num_samples):
            # Introduce storm at 30% through voyage
            if i == int(num_samples * 0.3):
                self.simulate_storm()
            # Clear storm at 60% through voyage
            if i == int(num_samples * 0.6):
                self.reset_normal()
            
            samples.append(self.generate_sample())
            time.sleep(interval_seconds / 1000)  # Scale down for demo
        
        return samples
