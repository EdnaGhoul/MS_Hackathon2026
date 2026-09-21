import { useEffect, useRef, useState } from "react";
import { Clock, RefreshCw, CheckCircle2 } from "lucide-react";
import type { MeetingBrief, Evidence } from "@/types/brief";
import { requestMeetingBrief, fetchMeetingBrief } from "@/lib/brief-store";
import { Button } from "@/components/ui/button";
import {
  Sheet, SheetContent, SheetHeader, SheetTitle, SheetDescription, SheetFooter,
} from "@/components/ui/sheet";

const EVIDENCE_GLYPH: Record<Evidence, string> = { verified: "✔ Verified", inferred: "~ Inferred", estimate: "≈ Estimate" };

type Phase = "idle" | "requesting" | "waiting" | "ready" | "timeout" | "error";
const POLL_MS = 10_000;
const POLL_CAP_MS = 120_000;

export function MeetingBriefPanel({
  open, onOpenChange, briefDate, eventId, title, start, end, preGenerated, prepared, onMarkPrepared,
}: {
  open: boolean;
  onOpenChange: (o: boolean) => void;
  briefDate: string;
  eventId: string;
  title: string;
  start: string;
  end: string;
  preGenerated?: MeetingBrief;
  prepared: boolean;
  onMarkPrepared: (prepared: boolean) => void;
}) {
  const [brief, setBrief] = useState<MeetingBrief | undefined>(preGenerated);
  const [phase, setPhase] = useState<Phase>(preGenerated ? "ready" : "idle");
  const pollTimer = useRef<number | null>(null);
  const startedAt = useRef<number>(0);

  useEffect(() => () => { if (pollTimer.current) window.clearTimeout(pollTimer.current); }, []);

  const poll = async () => {
    const fresh = await fetchMeetingBrief(briefDate, eventId);
    if (fresh) { setBrief(fresh); setPhase("ready"); return; }
    if (Date.now() - startedAt.current > POLL_CAP_MS) { setPhase("timeout"); return; }
    pollTimer.current = window.setTimeout(poll, POLL_MS);
  };

  const refresh = async () => {
    setPhase("requesting");
    try {
      await requestMeetingBrief(briefDate, eventId, title, start, end);
      startedAt.current = Date.now();
      setPhase("waiting");
      pollTimer.current = window.setTimeout(poll, POLL_MS);
    } catch {
      setPhase("error");
    }
  };

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent side="right" className="w-full overflow-y-auto sm:max-w-xl">
        <SheetHeader>
          <SheetTitle className="text-base leading-snug">Meeting brief — {title}</SheetTitle>
          <SheetDescription className="flex flex-wrap items-center gap-2">
            <span className="tabular-nums">{start} – {end}</span>
            {brief && <span className="inline-flex items-center gap-1 rounded-sm border border-border px-1.5 py-0.5 text-[11px] font-semibold"><Clock className="size-3" aria-hidden="true" />{brief.readTime} read</span>}
            {prepared && <span className="inline-flex items-center gap-1 rounded-sm border border-emerald-800 px-1.5 py-0.5 text-[11px] font-semibold text-emerald-900 dark:border-emerald-400 dark:text-emerald-200"><CheckCircle2 className="size-3" aria-hidden="true" />Prepared</span>}
          </SheetDescription>
        </SheetHeader>

        <div className="px-4 pb-4 text-sm">
          {phase === "waiting" || phase === "requesting" ? (
            <p role="status" aria-live="polite" className="rounded-md border border-dashed border-border p-3 text-muted-foreground">
              Request saved to your OneDrive. It is answered by the next scheduled Cowork run — or ask Cowork for it now ("brief me for {title}"). This panel checks for the answer for two minutes.
            </p>
          ) : null}
          {phase === "timeout" && (
            <p role="alert" className="rounded-md border border-amber-800 bg-amber-50 p-3 text-amber-900 dark:border-amber-400 dark:bg-amber-950/40 dark:text-amber-200">
              ◆ No brief has arrived yet. Your request is saved and will be answered by the next scheduled run; open this panel again later.{preGenerated ? " The morning brief is shown below in the meantime." : ""}
            </p>
          )}
          {phase === "error" && (
            <p role="alert" className="rounded-md border border-red-700 bg-red-50 p-3 text-red-800 dark:border-red-400 dark:bg-red-950/40 dark:text-red-200">
              ▲ Couldn't send the request to your OneDrive. Try again shortly.
            </p>
          )}
          {phase === "idle" && !brief && (
            <p className="rounded-md border border-dashed border-border p-3 text-muted-foreground">
              No brief was prepared for this meeting in the morning run. Request one — it is answered by the next scheduled run, or ask Cowork directly.
            </p>
          )}

          {brief && (
            <article className="mt-3 space-y-5">
              <section>
                <h3 className="text-[11px] font-bold uppercase tracking-wide text-muted-foreground">What's at stake and why it matters</h3>
                <p className="mt-1 leading-relaxed">{brief.stake.text} <span className="ml-1 text-[11px] text-muted-foreground">{EVIDENCE_GLYPH[brief.stake.evidence]}</span></p>
              </section>
              <section>
                <h3 className="text-[11px] font-bold uppercase tracking-wide text-muted-foreground">Decisions needed from me</h3>
                {brief.decisions.length === 0 ? <p className="mt-1 text-muted-foreground">None — this meeting expects no decision from you.</p> : (
                  <ul className="mt-1 space-y-1.5">
                    {brief.decisions.map((d, i) => <li key={i} className="flex gap-2"><span aria-hidden="true">▲</span><span><span className="font-medium">{d.text}</span> <span className="text-muted-foreground">— {d.owner}{d.deadline ? `, by ${d.deadline}` : ""}</span></span></li>)}
                  </ul>
                )}
              </section>
              <section>
                <h3 className="text-[11px] font-bold uppercase tracking-wide text-muted-foreground">Essential pre-reads</h3>
                {brief.preReads.length === 0 ? <p className="mt-1 text-muted-foreground">Nothing to read beforehand.</p> : (
                  <ul className="mt-1 space-y-1.5">
                    {brief.preReads.map((r, i) => (
                      <li key={i} className="flex gap-2"><span className="w-12 shrink-0 tabular-nums text-muted-foreground">{r.minutes} min</span><span>{r.url ? <a href={r.url} target="_blank" rel="noreferrer" className="font-medium text-primary underline-offset-2 hover:underline">{r.title}</a> : <span className="font-medium">{r.title}</span>} <span className="text-muted-foreground">— {r.why}</span></span></li>
                    ))}
                  </ul>
                )}
              </section>
              <section>
                <h3 className="text-[11px] font-bold uppercase tracking-wide text-muted-foreground">Five questions to ask — ranked by impact</h3>
                <ol className="mt-1 space-y-2">
                  {[...brief.questions].sort((a, b) => a.rank - b.rank).map((q) => (
                    <li key={q.rank} className="flex gap-3"><span className="inline-flex size-6 shrink-0 items-center justify-center rounded-sm bg-primary/10 text-xs font-bold text-primary">{q.rank}</span><span><span className="font-medium">{q.text}</span><br /><span className="text-xs text-muted-foreground">{q.impact}</span></span></li>
                  ))}
                </ol>
              </section>
              <section className="rounded-md border border-border border-l-4 border-l-primary bg-muted/40 p-3">
                <h3 className="text-[11px] font-bold uppercase tracking-wide text-muted-foreground">If we run out of time</h3>
                <p className="mt-1"><span className="font-semibold">Decide this:</span> {brief.outOfTime.criticalDecision}</p>
                <p className="mt-1"><span className="font-semibold">Fallback:</span> {brief.outOfTime.fallback}</p>
              </section>
              {brief.sources.length > 0 && (
                <section>
                  <h3 className="text-[11px] font-bold uppercase tracking-wide text-muted-foreground">Sources</h3>
                  <ul className="mt-1 flex flex-wrap gap-2 text-xs">
                    {brief.sources.map((s, i) => <li key={i}>{s.url ? <a href={s.url} target="_blank" rel="noreferrer" className="text-primary underline-offset-2 hover:underline">{s.type}: {s.label}</a> : <span className="text-muted-foreground">{s.type}: {s.label}</span>}</li>)}
                  </ul>
                  <p className="mt-2 text-[11px] text-muted-foreground">Generated {brief.generatedAt}.</p>
                </section>
              )}
            </article>
          )}
        </div>

        <SheetFooter className="flex-row justify-between gap-2 border-t border-border">
          <Button variant="outline" size="sm" className="rounded-sm" onClick={refresh} disabled={phase === "waiting" || phase === "requesting"} aria-pressed={phase === "waiting"}>
            <RefreshCw className="mr-1.5 size-3.5" aria-hidden="true" />{brief ? "Refresh brief" : "Request brief"}
          </Button>
          <Button size="sm" className="rounded-sm" variant={prepared ? "secondary" : "default"} onClick={() => onMarkPrepared(!prepared)} aria-pressed={prepared}>
            <CheckCircle2 className="mr-1.5 size-3.5" aria-hidden="true" />{prepared ? "Prepared ✓" : "Mark prepared"}
          </Button>
        </SheetFooter>
      </SheetContent>
    </Sheet>
  );
}
