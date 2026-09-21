/**
 * Colour theme — applied as a class on <html>.
 *
 *   auto  → (no class)        follows the OS via the prefers-color-scheme block in index.css
 *   light → "light"           opts out of OS-dark (:root:not(.light))
 *   dark  → "dark"            explicit dark tokens
 *   warm  → "light warm"      warm neutral surfaces; "light" guarantees warm never mixes with dark tokens
 *
 * The chosen value is cached in localStorage ("ecc-theme") so the very first paint uses it;
 * the source of truth is ExecCommandCenter/settings.json on the user's OneDrive (see brief-store).
 */
export type Theme = "auto" | "light" | "dark" | "warm";
export const THEMES: Theme[] = ["auto", "light", "dark", "warm"];
export const DEFAULT_THEME: Theme = "auto";
const CACHE_KEY = "ecc-theme";

export function isTheme(v: unknown): v is Theme { return typeof v === "string" && (THEMES as string[]).includes(v); }

export function applyTheme(t: Theme): void {
  if (typeof document === "undefined") return;
  const cl = document.documentElement.classList;
  cl.remove("light", "dark", "warm");
  if (t === "light") cl.add("light");
  else if (t === "dark") cl.add("dark");
  else if (t === "warm") cl.add("light", "warm");
}

export function readCachedTheme(): Theme {
  try { const v = localStorage.getItem(CACHE_KEY); return isTheme(v) ? v : DEFAULT_THEME; } catch { return DEFAULT_THEME; }
}

export function writeCachedTheme(t: Theme): void {
  try { localStorage.setItem(CACHE_KEY, t); } catch { /* storage unavailable — theme still applied for this session */ }
}
