import * as echarts from "echarts";
// Can't import tree-shakeable bundle. Backend can return any chart.
import { type Theme } from "@/components/ThemeProvider";

export const chartContainerID: string = "chartContainer";

export function renderChart(
  config: echarts.EChartsOption,
  theme: Theme,
): echarts.ECharts {
  const chart: echarts.ECharts = echarts.init(
    document.getElementById(chartContainerID),
    theme,
  );
  chart.setOption(config);
  return chart;
}
