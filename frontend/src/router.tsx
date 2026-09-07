import { createBrowserRouter } from "react-router";
import { Error, Home, Layout, Report } from "@/routes";
import { getChartFromPrompt } from "./lib/api";

export default createBrowserRouter([
  {
    Component: Layout,
    ErrorBoundary: Error,
    children: [
      { index: true, Component: Home },
      {
        path: "report/:reportID",
        Component: Report,
        action: getChartFromPrompt,
      },
    ],
  },
]);
