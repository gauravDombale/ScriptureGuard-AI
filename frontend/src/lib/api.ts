import type { ChatRequest, ChatResponse } from "@/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function sendChat(request: ChatRequest): Promise<ChatResponse> {
  if (request.mode === "image") {
    const response = await fetch(`${API_URL}/image/generate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        session_id: request.session_id,
        prompt: request.message,
        denomination: request.denomination,
        style: "classical painting",
      }),
    });
    if (!response.ok) {
      throw new Error(`Image request failed: ${response.status}`);
    }
    const image = await response.json();
    return {
      session_id: request.session_id,
      response: image.safety_blocked ? image.block_reason : image.revised_prompt,
      citations: [],
      image_url: image.image_url,
      safety_blocked: image.safety_blocked,
      block_reason: image.block_reason,
      denomination_notes: null,
      retrieval_score: null,
    };
  }

  const response = await fetch(`${API_URL}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });
  if (!response.ok) {
    throw new Error(`Chat request failed: ${response.status}`);
  }
  return response.json();
}

export async function streamChat(
  request: ChatRequest,
  handlers: {
    onDelta: (content: string) => void;
    onFinal: (response: ChatResponse) => void;
    onStatus?: (message: string) => void;
  },
): Promise<void> {
  const response = await fetch(`${API_URL}/chat/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });
  if (!response.ok) {
    throw new Error(`Chat stream failed: ${response.status}`);
  }
  if (!response.body) {
    throw new Error("Chat stream response has no body");
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const events = buffer.split("\n\n");
    buffer = events.pop() ?? "";
    for (const event of events) {
      handleSseEvent(event, handlers);
    }
  }

  if (buffer.trim()) {
    handleSseEvent(buffer, handlers);
  }
}

function handleSseEvent(
  rawEvent: string,
  handlers: {
    onDelta: (content: string) => void;
    onFinal: (response: ChatResponse) => void;
    onStatus?: (message: string) => void;
  },
) {
  const dataLine = rawEvent
    .split("\n")
    .find((line) => line.startsWith("data:"));
  if (!dataLine) return;

  const payload = JSON.parse(dataLine.slice("data:".length).trim());
  if (payload.type === "delta") {
    handlers.onDelta(payload.content ?? "");
    return;
  }
  if (payload.type === "status") {
    handlers.onStatus?.(payload.message ?? "");
    return;
  }
  if (payload.type === "final") {
    handlers.onFinal({
      session_id: requestSessionId(payload),
      response: payload.response ?? "",
      citations: payload.citations ?? [],
      image_url: null,
      safety_blocked: payload.safety_blocked ?? false,
      block_reason: payload.block_reason ?? null,
      denomination_notes: payload.denomination_notes ?? null,
      retrieval_score: payload.retrieval_score ?? null,
    });
  }
}

function requestSessionId(payload: { session_id?: string }) {
  return payload.session_id ?? "";
}
