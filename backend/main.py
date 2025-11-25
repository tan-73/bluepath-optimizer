"""
BluePath - Maritime Route Optimization System
FastAPI Backend with HACOPSO Algorithm
"""

from fastapi import FastAPI, WebSocket, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict
import asyncio
import json
from datetime import datetime
import hashlib
import hmac
import os

from hacopso import HACOPSO
from database import get_db, Route, Telemetry, AuditLog
from telemetry_simulator import TelemetrySimulator

app = FastAPI(
    title="BluePath API",
    description="Maritime Route Optimization with HACOPSO Algorithm",
    version="1.0.0"
)

# CORS middleware - Updated for production deployment
# Allow localhost for development + Vercel domains for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",
        "http://localhost:5173",
        "https://*.vercel.app",  # Vercel preview deployments
        "https://bluepath-optimizer.vercel.app",  # Production domain (update this with your actual domain)
        "*"  # Remove this in production after testing, keep only specific domains
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
active_websockets: Dict[str, List[WebSocket]] = {}
hacopso_optimizer = HACOPSO(
    n_particles=50,
    max_iterations=100,
    seed=42  # For reproducible demos
)

# Request/Response Models
class RouteRequest(BaseModel):
    start_lat: float
    start_lon: float
    dest_lat: float
    dest_lon: float
    priorities: Dict[str, float]  # fuel, time, safety
    ship_params: Optional[Dict] = None
    quantum_mode: bool = False

class RouteResponse(BaseModel):
    route_id: str
    path: List[List[float]]
    distance: float
    eta: str
    fuel_estimate: float
    optimization_scores: Dict[str, float]

class TelemetryData(BaseModel):
    route_id: str
    timestamp: str
    wave_height: float
    wind_speed: float
    current_speed: float
    visibility: float
    temperature: float

class AuditEntry(BaseModel):
    action: str
    data: Dict
    timestamp: str

# API Endpoints

@app.post("/api/route/compute", response_model=RouteResponse)
async def compute_route(request: RouteRequest, background_tasks: BackgroundTasks):
    """
    Compute optimal maritime route using HACOPSO algorithm
    """
    try:
        # Initialize optimizer with request parameters
        result = hacopso_optimizer.optimize(
            start=(request.start_lat, request.start_lon),
            destination=(request.dest_lat, request.dest_lon),
            priorities=request.priorities,
            quantum_enhanced=request.quantum_mode
        )
        
        # Generate route ID
        route_id = hashlib.sha256(
            f"{request.start_lat}{request.start_lon}{datetime.utcnow().isoformat()}".encode()
        ).hexdigest()[:16]
        
        # Store in database
        db = next(get_db())
        db_route = Route(
            route_id=route_id,
            path=json.dumps(result['path']),
            distance=result['distance'],
            eta=result['eta'],
            fuel_estimate=result['fuel'],
            scores=json.dumps(result['scores'])
        )
        db.add(db_route)
        db.commit()
        
        # Log to audit chain
        background_tasks.add_task(log_audit, "Route Computed", {
            "route_id": route_id,
            "distance": result['distance']
        })
        
        return RouteResponse(
            route_id=route_id,
            path=result['path'],
            distance=result['distance'],
            eta=result['eta'],
            fuel_estimate=result['fuel'],
            optimization_scores=result['scores']
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/route/{route_id}")
async def get_route(route_id: str):
    """
    Retrieve route information by ID
    """
    db = next(get_db())
    route = db.query(Route).filter(Route.route_id == route_id).first()
    
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    
    return {
        "route_id": route.route_id,
        "path": json.loads(route.path),
        "distance": route.distance,
        "eta": route.eta,
        "fuel_estimate": route.fuel_estimate,
        "scores": json.loads(route.scores)
    }

@app.post("/api/iot/push")
async def push_telemetry(data: TelemetryData):
    """
    Receive IoT telemetry data and trigger re-optimization if needed
    """
    db = next(get_db())
    
    # Store telemetry
    telemetry = Telemetry(
        route_id=data.route_id,
        timestamp=data.timestamp,
        wave_height=data.wave_height,
        wind_speed=data.wind_speed,
        current_speed=data.current_speed,
        visibility=data.visibility,
        temperature=data.temperature
    )
    db.add(telemetry)
    db.commit()
    
    # Check if re-optimization needed (e.g., high waves)
    if data.wave_height > 4.5:
        # Trigger re-optimization
        await trigger_reoptimization(data.route_id, data)
    
    # Broadcast to connected websockets
    if data.route_id in active_websockets:
        for ws in active_websockets[data.route_id]:
            await ws.send_json({
                "type": "telemetry_update",
                "data": data.dict()
            })
    
    return {"status": "received"}

@app.websocket("/ws/route/{route_id}")
async def websocket_route_updates(websocket: WebSocket, route_id: str):
    """
    WebSocket endpoint for real-time route updates
    """
    await websocket.accept()
    
    if route_id not in active_websockets:
        active_websockets[route_id] = []
    active_websockets[route_id].append(websocket)
    
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except:
        active_websockets[route_id].remove(websocket)
        if not active_websockets[route_id]:
            del active_websockets[route_id]

@app.post("/api/audit/log")
async def log_audit_entry(entry: AuditEntry):
    """
    Add entry to blockchain-style audit log
    """
    db = next(get_db())
    
    # Get previous hash
    last_entry = db.query(AuditLog).order_by(AuditLog.id.desc()).first()
    prev_hash = last_entry.hash if last_entry else "0" * 64
    
    # Compute new hash
    entry_data = f"{entry.action}{json.dumps(entry.data)}{entry.timestamp}{prev_hash}"
    new_hash = hashlib.sha256(entry_data.encode()).hexdigest()
    
    # Compute HMAC
    secret = os.getenv("AUDIT_SECRET", "default-secret-key")
    signature = hmac.new(secret.encode(), entry_data.encode(), hashlib.sha256).hexdigest()
    
    # Store
    audit_log = AuditLog(
        action=entry.action,
        data=json.dumps(entry.data),
        timestamp=entry.timestamp,
        hash=new_hash,
        signature=signature,
        prev_hash=prev_hash
    )
    db.add(audit_log)
    db.commit()
    
    return {"hash": new_hash, "signature": signature}

@app.get("/api/audit/verify")
async def verify_audit_chain():
    """
    Verify integrity of audit log chain
    """
    db = next(get_db())
    entries = db.query(AuditLog).order_by(AuditLog.id).all()
    
    if not entries:
        return {"valid": True, "message": "No entries to verify"}
    
    for i, entry in enumerate(entries):
        # Verify hash chain
        if i > 0:
            if entry.prev_hash != entries[i-1].hash:
                return {"valid": False, "message": f"Chain broken at entry {entry.id}"}
        
        # Verify signature
        secret = os.getenv("AUDIT_SECRET", "default-secret-key")
        entry_data = f"{entry.action}{entry.data}{entry.timestamp}{entry.prev_hash}"
        expected_sig = hmac.new(secret.encode(), entry_data.encode(), hashlib.sha256).hexdigest()
        
        if entry.signature != expected_sig:
            return {"valid": False, "message": f"Invalid signature at entry {entry.id}"}
    
    return {"valid": True, "message": f"All {len(entries)} entries verified"}

@app.post("/api/quantum/simulate")
async def quantum_simulate(request: Dict):
    """
    Quantum-enhanced route simulation (placeholder for quantum algorithm)
    """
    # This is a placeholder for quantum computing integration
    # In production, this would interface with actual quantum processors
    return {
        "quantum_enhanced": True,
        "entanglement_score": 0.95,
        "superposition_paths": 16,
        "message": "Quantum simulation completed"
    }

# Helper Functions

async def trigger_reoptimization(route_id: str, telemetry: TelemetryData):
    """
    Trigger route re-optimization based on telemetry
    """
    db = next(get_db())
    route = db.query(Route).filter(Route.route_id == route_id).first()
    
    if not route:
        return
    
    # Re-run optimization with updated environmental data
    result = hacopso_optimizer.reoptimize(
        current_path=json.loads(route.path),
        telemetry_data=telemetry.dict()
    )
    
    # Update route
    route.path = json.dumps(result['path'])
    route.distance = result['distance']
    route.eta = result['eta']
    route.fuel_estimate = result['fuel']
    db.commit()
    
    # Broadcast update
    if route_id in active_websockets:
        for ws in active_websockets[route_id]:
            await ws.send_json({
                "type": "route_update",
                "data": result
            })

async def log_audit(action: str, data: Dict):
    """
    Background task to log audit entries
    """
    entry = AuditEntry(
        action=action,
        data=data,
        timestamp=datetime.utcnow().isoformat()
    )
    await log_audit_entry(entry)

# Startup event
@app.on_event("startup")
async def startup_event():
    """
    Initialize database and load environmental data
    """
    print("🚢 BluePath Backend Starting...")
    print("📊 Loading environmental datasets...")
    print("🔄 Initializing HACOPSO optimizer...")
    print("✅ Backend ready!")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
