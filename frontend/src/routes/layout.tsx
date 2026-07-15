import { Outlet, useMatches } from "react-router";
import { projectTitle } from "@/shared/constants";
import { isTitleHandle } from "@/shared/types";
import ThemeToggle from "@/components/ThemeToggle";

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
        <ThemeToggle />
      </header>
      <main>
        <Outlet />
      </main>
    </div>
  );
}

export default Layout;
