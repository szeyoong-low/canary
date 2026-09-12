import { type EChartsOption } from "echarts";
import createClient from "openapi-fetch";
import { redirect, type ActionFunctionArgs } from "react-router";
import type { paths } from "@/lib/api.gen";
import { apiOrigin } from "@/lib/env";
import { getAccessToken } from "@/lib/auth0";
import { clearPromptDraft } from "@/lib/promptDraft";

// Headers must be built per call as a shared Headers instance would hold
// one user's token for the lifetime of the browser bundle, including after
// they sign out.

const LOCATION_HEADER_KEY: string = "Location";

// Typed against the backend's OpenAPI schema: paths, methods and bodies are
// checked at compile time. Safe to share as it only carries the origin.
const api = createClient<paths>({ baseUrl: apiOrigin });

export async function createBlankReport({
  context,
}: ActionFunctionArgs): Promise<Response> {
  const { response } = await api.POST("/reports/", {
    headers: {
      Authorization: `Bearer ${await getAccessToken(context)}`,
    },
  });

  if (!response.ok) {
    throw new Error(
      `Error: ${String(response.status)}: ${response.statusText}`,
    );
  }

  return redirect(response.headers.get(LOCATION_HEADER_KEY) ?? "/");
}

export async function getChartFromPrompt({
  request,
  context,
}: ActionFunctionArgs): Promise<EChartsOption> {
  const form_data: FormData = await request.formData();

  const response: Response = await fetch(new URL("/dev/agent/", apiOrigin), {
    method: "POST",
    body: JSON.stringify({ prompt: form_data.get("prompt") }),
    headers: new Headers({
      "Content-Type": "application/json",
      Authorization: `Bearer ${await getAccessToken(context)}`,
    }),
  });

  if (!response.ok) {
    throw new Error(
      `Server error: ${String(response.status)}: ${response.statusText}`,
    );
  }

  // Only once the prompt has actually produced a chart so that it exists in
  // after an expired session or failed request
  clearPromptDraft();

  // No validation will be done on the client's side. The backend is my own,
  // and output validation using Pydantic was already done there.
  return (await response.json()) as EChartsOption;
}
