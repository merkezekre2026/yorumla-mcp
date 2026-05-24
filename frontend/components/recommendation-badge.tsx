import { Badge } from "@/components/ui/badge";
import type { Recommendation } from "@/lib/types";

export function RecommendationBadge({ value }: { value: Recommendation }) {
  const colors = {
    ALINIR: "bg-emerald-100 text-emerald-800",
    "DİKKATLİ AL": "bg-amber-100 text-amber-800",
    "UZAK DUR": "bg-red-100 text-red-800"
  };
  return <Badge className={colors[value]}>{value}</Badge>;
}
