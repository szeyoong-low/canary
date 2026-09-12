import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { Auth0Provider, type AppState } from "@auth0/auth0-react";
import { RouterProvider } from "react-router/dom";
import { QueryClientProvider } from "@tanstack/react-query";
import router from "@/router";
import { auth0Client } from "@/lib/auth0";
import { queryClient } from "@/lib/queryClient";
import "@/styles/index.css";

const rootElement: HTMLElement | null = document.getElementById("root");
if (!rootElement) {
  throw new Error("Root element not found");
}

// Runs once Auth0 has redirected back and the authorisation code has been
// exchanged. Replacing the SDK's default means the `?code=&state=` URL is
// cleaned up through the router instead of `window.history`, so React Router's
// idea of the current location stays correct.
function onRedirectCallback(appState?: AppState): void {
  // `replace` so the browser's Back button does not return to the spent callback URL.
  void router.navigate(appState?.returnTo ?? "/", { replace: true });
}

createRoot(rootElement).render(
  <StrictMode>
    <Auth0Provider client={auth0Client} onRedirectCallback={onRedirectCallback}>
      <QueryClientProvider client={queryClient}>
        <RouterProvider router={router} />
      </QueryClientProvider>
    </Auth0Provider>
  </StrictMode>,
);
