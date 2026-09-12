import { type EChartsOption } from "echarts";
import { queryOptions } from "@tanstack/react-query";
import createClient from "openapi-fetch";
import { redirect, type ActionFunctionArgs } from "react-router";
import type { components, paths } from "@/lib/api.gen";
import { apiOrigin } from "@/lib/env";
import { getAccessToken } from "@/lib/auth0";
import { clearPromptDraft } from "@/lib/promptDraft";
import { APIError } from "@/shared/types";

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
  chart: EChartsOption | null;
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
    throw new APIError(response);
  }

  return redirect(response.headers.get(LOCATION_HEADER_KEY) ?? "/");
}

export async function getFullReport(reportID: string): Promise<Report> {
  const { data, error, response } = await api.GET("/reports/{report_id}", {
    headers: {
      Authorization: `${BEARER} ${await getAccessToken()}`,
    },
    params: {
      path: {
        report_id: reportID,
      },
    },
  });

  if (error) {
    throw new APIError(response);
  }

  return {
    ...data,
    content_containers: data.content_containers.map((container) => ({
      ...container,
      chart: container.chart as EChartsOption | null,
    })),
  };
}

// The key every cache entry for a single report is filed under.
export function reportQueryKey(reportID: string): readonly unknown[] {
  return ["reports", reportID];
}

// Pairs the key with its fetcher so the two can never drift apart.
export function reportQueryOptions(reportID: string) {
  return queryOptions({
    queryKey: reportQueryKey(reportID),
    queryFn: () => getFullReport(reportID),
  });
}

const APPEND_TO_END = null;

// Returns the saved container so the caller can place it in the cached report
// exactly as a refetch would have returned it.
export async function generateReportContent(
  reportID: string,
  prompt: string,
): Promise<ContentContainerType> {
  const { data, error, response } = await api.POST(
    "/reports/{report_id}/contents",
    {
      headers: {
        Authorization: `${BEARER} ${await getAccessToken()}`,
      },
      params: {
        path: { report_id: reportID },
        query: { position: APPEND_TO_END },
      },
      body: { prompt },
    },
  );

  if (error) {
    throw new APIError(response);
  }

  // Only once the prompt has actually produced a chart, so the draft survives
  // an expired session or a failed request.
  clearPromptDraft();

  return { ...data, chart: data.chart as EChartsOption | null };
}
