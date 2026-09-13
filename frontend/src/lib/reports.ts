import { type EChartsOption } from "echarts";
import { infiniteQueryOptions, queryOptions } from "@tanstack/react-query";
import createClient from "openapi-fetch";
import { redirect, type ActionFunctionArgs } from "react-router";
import type { components, paths } from "@/lib/api.gen";
import { apiOrigin } from "@/lib/env";
import { getAccessToken, getAccessTokenIfSignedIn } from "@/lib/auth0";
import { clearPromptDraft } from "@/lib/promptDraft";
import { APIError, type ReportRole } from "@/shared/types";

// Headers must be built per call as a shared Headers instance would hold
// one user's token for the lifetime of the browser bundle, including after
// they sign out.

const LOCATION_HEADER_KEY: string = "Location";
const REPORT_ROLE_HEADER_KEY: string = "Report-Role";
const BEARER: string = "Bearer";

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

// The caller's effective role, as the backend saw it on this response. Read off
// a header rather than the body because the metadata writes answer a bodyless
// 204, and this page never refetches after a write.
//
// Unlike everything else here, it is an unchecked cast: response headers are
// not modelled by the generated types. `hasAtLeastRole` treats an unrecognised
// value the same as no grant, since it will not be a key in the ladder.
function readReportRole(response: Response): ReportRole | null {
  return response.headers.get(REPORT_ROLE_HEADER_KEY) as ReportRole | null;
}

export type Report = Omit<
  components["schemas"]["ReportFull"],
  "content_containers"
> & {
  content_containers: ContentContainerType[];
  role: ReportRole | null;
};

export async function createBlankReport({
  context,
}: ActionFunctionArgs): Promise<Response> {
  const { error, response } = await api.POST("/reports/", {
    headers: {
      Authorization: `${BEARER} ${await getAccessToken(context)}`,
    },
  });

  // TODO: make schema document the error shape
  if (!response.ok) {
    throw new APIError(response, error);
  }

  return redirect(response.headers.get(LOCATION_HEADER_KEY) ?? "/");
}

export async function getFullReport(reportID: string): Promise<Report> {
  const token: string | null = await getAccessTokenIfSignedIn();

  const { data, error, response } = await api.GET("/reports/{report_id}", {
    headers: token ? { Authorization: `${BEARER} ${token}` } : {},
    params: {
      path: {
        report_id: reportID,
      },
    },
  });

  if (error) {
    throw new APIError(response, error);
  }

  return {
    ...data,
    role: readReportRole(response),
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
    // Only shown when a refetch fails while the report is already on screen.
    meta: { errorTitle: "Could not refresh this report" },
  });
}

const APPEND_TO_END = null;

// Returns the saved container so the caller can place it in the cached report
// exactly as a refetch would have returned it, and the role so a grant that
// changed since the page loaded is picked up without a refetch.
export async function generateReportContent(
  reportID: string,
  prompt: string,
): Promise<{ container: ContentContainerType; role: ReportRole | null }> {
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
    throw new APIError(response, error);
  }

  // Only once the prompt has actually produced a chart, so the draft survives
  // an expired session or a failed request.
  clearPromptDraft();

  return {
    container: { ...data, chart: data.chart as EChartsOption | null },
    role: readReportRole(response),
  };
}

// Both metadata writes answer 204, so the role is the only thing they return.
export async function renameReport(
  reportID: string,
  newTitle: string,
): Promise<ReportRole | null> {
  const { error, response } = await api.PUT("/reports/{report_id}/title", {
    headers: {
      Authorization: `${BEARER} ${await getAccessToken()}`,
    },
    params: {
      path: { report_id: reportID },
    },
    body: {
      title: newTitle,
    },
  });

  if (error) {
    throw new APIError(response, error);
  }

  return readReportRole(response);
}

export async function updateReportVisibility(
  reportID: string,
  publiclyVisible: boolean,
): Promise<ReportRole | null> {
  const { error, response } = await api.PUT("/reports/{report_id}/visibility", {
    headers: {
      Authorization: `${BEARER} ${await getAccessToken()}`,
    },
    params: {
      path: { report_id: reportID },
    },
    body: {
      public: publiclyVisible,
    },
  });

  if (error) {
    throw new APIError(response, error);
  }

  return readReportRole(response);
}

export type ReportPreview = Omit<
  components["schemas"]["ReportPreview"],
  "chart"
> & {
  chart: EChartsOption | null;
};

export type ReportPreviewPage = Omit<
  components["schemas"]["ReportPreviewPage"],
  "previews"
> & {
  previews: ReportPreview[];
};

export interface ReportPreviewFilters {
  publiclyVisible: boolean;
  minimumReportRole: ReportRole | null;
}

const FIRST_PAGE: string | null = null;

async function getReportPreviews(
  { publiclyVisible, minimumReportRole }: ReportPreviewFilters,
  cursor: string | null,
  // Page size left at backend default
): Promise<ReportPreviewPage> {
  const token: string | null = await getAccessTokenIfSignedIn();

  const { data, error, response } = await api.GET("/reports/previews", {
    headers: token ? { Authorization: `${BEARER} ${token}` } : {},
    params: {
      query: {
        public: publiclyVisible,
        minimum_report_role: minimumReportRole,
        cursor,
      },
    },
  });

  if (error) {
    throw new APIError(response, error);
  }

  return {
    ...data,
    previews: data.previews.map((preview) => ({
      ...preview,
      chart: preview.chart as EChartsOption | null,
    })),
  };
}

export function reportPreviewsQueryKey(
  filters: ReportPreviewFilters,
  isAuthenticated: boolean,
): readonly unknown[] {
  // Without `isAuthenticated`, signing in would leave the signed-out
  // page cached and the user would still see public reports only.
  //
  // The filters object is hashed structurally by the cache, so callers may pass a
  // fresh literal on every render without causing a refetch.
  return ["reports", "previews", filters, isAuthenticated];
}

export function reportPreviewsQueryOptions(
  filters: ReportPreviewFilters,
  isAuthenticated: boolean,
) {
  return infiniteQueryOptions({
    queryKey: reportPreviewsQueryKey(filters, isAuthenticated),
    // Covers a failed "load more" or refetch.
    meta: { errorTitle: "Could not load more reports" },
    queryFn: ({ pageParam }: { pageParam: string | null }) =>
      getReportPreviews(filters, pageParam),
    initialPageParam: FIRST_PAGE,
    // The backend sends `next_cursor: null` on the last page, which is exactly
    // how the cache is told there is nothing further to fetch.
    getNextPageParam: (lastPage: ReportPreviewPage) => lastPage.next_cursor,
    refetchOnMount: "always",
  });
}
