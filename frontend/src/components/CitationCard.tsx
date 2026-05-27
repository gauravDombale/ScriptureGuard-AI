import { CheckCircle2, TriangleAlert } from "lucide-react";
import type { VerseCitation } from "@/types";

type Props = {
  citation: VerseCitation;
};

export function CitationCard({ citation }: Props) {
  return (
    <details className="rounded-md border border-[#d8d0c2] bg-[#fffdf8]">
      <summary className="flex cursor-pointer list-none items-center justify-between gap-3 px-3 py-2 text-sm font-medium">
        <span>{citation.reference}</span>
        {citation.verified ? (
          <CheckCircle2 aria-label="Verified citation" className="text-[#23705a]" size={17} />
        ) : (
          <TriangleAlert aria-label="Unverified citation" className="text-[#a15b14]" size={17} />
        )}
      </summary>
      <p className="border-t border-[#e4ded3] px-3 py-2 text-sm leading-6 text-[#3c3933]">
        {citation.text}
      </p>
    </details>
  );
}
