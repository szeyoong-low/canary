import { createBrowserRouter, RouterContextProvider } from "react-router";
import { Error, Home, Layout, Report } from "@/routes";
import { auth0Client, auth0ClientContext } from "@/lib/auth0";
import { getChartFromPrompt } from "./lib/api";

export default createBrowserRouter(
  [
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
