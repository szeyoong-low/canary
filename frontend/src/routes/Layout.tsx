import { Link, Outlet } from "react-router";
import {
  AuthButton,
  ThemeProvider,
  ThemeToggle,
  ToastProvider,
} from "@/components";
import { projectName } from "@/shared/constants";
import "@/styles/layout.css";

export default function Layout() {
  return (
    <ThemeProvider>
      <ToastProvider>
        <header className="flex items-center justify-center-safe">
          <title>{projectName}</title>
          <Link to="/">
            <h1 className="page-title font-stretch-30% text-3xl">
              {projectName}
            </h1>
          </Link>
          <UtilityButtons />
        </header>
        <main>
          <Outlet />
        </main>
        <footer className="flex items-center justify-center gap-6">
          <a href="https://www.linkedin.com/in/szeyoong-low">Sze Yoong Low</a>
          <a href="https://github.com/szeyoong-low/canary">GitHub repository</a>
        </footer>
      </ToastProvider>
    </ThemeProvider>
  );
}

function UtilityButtons() {
  return (
    <div className="absolute right-3 flex items-center gap-4 px-4">
      <ThemeToggle className="hidden md:block" />
      <AuthButton />
    </div>
  );
}
