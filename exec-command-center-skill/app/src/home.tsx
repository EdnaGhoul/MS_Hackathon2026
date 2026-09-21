import { useEffect, useMemo, useRef, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { ExternalLink, RefreshCw, FileText, Users, Copy, Check, Monitor, Sun, Moon, Coffee } from "lucide-react";
import type { Brief, Status, Evidence, EventKind, TeamSignal } from "@/types/brief";
import {
  loadBrief, loadState, saveState, emptyState, loadDirectReports, loadMyProfile, loadSettings, saveSettings, MOCK_MODE,
  type BriefState, type LedgerStatus, type ActionEntry, type RosterEntry,
} from "@/lib/brief-store";
import { MeetingBriefPanel } from "@/components/meeting-brief-panel";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Textarea } from "@/components/ui/textarea";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group";
import { applyTheme, readCachedTheme, writeCachedTheme, isTheme, type Theme } from "@/lib/theme";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

/* ------------------------------------------------------------------ */
/* Types & data                                                        */
/* ------------------------------------------------------------------ */


/* Status = colour + shape + word (WCAG 2.2 SC 1.4.1: never colour alone). */
const STATUS: Record<Status, { glyph: string; word: string; cls: string; bar: string }> = {
  red:   { glyph: "▲", word: "RED",     cls: "border-red-700 text-red-800 bg-red-50 dark:text-red-200 dark:bg-red-950/40 dark:border-red-400",           bar: "border-l-red-700 dark:border-l-red-400" },
  amber: { glyph: "◆", word: "AMBER",   cls: "border-amber-800 text-amber-900 bg-amber-50 dark:text-amber-200 dark:bg-amber-950/40 dark:border-amber-400", bar: "border-l-amber-700 dark:border-l-amber-400" },
  green: { glyph: "●", word: "GREEN",   cls: "border-emerald-800 text-emerald-900 bg-emerald-50 dark:text-emerald-200 dark:bg-emerald-950/40 dark:border-emerald-400", bar: "border-l-emerald-700 dark:border-l-emerald-400" },
  grey:  { glyph: "■", word: "CONTEXT", cls: "border-border text-muted-foreground bg-muted", bar: "border-l-border" },
};

const EVIDENCE: Record<Evidence, { glyph: string; word: string; title: string }> = {
  verified: { glyph: "✔", word: "Verified", title: "Quoted and linked to a source" },
  inferred: { glyph: "~", word: "Inferred", title: "Pattern without direct proof" },
  estimate: { glyph: "≈", word: "Estimate", title: "Range or projection" },
};

const LEDGER: Record<LedgerStatus, { status: Status; word: string }> = {
  overdue: { status: "amber", word: "OVERDUE" },
  open:    { status: "amber", word: "OPEN" },
  waiting: { status: "grey",  word: "WAITING" },
  closed:  { status: "green", word: "CLOSED" },
};
const LEDGER_CYCLE: LedgerStatus[] = ["open", "waiting", "closed", "overdue"];

/* ------------------------------------------------------------------ */
/* Small presentational pieces                                         */
/* ------------------------------------------------------------------ */

function StatusPill({ status, word, count }: { status: Status; word?: string; count?: number | string }) {
  const s = STATUS[status];
  return (
    <span className={`inline-flex items-center gap-1.5 rounded-sm border px-2 py-0.5 text-[11px] font-bold tracking-wide ${s.cls}`}>
      <span aria-hidden="true">{s.glyph}</span>
      <span>{count !== undefined ? `${count} ` : ""}{word ?? s.word}</span>
    </span>
  );
}

function EvidenceTag({ kind }: { kind: Evidence }) {
  const e = EVIDENCE[kind];
  return (
    <span
      title={e.title}
      className={`inline-flex items-center gap-1 rounded-sm border px-1.5 py-0.5 text-[11px] font-semibold ${
        kind === "verified" ? "border-border text-foreground" : "border-dashed border-border text-muted-foreground"
      }`}
    >
      <span aria-hidden="true">{e.glyph}</span>
      {e.word}
    </span>
  );
}

function SectionHeading({ n, kicker, answer, children }: { n: number; kicker: string; answer: string; children?: React.ReactNode }) {
  return (
    <div className="flex items-start gap-3">
      <span aria-hidden="true" className="mt-0.5 inline-flex size-6 shrink-0 items-center justify-center rounded-sm bg-primary/10 text-xs font-bold text-primary">{n}</span>
      <div className="min-w-0 flex-1 text-left">
        <div className="flex flex-wrap items-center gap-2 text-[11px] font-semibold uppercase tracking-wide text-muted-foreground">
          <span>{kicker}</span>
          {children}
        </div>
        <h2 className="mt-0.5 text-[15px] font-semibold leading-snug">{answer}</h2>
      </div>
    </div>
  );
}

function ExtLink({ href, children }: { href: string; children: React.ReactNode }) {
  return (
    <a href={href} target="_blank" rel="noreferrer" className="inline-flex items-center gap-1 text-primary underline-offset-2 hover:underline">
      {children}
      <ExternalLink className="size-3" aria-hidden="true" />
    </a>
  );
}

/*
 * Copy button. Copy only — never posts or sends.
 *  1. navigator.clipboard.writeText  (denied inside sandboxed preview iframes without clipboard-write)
 *  2. hidden <textarea> + document.execCommand("copy")
 *  3. both failed → popover with the text pre-selected so the user can copy manually.
 * "Copied" is shown only when a path actually succeeded.
 */
type CopyPath = "clipboard" | "execCommand";
/* Preview diagnostics: the dev-server log only forwards console.error, so in DEV we use it for copy tracing. Silent in production. */
const copyTrace = (...a: unknown[]) => { if (import.meta.env.DEV) console.error("[copy]", ...a); };
async function copyText(text: string): Promise<CopyPath | null> {
  if (typeof navigator !== "undefined" && navigator.clipboard?.writeText) {
    try { await navigator.clipboard.writeText(text); return "clipboard"; } catch (e) { copyTrace("clipboard API denied, trying execCommand:", e instanceof Error ? e.message : e); }
  }
  try {
    const ta = document.createElement("textarea");
    ta.value = text;
    ta.setAttribute("readonly", "");
    ta.style.position = "fixed"; ta.style.top = "0"; ta.style.left = "0"; ta.style.opacity = "0"; ta.style.pointerEvents = "none";
    document.body.appendChild(ta);
    ta.focus(); ta.select(); ta.setSelectionRange(0, text.length);
    const ok = document.execCommand("copy");
    document.body.removeChild(ta);
    if (ok) return "execCommand";
    copyTrace("execCommand('copy') returned false");
  } catch (e) { copyTrace("execCommand path threw:", e instanceof Error ? e.message : e); }
  return null;
}

function CopyButton({ text, label }: { text: string; label: string }) {
  const [copied, setCopied] = useState(false);
  const [manual, setManual] = useState(false);
  const taRef = useRef<HTMLTextAreaElement>(null);
  useEffect(() => { copyTrace("CopyButton mounted"); }, []);
  useEffect(() => {
    if (!copied) return;
    const t = setTimeout(() => setCopied(false), 2000);
    return () => clearTimeout(t);
  }, [copied]);
  useEffect(() => {
    if (!manual) return;
    const t = setTimeout(() => { taRef.current?.focus(); taRef.current?.select(); }, 50);
    return () => clearTimeout(t);
  }, [manual]);
  const onCopy = async () => {
    const path = await copyText(text);
    if (path) { copyTrace(`succeeded via ${path}`); setCopied(true); setManual(false); }
    else { copyTrace("all paths failed — opening manual copy popover"); setManual(true); }
  };
  return (
    <Popover open={manual} onOpenChange={setManual}>
      <PopoverTrigger asChild>
        <Button type="button" variant="outline" size="sm" className="h-7 rounded-sm px-2 text-xs" onClick={(e) => { e.preventDefault(); void onCopy(); }} aria-live="polite">
          {copied ? <Check className="mr-1 size-3.5" aria-hidden="true" /> : <Copy className="mr-1 size-3.5" aria-hidden="true" />}
          {copied ? "Copied" : label}
        </Button>
      </PopoverTrigger>
      <PopoverContent align="start" className="w-80 rounded-md p-3">
        <p className="text-sm font-semibold">Suggested reply</p>
        <p className="mt-0.5 text-xs text-muted-foreground">Copying is blocked in this preview — select and copy manually.</p>
        <Textarea ref={taRef} readOnly value={text} rows={5} onFocus={(e) => e.currentTarget.select()} className="mt-2 rounded-sm text-sm" aria-label="Suggested reply text" />
      </PopoverContent>
    </Popover>
  );
}

/* Colour theme segmented control — Auto · Light · Dark · Warm. */
const THEME_OPTIONS: { value: Theme; label: string; Icon: typeof Sun }[] = [
  { value: "auto", label: "Auto", Icon: Monitor },
  { value: "light", label: "Light", Icon: Sun },
  { value: "dark", label: "Dark", Icon: Moon },
  { value: "warm", label: "Warm", Icon: Coffee },
];
function ThemeSwitch({ value, onChange }: { value: Theme; onChange: (t: Theme) => void }) {
  return (
    <ToggleGroup type="single" size="sm" variant="outline" value={value} onValueChange={(v) => { if (isTheme(v)) onChange(v); }} aria-label="Colour theme" className="rounded-sm">
      {THEME_OPTIONS.map(({ value: v, label, Icon }) => (
        <ToggleGroupItem key={v} value={v} aria-label={label} title={v === "auto" ? "Follow device" : label} className="h-8 gap-1 px-2 text-xs">
          <Icon className="size-3.5" aria-hidden="true" />
          <span className="hidden sm:inline">{label}</span>
        </ToggleGroupItem>
      ))}
    </ToggleGroup>
  );
}

/* ------------------------------------------------------------------ */
/* Persistence — state file on OneDrive, debounced save                */
/* ------------------------------------------------------------------ */

type SaveStatus = "idle" | "saving" | "saved" | "error";

function useBriefState(date: string, initial: BriefState, initialFileId: string | null) {
  const [state, setState] = useState<BriefState>(initial);
  const [saveStatus, setSaveStatus] = useState<SaveStatus>("idle");
  const fileId = useRef<string | null>(initialFileId);
  const dirty = useRef(false);
  const timer = useRef<number | null>(null);

  const update = (fn: (s: BriefState) => BriefState) => {
    dirty.current = true;
    setState((s) => fn(s));
  };

  useEffect(() => {
    if (!dirty.current) return;
    if (timer.current) window.clearTimeout(timer.current);
    timer.current = window.setTimeout(async () => {
      setSaveStatus("saving");
      try {
        fileId.current = await saveState(state, fileId.current);
        dirty.current = false;
        setSaveStatus("saved");
      } catch {
        setSaveStatus("error");
      }
    }, 800);
    return () => { if (timer.current) window.clearTimeout(timer.current); };
  }, [state]);

  return { state, update, saveStatus, setSaveStatus };
}

const nowIso = () => new Date().toISOString();
const entry = (e: Omit<ActionEntry, "ts" | "target" | "result">): ActionEntry => ({ ts: nowIso(), target: "none", result: "ok", ...e });

/* ------------------------------------------------------------------ */
/* Day timeline — the visual-first surface                             */
/* ------------------------------------------------------------------ */

const KIND_LABEL: Record<EventKind, string> = {
  accepted: "Accepted", customer: "Customer / partner", optional: "Optional", block: "Your block", personal: "Personal",
};
const KIND_FILL: Record<EventKind, string> = {
  accepted: "fill-primary/80", customer: "fill-amber-600", optional: "fill-muted-foreground/35", block: "fill-muted-foreground/60", personal: "fill-muted-foreground/60",
};
const KIND_PATTERN: Record<EventKind, boolean> = { accepted: false, customer: false, optional: true, block: false, personal: false };

function toHours(t: string) { const [h, m] = t.split(":").map(Number); return h + m / 60; }
/* Personal events are shown as a masked slot only — never their title or note. */
function displayTitle(ev: { title: string; kind: EventKind | string }) { return ev.kind === "personal" ? "Personal" : ev.title; }
function displayNote(ev: { note: string; kind: EventKind | string }) { return ev.kind === "personal" ? "" : ev.note; }
/* All-day: 00:00–00:00 / 00:00–23:59 / 00:00–24:00, or zero-length. Not plotted as a bar. */
function isAllDay(ev: { start: string; end: string }) {
  return ev.start === ev.end || (ev.start === "00:00" && (ev.end === "00:00" || ev.end === "23:59" || ev.end === "24:00"));
}

/*
 * Published-threshold parser. Format: segments separated by "·", each
 *   WORD <op> <number>   (ops ≥ >= ≤ <= < >)
 *   WORD <a>–<b>         (range, en-dash or hyphen, inclusive)
 *   WORD <number>        (equality)
 * WORD is RED / AMBER / GREEN; trailing words ("with conflict", "h") are ignored.
 * Returns null when nothing parses — callers keep the morning status in that case.
 *   "RED ≥ 3 · AMBER 1–2 · GREEN 0":  0→green, 1→amber, 2→amber, 3→red, 7→red
 *   "RED ≥ 4 · AMBER 1–3 · GREEN 0":  0→green, 1→amber, 3→amber, 4→red
 */
function statusFromThreshold(threshold: string, value: number): Status | null {
  const rules: { status: Status; test: (v: number) => boolean }[] = [];
  for (const raw of threshold.split("·")) {
    const m = raw.trim().match(/^(RED|AMBER|GREEN)\s*(?:(≥|>=|≤|<=|<|>)\s*(-?\d+(?:\.\d+)?)|(-?\d+(?:\.\d+)?)\s*[–-]\s*(-?\d+(?:\.\d+)?)|(-?\d+(?:\.\d+)?))/i);
    if (!m) continue;
    const status = m[1].toLowerCase() as Status;
    if (m[2]) {
      const n = Number(m[3]);
      const op = m[2];
      rules.push({ status, test: (v) => op === "≥" || op === ">=" ? v >= n : op === "≤" || op === "<=" ? v <= n : op === "<" ? v < n : v > n });
    } else if (m[4] !== undefined) {
      const a = Number(m[4]), b = Number(m[5]);
      rules.push({ status, test: (v) => v >= Math.min(a, b) && v <= Math.max(a, b) });
    } else {
      const n = Number(m[6]);
      rules.push({ status, test: (v) => v === n });
    }
  }
  if (rules.length === 0) return null;
  // Evaluate in published order (RED first) so the most severe matching band wins.
  return rules.find((r) => r.test(value))?.status ?? null;
}

function DayTimeline({ data, prepared, onOpenBrief }: { data: Brief; prepared: string[]; onOpenBrief: (eventId: string) => void }) {
  const { events } = data.calendar;
  const W = 1000, H = 190, padL = 8, padR = 8, top = 26;

  // Split: all-day → banner; optional → collapsed line; the rest are plotted.
  const allDay = events.filter(isAllDay);
  const optional = events.filter((e) => !isAllDay(e) && e.kind === "optional");
  const plotted = events.filter((e) => !isAllDay(e) && e.kind !== "optional");
  // Window = working hours 08–18, extended outward (to the hour) only by plotted events. dayStart/dayEnd are ignored for display.
  const dayStart = Math.min(8, ...plotted.map((e) => Math.floor(toHours(e.start))));
  const dayEnd = Math.max(18, ...plotted.map((e) => Math.ceil(toHours(e.end))));
  const span = Math.max(1, dayEnd - dayStart);
  const x = (h: number) => padL + ((h - dayStart) / span) * (W - padL - padR);

  // Lane packing: lane 0 = full-day/accepted spine, others stacked by overlap.
  const lanes: { id: string; lane: number }[] = [];
  const laneEnds: number[] = [];
  const sorted = [...plotted].sort((a, b) => toHours(a.start) - toHours(b.start) || toHours(b.end) - toHours(a.end));
  for (const ev of sorted) {
    const s = toHours(ev.start), e = toHours(ev.end);
    let lane = laneEnds.findIndex((end) => end <= s);
    if (lane === -1) { lane = laneEnds.length; laneEnds.push(e); } else laneEnds[lane] = e;
    lanes.push({ id: ev.id, lane });
  }
  const laneH = 34, gap = 6;
  const totalH = top + laneEnds.length * (laneH + gap) + 8;
  const lanePos = (id: string) => lanes.find((l) => l.id === id)?.lane ?? 0;

  const conflicts = useMemo(() => {
    const out: string[] = [];
    for (let i = 0; i < sorted.length; i++) for (let j = i + 1; j < sorted.length; j++) {
      const a = sorted[i], b = sorted[j];
      if (a.kind === "optional" || b.kind === "optional") continue;
      if (toHours(a.start) < toHours(b.end) && toHours(b.start) < toHours(a.end)) out.push(`${displayTitle(a)} overlaps ${displayTitle(b)}`);
    }
    return out;
  }, [sorted]);

  const hours = Array.from({ length: span + 1 }, (_, i) => dayStart + i);
  const titleId = "day-timeline-title", descId = "day-timeline-desc";

  return (
    <figure className="m-0">
      <figcaption className="mb-2 flex flex-wrap items-baseline justify-between gap-2 text-sm">
        <span className="font-medium">Today, {String(dayStart).padStart(2, "0")}:00 – {String(dayEnd).padStart(2, "0")}:00 — accepted time is the spine; customer calls sit above it.</span>
        <span className="text-xs text-muted-foreground">{conflicts.length} conflict{conflicts.length === 1 ? "" : "s"} · {events.filter((e) => e.kind === "customer").length} customer-facing · {events.length} events in total</span>
      </figcaption>
      {allDay.length > 0 && (
        <p className="mb-2 rounded-sm border border-border bg-muted/40 px-3 py-1.5 text-xs">
          <span className="font-semibold">All day:</span> {allDay.map(displayTitle).join(" · ")}
        </p>
      )}
      {optional.length > 0 && (
        <p className="mb-2 text-xs text-muted-foreground">
          {optional.length} optional broadcast{optional.length === 1 ? "" : "s"} —{" "}
          {optional.map((ev, i) => (
            <span key={ev.id}>
              {i > 0 && ", "}
              <button type="button" onClick={() => onOpenBrief(ev.id)} className="underline-offset-2 hover:underline focus-visible:outline-solid focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring" aria-label={`Open meeting brief for ${displayTitle(ev)}`} title={displayTitle(ev)}>
                {displayTitle(ev).length > 40 ? displayTitle(ev).slice(0, 39) + "…" : displayTitle(ev)}
              </button>
            </span>
          ))}
        </p>
      )}
      <svg viewBox={`0 0 ${W} ${Math.max(H, totalH)}`} role="img" aria-labelledby={`${titleId} ${descId}`} className="h-auto w-full">
        <title id={titleId}>Timeline of today's calendar</title>
        <desc id={descId}>
          {events.map((e) => `${displayTitle(e)} ${e.start}–${e.end} (${KIND_LABEL[e.kind as EventKind]})`).join("; ")}.
          {conflicts.length ? ` Conflicts: ${conflicts.join("; ")}.` : " No conflicts."}
        </desc>
        <defs>
          <pattern id="hatch" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
            <rect width="6" height="6" className="fill-muted" />
            <line x1="0" y1="0" x2="0" y2="6" className="stroke-muted-foreground/60" strokeWidth="2" />
          </pattern>
        </defs>
        {hours.map((h) => (
          <g key={h}>
            <line x1={x(h)} x2={x(h)} y1={top - 6} y2={totalH} className="stroke-border" strokeWidth="1" />
            <text x={x(h) + 3} y={12} className="fill-muted-foreground text-[11px]">{String(h).padStart(2, "0")}:00</text>
          </g>
        ))}
        {sorted.map((ev) => {
          const kind = ev.kind as EventKind;
          const x1 = x(toHours(ev.start)), x2 = x(toHours(ev.end));
          const y = top + lanePos(ev.id) * (laneH + gap);
          const w = Math.max(x2 - x1, 6);
          return (
            <g key={ev.id}>
              <rect x={x1} y={y} width={w} height={laneH} rx={3} className={KIND_PATTERN[kind] ? "" : KIND_FILL[kind]} fill={KIND_PATTERN[kind] ? "url(#hatch)" : undefined} />
              {kind === "customer" && <rect x={x1} y={y} width={4} height={laneH} className="fill-amber-900" />}
              {w > 60 && (
                <text x={x1 + 8} y={y + 21} className={`text-[12px] font-medium ${kind === "accepted" || kind === "customer" ? "fill-white" : "fill-foreground"}`}>
                  {displayTitle(ev).length > (w / 7) ? displayTitle(ev).slice(0, Math.max(3, Math.floor(w / 7) - 1)) + "…" : displayTitle(ev)}
                </text>
              )}
            </g>
          );
        })}
      </svg>
      <ul className="mt-3 divide-y divide-border text-sm">
        {sorted.map((ev) => (
          <li key={ev.id} className="flex flex-wrap items-baseline gap-x-3 gap-y-1 py-1.5">
            <span className="w-28 shrink-0 tabular-nums text-muted-foreground">{ev.start} – {ev.end}</span>
            <span className="font-medium">{displayTitle(ev)}</span>
            <StatusPill status={ev.kind === "customer" ? "amber" : ev.kind === "accepted" ? "green" : "grey"} word={KIND_LABEL[ev.kind as EventKind].toUpperCase()} />
            {ev.kind !== "personal" && (
              <Button variant={ev.brief ? "default" : "outline"} size="sm" className="h-7 rounded-sm px-2 text-xs" onClick={() => onOpenBrief(ev.id)} aria-label={`Open meeting brief for ${ev.title}`}>
                <FileText className="mr-1 size-3.5" aria-hidden="true" />{prepared.includes(ev.id) ? "Brief · prepared ✓" : ev.brief ? "Brief · 1 min" : "Request brief"}
              </Button>
            )}
            {displayNote(ev) && <span className="basis-full text-muted-foreground sm:basis-auto">{displayNote(ev)}</span>}
          </li>
        ))}
      </ul>
    </figure>
  );
}

/* ------------------------------------------------------------------ */
/* Page                                                                */
/* ------------------------------------------------------------------ */

export function HomePage() {
  const briefQ = useQuery({ queryKey: ["ecc-brief"], queryFn: loadBrief, staleTime: 60_000, retry: 1 });
  const date = briefQ.data?.meta.date;
  const stateQ = useQuery({
    queryKey: ["ecc-state", date],
    queryFn: () => loadState(date as string),
    enabled: !!date,
    retry: 1,
  });

  if (briefQ.isPending || (date && stateQ.isPending)) {
    return (
      <div className="mx-auto w-full max-w-6xl px-4 py-10 sm:px-6" role="status" aria-live="polite">
        <p className="text-[11px] font-semibold uppercase tracking-[0.08em] text-muted-foreground">Exec Command Center</p>
        <p className="mt-3 text-lg font-medium">Loading today's brief from your OneDrive…</p>
        <p className="mt-1 text-sm text-muted-foreground">Reading the daily brief written by the 07:30 run.</p>
      </div>
    );
  }
  if (briefQ.isError || !briefQ.data) {
    return (
      <div className="mx-auto w-full max-w-6xl px-4 py-10 sm:px-6" role="alert">
        <p className="text-[11px] font-semibold uppercase tracking-[0.08em] text-muted-foreground">Exec Command Center</p>
        <h1 className="mt-3 text-xl font-semibold">Your first brief isn't here yet</h1>
        <p className="mt-2 max-w-2xl text-sm text-muted-foreground">
          This page reads today's brief from your OneDrive folder. If you have just installed the command center, the first brief is being prepared and will appear when the install run finishes; afterwards it is written every weekday at the scheduled time. If your OneDrive connection needs re-consent, this page stays empty rather than show stale or invented content.
        </p>
        <Button className="mt-4 rounded-sm" onClick={() => briefQ.refetch()}><RefreshCw className="mr-2 size-4" aria-hidden="true" />Try again</Button>
      </div>
    );
  }
  const brief = briefQ.data;
  const loaded = stateQ.data ?? { state: emptyState(brief.meta.date), fileId: null };
  return <Board key={brief.meta.date} data={brief} initialState={loaded.state} initialFileId={loaded.fileId} stateFailed={stateQ.isError} onRefresh={() => { briefQ.refetch(); stateQ.refetch(); }} />;
}

function Board({ data, initialState, initialFileId, stateFailed, onRefresh }: { data: Brief; initialState: BriefState; initialFileId: string | null; stateFailed: boolean; onRefresh: () => void }) {
  const { state: local, update: setLocal, saveStatus, setSaveStatus } = useBriefState(data.meta.date, initialState, initialFileId);
  // Theme: cached value for first paint; OneDrive settings.json is the source of truth once loaded.
  const [theme, setTheme] = useState<Theme>(readCachedTheme);
  const settingsQ = useQuery({ queryKey: ["ecc-settings"], queryFn: loadSettings, staleTime: Infinity, retry: 1 });
  useEffect(() => {
    if (!settingsQ.data) return;
    setTheme(settingsQ.data.theme); applyTheme(settingsQ.data.theme); writeCachedTheme(settingsQ.data.theme);
  }, [settingsQ.data]);
  const changeTheme = async (t: Theme) => {
    setTheme(t); applyTheme(t); writeCachedTheme(t);
    if (MOCK_MODE) return;
    setSaveStatus("saving");
    try { await saveSettings({ theme: t }); setSaveStatus("saved"); } catch { setSaveStatus("error"); }
  };
  const [openBrief, setOpenBrief] = useState<string | null>(null);
  const [openSections, setOpenSections] = useState<string[]>(["decisions", "day", "risks", "ledger"]);
  const goToReplies = () => {
    setOpenSections((s) => (s.includes("inbox") ? s : [...s, "inbox"]));
    window.setTimeout(() => document.getElementById("replies")?.scrollIntoView({ behavior: "smooth", block: "start" }), 60);
  };
  const rosterQ = useQuery({ queryKey: ["ecc-roster"], queryFn: loadDirectReports, staleTime: 15 * 60_000, retry: 1 });
  const profileQ = useQuery({ queryKey: ["ecc-me"], queryFn: loadMyProfile, staleTime: 60 * 60_000, retry: 1 });
  const openEvent = openBrief ? data.calendar.events.find((e) => e.id === openBrief && e.kind !== "personal") : undefined;
  const markPrepared = (id: string, on: boolean) =>
    setLocal((s) => ({ ...s,
      meetingsPrepared: on ? [...new Set([...s.meetingsPrepared, id])] : s.meetingsPrepared.filter((m) => m !== id),
      log: [...s.log, entry({ itemType: "meeting", itemId: id, action: on ? "prepared" : "unprepared" })] }));

  const toggleDecision = (id: string, done: boolean) =>
    setLocal((s) => ({ ...s,
      decisionsDone: done ? [...new Set([...s.decisionsDone, id])] : s.decisionsDone.filter((d) => d !== id),
      log: [...s.log, entry({ itemType: "decision", itemId: id, action: done ? "taken" : "untaken" })] }));
  const toggleHygiene = (id: string, done: boolean) =>
    setLocal((s) => ({ ...s,
      hygieneDone: done ? [...new Set([...s.hygieneDone, id])] : s.hygieneDone.filter((d) => d !== id),
      log: [...s.log, entry({ itemType: "hygiene", itemId: id, action: done ? "done" : "undone" })] }));
  const cycleLedger = (id: string, current: LedgerStatus) => {
    const next = LEDGER_CYCLE[(LEDGER_CYCLE.indexOf(current) + 1) % LEDGER_CYCLE.length];
    setLocal((s) => ({ ...s,
      ledgerOverrides: { ...s.ledgerOverrides, [id]: next },
      log: [...s.log, entry({ itemType: "ledger", itemId: id, action: "status", value: next })] }));
  };

  const decisionsOpen = data.decisions.filter((d) => !local.decisionsDone.includes(d.id));
  const redCount = decisionsOpen.filter((d) => d.status === "red").length;
  const amberCount = decisionsOpen.filter((d) => d.status === "amber").length;

  const ledger = data.ledger.map((l) => ({ ...l, status: (local.ledgerOverrides[l.id] ?? l.status) as LedgerStatus }));
  const ledgerOpen = ledger.filter((l) => l.status === "open" || l.status === "overdue").length;
  const ledgerClosed = ledger.filter((l) => l.status === "closed").length;
  const ledgerWaiting = ledger.filter((l) => l.status === "waiting").length;

  const risksRed = data.risks.filter((r) => r.status === "red").length;
  const risksAmber = data.risks.filter((r) => r.status === "amber").length;
  const risksGreen = data.risks.filter((r) => r.status === "green").length;

  const hygieneDone = data.hygiene.filter((h) => local.hygieneDone.includes(h.id)).length;
  const noFreeDays = [...new Set(data.hygiene.filter((h) => h.dayFlag === "no free block").map((h) => h.day))];

  const briefable = data.calendar.events.filter((e) => e.kind === "customer" || e.kind === "accepted").length;
  const preparedCount = local.meetingsPrepared.length;

  // ---- Section headings: every sentence below is derived from the brief; nothing is fixed copy. ----
  const plural = (n: number, one: string, many = `${one}s`) => (n === 1 ? one : many);

  // 1 Decisions
  const decisionsAnswer = decisionsOpen.length === 0
    ? "All decisions cleared."
    : `${decisionsOpen.length} ${plural(decisionsOpen.length, "decision")} waiting — ${redCount} red, ${amberCount} amber.`;

  // 2 Day ahead — customer calls, accepted, personal (masked), overlaps among non-personal events.
  const events = data.calendar.events;
  const customerEvents = events.filter((e) => e.kind === "customer");
  const acceptedCount = events.filter((e) => e.kind === "accepted").length;
  const personalCount = events.filter((e) => e.kind === "personal").length;
  const publicEvents = events.filter((e) => e.kind !== "personal");
  let conflictCount = 0;
  for (let i = 0; i < publicEvents.length; i++) {
    for (let j = i + 1; j < publicEvents.length; j++) {
      const a = publicEvents[i], b = publicEvents[j];
      if (toHours(a.start) < toHours(b.end) && toHours(b.start) < toHours(a.end)) conflictCount++;
    }
  }
  const customerCount = customerEvents.length;
  const dayAnswer = events.length === 0
    ? "Nothing on your calendar today."
    : [
        customerCount === 0
          ? "No customer or partner calls"
          : `${customerCount} customer/partner ${plural(customerCount, "call")} — first is ${customerEvents[0].title} at ${customerEvents[0].start}`,
        `${acceptedCount} accepted ${plural(acceptedCount, "meeting")}`,
        personalCount > 0 ? `${personalCount} personal ${plural(personalCount, "event")} (kept private)` : null,
        conflictCount === 0 ? "no overlaps" : `${conflictCount} overlapping ${plural(conflictCount, "pair")}`,
      ].filter(Boolean).join("; ") + ".";

  // 3 Risks
  const redRisks = data.risks.filter((r) => r.status === "red");
  const amberRisks = data.risks.filter((r) => r.status === "amber");
  const riskLead = redRisks.length > 0
    ? (redRisks.length === 1
        ? `${redRisks[0].account} is the live risk`
        : `${redRisks.length} live risks — ${redRisks.map((r) => r.account).join(", ")}`)
    : amberRisks.length > 0
      ? `${amberRisks.length} amber ${plural(amberRisks.length, "risk")} — ${amberRisks.map((r) => r.account).join(", ")}`
      : "No red or amber risks";
  const risksAnswer = `${riskLead}${risksGreen > 0 ? `; ${risksGreen} closed` : ""}.${data.risksNote ? ` ${data.risksNote}` : ""}`;

  // Decision ↔ reply cross-link heuristic: the decision mentions the inbox, or a reply row's from/subject shares a ≥6-char word with the title.
  const words = (t: string) => new Set(t.toLowerCase().match(/[\p{L}\d]{6,}/gu) ?? []);
  const replyWords = words(data.inbox.reply.map((r) => `${r.from} ${r.subject}`).join(" "));
  const decisionHasReply = (d: { title: string; ask: string; recommendation: string }) =>
    data.inbox.reply.length > 0 && (/\binbox\b/i.test(`${d.ask} ${d.recommendation}`) || [...words(d.title)].some((w) => replyWords.has(w)));

  // 4 Replies & mentions
  const draftedCount = data.inbox.reply.filter((r) => r.draftUrl).length;
  const inboxAnswer = data.inbox.reply.length === 0 && data.inbox.fyi.length === 0
    ? "No replies or mentions need you."
    : `${data.inbox.reply.length} ${plural(data.inbox.reply.length, "reply", "replies")} owed — ${draftedCount} drafted for you; ${data.inbox.fyi.length} FYI need nothing.`;

  // 5 Ledger — oldest overdue age parsed from the leading number of `age` (e.g. "5 d").
  const overdueAges = ledger
    .filter((l) => l.status === "overdue")
    .map((l) => parseInt(String(l.age).trim(), 10))
    .filter((n) => Number.isFinite(n));
  const overdueCount = ledger.filter((l) => l.status === "overdue").length;
  const oldestOverdue = overdueAges.length > 0 ? Math.max(...overdueAges) : null;
  const ledgerAnswer = ledger.length === 0
    ? "No commitments tracked yet."
    : `${ledgerOpen} of your promises ${ledgerOpen === 1 ? "is" : "are"} still open — ${
        overdueCount === 0 ? "none overdue" : oldestOverdue !== null ? `the oldest is ${oldestOverdue} ${plural(oldestOverdue, "day")} overdue` : `${overdueCount} overdue`
      }; ${ledgerClosed} closed.`;

  // 6 Hygiene — counts per proposal verb, e.g. "3 decline, 2 flag".
  const proposalCounts = [...data.hygiene.reduce((m, h) => m.set(h.proposal, (m.get(h.proposal) ?? 0) + 1), new Map<string, number>())]
    .sort((a, b) => b[1] - a[1])
    .map(([p, n]) => `${n} ${p.toLowerCase()}`);
  const hygieneAnswer = data.hygiene.length === 0
    ? "No calendar proposals for the next 5 working days."
    : `${data.hygiene.length} ${plural(data.hygiene.length, "proposal")}, ${hygieneDone} actioned by you — ${proposalCounts.join(", ")}.`;

  // Team: live roster (direct reports) joined to engagement rows from the brief on UPN.
  const roster: RosterEntry[] = rosterQ.data ?? [];
  const team = data.team;
  const engagementByUpn = new Map((team?.members ?? []).map((m) => [m.upn.toLowerCase(), m]));
  const teamRows = roster.map((r) => ({ roster: r, eng: engagementByUpn.get(r.upn) ?? engagementByUpn.get(r.mail.toLowerCase()) }));
  const SIGNAL: Record<TeamSignal, { status: Status; word: string; rank: number }> = {
    blocked: { status: "red", word: "BLOCKED ON YOU", rank: 0 }, quiet: { status: "amber", word: "QUIET", rank: 1 }, nominal: { status: "green", word: "NOMINAL", rank: 2 },
  };
  teamRows.sort((a, b) => (a.eng ? SIGNAL[a.eng.signal].rank : 3) - (b.eng ? SIGNAL[b.eng.signal].rank : 3));
  const blockedCount = teamRows.filter((t) => t.eng?.signal === "blocked").length;
  const quietCount = teamRows.filter((t) => t.eng?.signal === "quiet").length;
  const fallbackPeople = team?.mode === "frequentContacts" ? team.members : undefined;
  const fbList = fallbackPeople ?? data.people;
  const fbWaiting = fbList.filter((p) => p.waitingOnYou).length;
  const fbYouWait = fbList.filter((p) => p.youWaitOn).length;
  const teamAnswer = rosterQ.isPending ? "Checking your direct reports in the directory…"
    : rosterQ.isError ? "Couldn't read your direct reports from the directory — showing engagement data from the brief only."
    : roster.length === 0 ? `No direct reports in the directory — showing your ${fbList.length} most frequent contacts instead: ${fbWaiting} waiting on you, you are waiting on ${fbYouWait}.`
    : `${roster.length} direct report${roster.length === 1 ? "" : "s"}: ${blockedCount} blocked on you, ${quietCount} gone quiet.`;

  // Greeting: directory givenName → displayName first token → brief owner first token. "Welcome back" while loading.
  const firstToken = (s: string | undefined) => (s ?? "").trim().split(/\s+/)[0] ?? "";
  const firstName = profileQ.isPending
    ? ""
    : firstToken(profileQ.data?.givenName) || firstToken(profileQ.data?.displayName) || firstToken(data.meta.owner);
  const greeting = firstName ? `Welcome back, ${firstName}` : "Welcome back";
  const calendarCount = data.meta.evidenceNote.match(/Calendar: (\d+ of \d+)/)?.[1];
  const metaLine = [data.meta.dayLabel, `Updated ${data.meta.generatedAt}`, calendarCount ? `Calendar ${calendarCount}` : null].filter(Boolean).join(" · ");

  // KPI tiles that react to your actions: decisions (open count) and overdue (effective ledger status).
  const overdueLive = ledger.filter((l) => l.status === "overdue").length;
  const kpis = data.kpis.map((k) => {
    const live = k.id === "decisions" ? decisionsOpen.length : k.id === "overdue" ? overdueLive : null;
    if (live === null) return k;
    return { ...k, value: live, status: statusFromThreshold(k.threshold, live) ?? k.status };
  });

  return (
    <div className="mx-auto w-full max-w-6xl px-4 py-6 sm:px-6">
      <a href="#decisions" className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-50 focus:rounded-sm focus:bg-primary focus:px-3 focus:py-2 focus:text-primary-foreground">
        Skip to decisions
      </a>

      {/* Header — greeting first */}
      <header className="border-b border-border pb-5">
        <p className="text-[11px] font-semibold uppercase tracking-[0.08em] text-muted-foreground">Exec Command Center</p>
        <h1 className="mt-2 text-3xl font-semibold tracking-tight text-foreground sm:text-4xl">{greeting}</h1>
        <p className="mt-2 text-sm text-muted-foreground">{metaLine}</p>
        {MOCK_MODE && (
          <p role="status" className="mt-3 inline-flex items-center gap-2 rounded-sm border border-amber-800 bg-amber-50 px-3 py-1.5 text-xs font-semibold text-amber-900 dark:border-amber-400 dark:bg-amber-950/40 dark:text-amber-200">
            ◆ MOCK-UP — fictional data for layout review. Nothing here is read from your mailbox, calendar or Teams, and actions are not saved.
          </p>
        )}
        <div className="mt-3 flex flex-wrap items-center gap-3 text-xs">
          <Button variant="outline" size="sm" className="rounded-sm" onClick={onRefresh}><RefreshCw className="mr-1.5 size-3.5" aria-hidden="true" />Refresh from OneDrive</Button>
          <ThemeSwitch value={theme} onChange={(t) => { void changeTheme(t); }} />
          <span role="status" aria-live="polite" className="text-muted-foreground">
            {saveStatus === "saving" && "Saving your actions…"}
            {saveStatus === "saved" && "Actions saved to your OneDrive."}
            {saveStatus === "error" && <span className="font-medium text-red-800 dark:text-red-300">▲ Couldn't save your last action — it is kept on screen; try again shortly.</span>}
            {saveStatus === "idle" && (stateFailed ? <span className="font-medium text-amber-900 dark:text-amber-200">◆ Earlier actions for today couldn't be read; starting from a clean slate.</span> : `${local.log.length} action${local.log.length === 1 ? "" : "s"} recorded today.`)}
          </span>
        </div>
        <div className="mt-4 flex flex-wrap items-center gap-x-5 gap-y-2 text-xs text-muted-foreground">
          <span className="font-semibold text-foreground">Legend</span>
          <span className="inline-flex flex-wrap items-center gap-1.5"><StatusPill status="red" /><StatusPill status="amber" /><StatusPill status="green" /><StatusPill status="grey" /></span>
          <span className="inline-flex flex-wrap items-center gap-1.5"><EvidenceTag kind="verified" /><EvidenceTag kind="inferred" /><EvidenceTag kind="estimate" /></span>
          <span>Thresholds are fixed and shown in each tile — not tuned after the fact.</span>
        </div>
      </header>

      {/* Today's answer — full-width callout */}
      <section aria-labelledby="answer-heading" className="mt-6 rounded-md border border-border border-l-4 border-l-primary bg-card p-5">
        <p id="answer-heading" className="text-[11px] font-semibold uppercase tracking-wide text-muted-foreground">Today's answer</p>
        <p className="mt-1.5 text-lg font-medium leading-snug sm:text-xl">{data.meta.governingAnswer}</p>
      </section>

      {/* KPI tiles with spec */}
      <section aria-labelledby="kpi-heading" className="mt-6">
        <h2 id="kpi-heading" className="sr-only">Key indicators</h2>
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {kpis.map((k) => (
            <div key={k.id} className="rounded-md border border-border bg-card p-4">
              <div className="flex items-start justify-between gap-2">
                <span className="text-[11px] font-semibold uppercase tracking-wide text-muted-foreground">{k.label}</span>
                <StatusPill status={k.status as Status} />
              </div>
              <div className="mt-1 flex items-baseline gap-1.5">
                <span className="text-3xl font-semibold tabular-nums tracking-tight">{k.value}</span>
                {k.unit && <span className="text-sm text-muted-foreground">{k.unit}</span>}
                <EvidenceTag kind={k.evidence as Evidence} />
              </div>
              <dl className="mt-3 space-y-1 border-t border-dashed border-border pt-3 text-xs">
                <div className="flex gap-2"><dt className="w-20 shrink-0 text-muted-foreground">Threshold</dt><dd>{k.threshold}</dd></div>
                <div className="flex gap-2"><dt className="w-20 shrink-0 text-muted-foreground">Fires</dt><dd>{k.fires}</dd></div>
                <div className="flex gap-2"><dt className="w-20 shrink-0 text-muted-foreground">Decision</dt><dd>{k.decision}</dd></div>
                <div className="flex gap-2"><dt className="w-20 shrink-0 text-muted-foreground">Trend</dt><dd className="text-muted-foreground">{k.trend}</dd></div>
              </dl>
            </div>
          ))}
        </div>
      </section>

      <Accordion type="multiple" value={openSections} onValueChange={setOpenSections} className="mt-6 space-y-3">

        {/* 1 Decisions */}
        <AccordionItem value="decisions" id="decisions" className="rounded-md border border-border bg-card px-4">
          <AccordionTrigger className="py-4 hover:no-underline">
            <SectionHeading n={1} kicker="Decisions required today" answer={decisionsAnswer}>
              {redCount > 0 && <StatusPill status="red" count={redCount} />}
              {amberCount > 0 && <StatusPill status="amber" count={amberCount} />}
              {local.decisionsDone.length > 0 && <StatusPill status="green" word="DONE" count={local.decisionsDone.length} />}
            </SectionHeading>
          </AccordionTrigger>
          <AccordionContent className="space-y-3 pb-4">
            {data.decisions.map((d, i) => {
              const done = local.decisionsDone.includes(d.id);
              const s = STATUS[d.status as Status];
              return (
                <article key={d.id} className={`rounded-md border border-border border-l-4 bg-background p-4 ${done ? "border-l-emerald-700 opacity-80" : s.bar}`}>
                  <div className="flex flex-wrap items-start gap-3">
                    <label className="mt-0.5 flex items-center gap-2 text-xs font-medium">
                      <Checkbox checked={done} onCheckedChange={(v) => toggleDecision(d.id, v === true)} aria-label={`Mark decision ${i + 1} as taken`} />
                      Taken
                    </label>
                    <div className="min-w-0 flex-1">
                      <h3 className={`text-[15px] font-semibold leading-snug ${done ? "line-through" : ""}`}>
                        <span className="mr-2 text-muted-foreground">{i + 1}.</span>{d.title}
                      </h3>
                      <div className="mt-1 flex flex-wrap items-center gap-1.5">
                        <StatusPill status={done ? "green" : (d.status as Status)} word={done ? "TAKEN" : undefined} />
                        <EvidenceTag kind={d.evidence as Evidence} />
                        <Badge variant="outline" className="rounded-sm text-[11px] font-bold uppercase tracking-wide">{d.verb}</Badge>
                      </div>
                    </div>
                  </div>
                  <dl className="mt-3 grid gap-x-4 gap-y-2 text-sm sm:grid-cols-[130px_1fr]">
                    <dt className="text-muted-foreground">Situation</dt><dd>{d.situation}</dd>
                    <dt className="text-muted-foreground">Complication</dt><dd>{d.complication}</dd>
                    <dt className="font-semibold text-foreground">Why now</dt><dd className="font-medium">{d.whyNow}</dd>
                    <dt className="text-muted-foreground">If nothing changes</dt><dd>{d.ifNothingChanges}</dd>
                    <dt className="text-muted-foreground">Recommendation</dt><dd><span className="font-semibold">{d.verb}:</span> {d.recommendation}</dd>
                    <dt className="text-muted-foreground">Ask</dt>
                    <dd>
                      {d.ask}
                      {(d.links.some((l) => l.url) || decisionHasReply(d)) && (
                        <span className="mt-2 flex flex-wrap gap-2">
                          {d.links.filter((l) => l.url).map((l) => (
                            <Button key={l.url} asChild variant="outline" size="sm" className="h-7 rounded-sm px-2 text-xs">
                              <a href={l.url} target="_blank" rel="noreferrer"><ExternalLink className="mr-1 size-3.5" aria-hidden="true" />{l.label}</a>
                            </Button>
                          ))}
                          {decisionHasReply(d) && (
                            <Button type="button" variant="outline" size="sm" className="h-7 rounded-sm px-2 text-xs" onClick={goToReplies}>Go to replies</Button>
                          )}
                        </span>
                      )}
                    </dd>
                  </dl>
                </article>
              );
            })}
          </AccordionContent>
        </AccordionItem>

        {/* 2 Day ahead — timeline */}
        <AccordionItem value="day" className="rounded-md border border-border bg-card px-4">
          <AccordionTrigger className="py-4 hover:no-underline">
            <SectionHeading n={2} kicker="Day ahead" answer={dayAnswer}>
              {(customerCount > 0 || conflictCount > 0) && <StatusPill status="amber" word={`${customerCount} CUSTOMER · ${conflictCount} CONFLICT`} />}
              <StatusPill status={preparedCount === briefable ? "green" : "grey"} word={`${preparedCount}/${briefable} BRIEFS PREPARED`} />
            </SectionHeading>
          </AccordionTrigger>
          <AccordionContent className="pb-4">
            <DayTimeline data={data} prepared={local.meetingsPrepared} onOpenBrief={setOpenBrief} />
          </AccordionContent>
        </AccordionItem>

        {/* 3 Risk */}
        <AccordionItem value="risks" className="rounded-md border border-border bg-card px-4">
          <AccordionTrigger className="py-4 hover:no-underline">
            <SectionHeading n={3} kicker="Customer risk & escalations" answer={risksAnswer}>
              {risksRed > 0 && <StatusPill status="red" count={risksRed} />}
              {risksAmber > 0 && <StatusPill status="amber" count={risksAmber} />}
              {risksGreen > 0 && <StatusPill status="green" word="CLOSED" count={risksGreen} />}
            </SectionHeading>
          </AccordionTrigger>
          <AccordionContent className="pb-4">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-28">Status</TableHead>
                  <TableHead>Account · item</TableHead>
                  <TableHead className="w-36">Owner</TableHead>
                  <TableHead className="w-24">Age</TableHead>
                  <TableHead className="w-56">If nothing changes by…</TableHead>
                  <TableHead className="w-56">Action</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {data.risks.map((r) => (
                  <TableRow key={r.id}>
                    <TableCell className="align-top"><StatusPill status={r.status as Status} word={r.status === "green" ? "CLOSED" : undefined} /></TableCell>
                    <TableCell className="min-w-0 whitespace-normal align-top">
                      <div className="font-semibold">{r.account} <EvidenceTag kind={r.evidence as Evidence} /></div>
                      <div className="text-muted-foreground">{r.item}</div>
                    </TableCell>
                    <TableCell className="whitespace-normal align-top">{r.owner}</TableCell>
                    <TableCell className="whitespace-normal align-top tabular-nums">{r.age}</TableCell>
                    <TableCell className="whitespace-normal align-top">
                      {r.projectionDate ? (<><span className="font-semibold">{r.projectionDate}</span> — {r.projection}</>) : <span className="text-muted-foreground">—</span>}
                    </TableCell>
                    <TableCell className="whitespace-normal align-top"><span className="font-semibold">{r.verb}</span> — {r.action}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
            <p className="mt-3 text-xs text-muted-foreground">{data.risksNote}</p>
          </AccordionContent>
        </AccordionItem>

        {/* 4 Replies & mentions */}
        <AccordionItem value="inbox" id="replies" className="rounded-md border border-border bg-card px-4">
          <AccordionTrigger className="py-4 hover:no-underline">
            <SectionHeading n={4} kicker="Replies & mentions" answer={inboxAnswer}>
              <StatusPill status="amber" word="NEED REPLY" count={data.inbox.reply.length} />
              <StatusPill status="grey" word="FYI" count={data.inbox.fyi.length} />
            </SectionHeading>
          </AccordionTrigger>
          <AccordionContent className="space-y-3 pb-4">
            {data.inbox.reply.map((m) => {
              const isTeams = m.channel === "teams";
              return (
                <article key={m.id} className="rounded-md border border-border border-l-4 border-l-amber-700 bg-background p-3 text-sm dark:border-l-amber-400">
                  <div className="flex flex-wrap items-center gap-2">
                    <StatusPill status="amber" word={isTeams ? "REPLY · TEAMS" : m.channel === "form" ? "ACTION" : "REPLY · EMAIL"} />
                    <span className="font-semibold">{m.from}</span>
                    {m.url ? <ExtLink href={m.url}>{m.subject}</ExtLink> : <span className="text-muted-foreground">— {m.subject}</span>}
                  </div>
                  <blockquote className="mt-1.5 border-l-2 border-border pl-3 italic text-muted-foreground">“{m.quote}”</blockquote>
                  {isTeams && m.action ? (
                    <p className="mt-2 rounded-sm border border-dashed border-border bg-muted/40 px-3 py-2"><span className="mr-1.5 text-[11px] font-semibold uppercase tracking-wide text-muted-foreground">Suggested reply</span>{m.action}</p>
                  ) : null}
                  <div className="mt-2 flex flex-wrap items-center gap-2">
                    {m.draftUrl ? (
                      <Button asChild size="sm" className="h-7 rounded-sm px-2 text-xs"><a href={m.draftUrl} target="_blank" rel="noreferrer"><FileText className="mr-1 size-3.5" aria-hidden="true" />Open draft reply in Outlook</a></Button>
                    ) : null}
                    {m.url ? (
                      <Button asChild variant="outline" size="sm" className="h-7 rounded-sm px-2 text-xs"><a href={m.url} target="_blank" rel="noreferrer"><ExternalLink className="mr-1 size-3.5" aria-hidden="true" />{isTeams ? "Open chat in Teams" : m.channel === "form" ? "Open request" : "Open email"}</a></Button>
                    ) : null}
                    {isTeams && m.action ? <CopyButton text={m.action} label="Copy suggested reply" /> : null}
                    {!isTeams && m.channel !== "form" && m.url && !m.draftUrl ? (
                      <span className="text-xs text-muted-foreground">No draft was prepared — reply from Outlook.</span>
                    ) : null}
                    {!(isTeams && m.action) && <span className="text-muted-foreground">{m.action}</span>}
                  </div>
                </article>
              );
            })}
            <Collapsible>
              <CollapsibleTrigger asChild>
                <Button variant="outline" size="sm" className="w-full justify-start rounded-sm">
                  <StatusPill status="grey" word="FYI" count={data.inbox.fyi.length} /> <span className="ml-2">Show context-only items</span>
                </Button>
              </CollapsibleTrigger>
              <CollapsibleContent>
                <ul className="mt-2 divide-y divide-border text-sm">
                  {data.inbox.fyi.map((f) => (
                    <li key={f.id} className="flex flex-wrap items-baseline gap-x-2 py-2">
                      <span className="font-semibold">{f.from}</span> — <span>{f.text}</span>
                      {f.url && <ExtLink href={f.url}>{f.channel === "teams" ? "Open in Teams" : "Open email"}</ExtLink>}
                    </li>
                  ))}
                </ul>
              </CollapsibleContent>
            </Collapsible>
          </AccordionContent>
        </AccordionItem>

        {/* 5 Ledger */}
        <AccordionItem value="ledger" className="rounded-md border border-border bg-card px-4">
          <AccordionTrigger className="py-4 hover:no-underline">
            <SectionHeading n={5} kicker="Commitment ledger" answer={ledgerAnswer}>
              {ledgerOpen > 0 && <StatusPill status="amber" word="OPEN / OVERDUE" count={ledgerOpen} />}
              {ledgerClosed > 0 && <StatusPill status="green" word="CLOSED" count={ledgerClosed} />}
              {ledgerWaiting > 0 && <StatusPill status="grey" word="WAITING" count={ledgerWaiting} />}
            </SectionHeading>
          </AccordionTrigger>
          <AccordionContent className="pb-4">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-36">Status</TableHead>
                  <TableHead>Commitment</TableHead>
                  <TableHead className="w-40">Owner</TableHead>
                  <TableHead className="w-20">Due</TableHead>
                  <TableHead className="w-16">Age</TableHead>
                  <TableHead className="w-48">Evidence</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {ledger.map((l) => {
                  const L = LEDGER[l.status];
                  return (
                    <TableRow key={l.id}>
                      <TableCell className="align-top">
                        <button
                          type="button"
                          onClick={() => cycleLedger(l.id, l.status)}
                          aria-label={`Status ${L.word}; click to change`}
                          title="Click to cycle status"
                          className="rounded-sm outline-none focus-visible:outline-solid focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring"
                        >
                          <StatusPill status={L.status} word={L.word} />
                        </button>
                      </TableCell>
                      <TableCell className={`min-w-0 whitespace-normal align-top ${l.status === "closed" ? "text-muted-foreground line-through" : ""}`}>{l.commitment}</TableCell>
                      <TableCell className="whitespace-normal align-top">{l.owner}</TableCell>
                      <TableCell className="align-top tabular-nums">{l.due}</TableCell>
                      <TableCell className="align-top tabular-nums">{l.age}</TableCell>
                      <TableCell className="whitespace-normal align-top"><EvidenceTag kind={l.evidence as Evidence} /> <span className="text-muted-foreground">{l.evidenceNote}</span></TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
            <p className="mt-3 text-xs text-muted-foreground">Items close only on evidence (a sent item, a reply, a calendar change). Status changes you make here are saved to today's state file on your OneDrive.</p>
          </AccordionContent>
        </AccordionItem>

        {/* 6 Calendar hygiene */}
        <AccordionItem value="hygiene" className="rounded-md border border-border bg-card px-4">
          <AccordionTrigger className="py-4 hover:no-underline">
            <SectionHeading n={6} kicker="Calendar hygiene, next 5 working days" answer={hygieneAnswer}>
              {noFreeDays.length > 0 && <StatusPill status="red" word={`NO FREE BLOCK: ${noFreeDays.join(", ").toUpperCase()}`} />}
            </SectionHeading>
          </AccordionTrigger>
          <AccordionContent className="pb-4">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-16">Done</TableHead>
                  <TableHead className="w-20">Day</TableHead>
                  <TableHead>Event</TableHead>
                  <TableHead className="w-52">Proposal</TableHead>
                  <TableHead>Why</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {data.hygiene.map((h) => {
                  const done = local.hygieneDone.includes(h.id);
                  return (
                    <TableRow key={h.id} className={done ? "opacity-70" : ""}>
                      <TableCell className="align-top"><Checkbox checked={done} onCheckedChange={(v) => toggleHygiene(h.id, v === true)} aria-label={`Mark proposal for ${h.event} as done`} /></TableCell>
                      <TableCell className="whitespace-normal align-top"><div className="font-semibold">{h.day}</div>{h.dayFlag && <div className="text-[11px] uppercase tracking-wide text-red-800 dark:text-red-300">▲ {h.dayFlag}</div>}</TableCell>
                      <TableCell className={`min-w-0 whitespace-normal align-top ${done ? "line-through" : ""}`}>{h.event}</TableCell>
                      <TableCell className="whitespace-normal align-top font-medium">{h.proposal}</TableCell>
                      <TableCell className="whitespace-normal align-top text-muted-foreground">{h.why}</TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
            <p className="mt-3 text-xs text-muted-foreground">Proposals only — nothing is changed in your calendar from here. Customer/partner meetings and personal events are never proposed for decline or move.</p>
          </AccordionContent>
        </AccordionItem>

        {/* 7 Team — direct reports (live roster) joined to engagement */}
        <AccordionItem value="people" className="rounded-md border border-border bg-card px-4">
          <AccordionTrigger className="py-4 hover:no-underline">
            <SectionHeading n={7} kicker={roster.length > 0 ? "Team · your direct reports" : "Team"} answer={teamAnswer}>
              {blockedCount > 0 && <StatusPill status="red" word="BLOCKED" count={blockedCount} />}
              {quietCount > 0 && <StatusPill status="amber" word="QUIET" count={quietCount} />}
              {roster.length > 0 && blockedCount + quietCount === 0 && <StatusPill status="green" word="ALL NOMINAL" />}
              {roster.length === 0 && !rosterQ.isPending && <StatusPill status="grey" word={fallbackPeople ? "FREQUENT CONTACTS" : "NO REPORTS"} />}
            </SectionHeading>
          </AccordionTrigger>
          <AccordionContent className="pb-4">
            {roster.length > 0 ? (
              <>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead className="w-36">Signal</TableHead>
                      <TableHead className="w-52">Report</TableHead>
                      <TableHead className="w-24">Last 1:1</TableHead>
                      <TableHead>Waiting on you</TableHead>
                      <TableHead>You're waiting on them</TableHead>
                      <TableHead>Raise in next 1:1</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {teamRows.map(({ roster: r, eng }) => (
                      <TableRow key={r.id}>
                        <TableCell className="align-top">{eng ? <StatusPill status={SIGNAL[eng.signal].status} word={SIGNAL[eng.signal].word} /> : <StatusPill status="grey" word="NO DATA YET" />}</TableCell>
                        <TableCell className="whitespace-normal align-top"><div className="font-semibold">{r.name}</div><div className="text-xs text-muted-foreground">{r.title}</div></TableCell>
                        <TableCell className="align-top tabular-nums">{eng ? (eng.daysSinceOneToOne === null ? "—" : `${eng.daysSinceOneToOne} d`) : "—"}{eng?.nextOneToOne && <div className="text-xs text-muted-foreground">next {eng.nextOneToOne}</div>}</TableCell>
                        <TableCell className="whitespace-normal align-top">{eng?.waitingOnYou || <span className="text-muted-foreground">—</span>}</TableCell>
                        <TableCell className="whitespace-normal align-top">{eng?.youWaitOn || <span className="text-muted-foreground">—</span>}</TableCell>
                        <TableCell className="whitespace-normal align-top">{eng?.raiseNext || <span className="text-muted-foreground">—</span>}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
                <p className="mt-3 text-xs text-muted-foreground">Roster is read live from your organisation's directory; engagement comes from the morning brief (quiet after {team?.quietAfterDays ?? 7} days without a touch). Engagement facts only — dates, counts and open asks — never performance judgements.</p>
              </>
            ) : (
              <>
                <div className="mb-3 flex items-center gap-2 rounded-md border border-dashed border-border p-3 text-sm text-muted-foreground">
                  <Users className="size-4 shrink-0" aria-hidden="true" />
                  {rosterQ.isPending ? "Checking the directory…" : rosterQ.isError ? "The directory couldn't be read right now." : "The directory lists no direct reports for you. When it does, this section switches to them automatically."}
                </div>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead className="w-52">Person</TableHead>
                      <TableHead className="w-56">Last touch</TableHead>
                      <TableHead>Waiting on you</TableHead>
                      <TableHead>You're waiting on them</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {(fallbackPeople ?? data.people).map((p) => (
                      <TableRow key={p.id}>
                        <TableCell className="whitespace-normal align-top"><div className="font-semibold">{p.name}</div><div className="text-xs text-muted-foreground">{p.role}</div></TableCell>
                        <TableCell className="whitespace-normal align-top">{p.lastTouch}</TableCell>
                        <TableCell className="whitespace-normal align-top">{p.waitingOnYou || <span className="text-muted-foreground">—</span>}</TableCell>
                        <TableCell className="whitespace-normal align-top">{p.youWaitOn || <span className="text-muted-foreground">—</span>}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </>
            )}
          </AccordionContent>
        </AccordionItem>
      </Accordion>

      {openEvent && (
        <MeetingBriefPanel
          key={openEvent.id}
          open={!!openBrief}
          onOpenChange={(o) => { if (!o) setOpenBrief(null); }}
          briefDate={data.meta.date}
          eventId={openEvent.id}
          title={displayTitle(openEvent)}
          start={openEvent.start}
          end={openEvent.end}
          preGenerated={openEvent.brief}
          prepared={local.meetingsPrepared.includes(openEvent.id)}
          onMarkPrepared={(on) => markPrepared(openEvent.id, on)}
        />
      )}

      <footer className="mt-8 border-t border-border pt-4 text-xs text-muted-foreground">
        <p><span className="font-semibold text-foreground">Method.</span> Decision-first: sections follow the decisions you make, not the data sources. RED/AMBER expanded, GREEN and CONTEXT counted. Every status is colour + shape + word. Thresholds are fixed and published. Claims are badged Verified, Inferred or Estimate. Leading items (what you can still change) come before lagging ones.</p>
        <p className="mt-2">{data.meta.updateMechanism}</p>
        <h2 className="mt-4 text-[11px] font-semibold uppercase tracking-wide text-foreground">How this brief was built</h2>
        <p className="mt-1">{data.meta.evidenceNote}</p>
      </footer>
    </div>
  );
}
