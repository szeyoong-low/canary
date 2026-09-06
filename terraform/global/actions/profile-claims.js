/**
 * Runs after a successful login, before the tokens are signed.
 * Copies the profile fields the backend needs onto the access token, otherwise
 * the backend sees only `sub`
 * 
 * Deployed by Terraform. Edits in the Auth0 dashboard will be overwritten on next apply.
 */

// Custom claims should be namespaced with a URL.
// https://auth0.com/docs/secure/tokens/json-web-tokens/create-custom-claims
// Must stay in step with the backend, which reads claims by this exact string.
const NAMESPACE = "https://canary.markets";

// http://auth0.com/docs/customize/actions/actions-overview
exports.onExecutePostLogin = async (event, api) => {
  if (event.user.name) {
    api.accessToken.setCustomClaim(`${NAMESPACE}/name`, event.user.name);
  }

  if (event.user.email) {
    api.accessToken.setCustomClaim(`${NAMESPACE}/email`, event.user.email);
  }
};
