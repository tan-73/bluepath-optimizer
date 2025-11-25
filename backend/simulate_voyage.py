#!/usr/bin/env python3
"""
Voyage Simulation CLI Tool
Simulates a complete maritime voyage with telemetry
"""

import asyncio
import argparse
from telemetry_simulator import TelemetrySimulator
import requests
import json

async def simulate_voyage(
    route_id: str,
    duration_minutes: int = 60,
    api_url: str = "http://localhost:8000"
):
    """
    Simulate a complete voyage with telemetry streaming
    """
    print(f"🚢 Starting voyage simulation for route {route_id}")
    print(f"⏱️  Duration: {duration_minutes} minutes")
    print(f"🌊 Generating environmental data...\n")
    
    simulator = TelemetrySimulator(seed=42)
    
    for minute in range(duration_minutes):
        sample = simulator.generate_sample()
        sample['route_id'] = route_id
        
        # Send to API
        try:
            response = requests.post(
                f"{api_url}/api/iot/push",
                json=sample,
                timeout=5
            )
            
            status = "✅" if response.status_code == 200 else "❌"
            print(f"{status} [{minute:3d}min] Wave: {sample['wave_height']}m | "
                  f"Wind: {sample['wind_speed']}kt | "
                  f"Visibility: {sample['visibility']}nm")
            
            # Alert on high waves
            if sample['wave_height'] > 4.5:
                print(f"  ⚠️  HIGH WAVE ALERT! Re-optimization triggered")
        
        except Exception as e:
            print(f"❌ Error sending telemetry: {e}")
        
        await asyncio.sleep(1)  # 1 second = 1 minute in simulation
    
    print(f"\n✅ Voyage simulation completed!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simulate maritime voyage")
    parser.add_argument("--route-id", required=True, help="Route ID to simulate")
    parser.add_argument("--duration", type=int, default=60, help="Duration in minutes")
    parser.add_argument("--api-url", default="http://localhost:8000", help="API base URL")
    
    args = parser.parse_args()
    
    asyncio.run(simulate_voyage(
        route_id=args.route_id,
        duration_minutes=args.duration,
        api_url=args.api_url
    ))
