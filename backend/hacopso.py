"""
HACOPSO - Hybrid Adaptive Chaotic Opposition-Based Particle Swarm Optimization
Complete implementation for maritime route optimization
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import math

@dataclass
class Particle:
    """Particle in the swarm"""
    position: np.ndarray
    velocity: np.ndarray
    best_position: np.ndarray
    best_fitness: float
    fitness: float

class HACOPSO:
    """
    HACOPSO Algorithm for Multi-Objective Maritime Route Optimization
    
    Features:
    - Chaos operator for global exploration
    - Adaptive coefficients (w, c1, c2)
    - Opposition-based learning
    - Multi-objective optimization (fuel, time, safety)
    """
    
    def __init__(
        self,
        n_particles: int = 50,
        max_iterations: int = 100,
        seed: Optional[int] = None
    ):
        self.n_particles = n_particles
        self.max_iterations = max_iterations
        self.seed = seed
        
        if seed is not None:
            np.random.seed(seed)
        
        # Adaptive parameters
        self.w_max = 0.9  # Max inertia weight
        self.w_min = 0.4  # Min inertia weight
        self.c1_max = 2.5  # Max cognitive coefficient
        self.c1_min = 1.5  # Min cognitive coefficient
        self.c2_max = 2.5  # Max social coefficient
        self.c2_min = 1.5  # Min social coefficient
        
        # Chaos parameters
        self.chaos_factor = 0.1
        self.chaos_map = lambda x: 4 * x * (1 - x)  # Logistic map
        
        self.particles: List[Particle] = []
        self.global_best_position: Optional[np.ndarray] = None
        self.global_best_fitness: float = float('inf')
    
    def optimize(
        self,
        start: Tuple[float, float],
        destination: Tuple[float, float],
        priorities: Dict[str, float],
        quantum_enhanced: bool = False
    ) -> Dict:
        """
        Main optimization method
        
        Args:
            start: (lat, lon) starting coordinates
            destination: (lat, lon) destination coordinates
            priorities: weights for fuel, time, safety objectives
            quantum_enhanced: enable quantum-inspired enhancements
        
        Returns:
            Optimized route with path, metrics, and scores
        """
        # Initialize swarm
        self._initialize_swarm(start, destination)
        
        # Optimization loop
        for iteration in range(self.max_iterations):
            # Adaptive parameter calculation
            w = self._adaptive_inertia(iteration)
            c1 = self._adaptive_cognitive(iteration)
            c2 = self._adaptive_social(iteration)
            
            for particle in self.particles:
                # Evaluate fitness
                fitness = self._multi_objective_fitness(
                    particle.position,
                    start,
                    destination,
                    priorities
                )
                particle.fitness = fitness
                
                # Update personal best
                if fitness < particle.best_fitness:
                    particle.best_position = particle.position.copy()
                    particle.best_fitness = fitness
                
                # Update global best
                if fitness < self.global_best_fitness:
                    self.global_best_position = particle.position.copy()
                    self.global_best_fitness = fitness
            
            # Update velocities and positions
            for particle in self.particles:
                # PSO velocity update with chaos
                r1, r2 = np.random.rand(2)
                chaos = self._chaos_perturbation(iteration)
                
                particle.velocity = (
                    w * particle.velocity +
                    c1 * r1 * (particle.best_position - particle.position) +
                    c2 * r2 * (self.global_best_position - particle.position) +
                    chaos
                )
                
                # Position update
                particle.position = particle.position + particle.velocity
                
                # Boundary handling
                particle.position = self._handle_boundaries(
                    particle.position,
                    start,
                    destination
                )
            
            # Opposition-based learning
            if iteration % 10 == 0:
                self._opposition_based_learning(start, destination, priorities)
            
            # Quantum enhancement
            if quantum_enhanced and iteration % 5 == 0:
                self._quantum_enhancement()
        
        # Generate final route
        path = self._generate_path(start, destination, self.global_best_position)
        
        # Calculate metrics
        distance = self._calculate_distance(path)
        eta = self._estimate_eta(distance)
        fuel = self._estimate_fuel(distance, priorities)
        
        # Calculate individual objective scores
        scores = {
            "fuel": self._fuel_score(path),
            "time": self._time_score(path),
            "safety": self._safety_score(path),
            "overall": 100 - (self.global_best_fitness * 10)
        }
        
        return {
            "path": path,
            "distance": distance,
            "eta": eta,
            "fuel": fuel,
            "scores": scores
        }
    
    def reoptimize(
        self,
        current_path: List[List[float]],
        telemetry_data: Dict
    ) -> Dict:
        """
        Re-optimize route based on new telemetry data
        """
        # Extract environmental risks from telemetry
        wave_risk = telemetry_data['wave_height'] / 10.0
        wind_risk = telemetry_data['wind_speed'] / 50.0
        
        # Adjust priorities based on risk
        adjusted_priorities = {
            "fuel": 0.3,
            "time": 0.3,
            "safety": 0.4 + (wave_risk + wind_risk) / 2
        }
        
        # Find current and destination points
        start = current_path[len(current_path) // 3]  # Use point 1/3 through route
        destination = current_path[-1]
        
        # Re-run optimization
        return self.optimize(
            start=tuple(start),
            destination=tuple(destination),
            priorities=adjusted_priorities,
            quantum_enhanced=False
        )
    
    def _initialize_swarm(self, start: Tuple, destination: Tuple):
        """Initialize particle swarm"""
        self.particles = []
        dimension = 10  # Number of waypoints to optimize
        
        for _ in range(self.n_particles):
            # Random position between start and destination
            position = np.random.rand(dimension * 2)
            velocity = np.random.rand(dimension * 2) * 0.1
            
            particle = Particle(
                position=position,
                velocity=velocity,
                best_position=position.copy(),
                best_fitness=float('inf'),
                fitness=float('inf')
            )
            self.particles.append(particle)
    
    def _multi_objective_fitness(
        self,
        position: np.ndarray,
        start: Tuple,
        destination: Tuple,
        priorities: Dict
    ) -> float:
        """
        Multi-objective fitness function
        Combines fuel efficiency, time optimization, and safety
        """
        path = self._generate_path(start, destination, position)
        
        # Fuel objective (minimize distance and avoid rough areas)
        fuel_cost = self._fuel_score(path)
        
        # Time objective (minimize ETA)
        time_cost = self._time_score(path)
        
        # Safety objective (avoid hazards)
        safety_cost = self._safety_score(path)
        
        # Weighted sum
        total_cost = (
            priorities.get('fuel', 0.33) * fuel_cost +
            priorities.get('time', 0.33) * time_cost +
            priorities.get('safety', 0.34) * safety_cost
        )
        
        return total_cost
    
    def _generate_path(
        self,
        start: Tuple,
        destination: Tuple,
        position: np.ndarray
    ) -> List[List[float]]:
        """Generate waypoint path from particle position"""
        path = [list(start)]
        
        # Convert position vector to waypoints
        n_waypoints = len(position) // 2
        for i in range(n_waypoints):
            lat = start[0] + (destination[0] - start[0]) * position[i * 2]
            lon = start[1] + (destination[1] - start[1]) * position[i * 2 + 1]
            path.append([lat, lon])
        
        path.append(list(destination))
        return path
    
    def _calculate_distance(self, path: List[List[float]]) -> float:
        """Calculate total path distance in nautical miles"""
        total = 0
        for i in range(len(path) - 1):
            total += self._haversine(path[i], path[i + 1])
        return total
    
    def _haversine(self, coord1: List[float], coord2: List[float]) -> float:
        """Haversine formula for great circle distance"""
        R = 3440  # Earth radius in nautical miles
        lat1, lon1 = np.radians(coord1)
        lat2, lon2 = np.radians(coord2)
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
        c = 2 * np.arcsin(np.sqrt(a))
        
        return R * c
    
    def _fuel_score(self, path: List[List[float]]) -> float:
        """Calculate fuel efficiency score (0-1, lower is better)"""
        distance = self._calculate_distance(path)
        # Normalize by a typical long voyage distance
        return min(distance / 5000.0, 1.0)
    
    def _time_score(self, path: List[List[float]]) -> float:
        """Calculate time efficiency score (0-1, lower is better)"""
        # Consider both distance and path smoothness
        distance = self._calculate_distance(path)
        
        # Calculate path deviation (how much it deviates from straight line)
        direct_distance = self._haversine(path[0], path[-1])
        deviation = (distance - direct_distance) / max(direct_distance, 1)
        
        return min((distance / 5000.0 + deviation) / 2, 1.0)
    
    def _safety_score(self, path: List[List[float]]) -> float:
        """Calculate safety score (0-1, lower is better)"""
        # Simulate environmental hazards
        # In production, this would use real weather/ocean data
        hazard_score = 0
        
        for waypoint in path:
            # Simulate hazard probability based on location
            lat, lon = waypoint
            # Tropical storm zones, piracy areas, etc.
            if -10 <= lat <= 10:  # Tropical zones
                hazard_score += 0.1
            if abs(lat) > 60:  # Polar regions
                hazard_score += 0.2
        
        return min(hazard_score / len(path), 1.0)
    
    def _estimate_eta(self, distance: float) -> str:
        """Estimate time of arrival"""
        avg_speed = 15  # knots
        hours = distance / avg_speed
        return f"{int(hours)} hrs"
    
    def _estimate_fuel(self, distance: float, priorities: Dict) -> float:
        """Estimate fuel consumption in tonnes"""
        base_consumption = 0.5  # tonnes per nautical mile
        efficiency_factor = 1.0 - (priorities.get('fuel', 0.33) * 0.3)
        return distance * base_consumption * efficiency_factor
    
    def _adaptive_inertia(self, iteration: int) -> float:
        """Adaptive inertia weight"""
        return self.w_max - (self.w_max - self.w_min) * iteration / self.max_iterations
    
    def _adaptive_cognitive(self, iteration: int) -> float:
        """Adaptive cognitive coefficient"""
        return self.c1_max - (self.c1_max - self.c1_min) * iteration / self.max_iterations
    
    def _adaptive_social(self, iteration: int) -> float:
        """Adaptive social coefficient"""
        return self.c2_min + (self.c2_max - self.c2_min) * iteration / self.max_iterations
    
    def _chaos_perturbation(self, iteration: int) -> np.ndarray:
        """Chaotic perturbation using logistic map"""
        r = np.random.rand()
        chaos_val = self.chaos_map(r)
        magnitude = self.chaos_factor * (1 - iteration / self.max_iterations)
        return np.random.randn(len(self.particles[0].position)) * chaos_val * magnitude
    
    def _opposition_based_learning(
        self,
        start: Tuple,
        destination: Tuple,
        priorities: Dict
    ):
        """Opposition-based learning to escape local optima"""
        for particle in self.particles[:self.n_particles // 4]:  # Apply to 25% of swarm
            # Create opposite particle
            opposite_position = 1.0 - particle.position
            opposite_fitness = self._multi_objective_fitness(
                opposite_position,
                start,
                destination,
                priorities
            )
            
            # Replace if better
            if opposite_fitness < particle.fitness:
                particle.position = opposite_position
                particle.fitness = opposite_fitness
    
    def _quantum_enhancement(self):
        """Quantum-inspired enhancement (superposition and entanglement)"""
        # Simulate quantum superposition by creating hybrid particles
        for i in range(0, len(self.particles) - 1, 2):
            p1, p2 = self.particles[i], self.particles[i + 1]
            
            # Quantum entanglement: create superposition state
            alpha = np.random.rand()
            superposition = alpha * p1.position + (1 - alpha) * p2.position
            
            # Measure superposition (collapse to one state)
            if np.random.rand() < 0.5:
                p1.position = superposition
            else:
                p2.position = superposition
    
    def _handle_boundaries(
        self,
        position: np.ndarray,
        start: Tuple,
        destination: Tuple
    ) -> np.ndarray:
        """Handle position boundaries"""
        return np.clip(position, 0.0, 1.0)
