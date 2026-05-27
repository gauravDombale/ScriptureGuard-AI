const BACKEND_API_URL = process.env.BACKEND_API_URL ?? "http://127.0.0.1:8000";

export function backendUrl(path: string) {
  return `${BACKEND_API_URL}${path}`;
}

export function proxyError(error: unknown) {
  const message = error instanceof Error ? error.message : "Backend request failed";
  return Response.json({ detail: message }, { status: 502 });
}
