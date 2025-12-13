import { Badge } from "@/components/ui/badge";
import { AlertCircle, Check, AlertTriangle } from "lucide-react";

interface StockIndicatorProps {
  quantity: number;
}

export function StockIndicator({ quantity }: StockIndicatorProps) {
  if (quantity === 0) {
    return (
      <Badge
        data-testid="badge-stock-sold-out"
        className="bg-red-500/90 text-white border-red-600/50 backdrop-blur-sm gap-1.5"
      >
        <AlertCircle className="w-3.5 h-3.5" />
        <span>Sold Out</span>
      </Badge>
    );
  }

  if (quantity <= 3) {
    return (
      <Badge
        data-testid="badge-stock-low"
        className="bg-amber-500/90 text-white border-amber-600/50 backdrop-blur-sm gap-1.5"
      >
        <AlertTriangle className="w-3.5 h-3.5" />
        <span>Only {quantity} left</span>
      </Badge>
    );
  }

  return (
    <Badge
      data-testid="badge-stock-available"
      className="bg-emerald-500/90 text-white border-emerald-600/50 backdrop-blur-sm gap-1.5"
    >
      <Check className="w-3.5 h-3.5" />
      <span>In Stock</span>
    </Badge>
  );
}
