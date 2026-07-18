import { describe, expect, it, vi } from "vitest";

import { getConfig, getOpsStatus } from "./api";

describe("management api client paths", () => {
  it("uses relative /api paths by default", async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      expect(url.startsWith("/api/")).toBe(true);
      expect(url.includes("localhost")).toBe(false);
      expect(url.includes("127.0.0.1")).toBe(false);
      return Response.json({ ok: true });
    });
    vi.stubGlobal("fetch", fetchMock);

    await getConfig();
    await getOpsStatus();

    expect(fetchMock).toHaveBeenCalledWith("/api/config", undefined);
    expect(fetchMock).toHaveBeenCalledWith("/api/ops/status", undefined);
    vi.unstubAllGlobals();
  });
});
