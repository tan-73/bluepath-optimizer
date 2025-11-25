import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Slider } from "@/components/ui/slider";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Navigation, Loader2 } from "lucide-react";
import { toast } from "sonner";

interface RouteControlsProps {
  onRouteGenerated: (route: any) => void;
  isQuantumMode: boolean;
}

const RouteControls = ({ onRouteGenerated, isQuantumMode }: RouteControlsProps) => {
  const [loading, setLoading] = useState(false);
  const [startLat, setStartLat] = useState("13.0827");
  const [startLon, setStartLon] = useState("80.2707");
  const [destLat, setDestLat] = useState("1.3521");
  const [destLon, setDestLon] = useState("103.8198");
  const [fuelPriority, setFuelPriority] = useState([50]);
  const [timePriority, setTimePriority] = useState([30]);
  const [safetyPriority, setSafetyPriority] = useState([20]);

  const generateRoute = async () => {
    setLoading(true);
    
    try {
      // Simulate route generation with HACOPSO
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      const start = [parseFloat(startLat), parseFloat(startLon)];
      const dest = [parseFloat(destLat), parseFloat(destLon)];
      
      // Generate a curved path between points
      const path = generateCurvedPath(start, dest, 20);
      
      const route = {
        path,
        distance: Math.round(calculateDistance(start, dest)),
        eta: "48 hrs",
        fuel: Math.round(calculateDistance(start, dest) * 0.5),
        optimization: {
          fuel: fuelPriority[0],
          time: timePriority[0],
          safety: safetyPriority[0],
        },
        quantumEnhanced: isQuantumMode,
      };
      
      onRouteGenerated(route);
    } catch (error) {
      toast.error("Failed to generate route");
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="bg-card border-border">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Navigation className="w-5 h-5 text-primary" />
          Route Configuration
        </CardTitle>
        <CardDescription>Configure waypoints and optimization priorities</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Start Port */}
        <div className="space-y-2">
          <Label className="text-sm font-medium">Start Port (Chennai)</Label>
          <div className="grid grid-cols-2 gap-2">
            <Input 
              placeholder="Latitude" 
              value={startLat}
              onChange={(e) => setStartLat(e.target.value)}
              className="bg-input border-border"
            />
            <Input 
              placeholder="Longitude" 
              value={startLon}
              onChange={(e) => setStartLon(e.target.value)}
              className="bg-input border-border"
            />
          </div>
        </div>

        {/* Destination Port */}
        <div className="space-y-2">
          <Label className="text-sm font-medium">Destination Port (Singapore)</Label>
          <div className="grid grid-cols-2 gap-2">
            <Input 
              placeholder="Latitude" 
              value={destLat}
              onChange={(e) => setDestLat(e.target.value)}
              className="bg-input border-border"
            />
            <Input 
              placeholder="Longitude" 
              value={destLon}
              onChange={(e) => setDestLon(e.target.value)}
              className="bg-input border-border"
            />
          </div>
        </div>

        {/* Priority Sliders */}
        <div className="space-y-4 pt-2">
          <div className="space-y-2">
            <div className="flex justify-between">
              <Label className="text-sm">Fuel Efficiency</Label>
              <span className="text-sm text-primary font-mono">{fuelPriority[0]}%</span>
            </div>
            <Slider 
              value={fuelPriority} 
              onValueChange={setFuelPriority}
              max={100}
              step={1}
              className="cursor-pointer"
            />
          </div>

          <div className="space-y-2">
            <div className="flex justify-between">
              <Label className="text-sm">Time Optimization</Label>
              <span className="text-sm text-primary font-mono">{timePriority[0]}%</span>
            </div>
            <Slider 
              value={timePriority} 
              onValueChange={setTimePriority}
              max={100}
              step={1}
              className="cursor-pointer"
            />
          </div>

          <div className="space-y-2">
            <div className="flex justify-between">
              <Label className="text-sm">Safety Priority</Label>
              <span className="text-sm text-primary font-mono">{safetyPriority[0]}%</span>
            </div>
            <Slider 
              value={safetyPriority} 
              onValueChange={setSafetyPriority}
              max={100}
              step={1}
              className="cursor-pointer"
            />
          </div>
        </div>

        {/* Generate Button */}
        <Button 
          onClick={generateRoute}
          disabled={loading}
          className="w-full bg-primary hover:bg-primary/90 text-primary-foreground shadow-neon"
        >
          {loading ? (
            <>
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              Computing Optimal Route...
            </>
          ) : (
            <>
              <Navigation className="w-4 h-4 mr-2" />
              Generate Route
            </>
          )}
        </Button>
      </CardContent>
    </Card>
  );
};

// Helper functions
function generateCurvedPath(start: number[], dest: number[], points: number): number[][] {
  const path: number[][] = [];
  for (let i = 0; i <= points; i++) {
    const t = i / points;
    const lat = start[0] + (dest[0] - start[0]) * t + Math.sin(t * Math.PI) * 2;
    const lon = start[1] + (dest[1] - start[1]) * t + Math.cos(t * Math.PI) * 1;
    path.push([lat, lon]);
  }
  return path;
}

function calculateDistance(start: number[], dest: number[]): number {
  const R = 3440; // Earth radius in nautical miles
  const lat1 = start[0] * Math.PI / 180;
  const lat2 = dest[0] * Math.PI / 180;
  const dLat = (dest[0] - start[0]) * Math.PI / 180;
  const dLon = (dest[1] - start[1]) * Math.PI / 180;
  
  const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
           Math.cos(lat1) * Math.cos(lat2) *
           Math.sin(dLon/2) * Math.sin(dLon/2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
  
  return R * c;
}

export default RouteControls;
