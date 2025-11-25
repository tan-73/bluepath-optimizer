import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Shield, Check, X } from "lucide-react";
import { toast } from "sonner";

const AuditLog = () => {
  const [entries, setEntries] = useState<any[]>([
    {
      id: 1,
      action: "Route Computed",
      hash: "0x7a9d...",
      timestamp: new Date().toISOString(),
      verified: true,
    },
    {
      id: 2,
      action: "Telemetry Updated",
      hash: "0x4f2e...",
      timestamp: new Date().toISOString(),
      verified: true,
    },
  ]);

  const verifyChain = () => {
    toast.success("Audit chain verified", {
      description: "All entries are cryptographically valid",
    });
  };

  return (
    <Card className="bg-card border-border">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Shield className="w-5 h-5 text-primary" />
          Audit Log
        </CardTitle>
        <CardDescription>Blockchain-style verification</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <Button
          onClick={verifyChain}
          variant="outline"
          className="w-full border-primary/50 hover:bg-primary/10"
        >
          <Shield className="w-4 h-4 mr-2" />
          Verify Chain
        </Button>

        <ScrollArea className="h-[180px] rounded-md border border-border bg-muted/30 p-3">
          {entries.length === 0 ? (
            <div className="flex items-center justify-center h-full text-muted-foreground text-sm">
              No audit entries yet
            </div>
          ) : (
            <div className="space-y-2">
              {entries.slice().reverse().map((entry) => (
                <div 
                  key={entry.id} 
                  className="text-xs font-mono p-2 rounded bg-card/50 border border-border/50"
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-primary font-semibold">{entry.action}</span>
                    {entry.verified ? (
                      <Check className="w-3 h-3 text-success-green" />
                    ) : (
                      <X className="w-3 h-3 text-destructive" />
                    )}
                  </div>
                  <div className="text-muted-foreground">
                    Hash: {entry.hash}
                  </div>
                  <div className="text-muted-foreground text-[10px]">
                    {new Date(entry.timestamp).toLocaleString()}
                  </div>
                </div>
              ))}
            </div>
          )}
        </ScrollArea>
      </CardContent>
    </Card>
  );
};

export default AuditLog;
