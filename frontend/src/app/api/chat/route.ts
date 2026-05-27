import { proxyError, proxyPost } from "../_backend";

export async function POST(request: Request) {
  try {
    const response = await proxyPost(request, "/chat");

    return new Response(response.body, {
      status: response.status,
      headers: {
        "Content-Type": response.headers.get("Content-Type") ?? "application/json",
        "X-Request-ID": response.headers.get("X-Request-ID") ?? "",
      },
    });
  } catch (error) {
    return proxyError(error);
  }
}
