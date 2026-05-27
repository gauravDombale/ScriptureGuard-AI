import { FormEvent, KeyboardEvent, useLayoutEffect, useRef, useState } from "react";
import { Textarea } from "./ui/Textarea";

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
      <div className="relative">
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
        <div className="absolute bottom-3 left-3 flex items-center gap-3">
          <button
            type="button"
            title="Text mode"
            aria-pressed={mode === "text"}
            onClick={() => onModeChange("text")}
            className="grid h-7 w-7 place-items-center opacity-45 transition-opacity aria-pressed:opacity-100"
          >
            <img src="/text-svgrepo-com.svg" alt="" aria-hidden="true" className="h-6 w-6" />
          </button>
          <button
            type="button"
            title="Image mode"
            aria-pressed={mode === "image"}
            onClick={() => onModeChange("image")}
            className="grid h-7 w-7 place-items-center opacity-45 transition-opacity aria-pressed:opacity-100"
          >
            <img src="/image-square-svgrepo-com.svg" alt="" aria-hidden="true" className="h-6 w-6" />
          </button>
        </div>
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
    </form>
  );
}
