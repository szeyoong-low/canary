import { createBrowserRouter } from "react-router";

function Root() {
  return <p>Canary is here</p>;
}

const router = createBrowserRouter([{ path: "/", Component: Root }]);

export default router;
