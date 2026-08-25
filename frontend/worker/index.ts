import { resolveAPIOrigin } from "./env.ts";

interface Env {
  ASSETS: Fetcher;
}

// Must match the id read by src/lib/env.ts.
const ENV_SCRIPT_ID: string = "__ENV__";

// A `<` inside a `<script>` block can terminate the tag early, even when the
// tag is inert JSON. Encoding it keeps the payload valid JSON that parses back
// to exactly the same string.
function escapeForScriptTag(json: string): string {
  return json.replaceAll("<", "\\u003c");
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const response: Response = await env.ASSETS.fetch(request);

    // Hashed JS/CSS and images pass through untouched, so they keep their
    // original headers and are never buffered.
    const contentType: string = response.headers.get("content-type") ?? "";

    if (!contentType.includes("text/html")) {
      return response;
    }

    const config: string = escapeForScriptTag(
      JSON.stringify({
        apiOrigin: resolveAPIOrigin(new URL(request.url).hostname),
      }),
    );

    return new HTMLRewriter()
      .on("head", {
        element(head): void {
          head.append(
            `<script type="application/json" id="${ENV_SCRIPT_ID}">${config}</script>`,
            { html: true },
          );
        },
      })
      .transform(response);
  },
} satisfies ExportedHandler<Env>;
