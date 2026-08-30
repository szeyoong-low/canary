// Resolves the backend origin from the hostname the browser used.
//
// Deriving this from the request keeps the build environment-independent.
// Since this mapping is constant across environments, there is no need to pass
// environment variables. For Workers, these are captured together with the
// static assets in a version. Avoiding them allows me to have only one Worker
// that I create versions of and promote.

const LOCAL_ORIGIN: string = "http://localhost:8000";
const PRODUCTION_ORIGIN: string = "https://api.canary.markets";

// Development deployments are published as `dev-<pull>-canary.low-szeyoong.workers.dev`
// by `wrangler versions upload --preview-alias dev-<pull>`.
const PREVIEW_HOSTNAME: RegExp = /^dev-(?<pull>\d+)-canary\./;

export function resolveAPIOrigin(hostname: string): string {
  if (hostname === "localhost" || hostname === "127.0.0.1") {
    return LOCAL_ORIGIN;
  }

  const pull: string | undefined =
    PREVIEW_HOSTNAME.exec(hostname)?.groups?.pull;

  if (typeof pull !== "undefined") {
    return `https://dev-${pull}-api.canary.markets`;
  }

  // Anything else is a custom domain, so it is production. Defaulting this way
  // means an unrecognised hostname degrades to a working site rather than a
  // broken one. The backend's CORS rules will take care of this.
  return PRODUCTION_ORIGIN;
}
