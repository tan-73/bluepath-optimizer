import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Activity, Play, Square, AlertTriangle } from "lucide-react";
import { toast } from "sonner";

interface TelemetryPanelProps {
  telemetry: any[];
  onTelemetryUpdate: (data: any) => void;
}

const TelemetryPanel = ({ telemetry, onTelemetryUpdate }: TelemetryPanelProps) => {
  const [isSimulating, setIsSimulating] = useState(false);
  const [intervalId, setIntervalId] = useState<NodeJS.Timeout | null>(null);

  const startSimulation = () => {
    setIsSimulating(true);
    toast.success("Telemetry simulation started");
    
    const id = setInterval(() => {
      const data = {
        timestamp: new Date().toISOString(),
        waveHeight: (Math.random() * 5 + 1).toFixed(2),
        windSpeed: (Math.random() * 30 + 10).toFixed(2),
        current: (Math.random() * 2).toFixed(2),
        visibility: (Math.random() * 10 + 5).toFixed(2),
        temperature: (Math.random() * 10 + 20).toFixed(2),
      };
      onTelemetryUpdate(data);
      
      // Alert on high waves
      if (parseFloat(data.waveHeight) > 4.5) {
        toast.warning("High wave alert!", {
          description: `Wave height: ${data.waveHeight}m`,
        });
      }
    }, 2000);
    
    setIntervalId(id);
  };

  const stopSimulation = () => {
    if (intervalId) {
      clearInterval(intervalId);
      setIntervalId(null);
    }
    setIsSimulating(false);
    toast.info("Telemetry simulation stopped");
  };

  return (
    <Card className="bg-card border-border">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Activity className="w-5 h-5 text-primary" />
          Live Telemetry
        </CardTitle>
        <CardDescription>Real-time environmental data</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <Button
          onClick={isSimulating ? stopSimulation : startSimulation}
          variant={isSimulating ? "secondary" : "default"}
          className="w-full"
        >
          {isSimulating ? (
            <>
              <Square className="w-4 h-4 mr-2" />
              Stop Simulation
            </>
          ) : (
            <>
              <Play className="w-4 h-4 mr-2" />
              Start Simulation
            </>
          )}
        </Button>

        <ScrollArea className="h-[200px] rounded-md border border-border bg-muted/30 p-3">
          {telemetry.length === 0 ? (
            <div className="flex items-center justify-center h-full text-muted-foreground text-sm">
              No telemetry data yet
            </div>
          ) : (
            <div className="space-y-2">
              {telemetry.slice().reverse().map((data, idx) => (
                <div 
                  key={idx} 
                  className="text-xs font-mono space-y-1 p-2 rounded bg-card/50 border border-border/50"
                >
                  <div className="text-muted-foreground">
                    {new Date(data.timestamp).toLocaleTimeString()}
                  </div>
                  <div className="grid grid-cols-2 gap-x-2">
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Wave:</span>
                      <span className={`text-primary ${parseFloat(data.waveHeight) > 4.5 ? 'text-destructive' : ''}`}>
                        {data.waveHeight}m
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Wind:</span>
                      <span className="text-primary">{data.windSpeed}kt</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Current:</span>
                      <span className="text-primary">{data.current}kt</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Vis:</span>
                      <span className="text-primary">{data.visibility}nm</span>
                    </div>
                  </div>
                  {parseFloat(data.waveHeight) > 4.5 && (
                    <div className="flex items-center gap-1 text-destructive">
                      <AlertTriangle className="w-3 h-3" />
                      <span>High wave warning</span>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </ScrollArea>
      </CardContent>
    </Card>
  );
};

export default TelemetryPanel;
