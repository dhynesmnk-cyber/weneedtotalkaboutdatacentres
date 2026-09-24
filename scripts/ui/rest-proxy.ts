/**
 * Test only: makes a bare PostgREST look like a Supabase project's REST API.
 *
 * supabase-js calls `<url>/rest/v1/...` and sends the anon key as a bearer
 * token. PostgREST serves from `/` and, with no JWT secret configured, rejects
 * any bearer token, so this strips both. Every request then runs as PostgREST's
 * anon role, which is exactly the role the public site reads as, so RLS is
 * exercised as it is in production.
 *
 *   tsx scripts/ui/rest-proxy.ts <listen port> <postgrest port>
 */
import http from 'node:http';

const [listenPort = '3200', upstreamPort = '3100'] = process.argv.slice(2);

http
  .createServer((req, res) => {
    const headers: http.OutgoingHttpHeaders = {
      ...req.headers,
      host: `127.0.0.1:${upstreamPort}`,
    };
    delete headers.authorization;
    delete headers.apikey;

    const upstream = http.request(
      {
        host: '127.0.0.1',
        port: Number(upstreamPort),
        path: (req.url ?? '/').replace(/^\/rest\/v1/, ''),
        method: req.method,
        headers,
      },
      (upstreamRes) => {
        res.writeHead(upstreamRes.statusCode ?? 502, upstreamRes.headers);
        upstreamRes.pipe(res);
      },
    );
    upstream.on('error', (error) => {
      res.writeHead(502);
      res.end(String(error));
    });
    req.pipe(upstream);
  })
  .listen(Number(listenPort), '127.0.0.1');
