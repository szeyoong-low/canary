import clsx, { type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

// Source - https://stackoverflow.com/a/75145528
export const mergeClassName = (...classes: ClassValue[]) =>
  twMerge(clsx(...classes));
