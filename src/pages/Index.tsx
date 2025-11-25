import { useState } from "react";
import MapView from "@/components/MapView";
import RouteControls from "@/components/RouteControls";
import TelemetryPanel from "@/components/TelemetryPanel";
import AuditLog from "@/components/AuditLog";
import Header from "@/components/Header";

const Index = () => {
  const [route, setRoute] = useState<any>(null);
  const [telemetry, setTelemetry] = useState<any[]>([]);
  const [isQuantumMode, setIsQuantumMode] = useState(false);

  const handleRouteGenerated = (newRoute: any) => {
    setRoute(newRoute);
  };

  const handleTelemetryUpdate = (data: any) => {
    setTelemetry(prev => [...prev.slice(-50), data]);
  };

  return (
    <div className="min-h-screen bg-gradient-ocean flex flex-col">
      <Header 
        isQuantumMode={isQuantumMode} 
        onQuantumToggle={() => setIsQuantumMode(!isQuantumMode)} 
      />
      
      <main className="flex-1 flex gap-4 p-4">
        {/* Map - Takes most of the space */}
        <div className="flex-1 rounded-lg overflow-hidden border border-border shadow-deep">
          <MapView route={route} telemetry={telemetry} isQuantumMode={isQuantumMode} />
        </div>

        {/* Side Panel */}
        <aside className="w-96 flex flex-col gap-4">
          <RouteControls 
            onRouteGenerated={handleRouteGenerated}
            isQuantumMode={isQuantumMode}
          />
          <TelemetryPanel 
            telemetry={telemetry}
            onTelemetryUpdate={handleTelemetryUpdate}
          />
          <AuditLog />
        </aside>
      </main>
    </div>
  );
};

export default Index;
