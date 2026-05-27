import { FormEvent, useState } from "react";
import { ImageIcon, Send, TextCursorInput } from "lucide-react";

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
    <form onSubmit={submit} className="border-t border-[#d8d0c2] pt-4">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-end">
        <div className="flex h-11 w-fit rounded-md border border-[#bdb3a2] bg-white p-1">
          <button
            type="button"
            title="Text mode"
            aria-pressed={mode === "text"}
            onClick={() => onModeChange("text")}
            className={`grid h-9 w-10 place-items-center rounded ${
              mode === "text" ? "bg-[#173f35] text-white" : "text-[#3c3933]"
            }`}
          >
            <TextCursorInput aria-hidden="true" size={18} />
          </button>
          <button
            type="button"
            title="Image mode"
            aria-pressed={mode === "image"}
            onClick={() => onModeChange("image")}
            className={`grid h-9 w-10 place-items-center rounded ${
              mode === "image" ? "bg-[#173f35] text-white" : "text-[#3c3933]"
            }`}
          >
            <ImageIcon aria-hidden="true" size={18} />
          </button>
        </div>
        <textarea
          value={value}
          onChange={(event) => setValue(event.target.value)}
          rows={2}
          maxLength={2000}
          className="min-h-12 flex-1 resize-none rounded-md border border-[#bdb3a2] bg-white px-3 py-2 text-sm leading-6 outline-none focus:border-[#2f6f61]"
          placeholder={mode === "text" ? "Ask about Scripture or theology" : "Describe reverent Christian artwork"}
        />
        <button
          type="submit"
          disabled={isLoading || !value.trim()}
          title="Send"
          className="grid h-12 w-12 shrink-0 place-items-center rounded-md bg-[#173f35] text-white disabled:cursor-not-allowed disabled:bg-[#9a958c]"
        >
          <Send aria-hidden="true" size={18} />
        </button>
      </div>
    </form>
  );
}
