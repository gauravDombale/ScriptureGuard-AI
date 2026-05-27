import { useEffect, useRef } from "react";
import type { ChatMessage } from "@/types";
import { MessageBubble } from "./MessageBubble";

type Props = {
  messages: ChatMessage[];
  isLoading: boolean;
  error: string | null;
};

export function ChatWindow({ messages, isLoading, error }: Props) {
  const anchorRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    anchorRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, isLoading]);

  return (
    <section className="min-h-0 flex-1 overflow-y-auto py-5">
      <div className="grid gap-4">
        {messages.length === 0 && (
          <div className="rounded-md border border-dashed border-[#bdb3a2] bg-[#fffdf8] p-5 text-sm leading-6 text-[#504a42]">
            Ask a theology or Scripture question. Every cited verse is validated against the
            local KJV corpus before it is shown here.
          </div>
        )}
        {messages.map((message) => (
          <MessageBubble key={message.id} message={message} />
        ))}
        {error && (
          <div className="rounded-md border border-[#c96565] bg-[#fff1f1] p-3 text-sm text-[#7a1e1e]">
            {error}
          </div>
        )}
        <div ref={anchorRef} />
      </div>
    </section>
  );
}
