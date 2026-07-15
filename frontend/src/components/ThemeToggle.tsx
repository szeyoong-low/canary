import { Switch } from "@base-ui/react/switch";
import { useEffect, useState } from "react";
import "@/styles/component.css";

// Constants MUST match the inline no-flash script in index.html.
// Sharing is not possible because that script is plain JS embedded in HTML.
type Theme = "light" | "dark";
const dark = "dark";
const light = "light";
const darkMediaQuery = `(prefers-color-scheme: ${dark})`;
const themeKey = "theme";

function getInitialTheme(): Theme {
  const stored = localStorage.getItem(themeKey);
  if (stored === light || stored === dark) return stored;
  return window.matchMedia(darkMediaQuery).matches ? dark : light;
}

function ThemeToggle() {
  const [theme, setTheme] = useState<Theme>(getInitialTheme);

  useEffect(() => {
    localStorage.setItem(themeKey, theme);
    document.documentElement.style.colorScheme = theme;
  }, [theme]);

  return (
    <form>
      <div className="flex items-center">
        <label id="theme-toggle-label" htmlFor="theme-toggle">
          {theme === dark ? "Dark mode" : "Light mode"}
        </label>
        <Switch.Root
          id="theme-toggle"
          aria-labelledby="theme-toggle-label"
          checked={theme === dark}
          onCheckedChange={(checked) => {
            setTheme(checked ? dark : light);
          }}
          className="SwitchRoot"
          nativeButton
          render={<button />}
        >
          <Switch.Thumb className="SwitchThumb" />
        </Switch.Root>
      </div>
    </form>
  );
}

export default ThemeToggle;
