const BACKEND_API_URL = process.env.BACKEND_API_URL ?? "http://127.0.0.1:8000";
const BACKEND_REQUEST_TIMEOUT_MS = Number(process.env.BACKEND_REQUEST_TIMEOUT_MS ?? 180_000);
export const IMAGE_BACKEND_REQUEST_TIMEOUT_MS = Number(
  process.env.IMAGE_BACKEND_REQUEST_TIMEOUT_MS ?? 420_000,
);
const BACKEND_API_KEY = process.env.BACKEND_API_KEY ?? "";

export function backendUrl(path: string) {
  return `${BACKEND_API_URL}${path}`;
}

export function proxyError(error: unknown) {
  const message =
    error instanceof DOMException && error.name === "AbortError"
      ? "Backend request timed out"
      : error instanceof Error
        ? error.message
        : "Backend request failed";
  return Response.json({ detail: message }, { status: 502 });
}

export async function proxyPost(request: Request, path: string, timeoutMs = BACKEND_REQUEST_TIMEOUT_MS) {
  const body = await request.text();
  const requestId = request.headers.get("x-request-id") ?? crypto.randomUUID();
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), timeoutMs);
  try {
    return await fetch(backendUrl(path), {
      method: "POST",
      headers: {
        "Content-Type": request.headers.get("Content-Type") ?? "application/json",
        "X-Request-ID": requestId,
        ...(BACKEND_API_KEY ? { "X-API-Key": BACKEND_API_KEY } : {}),
      },
      body,
      signal: controller.signal,
    });
  } finally {
    clearTimeout(timeout);
  }
}
