// Reads the configuration the Worker injected into `index.html` at request time.

import * as z from "zod";

// Must match the id written by worker/index.ts.
const ENV_SCRIPT_ID: string = "__ENV__";

// The client's contract with worker/env.ts. Cannot share declaration because
// they compile under separate tsconfigs and the payload crosses the wire as
// JSON in the DOM.
const runtimeEnvSchema = z.object({
  apiOrigin: z.url(),

  // Passed to `Auth0Provider` as-is, minus `redirect_uri`, which is this
  // browser's own origin and so is supplied at the call site.
  auth0Config: z.object({
    domain: z.string().nonempty(), // A bare hostname
    clientId: z.string().nonempty(),
    authorizationParams: z.object({
      audience: z.url(),
    }),
  }),
});

type RuntimeEnv = z.infer<typeof runtimeEnvSchema>;

function readRuntimeEnv(): RuntimeEnv {
  const tag: HTMLElement | null = document.getElementById(ENV_SCRIPT_ID);

  if (tag === null) {
    throw new Error(
      `Missing #${ENV_SCRIPT_ID}: the page was served without the Worker's environment injection`,
    );
  }

  // The tag is machine-written, so this guards against a Worker/client version
  // skew rather than against hostile input. `safeParse` is used over `parse`
  // only to attach that context to the message a developer will read.
  const result = runtimeEnvSchema.safeParse(JSON.parse(tag.textContent));

  if (!result.success) {
    throw new Error(
      `Malformed #${ENV_SCRIPT_ID}: the Worker and the client disagree on the payload\n${z.prettifyError(result.error)}`,
    );
  }

  return result.data;
}

// Evaluated once when this module is first imported, so a missing or malformed
// injection fails loudly at start-up instead of on the first fetch.
export const { apiOrigin, auth0Config } = readRuntimeEnv();
