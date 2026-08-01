import { type ECharts, type EChartsOption, init } from "echarts";
// Can't tree-shake bundle as backend can return any chart.
import { type RefObject, useEffect, useRef } from "react";
import { twMerge } from "tailwind-merge";
import { type Theme, useTheme } from "@/lib/themeContext";

// ECharts ships "default" (light) and "dark".
const echartsTheme: Record<Theme, string> = {
  light: "default",
  dark: "dark",
};

export default function Chart({ config, className = "" }: { config: EChartsOption, className?: string }) {
  const containerRef: RefObject<HTMLDivElement | null> =
    useRef<HTMLDivElement>(null);

  const { theme }: { theme: Theme } = useTheme(); // Only reactive elements can be deps
  const themeRef: RefObject<Theme> = useRef<Theme>(theme); // Needed: react hooks need exhaustive deps
  const chartRef: RefObject<ECharts | undefined> = useRef<ECharts>(undefined);

  useEffect(() => {
    const chart: ECharts = init(
      containerRef.current,
      echartsTheme[themeRef.current],
    );
    chart.setOption(config);
    chartRef.current = chart;

    // ECharts doesn't auto-resize with its container, so watch the
    // container element and tell the chart to resize when it does.
    const resizeObserver: ResizeObserver = new ResizeObserver(() => {
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
  }, [config]);

  useEffect(() => {
    chartRef.current?.setTheme(echartsTheme[theme]);
    themeRef.current = theme;
  }, [theme]);

  return (
    <div ref={containerRef} className={twMerge("w-200 h-100 md:w-250 md:h-150", className)}></div>
  );
}
