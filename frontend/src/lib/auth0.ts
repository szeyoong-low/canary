// The Auth0 client is created here, outside React, so that the component tree
// and the router's data layer can share one instance.
//
// An Auth0Client is a manager of Auth0 sessions, which the Auth0Provider
// exposes as context through useAuth0. It manages the login exchange with the
// authentication server, caches tokens, and renews them with the refresh token
// (and claims a new one).

import { Auth0Client } from "@auth0/auth0-spa-js";
import { createContext, type RouterContext } from "react-router";
import { auth0Config } from "@/lib/env";

// One instance for the page's lifetime, else a second instance would race the
// first and invalidate refresh tokens it had already rotated.
// https://auth0.com/blog/refresh-tokens-what-are-they-and-when-to-use-them/
export const auth0Client: Auth0Client = new Auth0Client({
  ...auth0Config,
  authorizationParams: {
    ...auth0Config.authorizationParams,
    redirect_uri: window.location.origin,
  },
  // Terraform configures rotating refresh tokens, but the SDK only asks for one
  // when this is set.
  useRefreshTokens: true,
});

// The channel that carries the client to route actions (wired up in
// router.tsx). Actions receive it as an argument instead of importing this
// module, which keeps them callable in a test with a stand-in client.
// No default value: `getContext` always sets one, and an unset read should
// throw rather than silently fall back to an unauthenticated client.
export const auth0ClientContext: RouterContext<Auth0Client> =
  createContext<Auth0Client>();

// Sends the user to the login page, remembering where they were so they can be
// put back there afterwards. `appState` is round-tripped by Auth0 and handed
// back to `onRedirectCallback` (see main.tsx), which does the actual navigating.
export async function loginWithReturn(): Promise<void> {
  await auth0Client.loginWithRedirect({
    appState: {
      returnTo: window.location.pathname + window.location.search,
    },
  });
}
