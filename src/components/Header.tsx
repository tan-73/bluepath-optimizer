import { Ship, Zap } from "lucide-react";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";

interface HeaderProps {
  isQuantumMode: boolean;
  onQuantumToggle: () => void;
}

const Header = ({ isQuantumMode, onQuantumToggle }: HeaderProps) => {
  return (
    <header className="border-b border-border bg-card/50 backdrop-blur-sm">
      <div className="container mx-auto px-4 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="relative">
            <Ship className="w-8 h-8 text-primary" />
            <div className="absolute inset-0 blur-lg bg-primary/30 -z-10" />
          </div>
          <div>
            <h1 className="text-2xl font-bold bg-gradient-neon bg-clip-text text-transparent">
              BluePath
            </h1>
            <p className="text-xs text-muted-foreground">Maritime Route Optimization</p>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <Zap className={`w-4 h-4 ${isQuantumMode ? 'text-accent' : 'text-muted-foreground'}`} />
            <Label htmlFor="quantum-mode" className="text-sm cursor-pointer">
              Quantum Mode
            </Label>
            <Switch 
              id="quantum-mode"
              checked={isQuantumMode} 
              onCheckedChange={onQuantumToggle}
              className="data-[state=checked]:bg-accent"
            />
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
