import type { ButtonHTMLAttributes } from "react";
import { cn } from "@/lib/utils";

type ButtonVariant = "primary" | "secondary" | "ghost" | "icon";

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: ButtonVariant;
};

export function Button({ className, variant = "primary", ...props }: ButtonProps) {
  return (
    <button
      className={cn(
        "inline-flex h-10 items-center justify-center rounded-md text-sm font-semibold transition-colors disabled:pointer-events-none disabled:opacity-50",
        variant === "primary" && "bg-[#111111] px-4 text-white active:bg-[#242424]",
        variant === "secondary" &&
          "border border-[#e5e7eb] bg-white px-4 text-[#111111] active:bg-[#f5f5f5]",
        variant === "ghost" && "bg-transparent px-3 text-[#374151] active:bg-[#f5f5f5]",
        variant === "icon" &&
          "h-10 w-10 rounded-full border border-[#e5e7eb] bg-white text-[#111111] active:bg-[#f5f5f5]",
        className,
      )}
      {...props}
    />
  );
}
