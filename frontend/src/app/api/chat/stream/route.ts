import { backendUrl, proxyError } from "../../_backend";

export async function POST(request: Request) {
  try {
    const response = await fetch(backendUrl("/chat/stream"), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: await request.text(),
    });

    return new Response(response.body, {
      status: response.status,
      headers: {
        "Cache-Control": "no-cache, no-transform",
        "Content-Type": response.headers.get("Content-Type") ?? "text/event-stream",
        "X-Accel-Buffering": "no",
      },
    });
  } catch (error) {
    return proxyError(error);
  }
}
