import { afterEach, describe, expect, it, vi } from "vitest";
import { apiPath, basePath } from "./base";
afterEach(() => vi.unstubAllGlobals());
describe("runtime deployment prefix", () => {
  it("supports root without a DOM", () => {
    expect(basePath()).toBe("");
    expect(apiPath("/session")).toBe("/api/session");
  });
  it("uses the server-injected base for API and router history", () => {
    vi.stubGlobal("document", {
      querySelector: () => ({ getAttribute: () => "/apps/console/" }),
    });
    expect(basePath()).toBe("/apps/console");
    expect(apiPath("/media")).toBe("/apps/console/api/media");
  });
});
