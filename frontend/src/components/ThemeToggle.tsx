import { Switch } from "@base-ui/react/switch";
import { clsx } from "clsx";
import { type ClassNameProps } from "@/shared/types";
import {
  dark,
  light,
  type ThemeContextValue,
  useTheme,
} from "@/components/ThemeProvider";
import "@/styles/component.css";

export default function ThemeToggle({ className }: ClassNameProps) {
  const themeContext: ThemeContextValue = useTheme();

  return (
    <form className={clsx(className)}>
      <div className="flex items-center gap-x-2">
        <label id="theme-toggle-label" htmlFor="theme-toggle">
          {themeContext.theme === dark ? "Dark" : "Light"}
        </label>
        <Switch.Root
          id="theme-toggle"
          aria-labelledby="theme-toggle-label"
          checked={themeContext.theme === dark}
          onCheckedChange={(checked) => {
            themeContext.setTheme(checked ? dark : light);
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
