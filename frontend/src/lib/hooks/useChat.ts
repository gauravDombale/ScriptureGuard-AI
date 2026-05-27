"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { sendChat, streamChat } from "@/lib/api";
import type { ChatMessage, Denomination } from "@/types";

export function useChat(sessionId: string) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [denomination, setDenomination] = useState<Denomination>("protestant");
  const [mode, setMode] = useState<"text" | "image">("text");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const activeRequestRef = useRef<AbortController | null>(null);
  const mountedRef = useRef(true);

  useEffect(() => {
    return () => {
      mountedRef.current = false;
      activeRequestRef.current?.abort();
    };
  }, []);

  const send = useCallback(
    async (content: string) => {
      if (!sessionId || !content.trim() || isLoading) return;
      activeRequestRef.current?.abort();
      const controller = new AbortController();
      activeRequestRef.current = controller;
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
                    message.id === assistantId && activeRequestRef.current === controller
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
                    message.id === assistantId && activeRequestRef.current === controller
                      ? { ...message, streamStatus: status }
                      : message,
                  ),
                );
              },
              onFinal: (response) => {
                setMessages((current) =>
                  current.map((message) =>
                    message.id === assistantId && activeRequestRef.current === controller
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
            { signal: controller.signal },
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

        const response = await sendChat(
          {
            session_id: sessionId,
            message: content,
            denomination,
            mode,
          },
          { signal: controller.signal },
        );
        setMessages((current) =>
          current.map((message) =>
            message.id === assistantId && activeRequestRef.current === controller
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
        if (controller.signal.aborted) return;
        const message = caught instanceof Error ? caught.message : "Request failed";
        setError(message);
        setMessages((current) =>
          current.map((chatMessage) =>
            chatMessage.isStreaming || chatMessage.isImageLoading
              ? {
                  ...chatMessage,
                  isStreaming: false,
                  isImageLoading: false,
                  streamStatus: undefined,
                  content: chatMessage.content || message,
                  blocked: chatMessage.blocked,
                }
              : chatMessage,
          ),
        );
      } finally {
        if (activeRequestRef.current === controller) {
          activeRequestRef.current = null;
        }
        if (mountedRef.current) {
          setIsLoading(false);
        }
      }
    },
    [denomination, isLoading, mode, sessionId],
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
