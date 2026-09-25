import { describe, it, expect } from "vitest";
import { safeReturn, duration } from "./api";
describe("safe return URL", () => {
  it.each(["https://evil.test", "//evil.test", "/\\evil.test", "/login", null])(
    "rejects %s",
    (url) => expect(safeReturn(url)).toBe("/dashboard"),
  );
  it("preserves local media target", () =>
    expect(safeReturn("/media/0_abcdefgh?q=x")).toBe("/media/0_abcdefgh?q=x"));
});
it("formats duration", () => expect(duration(125)).toBe("2:05"));
