import { type EChartsOption } from "echarts";
import createClient from "openapi-fetch";
import { redirect, type ActionFunctionArgs } from "react-router";
import type { components, paths } from "@/lib/api.gen";
import { apiOrigin } from "@/lib/env";
import { getAccessToken } from "@/lib/auth0";
import { clearPromptDraft } from "@/lib/promptDraft";

// Headers must be built per call as a shared Headers instance would hold
// one user's token for the lifetime of the browser bundle, including after
// they sign out.

const LOCATION_HEADER_KEY: string = "Location";
const BEARER: string = "Bearer";

export const PROMPT_FORM_FIELD: string = "prompt";

// Typed against the backend's OpenAPI schema: paths, methods and bodies are
// checked at compile time. Safe to share as it only carries the origin.
const api = createClient<paths>({ baseUrl: apiOrigin });

// The backend's `ChartConfigModel` and ECharts' `EChartsOption` describe the
// same object with different strictness, so consumers get the ECharts type and
// never have to know the generated one exists.
export type ContentContainerType = Omit<
  components["schemas"]["DisplayedContentContainer"],
  "chart"
> & {
  chart: EChartsOption;
};

export type Report = Omit<
  components["schemas"]["ReportFull"],
  "content_containers"
> & {
  content_containers: ContentContainerType[];
};

export async function createBlankReport({
  context,
}: ActionFunctionArgs): Promise<Response> {
  const { response } = await api.POST("/reports/", {
    headers: {
      Authorization: `${BEARER} ${await getAccessToken(context)}`,
    },
  });

  // TODO: make schema document the error shape
  if (!response.ok) {
    throw new Error(
      `Error: ${String(response.status)}: ${response.statusText}`,
    );
  }

  return redirect(response.headers.get(LOCATION_HEADER_KEY) ?? "/");
}

export async function getFullReport({
  params,
  context,
}: ActionFunctionArgs): Promise<Report> {
  // Guaranteed by the route segment. Just for type narrowing.
  if (!params.reportID) {
    throw new Error("Missing `reportID` route parameter.");
  }

  const { data, error, response } = await api.GET("/reports/{report_id}", {
    headers: {
      Authorization: `${BEARER} ${await getAccessToken(context)}`,
    },
    params: {
      path: {
        report_id: params.reportID,
      },
    },
  });

  if (error) {
    throw new Error(
      `Error: ${String(response.status)}: ${response.statusText}`,
    );
  }

  return {
    ...data,
    content_containers: data.content_containers.map((container) => ({
      ...container,
      chart: container.chart as EChartsOption,
    })),
  };
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
