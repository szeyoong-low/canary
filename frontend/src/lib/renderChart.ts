import { type ECharts, type EChartsOption, init } from "echarts";
// Can't tree-shake bundle as backend can return any chart.

export const chartContainerID: string = "chartContainer";

export function renderChart(config: EChartsOption, theme: string): ECharts {
  const chart: ECharts = init(document.getElementById(chartContainerID), theme);
  chart.setOption(config);
  return chart;
}
