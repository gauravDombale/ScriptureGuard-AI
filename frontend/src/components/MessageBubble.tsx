import Image from "next/image";
import { Bot, Loader2, User } from "lucide-react";
import type { ChatMessage } from "@/types";
import { cn } from "@/lib/utils";
import { CitationCard } from "./CitationCard";
import { ImageGenerationLoader } from "./ImageGenerationLoader";
import { SafetyBanner } from "./SafetyBanner";

type Props = {
  message: ChatMessage;
};

export function MessageBubble({ message }: Props) {
  const isUser = message.role === "user";

  return (
    <article className={`flex gap-3 ${isUser ? "justify-end" : "justify-start"}`}>
      {!isUser && (
        <div className="grid h-9 w-9 shrink-0 place-items-center rounded-full border border-[#e5e7eb] bg-white text-[#111111]">
          <Bot aria-hidden="true" size={18} />
        </div>
      )}
      <div
        className={cn(
          "max-w-[88%] rounded-lg px-4 py-3 text-sm shadow-[0_1px_2px_rgba(0,0,0,0.05)] sm:max-w-[76%]",
          isUser
            ? "bg-[#111111] text-white"
            : "border border-[#e5e7eb] bg-white text-[#111111]",
          message.isImageLoading && "w-full max-w-full sm:max-w-[92%]",
        )}
      >
        {message.isImageLoading ? (
          <ImageGenerationLoader prompt={message.prompt} />
        ) : message.blocked ? (
          <SafetyBanner message={message.content} />
        ) : (
          <div className="grid gap-2">
            {message.streamStatus && (
              <div className="flex items-center gap-2 text-xs text-[#6b7280]" role="status">
                <Loader2 aria-hidden="true" className="animate-spin" size={14} />
                <span>{message.streamStatus}</span>
              </div>
            )}
            <p className="whitespace-pre-wrap text-sm leading-6">
              {message.content}
              {message.isStreaming && message.content && (
                <span className="ml-0.5 inline-block h-4 w-1 animate-pulse bg-[#111111] align-text-bottom" />
              )}
            </p>
          </div>
        )}

        {message.imageUrl && (
          <div className="mt-3 overflow-hidden rounded-lg border border-[#e5e7eb] bg-[#f8f9fa]">
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
        <div className="grid h-9 w-9 shrink-0 place-items-center rounded-full bg-[#f5f5f5] text-[#111111]">
          <User aria-hidden="true" size={18} />
        </div>
      )}
    </article>
  );
}
