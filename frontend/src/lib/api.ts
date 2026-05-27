import type { ChatRequest, ChatResponse } from "@/types";

const API_URL = "/api";

type RequestOptions = {
  signal?: AbortSignal;
};

export class ApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

export async function sendChat(
  request: ChatRequest,
  options: RequestOptions = {},
): Promise<ChatResponse> {
  if (request.mode === "image") {
    const response = await fetch(`${API_URL}/image/generate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      signal: options.signal,
      body: JSON.stringify({
        session_id: request.session_id,
        prompt: request.message,
        denomination: request.denomination,
        style: "classical painting",
      }),
    });
    if (!response.ok) {
      throw await apiError(response, "Image request failed");
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
    signal: options.signal,
    body: JSON.stringify(request),
  });
  if (!response.ok) {
    throw await apiError(response, "Chat request failed");
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
  options: RequestOptions = {},
): Promise<void> {
  const response = await fetch(`${API_URL}/chat/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    signal: options.signal,
    body: JSON.stringify(request),
  });
  if (!response.ok) {
    throw await apiError(response, "Chat stream failed");
  }
  if (!response.body) {
    throw new Error("Chat stream response has no body");
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  try {
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

    const remaining = buffer + decoder.decode();
    if (remaining.trim()) {
      handleSseEvent(remaining, handlers);
    }
  } finally {
    reader.releaseLock();
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
  const data = rawEvent
    .split("\n")
    .filter((line) => line.startsWith("data:"))
    .map((line) => line.slice("data:".length).trimStart())
    .join("\n");
  if (!data) return;

  let payload: {
    type?: string;
    content?: string;
    message?: string;
    response?: string;
    citations?: ChatResponse["citations"];
    session_id?: string;
    safety_blocked?: boolean;
    block_reason?: string | null;
    denomination_notes?: string | null;
    retrieval_score?: number | null;
  };
  try {
    payload = JSON.parse(data);
  } catch {
    throw new Error("Received malformed chat stream event");
  }
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

async function apiError(response: Response, fallback: string): Promise<ApiError> {
  let detail = "";
  try {
    const contentType = response.headers.get("Content-Type") ?? "";
    if (contentType.includes("application/json")) {
      const payload = await response.json();
      detail = typeof payload.detail === "string" ? payload.detail : "";
    } else {
      detail = await response.text();
    }
  } catch {
    detail = "";
  }
  return new ApiError(detail || `${fallback}: ${response.status}`, response.status);
}
