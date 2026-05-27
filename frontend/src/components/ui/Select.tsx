import type { SelectHTMLAttributes } from "react";
import { cn } from "@/lib/utils";

export function Select({ className, ...props }: SelectHTMLAttributes<HTMLSelectElement>) {
  return (
    <select
      className={cn(
        "h-10 rounded-md border border-[#e5e7eb] bg-white px-3 text-sm font-medium text-[#111111] outline-none focus:border-[#111111]",
        className,
      )}
      {...props}
    />
  );
}
