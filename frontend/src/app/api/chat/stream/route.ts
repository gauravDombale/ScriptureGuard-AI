import { proxyError, proxyPost } from "../../_backend";

export async function POST(request: Request) {
  try {
    const response = await proxyPost(request, "/chat/stream");

    return new Response(response.body, {
      status: response.status,
      headers: {
        "Cache-Control": "no-cache, no-transform",
        "Content-Type": response.headers.get("Content-Type") ?? "text/event-stream",
        "X-Accel-Buffering": "no",
        "X-Request-ID": response.headers.get("X-Request-ID") ?? "",
      },
    });
  } catch (error) {
    return proxyError(error);
  }
}
