// Reads the configuration the Worker injected into `index.html` at request time.

// Must match the id written by worker/index.ts.
const ENV_SCRIPT_ID: string = "__ENV__";

interface RuntimeEnv {
  apiOrigin: string;
}

function readRuntimeEnv(): RuntimeEnv {
  const tag: HTMLElement | null = document.getElementById(ENV_SCRIPT_ID);

  if (tag === null) {
    throw new Error(
      `Missing #${ENV_SCRIPT_ID}: the page was served without the Worker's environment injection`,
    );
  }

  const parsed: unknown = JSON.parse(tag.textContent);

  // The tag is machine-written, so this guards against a Worker/client version
  // skew rather than against hostile input.
  if (
    typeof parsed !== "object" ||
    parsed === null ||
    typeof (parsed as RuntimeEnv).apiOrigin !== "string"
  ) {
    throw new Error(
      `Malformed #${ENV_SCRIPT_ID}: expected an apiOrigin string`,
    );
  }

  return parsed as RuntimeEnv;
}

// Evaluated once when this module is first imported, so a missing or malformed
// injection fails loudly at start-up instead of on the first fetch.
export const { apiOrigin } = readRuntimeEnv();
