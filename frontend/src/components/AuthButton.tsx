import { useAuth0 } from "@auth0/auth0-react";
import { BounceLoader } from "react-spinners";
import { type ClassNameProps } from "@/shared/types";
import { canaryThemeColour } from "@/shared/constants";
import { mergeClassName } from "@/lib/mergeClassName";
import { useErrorToast } from "@/lib/useToast";

export default function AuthButton({ className }: ClassNameProps) {
  const { isLoading, isAuthenticated, error, loginWithRedirect, logout } =
    useAuth0();

  // Hooks cannot run conditionally, so this sits above the early returns below.
  useErrorToast(error, { id: "auth-error", title: "Sign-in failed" });

  const buttonClassName: string = mergeClassName(className, "AuthButton");

  // True while the SDK looks for an existing session on mount, and again while
  // it exchanges the authorisation code after Auth0 redirects back.
  if (isLoading) {
    return (
      <BounceLoader
        color={canaryThemeColour}
        size="1em"
        className={buttonClassName}
        aria-label="Checking your session"
      />
    );
  }

  if (isAuthenticated) {
    return (
      <button
        className={buttonClassName}
        type="button"
        onClick={() => {
          void logout({ logoutParams: { returnTo: window.location.origin } });
        }}
      >
        Sign out
      </button>
    );
  }

  return (
    // Failed login leaves the user logged out, so the button stays
    <button
      className={buttonClassName}
      type="button"
      onClick={() => {
        void loginWithRedirect();
      }}
    >
      Sign in
    </button>
  );
}
