export type Status = "red" | "amber" | "green" | "grey";
export type Evidence = "verified" | "inferred" | "estimate";
export type EventKind = "accepted" | "customer" | "optional" | "block" | "personal";

export interface MeetingBrief {
  readTime: string;
  stake: { text: string; evidence: Evidence };
  decisions: { text: string; owner: string; deadline: string }[];
  preReads: { title: string; url: string; why: string; minutes: number }[];
  questions: { rank: number; text: string; impact: string }[];
  outOfTime: { criticalDecision: string; fallback: string };
  sources: { type: "email" | "chat" | "transcript" | "file" | "calendar"; label: string; url: string }[];
  generatedAt: string;
}

export type TeamSignal = "blocked" | "quiet" | "nominal";

export interface TeamMember {
  id: string;
  upn: string;           // join key to the live directory roster (mail / UPN)
  name: string;
  role: string;
  lastTouch: string;
  lastOneToOne: string;
  nextOneToOne: string;
  waitingOnYou: string;
  youWaitOn: string;
  raiseNext: string;     // one line: what to raise in the next 1:1
  signal: TeamSignal;
  daysSinceOneToOne: number | null;
}

export interface Brief {
  schemaVersion?: number;
  meta: { date: string; dayLabel: string; generatedAt: string; owner: string; governingAnswer: string; evidenceNote: string; updateMechanism: string };
  kpis: { id: string; label: string; value: number; unit: string; status: Status; threshold: string; fires: string; decision: string; trend: string; evidence: Evidence }[];
  decisions: { id: string; status: Status; evidence: Evidence; title: string; situation: string; complication: string; whyNow: string; ifNothingChanges: string; verb: string; recommendation: string; ask: string; links: { label: string; url: string }[] }[];
  calendar: { dayStart: number; dayEnd: number; events: { id: string; title: string; start: string; end: string; kind: EventKind; note: string; brief?: MeetingBrief }[] };
  risks: { id: string; status: Status; evidence: Evidence; account: string; item: string; owner: string; age: string; projectionDate: string; projection: string; verb: string; action: string }[];
  risksNote: string;
  inbox: {
    /** url = link to the original email or Teams message; draftUrl = link to the Outlook draft reply (emails only); channel tells the app which icon/wording to use. */
    reply: { id: string; from: string; subject: string; quote: string; action: string; url: string; draftUrl?: string; channel?: "email" | "teams" | "form" }[];
    fyi: { id: string; from: string; text: string; url?: string; channel?: "email" | "teams" }[];
  };
  ledger: { id: string; status: "overdue" | "open" | "waiting" | "closed"; commitment: string; owner: string; due: string; age: string; evidence: Evidence; evidenceNote: string }[];
  hygiene: { id: string; day: string; dayFlag: string; event: string; proposal: string; why: string }[];
  /** Engagement rows for the team. mode tells the app whether these are direct reports or a frequent-contacts fallback. */
  team?: { mode: "directReports" | "frequentContacts"; quietAfterDays: number; members: TeamMember[] };
  /** Legacy (schema v1) frequent-contacts list — still rendered when `team` is absent. */
  people: { id: string; name: string; role: string; lastTouch: string; waitingOnYou: string; youWaitOn: string }[];
  weekInReview?: { summary: string; series?: { name: string; points: { week: string; value: number }[] }[] };
}
