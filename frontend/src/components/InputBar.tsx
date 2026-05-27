import { FormEvent, KeyboardEvent, useLayoutEffect, useRef, useState } from "react";
import { ImageIcon, TextCursorInput } from "lucide-react";
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
  const formRef = useRef<HTMLFormElement | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);

  useLayoutEffect(() => {
    const textarea = textareaRef.current;
    if (!textarea) return;
    textarea.style.height = "auto";
    textarea.style.height = `${Math.min(textarea.scrollHeight, 160)}px`;
  }, [value]);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const message = value.trim();
    if (!message || isLoading) return;
    setValue("");
    await onSend(message);
  }

  function handleKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key !== "Enter" || event.shiftKey) return;
    event.preventDefault();
    formRef.current?.requestSubmit();
  }

  return (
    <form ref={formRef} onSubmit={submit}>
      <div className="flex flex-col gap-3 sm:flex-row sm:items-end">
        <div className="flex h-12 w-fit shrink-0 rounded-full bg-[#f8f9fa] p-1">
          <button
            type="button"
            title="Text mode"
            aria-pressed={mode === "text"}
            onClick={() => onModeChange("text")}
            className={cn(
              "grid h-10 w-10 place-items-center rounded-full text-[#6b7280]",
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
              "grid h-10 w-10 place-items-center rounded-full text-[#6b7280]",
              mode === "image" && "bg-white text-[#111111] shadow-[0_1px_2px_rgba(0,0,0,0.06)]",
            )}
          >
            <ImageIcon aria-hidden="true" size={18} />
          </button>
        </div>
        <div className="relative flex-1">
          <Textarea
            ref={textareaRef}
            value={value}
            onChange={(event) => setValue(event.target.value)}
            onKeyDown={handleKeyDown}
            rows={2}
            maxLength={2000}
            className="max-h-40 min-h-12 w-full overflow-y-auto pb-14 pr-14"
            placeholder={mode === "text" ? "Ask about Scripture or theology" : "Describe reverent Christian artwork"}
          />
          <button
            type="submit"
            disabled={isLoading || !value.trim()}
            title="Send"
            className="absolute bottom-3 right-3 grid h-7 w-7 place-items-center rounded-full disabled:cursor-not-allowed disabled:opacity-40"
          >
            <img
              src="/arrow-sm-right-svgrepo-com.svg"
              alt=""
              aria-hidden="true"
              className="h-6 w-6"
            />
          </button>
        </div>
      </div>
    </form>
  );
}
