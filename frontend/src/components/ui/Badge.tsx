import type { HTMLAttributes } from "react";
import { cn } from "@/lib/utils";

export function Badge({ className, ...props }: HTMLAttributes<HTMLSpanElement>) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full bg-[#f5f5f5] px-3 py-1 text-[13px] font-medium text-[#111111]",
        className,
      )}
      {...props}
    />
  );
}
