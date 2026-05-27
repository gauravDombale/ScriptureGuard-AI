import { CheckCircle2, TriangleAlert } from "lucide-react";
import type { VerseCitation } from "@/types";
import { Badge } from "./ui/Badge";

type Props = {
  citation: VerseCitation;
};

export function CitationCard({ citation }: Props) {
  return (
    <details className="rounded-md border border-[#e5e7eb] bg-[#f8f9fa]">
      <summary className="flex cursor-pointer list-none items-center justify-between gap-3 px-3 py-2 text-sm font-medium text-[#111111]">
        <span>{citation.reference}</span>
        {citation.verified ? (
          <Badge className="gap-1 bg-white px-2 py-0.5 text-xs">
            <CheckCircle2 aria-label="Verified citation" className="text-[#10b981]" size={14} />
            Verified
          </Badge>
        ) : (
          <TriangleAlert aria-label="Unverified citation" className="text-[#f59e0b]" size={17} />
        )}
      </summary>
      <p className="border-t border-[#e5e7eb] bg-white px-3 py-2 text-sm leading-6 text-[#374151]">
        {citation.text}
      </p>
    </details>
  );
}
