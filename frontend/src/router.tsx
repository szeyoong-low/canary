import { createBrowserRouter } from "react-router";
import { loadChartConfig } from "@/lib/api";
import Demo from "@/routes/Demo";
import Home from "@/routes/Home";
import Layout from "@/routes/Layout";

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
