import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { Auth0Provider } from "@auth0/auth0-react";
import { RouterProvider } from "react-router/dom";
import router from "@/router";
import { auth0Config } from "@/lib/env";
import "@/styles/index.css";

const rootElement: HTMLElement | null = document.getElementById("root");
if (!rootElement) {
  throw new Error("Root element not found");
}

createRoot(rootElement).render(
  <StrictMode>
    <Auth0Provider
      {...auth0Config}
      authorizationParams={{
        ...auth0Config.authorizationParams,
        redirect_uri: window.location.origin,
      }}
      // Terraform configures rotating refresh tokens, but the SDK only asks for
      // one when this is set.
      useRefreshTokens
    >
      <RouterProvider router={router} />
    </Auth0Provider>
  </StrictMode>,
);
