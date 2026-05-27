import { FormEvent, useState } from "react";
import { ImageIcon, Send, TextCursorInput } from "lucide-react";
import { Button } from "./ui/Button";
import { Textarea } from "./ui/Textarea";
import { cn } from "@/lib/utils";

type Props = {
  mode: "text" | "image";
  onModeChange: (mode: "text" | "image") => void;
  onSend: (message: string) => Promise<void>;
  isLoading: boolean;
};

export function InputBar({ mode, onModeChange, onSend, isLoading }: Props) {
  const [value, setValue] = useState("");

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const message = value.trim();
    if (!message || isLoading) return;
    setValue("");
    await onSend(message);
  }

  return (
    <form onSubmit={submit}>
      <div className="flex flex-col gap-3 sm:flex-row sm:items-end">
        <div className="flex h-11 w-fit rounded-full bg-[#f8f9fa] p-1">
          <button
            type="button"
            title="Text mode"
            aria-pressed={mode === "text"}
            onClick={() => onModeChange("text")}
            className={cn(
              "grid h-9 w-10 place-items-center rounded-full text-[#6b7280]",
              mode === "text" && "bg-white text-[#111111] shadow-[0_1px_2px_rgba(0,0,0,0.06)]",
            )}
          >
            <TextCursorInput aria-hidden="true" size={18} />
          </button>
          <button
            type="button"
            title="Image mode"
            aria-pressed={mode === "image"}
            onClick={() => onModeChange("image")}
            className={cn(
              "grid h-9 w-10 place-items-center rounded-full text-[#6b7280]",
              mode === "image" && "bg-white text-[#111111] shadow-[0_1px_2px_rgba(0,0,0,0.06)]",
            )}
          >
            <ImageIcon aria-hidden="true" size={18} />
          </button>
        </div>
        <Textarea
          value={value}
          onChange={(event) => setValue(event.target.value)}
          rows={2}
          maxLength={2000}
          className="min-h-12 flex-1"
          placeholder={mode === "text" ? "Ask about Scripture or theology" : "Describe reverent Christian artwork"}
        />
        <Button
          type="submit"
          variant="primary"
          disabled={isLoading || !value.trim()}
          title="Send"
          className="h-12 w-12 shrink-0 px-0"
        >
          <Send aria-hidden="true" size={18} />
        </Button>
      </div>
    </form>
  );
}
