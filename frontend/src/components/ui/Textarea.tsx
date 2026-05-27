import type { TextareaHTMLAttributes } from "react";
import { cn } from "@/lib/utils";

export function Textarea({ className, ...props }: TextareaHTMLAttributes<HTMLTextAreaElement>) {
  return (
    <textarea
      className={cn(
        "min-h-11 resize-none rounded-md border border-[#e5e7eb] bg-white px-3 py-2 text-sm leading-6 text-[#111111] outline-none placeholder:text-[#898989] focus:border-[#111111]",
        className,
      )}
      {...props}
    />
  );
}
