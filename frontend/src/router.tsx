import { createBrowserRouter } from "react-router";
import { getChartFromPrompt, loadChartConfig } from "@/lib/api";
import { Ask, Demo, Error, Home, Layout } from "@/routes";

export default createBrowserRouter([
  {
    Component: Layout,
    ErrorBoundary: Error,
    children: [
      { index: true, Component: Home },
      { path: "demo/ask", Component: Ask, action: getChartFromPrompt },
      {
        path: "demo/:demoID",
        Component: Demo,
        loader: loadChartConfig,
      },
    ],
  },
]);
