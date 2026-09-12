import { type EChartsOption } from "echarts";
import { redirect, type ActionFunctionArgs } from "react-router";
import { apiOrigin } from "@/lib/env";
import { getAccessToken } from "@/lib/auth0";
import { clearPromptDraft } from "@/lib/promptDraft";
import {
  AGENT_PATH,
  POST,
  PROMPT_FIELD,
  REPORT_API_PATH,
} from "@/shared/constants";

// Headers must be built per call as a shared Headers instance would hold
// one user's token for the lifetime of the browser bundle, including after
// they sign out.
const JSON_HEADER: Record<string, string> = {
  "Content-Type": "application/json",
};

const LOCATION_HEADER_KEY: string = "Location";

export async function createBlankReport({
  context,
}: ActionFunctionArgs): Promise<Response> {
  const response: Response = await fetch(new URL(REPORT_API_PATH, apiOrigin), {
    method: POST,
    headers: new Headers({
      ...JSON_HEADER,
      Authorization: `Bearer ${await getAccessToken(context)}`,
    }),
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

  const response: Response = await fetch(new URL(AGENT_PATH, apiOrigin), {
    method: POST,
    body: JSON.stringify({ prompt: form_data.get(PROMPT_FIELD) }),
    // Built per call: a shared Headers instance would hold one user's token for
    // the lifetime of the page, including after they sign out.
    headers: new Headers({
      ...JSON_HEADER,
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
