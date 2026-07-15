import { Outlet, useMatches } from "react-router";
import { projectTitle } from "@/shared/constants";
import { isTitleHandle } from "@/shared/types";

function Layout() {
  // Search from the deepest match outward so the most specific route is used.
  const title =
    useMatches()
      .reverse()
      .map((match) =>
        isTitleHandle(match.handle) ? match.handle.title : undefined,
      )
      .find(Boolean) ?? projectTitle;

  return (
    <div>
      <header>
        <title>{title}</title>
        <h1>{title}</h1>
      </header>
      <main>
        <Outlet />
      </main>
    </div>
  );
}

export default Layout;
