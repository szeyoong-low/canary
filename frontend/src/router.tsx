import { createBrowserRouter, RouterContextProvider } from "react-router";
import { Error, Home, Layout, Report, ReportCreation } from "@/routes";
import { auth0Client, auth0ClientContext } from "@/lib/auth0";
import { createBlankReport, getChartFromPrompt } from "@/lib/reports";

const REPORT_BROWSER_PATH: string = "reports";
const REPORT_ID_BROWSER_PATH_PARAM: string = ":reportID";

export default createBrowserRouter(
  [
    {
      Component: Layout,
      ErrorBoundary: Error,
      children: [
        { index: true, Component: Home },
        {
          path: REPORT_BROWSER_PATH,
          Component: ReportCreation,
          action: createBlankReport,
        },
        {
          path: `${REPORT_BROWSER_PATH}/${REPORT_ID_BROWSER_PATH_PARAM}`,
          Component: Report,
          action: getChartFromPrompt,
        },
      ],
    },
  ],
  {
    // Called once per navigation or fetcher call to build the `context` argument
    // that loaders and actions receive.
    getContext() {
      const context = new RouterContextProvider();
      context.set(auth0ClientContext, auth0Client);
      return context;
    },
  },
);
