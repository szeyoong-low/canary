import { createBrowserRouter } from "react-router";
import { loadChartConfig } from "@/lib/api";
import { Ask, Demo, Error, Home, Layout } from "@/routes";

export default createBrowserRouter([
  {
    Component: Layout,
    ErrorBoundary: Error,
    children: [
      { index: true, Component: Home },
      { path: "demo/ask", Component: Ask },
      {
        path: "demo/:demoID",
        Component: Demo,
        loader: loadChartConfig,
      },
    ],
  },
]);
