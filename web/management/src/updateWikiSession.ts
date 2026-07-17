const STORAGE_KEY = "update-wiki-active-run-id";

export function readStoredUpdateWikiRunId(): string | null {
  try {
    return sessionStorage.getItem(STORAGE_KEY);
  } catch {
    return null;
  }
}

export function writeStoredUpdateWikiRunId(runId: string): void {
  try {
    sessionStorage.setItem(STORAGE_KEY, runId);
  } catch {
    // Ignore storage failures in restricted browser contexts.
  }
}

export function clearStoredUpdateWikiRunId(): void {
  try {
    sessionStorage.removeItem(STORAGE_KEY);
  } catch {
    // Ignore storage failures in restricted browser contexts.
  }
}
