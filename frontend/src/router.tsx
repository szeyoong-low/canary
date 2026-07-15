import { createBrowserRouter } from "react-router";
import Home from "@/routes/Home";
import Layout from "@/routes/Layout";

const router = createBrowserRouter([
  {
    Component: Layout,
    children: [{ index: true, Component: Home }],
  },
]);

export default router;
