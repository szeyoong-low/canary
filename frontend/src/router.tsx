import { createBrowserRouter } from "react-router";
import { Error, Home, Layout } from "@/routes";

export default createBrowserRouter([
  {
    Component: Layout,
    ErrorBoundary: Error,
    children: [{ index: true, Component: Home }],
  },
]);
