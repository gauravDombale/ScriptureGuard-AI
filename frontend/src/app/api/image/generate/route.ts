import { backendUrl, proxyError } from "../../_backend";

export async function POST(request: Request) {
  try {
    const response = await fetch(backendUrl("/image/generate"), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: await request.text(),
    });

    return new Response(response.body, {
      status: response.status,
      headers: {
        "Content-Type": response.headers.get("Content-Type") ?? "application/json",
      },
    });
  } catch (error) {
    return proxyError(error);
  }
}
