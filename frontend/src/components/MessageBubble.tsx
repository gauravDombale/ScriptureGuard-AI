import Image from "next/image";
import { Bot, Loader2, User } from "lucide-react";
import type { ChatMessage } from "@/types";
import { CitationCard } from "./CitationCard";
import { SafetyBanner } from "./SafetyBanner";

type Props = {
  message: ChatMessage;
};

export function MessageBubble({ message }: Props) {
  const isUser = message.role === "user";

  return (
    <article className={`flex gap-3 ${isUser ? "justify-end" : "justify-start"}`}>
      {!isUser && (
        <div className="grid h-9 w-9 shrink-0 place-items-center rounded-md bg-[#173f35] text-white">
          <Bot aria-hidden="true" size={18} />
        </div>
      )}
      <div
        className={`max-w-[86%] rounded-md px-4 py-3 shadow-sm sm:max-w-[72%] ${
          isUser
            ? "bg-[#2f6f61] text-white"
            : "border border-[#d8d0c2] bg-white text-[#1c1b18]"
        }`}
      >
        {message.blocked ? (
          <SafetyBanner message={message.content} />
        ) : (
          <div className="grid gap-2">
            {message.streamStatus && (
              <div className="flex items-center gap-2 text-xs text-[#625c52]" role="status">
                <Loader2 aria-hidden="true" className="animate-spin" size={14} />
                <span>{message.streamStatus}</span>
              </div>
            )}
            <p className="whitespace-pre-wrap text-sm leading-6">
              {message.content}
              {message.isStreaming && message.content && (
                <span className="ml-0.5 inline-block h-4 w-1 animate-pulse bg-[#2f6f61] align-text-bottom" />
              )}
            </p>
          </div>
        )}

        {message.imageUrl && (
          <div className="mt-3 overflow-hidden rounded-md border border-[#d8d0c2]">
            {message.imageUrl.startsWith("data:") ? (
              <img
                src={message.imageUrl}
                alt="Generated Christian artwork"
                className="h-auto w-full"
              />
            ) : (
              <Image
                src={message.imageUrl}
                alt="Generated Christian artwork"
                width={768}
                height={768}
                className="h-auto w-full"
              />
            )}
          </div>
        )}

        {message.citations.length > 0 && (
          <div className="mt-3 grid gap-2">
            {message.citations.map((citation) => (
              <CitationCard key={`${message.id}-${citation.reference}`} citation={citation} />
            ))}
          </div>
        )}
      </div>
      {isUser && (
        <div className="grid h-9 w-9 shrink-0 place-items-center rounded-md bg-[#6b4f2a] text-white">
          <User aria-hidden="true" size={18} />
        </div>
      )}
    </article>
  );
}
