const PREFIX = "/api/engine";
function json(message, status) {
  return new Response(JSON.stringify({ error: message }), {
    status,
    headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" },
  });
}

export async function onRequest({ request, env }) {
  const backendValue = env.LINKORA_BACKEND_URL;
  const apiKey = env.LINKORA_API_KEY;
  if (!backendValue || !apiKey) {
    return json("LINKORA's download engine is not connected yet.", 503);
  }

  let backend;
  try {
    backend = new URL(backendValue);
  } catch {
    return json("Download engine configuration is invalid.", 503);
  }
  if (backend.protocol !== "https:" || backend.username || backend.password || backend.pathname !== "/") {
    return json("Download engine must use a secure HTTPS address.", 503);
  }

  const incoming = new URL(request.url);
  const path = incoming.pathname.slice(PREFIX.length);
  const allowedPath =
    path === "/info" ||
    path === "/downloads" ||
    /^\/downloads\/[a-f0-9]{32}$/i.test(path) ||
    /^\/downloads\/[a-f0-9]{32}\/(file|cancel|retry)$/i.test(path);
  if (!allowedPath) return json("Unknown download-engine endpoint.", 404);
  if (request.method !== "GET" && request.method !== "POST") {
    return json("Method not allowed.", 405);
  }

  const length = Number(request.headers.get("content-length") || 0);
  if (length > 10000) return json("Request is too large.", 413);

  const target = new URL(path + incoming.search, backend.origin);
  const headers = new Headers();
  headers.set("X-LINKORA-API-KEY", apiKey);
  const contentType = request.headers.get("content-type");
  if (contentType) headers.set("content-type", contentType);
  const accept = request.headers.get("accept");
  if (accept) headers.set("accept", accept);

  let body;
  if (request.method === "POST") {
    body = await request.arrayBuffer();
    if (body.byteLength > 10000) return json("Request is too large.", 413);
  }

  try {
    const upstream = await fetch(target.toString(), {
      method: request.method,
      headers,
      body,
      redirect: "manual",
    });
    const responseHeaders = new Headers();
    for (const name of ["content-type", "content-length", "content-disposition", "cache-control"]) {
      const value = upstream.headers.get(name);
      if (value) responseHeaders.set(name, value);
    }
    responseHeaders.set("cache-control", "no-store");
    return new Response(upstream.body, {
      status: upstream.status,
      headers: responseHeaders,
    });
  } catch {
    return json("The download engine could not be reached. Please try again later.", 502);
  }
}
