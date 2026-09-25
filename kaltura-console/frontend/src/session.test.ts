import { beforeEach, describe, it, expect, vi } from "vitest";
import { createPinia, setActivePinia } from "pinia";
import { useSession } from "./session";
import { api, APIError } from "./api";
vi.mock("./api", async (importOriginal) => {
  const actual = await importOriginal<typeof import("./api")>();
  return { ...actual, api: vi.fn() };
});
const payload = {
  user: {
    id: 1,
    name: "Test",
    email: "test@example.test",
    role: "admin" as const,
  },
  csrf: "test-token",
  partner_id: 102,
  version: "test",
};
beforeEach(() => {
  setActivePinia(createPinia());
  vi.mocked(api).mockReset();
});
describe("session store", () => {
  it("restores session and computes role", async () => {
    vi.mocked(api).mockResolvedValue(payload);
    const s = useSession();
    await s.load();
    expect(s.admin).toBe(true);
    expect(s.loaded).toBe(true);
  });
  it("treats 401 as anonymous", async () => {
    vi.mocked(api).mockRejectedValue(new APIError(401, "login"));
    const s = useSession();
    await s.load();
    expect(s.data).toBeNull();
    expect(s.loaded).toBe(true);
  });
  it("reports unexpected failures", async () => {
    vi.mocked(api).mockRejectedValue(new APIError(500, "failure"));
    await expect(useSession().load()).rejects.toThrow("failure");
  });
  it("logs in and revokes on logout", async () => {
    vi.mocked(api)
      .mockResolvedValueOnce(payload)
      .mockResolvedValueOnce(undefined);
    const s = useSession();
    await s.login("test@example.test", "password", true);
    expect(s.data?.csrf).toBe("test-token");
    await s.logout();
    expect(s.data).toBeNull();
    expect(api).toHaveBeenLastCalledWith(
      "/logout",
      "POST",
      undefined,
      "test-token",
    );
  });
});
