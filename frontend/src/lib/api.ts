import { type EChartsOption } from "echarts";
import { type Params } from "react-router";
import { apiOrigin } from "@/lib/env";
import {
  AGENT_PATH,
  POST,
  PROMPT_FIELD,
  TERMINAL_PATH,
} from "@/shared/constants";
import { isDemoParams } from "@/shared/types";

const requestPath: string[] = ["asset-price-daily", "market-composition"];

const requestBody: object[] = [
  {
    display: "time-series",
    analysis: [
      {
        name: "Volume-weighted average price",
        show: false,
        analysis: "",
        metric: "vwap",
      },
      {
        name: "Indexed price",
        show: true,
        analysis: "index-to-date",
        metric: "Volume-weighted average price",
        base: 100,
        reference: "2026-01-02",
      },
    ],
    symbol: ["aapl", "goog", "msft", "nvda", "tsla", "jpm", "bac"],
    start_date: "2026-01-01",
    end_date: "2026-03-31",
  },
  {
    display: "treemap",
    analysis: [
      {
        name: "Market capitalisation",
        show: true,
        analysis: "",
        metric: "marketCap",
      },
      {
        name: "Share price",
        show: true,
        analysis: "",
        metric: "price",
      },
    ],
    drilldown: ["sector", "industry", "companyName"],
    aggregate_col: "marketCap",
  },
];

const demoHeaders: Headers = new Headers({
  "Content-Type": "application/json",
});

const agentHeaders: Headers = new Headers({
  "Content-Type": "application/json",
});

export async function loadChartConfig({
  params,
}: {
  params: Params;
}): Promise<EChartsOption> {
  if (!isDemoParams(params)) {
    throw new Error("Can't parse demo ID");
  }

  const demoID: number = parseInt(params.demoID, 10);

  if (Number.isNaN(demoID)) {
    throw new Error("Demo ID is an integer");
  }

  const requestURL: string | undefined = requestPath[demoID];

  if (typeof requestURL === "undefined") {
    throw new Error(
      `Demo IDs must be an integer between 0 and ${String(requestPath.length - 1)}`,
    );
  }

  const response: Response = await fetch(
    new URL(`${TERMINAL_PATH}${requestURL}`, apiOrigin),
    {
      method: POST,
      body: JSON.stringify(requestBody[demoID]),
      headers: demoHeaders,
    },
  );

  if (!response.ok) {
    throw new Error(
      `Server error at ${response.url}: ${String(response.status)}: ${response.statusText}`,
    );
  }

  // No validation will be done on the client's side. The backend is my own,
  // and output validation using Pydantic was already done there.
  return (await response.json()) as EChartsOption;
}

export async function getChartFromPrompt({
  request,
}: {
  request: Request;
}): Promise<EChartsOption> {
  const form_data: FormData = await request.formData();

  const response: Response = await fetch(new URL(AGENT_PATH, apiOrigin), {
    method: POST,
    body: JSON.stringify({ text: form_data.get(PROMPT_FIELD) }),
    headers: agentHeaders,
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
