import { type EChartsOption } from "echarts";
import { type ActionFunctionArgs } from "react-router";
import {
  type Auth0Client,
  GenericError,
  MissingRefreshTokenError,
} from "@auth0/auth0-spa-js";
import { apiOrigin } from "@/lib/env";
import { auth0ClientContext, loginWithReturn } from "@/lib/auth0";
import { AGENT_PATH, POST, PROMPT_FIELD } from "@/shared/constants";

const REAUTHENTICATION_CODES: ReadonlySet<string> = new Set([
  "login_required", // No session at Auth0 any more
  "consent_required", // Session exists, but this audience was never consented to
]);

function needsReauthentication(error: unknown): boolean {
  if (error instanceof MissingRefreshTokenError) {
    return true;
  }

  return (
    error instanceof GenericError && REAUTHENTICATION_CODES.has(error.error)
  );
}

export async function getChartFromPrompt({
  request,
  context,
}: ActionFunctionArgs): Promise<EChartsOption> {
  const auth0Client: Auth0Client = context.get(auth0ClientContext);

  let accessToken: string;
  try {
    // Serves the cached token when it is still valid, and silently redeems the
    // refresh token when it is not.
    accessToken = await auth0Client.getTokenSilently();
  } catch (error: unknown) {
    if (!needsReauthentication(error)) {
      throw error;
    }

    // Leaves the page, so nothing below this runs. The `throw` is unreachable at
    // runtime and exists to tell TypeScript the function ends here.
    await loginWithReturn();
    throw error;
  }

  const form_data: FormData = await request.formData();

  const response: Response = await fetch(new URL(AGENT_PATH, apiOrigin), {
    method: POST,
    body: JSON.stringify({ prompt: form_data.get(PROMPT_FIELD) }),
    // Built per call: a shared Headers instance would hold one user's token for
    // the lifetime of the page, including after they sign out.
    headers: new Headers({
      "Content-Type": "application/json",
      Authorization: `Bearer ${accessToken}`,
    }),
  });

  if (!response.ok) {
    throw new Error(
      `Server error: ${String(response.status)}: ${response.statusText}`,
    );
  }

  // No validation will be done on the client's side. The backend is my own,
  // and output validation using Pydantic was already done there.
  return (await response.json()) as EChartsOption;
}
