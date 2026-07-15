import { createBrowserRouter } from "react-router";
import Home from "@/routes/home";
import Layout from "@/routes/layout";

const router = createBrowserRouter([
  {
    Component: Layout,
    children: [{ index: true, Component: Home, handle: { title: "Home" } }],
  },
]);

export default router;
