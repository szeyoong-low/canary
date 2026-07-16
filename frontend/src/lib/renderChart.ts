import * as echarts from "echarts";
// Can't import tree-shakeable bundle. Backend can return any chart.

export const chartContainerID: string = "chartContainer";

export function renderChart(
  config: echarts.EChartsOption,
  theme: string,
): echarts.ECharts {
  const chart: echarts.ECharts = echarts.init(
    document.getElementById(chartContainerID),
    theme,
  );
  chart.setOption(config);
  return chart;
}
