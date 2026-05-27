"use client";

import { useCallback, useState } from "react";
import { sendChat, streamChat } from "@/lib/api";
import type { ChatMessage, Denomination } from "@/types";

export function useChat(sessionId: string) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [denomination, setDenomination] = useState<Denomination>("protestant");
  const [mode, setMode] = useState<"text" | "image">("text");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const send = useCallback(
    async (content: string) => {
      if (!sessionId || !content.trim()) return;
      const userMessage: ChatMessage = {
        id: crypto.randomUUID(),
        role: "user",
        content,
        citations: [],
      };
      setMessages((current) => [...current, userMessage]);
      setIsLoading(true);
      setError(null);
      try {
        if (mode === "text") {
          const assistantId = crypto.randomUUID();
          setMessages((current) => [
            ...current,
            {
              id: assistantId,
              role: "assistant",
              content: "",
              citations: [],
              isStreaming: true,
              streamStatus: "Connecting to ScriptureGuard...",
            },
          ]);
          await streamChat(
            {
              session_id: sessionId,
              message: content,
              denomination,
              mode,
            },
            {
              onDelta: (delta) => {
                setMessages((current) =>
                  current.map((message) =>
                    message.id === assistantId
                      ? {
                          ...message,
                          content: message.content + delta,
                          streamStatus: undefined,
                        }
                      : message,
                  ),
                );
              },
              onStatus: (status) => {
                setMessages((current) =>
                  current.map((message) =>
                    message.id === assistantId
                      ? { ...message, streamStatus: status }
                      : message,
                  ),
                );
              },
              onFinal: (response) => {
                setMessages((current) =>
                  current.map((message) =>
                    message.id === assistantId
                      ? {
                          ...message,
                          content: response.response,
                          citations: response.citations,
                          imageUrl: response.image_url,
                          blocked: response.safety_blocked,
                          isStreaming: false,
                          streamStatus: undefined,
                        }
                      : message,
                  ),
                );
              },
            },
          );
          return;
        }

        const assistantId = crypto.randomUUID();
        setMessages((current) => [
          ...current,
          {
            id: assistantId,
            role: "assistant",
            content: "",
            citations: [],
            isImageLoading: true,
            prompt: content,
          },
        ]);

        const response = await sendChat({
          session_id: sessionId,
          message: content,
          denomination,
          mode,
        });
        setMessages((current) =>
          current.map((message) =>
            message.id === assistantId
              ? {
                  ...message,
                  content: response.response,
                  citations: response.citations,
                  imageUrl: response.image_url,
                  blocked: response.safety_blocked,
                  isImageLoading: false,
                  prompt: undefined,
                }
              : message,
          ),
        );
      } catch (caught) {
        setError(caught instanceof Error ? caught.message : "Request failed");
      } finally {
        setIsLoading(false);
      }
    },
    [denomination, mode, sessionId],
  );

  return {
    messages,
    denomination,
    setDenomination,
    mode,
    setMode,
    isLoading,
    error,
    send,
  };
}
