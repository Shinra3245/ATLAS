import http from "node:http";
import { createReadStream, existsSync, statSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { networkInterfaces } from "node:os";

const root = fileURLToPath(new URL("../dist/", import.meta.url));
const port = Number(process.env.ATLAS_PREVIEW_PORT || 5173);
const hosts = [
  ...new Set(
    (process.env.ATLAS_PREVIEW_HOSTS || "127.0.0.1")
      .split(",")
      .map((h) => h.trim())
      .filter(Boolean),
  ),
];
const available = new Set([
  "127.0.0.1",
  ...Object.values(networkInterfaces())
    .flat()
    .filter((r) => r?.family === "IPv4")
    .map((r) => r.address),
]);
const target = new URL(process.env.ATLAS_API_TARGET || "http://127.0.0.1:8000");
if (
  target.protocol !== "http:" ||
  !["localhost", "127.0.0.1", "[::1]"].includes(target.hostname)
)
  throw new Error("El proxy solo puede apuntar a una API del mismo nodo.");
if (!existsSync(path.join(root, "index.html")))
  throw new Error("Ejecuta npm run build antes de iniciar.");
for (const host of hosts) {
  if (
    !available.has(host) ||
    !/^(127\.|192\.168\.|10\.|172\.(1[6-9]|2\d|3[01])\.|100\.)/.test(host)
  )
    throw new Error(`Dirección privada no disponible: ${host}`);
}
const allowedPaths =
  /^\/api\/(health|meta|layers|locations(?:\/[^/]+)?|sources|ml\/status|analyze|compare)$/;
const contentTypes = {
  ".html": "text/html; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".svg": "image/svg+xml",
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".woff2": "font/woff2",
  ".woff": "font/woff",
  ".json": "application/json; charset=utf-8",
};
function json(res, status, error, message) {
  res.writeHead(status, { "Content-Type": "application/json; charset=utf-8" });
  res.end(JSON.stringify({ error, message }));
}
function handler(req, res) {
  res.setHeader("X-Content-Type-Options", "nosniff");
  res.setHeader("Referrer-Policy", "strict-origin-when-cross-origin");
  res.setHeader("X-Frame-Options", "SAMEORIGIN");
  res.setHeader(
    "Content-Security-Policy",
    "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https://tile.openstreetmap.org; font-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'self'",
  );
  let url;
  try {
    url = new URL(req.url, `http://${req.headers.host}`);
  } catch {
    return json(res, 400, "BAD_REQUEST", "URL inválida.");
  }
  if (url.pathname.startsWith("/api/")) {
    if (
      !allowedPaths.test(url.pathname) ||
      !["GET", "POST"].includes(req.method)
    )
      return json(res, 404, "NOT_FOUND", "Operación no publicada.");
    const needsPost = ["/api/analyze", "/api/compare"].includes(url.pathname);
    if (
      (needsPost && req.method !== "POST") ||
      (!needsPost && req.method !== "GET")
    )
      return json(res, 405, "METHOD_NOT_ALLOWED", "Método no permitido.");
    if (
      req.headers.origin &&
      req.headers.origin !== `http://${req.headers.host}`
    )
      return json(res, 403, "ORIGIN_NOT_ALLOWED", "Origen no permitido.");
    if (
      needsPost &&
      !req.headers["content-type"]?.startsWith("application/json")
    )
      return json(res, 415, "JSON_REQUIRED", "Enviar application/json.");
    const chunks = [];
    let bytes = 0;
    let rejected = false;
    req.on("data", (chunk) => {
      bytes += chunk.length;
      if (bytes > 65536) {
        if (!rejected)
          json(res, 413, "BODY_TOO_LARGE", "Solicitud demasiado grande.");
        rejected = true;
      } else chunks.push(chunk);
    });
    req.on("end", () => {
      if (rejected) return;
      const upstream = http.request(
        new URL(`${url.pathname}${url.search}`, target),
        {
          method: req.method,
          headers: needsPost ? { "Content-Type": "application/json" } : {},
          timeout: 40000,
        },
        (response) => {
          res.writeHead(response.statusCode, {
            "Content-Type":
              response.headers["content-type"] || "application/json",
            "Cache-Control": "no-store",
          });
          response.pipe(res);
        },
      );
      upstream.on("timeout", () => upstream.destroy(new Error("timeout")));
      upstream.on("error", () => {
        if (!res.headersSent)
          json(
            res,
            503,
            "API_UNAVAILABLE",
            "La API del nodo no está disponible.",
          );
        else res.end();
      });
      res.on("close", () => {
        if (!res.writableEnded) upstream.destroy();
      });
      upstream.end(Buffer.concat(chunks));
    });
    return;
  }
  if (!["GET", "HEAD"].includes(req.method))
    return json(res, 405, "METHOD_NOT_ALLOWED", "Método no permitido.");
  let pathname;
  try {
    pathname = decodeURIComponent(url.pathname);
  } catch {
    return json(res, 400, "BAD_REQUEST", "Ruta inválida.");
  }
  const file = path.resolve(
    root,
    `.${pathname === "/" ? "/index.html" : pathname}`,
  );
  if (
    !file.startsWith(root) ||
    pathname.includes("\\") ||
    pathname.split("/").some((p) => p.startsWith("."))
  )
    return json(res, 403, "FORBIDDEN", "Ruta no permitida.");
  if (!existsSync(file) || !statSync(file).isFile())
    return json(res, 404, "NOT_FOUND", "Archivo no encontrado.");
  res.writeHead(200, {
    "Content-Type":
      contentTypes[path.extname(file)] || "application/octet-stream",
    "Cache-Control": pathname.startsWith("/assets/")
      ? "public, max-age=31536000, immutable"
      : "no-cache",
  });
  if (req.method === "HEAD") return res.end();
  createReadStream(file).pipe(res);
}
const servers = hosts.map((host) => {
  const server = http.createServer(handler);
  server.requestTimeout = 45000;
  server.headersTimeout = 15000;
  server.on("error", (error) => {
    console.error(`No se pudo abrir ${host}:${port}: ${error.message}`);
    for (const item of servers) item.close();
    process.exitCode = 1;
  });
  server.listen(port, host, () =>
    console.log(`ATLAS disponible: http://${host}:${port}`),
  );
  return server;
});
function close() {
  for (const server of servers) server.close();
}
process.on("SIGINT", close);
process.on("SIGTERM", close);
