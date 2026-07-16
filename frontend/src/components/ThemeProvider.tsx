import {
  getTheme,
  type Theme,
  ThemeContext,
  themeKey,
} from "@/lib/themeContext";
import { useEffect, useState, type ReactNode } from "react";

export default function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setTheme] = useState<Theme>(getTheme);

  useEffect(() => {
    localStorage.setItem(themeKey, theme);
    document.documentElement.dataset.theme = theme;
  }, [theme]);

  return <ThemeContext value={{ theme, setTheme }}>{children}</ThemeContext>;
}
