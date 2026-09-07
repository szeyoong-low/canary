import { Link, Outlet } from "react-router";
import { AuthButton, ThemeProvider, ThemeToggle } from "@/components";
import { projectName } from "@/shared/constants";
import "@/styles/layout.css";

export default function Layout() {
  return (
    <ThemeProvider>
      <header className="flex items-center justify-center-safe">
        <title>{projectName}</title>
        <h1 className="page-title font-medium font-stretch-30% text-3xl">
          <Link to="/">{projectName}</Link>
        </h1>
        <div className="absolute right-3 flex items-center gap-4 px-4">
          <ThemeToggle />
          <AuthButton />
        </div>
      </header>
      <main>
        <Outlet />
      </main>
    </ThemeProvider>
  );
}
