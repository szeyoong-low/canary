import { createBrowserRouter } from "react-router";
import { loadChartConfig } from "@/lib/api";
import { Demo, Home, Layout } from "@/routes/index";

const router = createBrowserRouter([
  {
    Component: Layout,
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
