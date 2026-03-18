import { createServer } from "node:http";
import { Readable } from "node:stream";
import path from "node:path";
import { fileURLToPath } from "node:url";
import sirv from "sirv";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const { default: handler } = await import("./dist/server/server.js");

const PORT = parseInt(process.env.PORT || "3000", 10);
const HOST = process.env.HOST || "0.0.0.0";

// Serve static assets from dist/client before falling through to SSR.
// Hashed filenames in /assets/ get immutable caching (1 year).
const serve = sirv(path.join(__dirname, "dist/client"), {
  etag: true,
  gzip: true,
  immutable: true,
  maxAge: 31536000,
});

const server = createServer((req, res) => {
  // Try static files first; fall through to SSR handler if no match
  serve(req, res, async () => {
    try {
      const url = new URL(req.url, `http://${req.headers.host}`);
      const headers = new Headers();
      for (const [key, value] of Object.entries(req.headers)) {
        if (value) headers.set(key, Array.isArray(value) ? value.join(", ") : value);
      }

      const body =
        req.method !== "GET" && req.method !== "HEAD"
          ? Readable.toWeb(req)
          : undefined;

      const request = new Request(url.href, {
        method: req.method,
        headers,
        body,
        duplex: body ? "half" : undefined,
      });

      const response = await handler.fetch(request);

      res.writeHead(response.status, Object.fromEntries(response.headers.entries()));

      if (response.body) {
        const reader = response.body.getReader();
        const pump = async () => {
          while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            res.write(value);
          }
          res.end();
        };
        await pump();
      } else {
        res.end();
      }
    } catch (err) {
      console.error("Server error:", err);
      if (!res.headersSent) {
        res.writeHead(500, { "Content-Type": "text/plain" });
      }
      res.end("Internal Server Error");
    }
  });
});

server.listen(PORT, HOST, () => {
  console.log(`Production server listening on http://${HOST}:${PORT}`);
});
