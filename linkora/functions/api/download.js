const MAX_BYTES = 100 * 1024 * 1024;
const SOCIAL_HOSTS = [
  "instagram.com", "tiktok.com", "facebook.com", "fb.watch", "x.com",
  "twitter.com", "youtube.com", "youtu.be", "vimeo.com", "twitch.tv",
  "soundcloud.com", "pinterest.com", "reddit.com"
];
const FILE_EXTENSIONS = new Set([
  "mp4","webm","mov","m4v","mkv","avi","mp3","wav","m4a","ogg","flac",
  "jpg","jpeg","png","webp","gif","avif","svg","pdf","txt","csv","json",
  "doc","docx","xls","xlsx","ppt","pptx","zip","7z","rar","tar","gz",
  "epub","apk","dmg","iso"
]);

function isSocial(host) {
  host = host.toLowerCase();
  return SOCIAL_HOSTS.some(domain => host === domain || host.endsWith("." + domain));
}
function isPrivateHost(host) {
  const h = host.toLowerCase().replace(/^\[|\]$/g, "");
  if (h === "localhost" || h.endsWith(".localhost") || h.endsWith(".local")) return true;
  if (h === "::" || h === "::1" || h.startsWith("fc") || h.startsWith("fd") || h.startsWith("fe80:")) return true;
  if (/^\d{1,3}(\.\d{1,3}){3}$/.test(h)) {
    const p = h.split(".").map(Number);
    if (p.some(n => n > 255)) return true;
    const [a,b] = p;
    return a === 0 || a === 10 || a === 127 || a >= 224 ||
      (a === 169 && b === 254) || (a === 172 && b >= 16 && b <= 31) ||
      (a === 192 && b === 168) || (a === 100 && b >= 64 && b <= 127);
  }
  return false;
}
function validateUrl(raw) {
  let url;
  try { url = new URL(raw); } catch { throw new Error("Enter a valid public HTTP or HTTPS file URL."); }
  if (!["http:", "https:"].includes(url.protocol) || url.username || url.password ||
      isPrivateHost(url.hostname) || isSocial(url.hostname)) {
    throw new Error("This URL is not supported. Use a public direct file link, not a social-platform page or private address.");
  }
  return url;
}
function filenameFrom(url, disposition) {
  let name = "";
  const star = disposition.match(/filename\*=UTF-8''([^;]+)/i);
  const plain = disposition.match(/filename\s*=\s*"([^"]+)"/i) || disposition.match(/filename\s*=\s*([^;]+)/i);
  if (star) { try { name = decodeURIComponent(star[1].replace(/^"|"$/g, "")); } catch {} }
  if (!name && plain) name = plain[1].trim();
  if (!name) name = decodeURIComponent(url.pathname.split("/").pop() || "linkora-download");
  name = name.replace(/[\\/\u0000-\u001f\u007f]/g, "_").replace(/^\.+/, "").trim();
  return (name || "linkora-download").slice(0, 120);
}
function isFileResponse(response, url) {
  const type = (response.headers.get("content-type") || "").split(";")[0].toLowerCase();
  const ext = url.pathname.toLowerCase().match(/\.([a-z0-9]{2,8})$/)?.[1] || "";
  if (type.startsWith("video/") || type.startsWith("audio/") || type.startsWith("image/")) return true;
  if (["application/pdf","application/zip","application/x-zip-compressed","application/octet-stream",
       "application/msword","application/vnd.openxmlformats-officedocument.wordprocessingml.document",
       "application/vnd.ms-excel","application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
       "application/vnd.ms-powerpoint","application/vnd.openxmlformats-officedocument.presentationml.presentation",
       "application/epub+zip","application/x-7z-compressed","application/vnd.android.package-archive"].includes(type)) return true;
  return FILE_EXTENSIONS.has(ext);
}
async function fetchPublic(url, method, useRange = false) {
  let current = validateUrl(url);
  for (let hop = 0; hop <= 5; hop++) {
    const response = await fetch(current.href, {
      method, redirect: "manual",
      headers: method === "GET" ? (useRange ? { "Accept": "*/*", "Range": "bytes=0-0" } : { "Accept": "*/*" }) : {}
    });
    if ([301,302,303,307,308].includes(response.status)) {
      const location = response.headers.get("location");
      if (!location || hop === 5) throw new Error("Too many or invalid redirects from the file host.");
      const next = new URL(location, current);
      current = validateUrl(next.href);
      continue;
    }
    return { response, finalUrl: current };
  }
  throw new Error("The file host redirected too many times.");
}
function responseHeaders(upstream, filename, size) {
  const headers = new Headers();
  const type = upstream.headers.get("content-type");
  if (type) headers.set("Content-Type", type);
  if (Number.isFinite(size) && size >= 0) headers.set("Content-Length", String(size));
  const range = upstream.headers.get("content-range");
  if (range) headers.set("Content-Range", range);
  const accepts = upstream.headers.get("accept-ranges");
  if (accepts) headers.set("Accept-Ranges", accepts);
  headers.set("Content-Disposition", 'attachment; filename="' + filename.replace(/"/g, "") + '"');
  headers.set("Cache-Control", "no-store");
  headers.set("X-Content-Type-Options", "nosniff");
  headers.set("X-Download-Options", "noopen");
  return headers;
}

export async function onRequest({ request }) {
  const cors = { "Access-Control-Allow-Origin": new URL(request.url).origin };
  if (request.method !== "GET" && request.method !== "HEAD") {
    return new Response("Method not allowed.", { status: 405, headers: { ...cors, "Allow": "GET, HEAD" } });
  }
  const requestUrl = new URL(request.url);
  const raw = requestUrl.searchParams.get("url");
  if (!raw) return new Response("Missing file URL.", { status: 400, headers: cors });

  try {
    let { response: upstream, finalUrl } = await fetchPublic(raw, request.method);
    if ((upstream.status === 405 || upstream.status === 501) && request.method === "HEAD") {
      const ranged = await fetchPublic(raw, "GET", true);
      upstream = ranged.response;
      finalUrl = ranged.finalUrl;
      if (upstream.body) await upstream.body.cancel();
      if (upstream.status !== 206 && !upstream.ok) {
        return new Response("The file host does not support file inspection.", { status: upstream.status, headers: cors });
      }
    } else if (!upstream.ok) {
      return new Response("The file host returned HTTP " + upstream.status + ".", { status: upstream.status, headers: cors });
    }

    if (!isFileResponse(upstream, finalUrl)) {
      if (upstream.body) await upstream.body.cancel();
      return new Response("This link does not appear to be a direct downloadable file. Paste a direct media or file URL.", { status: 415, headers: cors });
    }

    let size = Number(upstream.headers.get("content-length") || 0);
    if (upstream.status === 206) {
      const contentRange = upstream.headers.get("content-range") || "";
      const total = contentRange.match(/\/\s*(\d+)$/);
      if (total) size = Number(total[1]);
    }
    if (size > MAX_BYTES) {
      if (upstream.body) await upstream.body.cancel();
      return new Response("This file exceeds LINKORA's 100 MiB limit.", { status: 413, headers: cors });
    }

    const filename = filenameFrom(finalUrl, upstream.headers.get("content-disposition") || "");
    const headers = responseHeaders(upstream, filename, size || undefined);
    if (request.method === "HEAD") {
      if (upstream.body) await upstream.body.cancel();
      return new Response(null, { status: 200, headers });
    }
    if (!upstream.body) return new Response("The file host returned an empty response.", { status: 502, headers: cors });

    let transferred = 0;
    const limiter = new TransformStream({
      transform(chunk, controller) {
        transferred += chunk.byteLength;
        if (transferred > MAX_BYTES) throw new Error("File exceeds LINKORA's 100 MiB download limit.");
        controller.enqueue(chunk);
      }
    });
    return new Response(upstream.body.pipeThrough(limiter), { status: 200, headers });
  } catch (error) {
    return new Response(error instanceof Error ? error.message : "Unable to retrieve this file.", {
      status: 400, headers: { ...cors, "Cache-Control": "no-store", "Content-Type": "text/plain; charset=utf-8" }
    });
  }
}
