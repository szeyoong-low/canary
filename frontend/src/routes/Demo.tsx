import { type ECharts, type EChartsOption } from "echarts";
import { useEffect, useRef } from "react";
import { useLoaderData, useParams } from "react-router";
import { chartContainerID, renderChart } from "@/lib/renderChart";
import { type Theme, useTheme } from "@/lib/themeContext";
import { demoTitles } from "@/shared/constants";
import { isDemoParams } from "@/shared/types";

export default function Demo() {
  const chartConfig: EChartsOption = useLoaderData<EChartsOption>();
  const containerRef = useRef<HTMLDivElement>(null);
  const { theme } = useTheme(); // Only reactive elements can be deps
  const themeRef = useRef<Theme>(theme); // Needed: react hooks need exhaustive deps
  const chartRef = useRef<ECharts>(undefined);
  const params = useParams();
  if (!isDemoParams(params)) {
    throw new Error("Can't parse demo ID");
  }
  const demoID: number = parseInt(params.demoID, 10);
  if (Number.isNaN(demoID)) {
    throw new Error("Demo ID is an integer");
  }

  useEffect(() => {
    const chart = renderChart(chartConfig, themeRef.current);
    chartRef.current = chart;

    // ECharts doesn't auto-resize with its container, so watch the
    // container element and tell the chart to resize when it does.
    const resizeObserver = new ResizeObserver(() => {
      chart.resize();
    });
    // Will have been set as effects run after mount
    if (containerRef.current) {
      resizeObserver.observe(containerRef.current);
    }

    return () => {
      resizeObserver.disconnect();
      chart.dispose();
      chartRef.current = undefined;
    };
  }, [chartConfig]);

  useEffect(() => {
    chartRef.current?.setTheme(theme);
    themeRef.current = theme;
  }, [theme]);

  return (
    <div className="flex flex-col items-center page-title text-xl">
      <div>
        <h2>{demoTitles[demoID]}</h2>
      </div>
      <div
        ref={containerRef}
        id={chartContainerID}
        className="w-200 h-100 md:w-250 md:h-150"
      ></div>
    </div>
  );
}
