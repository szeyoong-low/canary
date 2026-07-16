import {
  createContext,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";

// Constants MUST match the inline no-flash script in index.html.
// Sharing is not possible because that script is plain JS embedded in HTML.
export type Theme = "light" | "dark";
export const light = "light";
export const dark = "dark";
const darkMediaQuery = `(prefers-color-scheme: ${dark})`;
const themeKey = "theme";

export type ThemeContextValue = {
  theme: Theme;
  setTheme: (theme: Theme) => void;
};

function getTheme(): Theme {
  const stored = localStorage.getItem(themeKey);
  if (stored === light || stored === dark) return stored;
  return window.matchMedia(darkMediaQuery).matches ? dark : light;
}

const ThemeContext = createContext<ThemeContextValue | undefined>(undefined);

export function useTheme() {
  const themeContext = useContext(ThemeContext);
  if (!themeContext) {
    throw new Error("useTheme must be used within ThemeProvider");
  }
  return themeContext;
}

export default function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setTheme] = useState<Theme>(getTheme);

  useEffect(() => {
    localStorage.setItem(themeKey, theme);
    document.documentElement.style.colorScheme = theme;
  }, [theme]);

  return <ThemeContext value={{ theme, setTheme }}>{children}</ThemeContext>;
}
