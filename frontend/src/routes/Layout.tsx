import { Outlet } from "react-router";
import { ThemeProvider, ThemeToggle } from "@/components";
import { projectName } from "@/shared/constants";
import "@/styles/layout.css";

export default function Layout() {
  return (
    <ThemeProvider>
      <header className="flex items-center justify-center-safe">
        <title>{projectName}</title>
        <h1 className="page-title font-medium font-stretch-30% text-3xl">
          {projectName}
        </h1>
        <ThemeToggle className="absolute right-3" />
      </header>
      <main>
        <Outlet />
      </main>
    </ThemeProvider>
  );
}
