export interface ClassNameProps {
  className?: string;
}

// Carries the HTTP status so callers can tell a permanent failure (403, 404)
// from a transient one. The cache's retry policy reads `status` off this.
export class APIError extends Error {
  readonly status: number;

  constructor(response: Response) {
    super(`Error ${String(response.status)}: ${response.statusText}`);
    this.name = "APIError";
    this.status = response.status;
  }
}
