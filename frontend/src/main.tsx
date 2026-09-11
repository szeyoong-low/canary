import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { Auth0Provider } from "@auth0/auth0-react";
import { RouterProvider } from "react-router/dom";
import router from "@/router";
import { auth0Client } from "@/lib/auth0";
import "@/styles/index.css";

const rootElement: HTMLElement | null = document.getElementById("root");
if (!rootElement) {
  throw new Error("Root element not found");
}

createRoot(rootElement).render(
  <StrictMode>
    <Auth0Provider client={auth0Client}>
      <RouterProvider router={router} />
    </Auth0Provider>
  </StrictMode>,
);
