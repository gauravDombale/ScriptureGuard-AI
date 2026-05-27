import { useEffect, useRef } from "react";
import { BookOpenCheck, ShieldCheck } from "lucide-react";
import type { ChatMessage } from "@/types";
import { MessageBubble } from "./MessageBubble";
import { SoftCard } from "./ui/Card";

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
    <section className="min-h-0 flex-1 overflow-y-auto p-4">
      <div className="grid gap-4">
        {messages.length === 0 && (
          <SoftCard className="p-5">
            <div className="grid gap-4 sm:grid-cols-[1fr_240px] sm:items-center">
              <div>
                <div className="display-title text-xl">Start a grounded conversation</div>
                <p className="mt-2 max-w-xl text-sm leading-6 text-[#6b7280]">
                  Ask a theology or Scripture question. Responses stream into this panel and
                  citations appear as verified cards under the answer.
                </p>
              </div>
              <div className="rounded-lg border border-[#e5e7eb] bg-white p-3">
                <div className="mb-3 flex items-center gap-2 text-sm font-semibold text-[#111111]">
                  <ShieldCheck aria-hidden="true" size={16} />
                  Citation check
                </div>
                <div className="grid gap-2">
                  <div className="flex items-center justify-between rounded-md bg-[#f8f9fa] px-3 py-2 text-xs text-[#374151]">
                    <span>Reference</span>
                    <BookOpenCheck aria-hidden="true" size={14} />
                  </div>
                  <div className="h-2 rounded-full bg-[#e5e7eb]" />
                  <div className="h-2 w-4/5 rounded-full bg-[#e5e7eb]" />
                </div>
              </div>
            </div>
          </SoftCard>
        )}
        {messages.map((message) => (
          <MessageBubble key={message.id} message={message} />
        ))}
        {error && (
          <div className="rounded-md border border-[#fecaca] bg-[#fef2f2] p-3 text-sm text-[#991b1b]">
            {error}
          </div>
        )}
        <div ref={anchorRef} />
      </div>
    </section>
  );
}
