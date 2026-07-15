import { type EChartsOption } from "echarts";
import { type Params } from "react-router";
import { isDemoParams } from "@/shared/types";

const requestLookup: string[] = [
  "asset-price-daily/time-series?analysis=vwap/index-to-date&symbol=aapl&symbol=goog&symbol=msft&symbol=nvda&symbol=tsla&symbol=jpm&symbol=bac&start_date=2026-01-01&end_date=2026-03-31&base=100&reference=2026-01-02",
];

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

  const requestURL: string | undefined = requestLookup[demoID];

  if (typeof requestURL === "undefined") {
    throw new Error(
      `Demo IDs must be an integer between 0 and ${String(requestLookup.length - 1)}`,
    );
  }

  const response: Response = await fetch(
    `${String(import.meta.env.VITE_TERMINAL_ENDPOINT)}${requestURL}`,
  );

  if (!response.ok) {
    throw new Error(
      `Server error: ${String(response.status)}: ${response.statusText}`,
    );
  }

  // No validation will be done on the client's side. The backend is my own,
  // and output validation using Pydantic was already done there.
  return (await response.json()) as EChartsOption;
}
