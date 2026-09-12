import { type ComponentProps } from "react";
import { mergeClassName } from "@/lib/mergeClassName";
import "@/styles/component.css";

interface OptionCardProps extends ComponentProps<"button"> {
  pending?: boolean;
}

export default function OptionCard({
  className,
  pending = false,
  disabled = false,
  ...props
}: OptionCardProps) {
  return (
    <button
      {...props}
      disabled={disabled || pending}
      data-pending={pending || undefined}
      aria-busy={pending}
      className={mergeClassName("OptionCard", className)}
    />
  );
}
