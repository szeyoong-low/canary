import { Outlet, useMatches } from "react-router";
import { projectTitle } from "@/shared/constants";
import { isTitleHandle } from "@/shared/types";
import ThemeToggle from "@/components/ThemeToggle";
import "@/styles/layout.css";

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
      <header className="flex items-center justify-center-safe">
        <title>{title}</title>
        <h1 className="page-title font-medium font-stretch-30% text-3xl">
          {title}
        </h1>
        <ThemeToggle className="absolute right-3" />
      </header>
      <main>
        <Outlet />
      </main>
    </div>
  );
}

export default Layout;
