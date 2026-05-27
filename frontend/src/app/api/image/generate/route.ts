import { IMAGE_BACKEND_REQUEST_TIMEOUT_MS, proxyError, proxyPost } from "../../_backend";

export async function POST(request: Request) {
  try {
    const response = await proxyPost(
      request,
      "/image/generate",
      IMAGE_BACKEND_REQUEST_TIMEOUT_MS,
    );

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
