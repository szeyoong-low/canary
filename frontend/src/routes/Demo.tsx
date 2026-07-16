import { type ECharts, type EChartsOption } from "echarts";
import { useEffect, useRef } from "react";
import { useLoaderData } from "react-router";
import { type Theme, useTheme } from "@/components/ThemeProvider";
import { chartContainerID, renderChart } from "@/lib/renderChart";

export default function Demo() {
  const chartConfig: EChartsOption = useLoaderData<EChartsOption>();
  const containerRef = useRef<HTMLDivElement>(null);
  const { theme } = useTheme(); // Only reactive elements can be deps
  const themeRef = useRef<Theme>(theme); // Needed: react hooks need exhaustive deps
  const chartRef = useRef<ECharts>(undefined);

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
    <div className="flex flex-col items-center">
      <div
        ref={containerRef}
        id={chartContainerID}
        className="w-100 h-80 md:w-175 md:h-130"
      ></div>
    </div>
  );
}
