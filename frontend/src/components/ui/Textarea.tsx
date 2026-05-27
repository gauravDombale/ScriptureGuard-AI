import { forwardRef, type TextareaHTMLAttributes } from "react";
import { cn } from "@/lib/utils";

export const Textarea = forwardRef<HTMLTextAreaElement, TextareaHTMLAttributes<HTMLTextAreaElement>>(
  function Textarea({ className, ...props }, ref) {
    return (
      <textarea
        ref={ref}
        className={cn(
          "min-h-11 resize-none rounded-md border border-[#e5e7eb] bg-white px-3 py-2 text-sm leading-6 text-[#111111] outline-none placeholder:text-[#898989] focus:border-[#111111]",
          className,
        )}
        {...props}
      />
    );
  },
);
