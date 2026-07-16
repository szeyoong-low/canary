import { createBrowserRouter } from "react-router";
import { loadChartConfig } from "@/lib/api";
import { Demo, Error, Home, Layout } from "@/routes";

const router = createBrowserRouter([
  {
    Component: Layout,
    ErrorBoundary: Error,
    children: [
      { index: true, Component: Home },
      {
        path: "demo/:demoID",
        Component: Demo,
        loader: loadChartConfig,
      },
    ],
  },
]);

export default router;
