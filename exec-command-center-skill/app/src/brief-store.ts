/**
 * Brief + state storage on the user's OneDrive (folder /ExecCommandCenter).
 *
 *  - latest.json           — today's brief, written by the daily Cowork run (read-only here)
 *  - state-YYYY-MM-DD.json — the user's actions for that brief (written by this app)
 *
 * All calls run under the signed-in user's OneDrive connection.
 */
// MOCK-UP PHASE: typed stand-ins. Build phase: repoint both to "../../generated/services/*" and delete mock-connectors.ts.
import { OneDriveforBusinessService, Office365UsersService } from "./mock-connectors";
import type { Brief, MeetingBrief } from "@/types/brief";
import { DEFAULT_THEME, isTheme, readCachedTheme, writeCachedTheme, type Theme } from "@/lib/theme";

export const FOLDER = "ExecCommandCenter";

/**
 * MOCK_MODE — the install flow's mock-up phase. When true the app keeps actions in memory and
 * never touches OneDrive or the directory. Flipped to false at build phase: the app now reads
 * the live brief from OneDrive and the live roster from the directory.
 */
export const MOCK_MODE = false;
const BRIEF_PATH = `${FOLDER}/latest.json`;

export type LedgerStatus = "overdue" | "open" | "waiting" | "closed";

export interface ActionEntry {
  ts: string;                 // ISO timestamp
  itemType: "decision" | "hygiene" | "ledger" | "meeting" | "system";
  itemId: string;
  action: string;             // taken / untaken / done / undone / status
  value?: string;
  target: "none" | "planner" | "outlook" | "teams";
  result: "ok" | "error";
  note?: string;
}

export interface BriefState {
  briefDate: string;
  decisionsDone: string[];
  hygieneDone: string[];
  meetingsPrepared: string[];
  ledgerOverrides: Record<string, LedgerStatus>;
  log: ActionEntry[];
}

export const emptyState = (date: string): BriefState => ({
  briefDate: date, decisionsDone: [], hygieneDone: [], meetingsPrepared: [], ledgerOverrides: {}, log: [],
});

export class StoreError extends Error {}

/**
 * Connector file-content responses arrive in one of several shapes:
 *  - a plain JSON string
 *  - an already-parsed object
 *  - a Power Platform content envelope { "$content-type": "...", "$content": "<base64>" }
 *  - a data: URL or base64 string
 * Normalise all of them to the parsed document.
 */
function decodeBase64Utf8(b64: string): string {
  const bin = atob(b64.replace(/\s/g, ""));
  const bytes = Uint8Array.from(bin, (c) => c.charCodeAt(0));
  return new TextDecoder("utf-8").decode(bytes);
}

function parseJson<T>(raw: unknown): T {
  if (raw == null) throw new StoreError("empty content");
  if (raw instanceof ArrayBuffer) return parseJson<T>(new TextDecoder("utf-8").decode(new Uint8Array(raw)));
  if (raw instanceof Uint8Array) return parseJson<T>(new TextDecoder("utf-8").decode(raw));
  if (typeof raw === "object") {
    const env = raw as Record<string, unknown>;
    // Byte array serialised as an object/array of numbers: {"0":123,"1":10,...} or [123,10,...]
    const keys = Object.keys(env);
    if (keys.length > 0 && keys.every((k, i) => k === String(i)) && typeof env["0"] === "number") {
      const bytes = Uint8Array.from(keys.map((k) => env[k] as number));
      return parseJson<T>(new TextDecoder("utf-8").decode(bytes));
    }
    if (typeof env["$content"] === "string") return parseJson<T>(env["$content"]);
    if (typeof env["content"] === "string") return parseJson<T>(env["content"]);
    return raw as T;
  }
  if (typeof raw === "string") {
    const text = raw.trim();
    if (text.startsWith("{") || text.startsWith("[")) return JSON.parse(text) as T;
    if (text.startsWith("data:")) {
      const comma = text.indexOf(",");
      return parseJson<T>(decodeBase64Utf8(text.slice(comma + 1)));
    }
    // bare base64
    try { return parseJson<T>(decodeBase64Utf8(text)); } catch { /* fall through */ }
    return JSON.parse(text) as T;
  }
  throw new StoreError("unsupported content");
}

function assertBrief(b: unknown): Brief {
  const x = b as Partial<Brief> | null;
  if (!x || typeof x !== "object" || !x.meta || typeof x.meta.date !== "string" || !Array.isArray(x.kpis) || !x.calendar) {
    console.error("brief has unexpected shape", b);
    throw new StoreError("shape");
  }
  return {
    ...x,
    decisions: x.decisions ?? [], risks: x.risks ?? [], ledger: x.ledger ?? [], hygiene: x.hygiene ?? [], people: x.people ?? [],
    inbox: x.inbox ?? { reply: [], fyi: [] }, risksNote: x.risksNote ?? "",
  } as Brief;
}

export async function loadBrief(): Promise<Brief> {
  if (MOCK_MODE) throw new StoreError("mock brief removed — MOCK_MODE is off in the built app");
  const r = await OneDriveforBusinessService.GetFileContentByPath(BRIEF_PATH, true);
  if (!r.success) { console.error("brief load failed", r.error); throw new StoreError("brief"); }
  try {
    return assertBrief(parseJson<unknown>(r.data));
  } catch (e) {
    const d: unknown = r.data;
    const preview = typeof d === "string" ? d.slice(0, 300) : d && typeof d === "object" ? JSON.stringify(d).slice(0, 300) : String(d);
    console.error("brief parse failed", typeof d, preview, e instanceof Error ? e.message : e);
    throw e;
  }
}

export interface LoadedState { state: BriefState; fileId: string | null }

export async function loadState(date: string): Promise<LoadedState> {
  if (MOCK_MODE) return { state: emptyState(date), fileId: null };
  const path = `${FOLDER}/state-${date}.json`;
  const meta = await OneDriveforBusinessService.GetFileMetadataByPath(path);
  if (!meta.success || !meta.data?.Id) {
    // No state yet for this brief — a normal first-open condition.
    return { state: emptyState(date), fileId: null };
  }
  const r = await OneDriveforBusinessService.GetFileContent(meta.data.Id, true);
  if (!r.success) { console.error("state load failed", r.error); throw new StoreError("state"); }
  try {
    return { state: { ...emptyState(date), ...parseJson<BriefState>(r.data) }, fileId: meta.data.Id };
  } catch {
    return { state: emptyState(date), fileId: meta.data.Id };
  }
}

export async function saveState(state: BriefState, fileId: string | null): Promise<string> {
  if (MOCK_MODE) return "mock";
  const body = JSON.stringify(state, null, 2);
  if (fileId) {
    const r = await OneDriveforBusinessService.UpdateFile(fileId, body);
    if (!r.success) { console.error("state save failed", r.error); throw new StoreError("save"); }
    return r.data?.Id ?? fileId;
  }
  const r = await OneDriveforBusinessService.CreateFile(FOLDER, `state-${state.briefDate}.json`, body);
  if (!r.success || !r.data?.Id) { console.error("state create failed", r.error); throw new StoreError("create"); }
  return r.data.Id;
}

/* ------------------------------------------------------------------ */
/* User settings — ONE file, ExecCommandCenter/settings.json            */
/* Written only by this app (theme choice). The daily run never touches */
/* it. In MOCK_MODE the app uses localStorage only.                      */
/* ------------------------------------------------------------------ */

export interface Settings { schemaVersion: 1; theme: Theme }
export const defaultSettings = (): Settings => ({ schemaVersion: 1, theme: DEFAULT_THEME });
const SETTINGS_NAME = "settings.json";
const SETTINGS_PATH = `${FOLDER}/${SETTINGS_NAME}`;
let settingsFileId: string | null = null;

export async function loadSettings(): Promise<Settings> {
  if (MOCK_MODE) return { ...defaultSettings(), theme: readCachedTheme() };
  const meta = await OneDriveforBusinessService.GetFileMetadataByPath(SETTINGS_PATH);
  if (!meta.success || !meta.data?.Id) return defaultSettings();          // missing file → defaults
  settingsFileId = meta.data.Id;
  const r = await OneDriveforBusinessService.GetFileContent(meta.data.Id, true);
  if (!r.success) { console.error("settings load failed", r.error); throw new StoreError("settings"); }
  try {
    const parsed = parseJson<Partial<Settings>>(r.data);
    return { ...defaultSettings(), ...(isTheme(parsed.theme) ? { theme: parsed.theme } : {}) };
  } catch { return defaultSettings(); }
}

export async function saveSettings(partial: Partial<Omit<Settings, "schemaVersion">>): Promise<Settings> {
  const current = MOCK_MODE ? { ...defaultSettings(), theme: readCachedTheme() } : await loadSettings().catch(() => defaultSettings());
  const next: Settings = { ...current, ...partial, schemaVersion: 1 };
  if (isTheme(next.theme)) writeCachedTheme(next.theme);
  if (MOCK_MODE) return next;
  const body = JSON.stringify(next, null, 2);
  if (settingsFileId) {
    const r = await OneDriveforBusinessService.UpdateFile(settingsFileId, body);
    if (!r.success) { console.error("settings save failed", r.error); throw new StoreError("settings-save"); }
    settingsFileId = r.data?.Id ?? settingsFileId;
    return next;
  }
  const r = await OneDriveforBusinessService.CreateFile(FOLDER, SETTINGS_NAME, body);
  if (!r.success || !r.data?.Id) { console.error("settings create failed", r.error); throw new StoreError("settings-create"); }
  settingsFileId = r.data.Id;
  return next;
}

/* ------------------------------------------------------------------ */
/* Live directory roster (Office 365 Users) — direct reports           */
/* ------------------------------------------------------------------ */

export interface RosterEntry { id: string; upn: string; name: string; title: string; mail: string }

/** Signed-in user's own profile (for the greeting). Returns null in MOCK_MODE. */
export interface MyProfile { givenName: string; displayName: string }
export async function loadMyProfile(): Promise<MyProfile | null> {
  if (MOCK_MODE) return null;
  const me = await Office365UsersService.MyProfile_V2("givenName,displayName");
  if (!me.success || !me.data) { console.error("my profile load failed", me.error); throw new StoreError("profile"); }
  return { givenName: me.data.givenName ?? "", displayName: me.data.displayName ?? "" };
}

export async function loadDirectReports(): Promise<RosterEntry[]> {
  if (MOCK_MODE) return [];
  const me = await Office365UsersService.MyProfile_V2("id,mail,userPrincipalName");
  if (!me.success || !me.data?.id) { console.error("profile load failed", me.error); throw new StoreError("profile"); }
  const r = await Office365UsersService.DirectReports_V2(me.data.id, "id,displayName,jobTitle,mail,userPrincipalName", 50);
  if (!r.success) { console.error("direct reports load failed", r.error); throw new StoreError("reports"); }
  const rows = r.data?.value ?? [];                     // wrapper shape: { value: GraphUser_V1[] }
  return rows.map((u) => ({
    id: u.id ?? "",
    upn: (u.userPrincipalName ?? u.mail ?? "").toLowerCase(),
    name: u.displayName ?? "",
    title: u.jobTitle ?? "",
    mail: u.mail ?? "",
  })).filter((u) => u.id);
}

/* ------------------------------------------------------------------ */
/* On-demand meeting brief: app writes a request; Cowork writes reply   */
/* ------------------------------------------------------------------ */

const REQUESTS = `${FOLDER}/requests`;
const BRIEFS = `${FOLDER}/briefs`;

export async function requestMeetingBrief(briefDate: string, eventId: string, title: string, start: string, end: string): Promise<void> {
  if (MOCK_MODE) return;
  const body = JSON.stringify({ requestedAt: new Date().toISOString(), briefDate, eventId, title, start, end, type: "meeting-brief" }, null, 2);
  const r = await OneDriveforBusinessService.CreateFile(REQUESTS, `brief-${briefDate}-${eventId}.json`, body);
  if (!r.success) { console.error("brief request failed", r.error); throw new StoreError("request"); }
}

/** Returns the brief if Cowork has written it yet, otherwise null (not an error). */
export async function fetchMeetingBrief(briefDate: string, eventId: string): Promise<MeetingBrief | null> {
  if (MOCK_MODE) return null;
  const path = `${BRIEFS}/${briefDate}-${eventId}.json`;
  const meta = await OneDriveforBusinessService.GetFileMetadataByPath(path);
  if (!meta.success || !meta.data?.Id) return null;
  const r = await OneDriveforBusinessService.GetFileContent(meta.data.Id, true);
  if (!r.success) return null;
  try { return parseJson<MeetingBrief>(r.data); } catch { return null; }
}
