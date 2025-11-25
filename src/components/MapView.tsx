import { useEffect, useRef, useState } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { toast } from "sonner";

// Fix for default marker icons
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
});

interface MapViewProps {
  route: any;
  telemetry: any[];
  isQuantumMode: boolean;
}

const MapView = ({ route, telemetry, isQuantumMode }: MapViewProps) => {
  const mapRef = useRef<L.Map | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const routeLayerRef = useRef<L.Polyline | null>(null);
  const shipMarkerRef = useRef<L.Marker | null>(null);
  const [animationProgress, setAnimationProgress] = useState(0);

  // Initialize map
  useEffect(() => {
    if (!containerRef.current || mapRef.current) return;

    const map = L.map(containerRef.current, {
      zoomControl: true,
      attributionControl: false,
    }).setView([20, 0], 2);

    // Dark ocean theme tiles
    L.tileLayer("https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png", {
      maxZoom: 19,
    }).addTo(map);

    mapRef.current = map;

    return () => {
      map.remove();
      mapRef.current = null;
    };
  }, []);

  // Update route
  useEffect(() => {
    if (!mapRef.current || !route?.path) return;

    // Remove old route
    if (routeLayerRef.current) {
      mapRef.current.removeLayer(routeLayerRef.current);
    }

    // Add new route with glowing effect
    const polyline = L.polyline(route.path, {
      color: isQuantumMode ? "#00ffff" : "#00bfff",
      weight: 3,
      opacity: 0.8,
      className: "route-line",
    }).addTo(mapRef.current);

    routeLayerRef.current = polyline;

    // Fit bounds to route
    mapRef.current.fitBounds(polyline.getBounds(), { padding: [50, 50] });

    // Add start and end markers
    if (route.path.length > 0) {
      L.marker(route.path[0])
        .addTo(mapRef.current)
        .bindPopup("Start Port");
      
      L.marker(route.path[route.path.length - 1])
        .addTo(mapRef.current)
        .bindPopup("Destination Port");
    }

    toast.success("Route generated successfully!");
  }, [route, isQuantumMode]);

  // Animate ship along route
  useEffect(() => {
    if (!mapRef.current || !route?.path || route.path.length < 2) return;

    const shipIcon = L.divIcon({
      className: "ship-marker",
      html: `
        <div class="relative">
          <div class="w-6 h-6 bg-primary rounded-full flex items-center justify-center shadow-glow-cyan">
            <svg class="w-4 h-4 text-background" fill="currentColor" viewBox="0 0 20 20">
              <path d="M3 10l7-7 7 7-7 7-7-7z"/>
            </svg>
          </div>
          <div class="absolute inset-0 bg-primary/30 rounded-full blur-lg -z-10"></div>
        </div>
      `,
      iconSize: [24, 24],
      iconAnchor: [12, 12],
    });

    if (shipMarkerRef.current) {
      mapRef.current.removeLayer(shipMarkerRef.current);
    }

    const marker = L.marker(route.path[0], { icon: shipIcon }).addTo(mapRef.current);
    shipMarkerRef.current = marker;

    // Animation loop
    let frame = 0;
    const totalFrames = route.path.length;
    const animationSpeed = 50;

    const animate = () => {
      if (frame < totalFrames - 1) {
        frame++;
        const progress = frame / (totalFrames - 1);
        setAnimationProgress(progress);
        
        if (shipMarkerRef.current && mapRef.current) {
          shipMarkerRef.current.setLatLng(route.path[frame]);
        }
        
        setTimeout(animate, animationSpeed);
      }
    };

    setTimeout(animate, 1000);
  }, [route]);

  return (
    <div className="relative w-full h-full">
      <div ref={containerRef} className="w-full h-full min-h-[600px]" />
      
      {/* Progress indicator */}
      {route && animationProgress > 0 && (
        <div className="absolute top-4 left-4 bg-card/90 backdrop-blur-sm p-3 rounded-lg border border-border shadow-deep">
          <div className="text-xs text-muted-foreground mb-1">Voyage Progress</div>
          <div className="flex items-center gap-2">
            <div className="w-32 h-2 bg-secondary rounded-full overflow-hidden">
              <div 
                className="h-full bg-gradient-neon transition-all duration-300"
                style={{ width: `${animationProgress * 100}%` }}
              />
            </div>
            <span className="text-sm font-mono text-primary">
              {Math.round(animationProgress * 100)}%
            </span>
          </div>
        </div>
      )}

      {/* Route info */}
      {route && (
        <div className="absolute bottom-4 left-4 bg-card/90 backdrop-blur-sm p-4 rounded-lg border border-border shadow-deep">
          <div className="grid grid-cols-3 gap-4 text-sm">
            <div>
              <div className="text-muted-foreground text-xs mb-1">Distance</div>
              <div className="text-primary font-mono">{route.distance || "N/A"} nm</div>
            </div>
            <div>
              <div className="text-muted-foreground text-xs mb-1">ETA</div>
              <div className="text-primary font-mono">{route.eta || "N/A"}</div>
            </div>
            <div>
              <div className="text-muted-foreground text-xs mb-1">Fuel Est.</div>
              <div className="text-primary font-mono">{route.fuel || "N/A"} t</div>
            </div>
          </div>
        </div>
      )}

      <style>{`
        .ship-marker {
          animation: pulse 2s ease-in-out infinite;
        }
        
        @keyframes pulse {
          0%, 100% { transform: scale(1); }
          50% { transform: scale(1.1); }
        }

        .route-line {
          filter: drop-shadow(0 0 10px rgba(0, 191, 255, 0.5));
        }
      `}</style>
    </div>
  );
};

export default MapView;
