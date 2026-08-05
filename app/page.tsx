"use client";

import { useState } from "react";
import GaugeStrip from "@/components/GaugeStrip";
import OutboundDemoCall from "@/components/OutboundDemoCall";
import {
  Wrench,
  Mic,
  MessagesSquare,
  ShieldAlert,
  PhoneCall,
  ChevronDown,
  Play,
  Save,
  X,
  FileText,
  ArrowRight,
} from "lucide-react";

type Tool = {
  id: string;
  name: string;
  description: string;
  lastCalled: string | null;
};

const INITIAL_TOOLS: Tool[] = [
  { id: "check_availability", name: "check_availability", description: "Queries the service/sales calendar for open slots", lastCalled: null },
  { id: "book_appointment", name: "book_appointment", description: "Creates a calendar event and sends a confirmation email directly", lastCalled: null },
  { id: "reschedule_appointment", name: "reschedule_appointment", description: "Moves an existing appointment to a new slot", lastCalled: null },
  { id: "cancel_appointment", name: "cancel_appointment", description: "Cancels an existing appointment and sends a cancellation email", lastCalled: null },
  { id: "find_appointment", name: "find_appointment", description: "Looks up an existing appointment by email or phone from an earlier call", lastCalled: null },
  { id: "intake_trade_in", name: "intake_trade_in", description: "Captures make, model, mileage, and condition for a trade-in", lastCalled: null },
  { id: "check_vehicle_status", name: "check_vehicle_status", description: "Looks up service/recall status by VIN", lastCalled: null },
  { id: "dealership_faq_lookup", name: "dealership_faq_lookup", description: "Answers general questions grounded in the uploaded knowledge base", lastCalled: null },
  { id: "trigger_outbound_reminder", name: "trigger_outbound_reminder", description: "Places a real outbound reminder call directly via ElevenLabs", lastCalled: null },
];

type TraceStep = {
  speaker: "caller" | "agent" | "tool";
  text: string;
};

const DEMO_TRACE: TraceStep[] = [
  { speaker: "caller", text: "Hi, I need to bring my car in and I'm also thinking about test driving something new." },
  { speaker: "agent", text: "Happy to help with both. What day works for dropping off your car for service?" },
  { speaker: "caller", text: "Thursday afternoon, maybe 2pm?" },
  { speaker: "tool", text: "check_availability({ date: \"Thursday\", department: \"service\" }) \u2192 3 open slots, 2:00 PM available" },
  { speaker: "tool", text: "book_appointment({ time: \"Thursday 2:00 PM\", department: \"service\" }) \u2192 confirmed" },
  { speaker: "agent", text: "You're booked for 2 PM Thursday. Since you're dropping the car off right then, I can get you a test drive right after, would 2:30 work?" },
  { speaker: "caller", text: "Perfect, yes." },
  { speaker: "tool", text: "book_appointment({ time: \"Thursday 2:30 PM\", department: \"sales\", type: \"test_drive\" }) \u2192 confirmed" },
  { speaker: "caller", text: "Can you email me the confirmation? It's jose@example.com" },
  { speaker: "agent", text: "Done, confirmation's on its way to your inbox. See you Thursday." },
];

const CONVERSATIONS = [
  { id: "c1", time: "Today, 2:14 PM", useCase: "Appointment + Trade-in chain", status: "Completed", duration: "2m 41s" },
  { id: "c2", time: "Today, 11:03 AM", useCase: "Outbound service reminder", status: "Completed", duration: "0m 52s" },
  { id: "c3", time: "Yesterday, 4:47 PM", useCase: "General FAQ", status: "Handed off", duration: "1m 18s" },
];

function SectionCard({
  icon,
  title,
  subtitle,
  children,
}: {
  icon: React.ReactNode;
  title: string;
  subtitle?: string;
  children: React.ReactNode;
}) {
  return (
    <div className="border border-border rounded-lg bg-surface">
      <div className="flex items-center gap-3 px-5 py-4 border-b border-border">
        <div className="w-8 h-8 rounded-md bg-surface-raised border border-border flex items-center justify-center text-amber shrink-0">
          {icon}
        </div>
        <div>
          <h2 className="text-sm font-medium text-foreground">{title}</h2>
          {subtitle && <p className="text-xs text-muted mt-0.5">{subtitle}</p>}
        </div>
      </div>
      <div className="p-5 flex flex-col gap-4">{children}</div>
    </div>
  );
}

function Field({
  label,
  hint,
  children,
}: {
  label: string;
  hint?: string;
  children: React.ReactNode;
}) {
  return (
    <div className="flex flex-col gap-1.5">
      <label className="text-xs font-medium text-muted uppercase tracking-wide">
        {label}
      </label>
      {children}
      {hint && <p className="text-xs text-muted-dim">{hint}</p>}
    </div>
  );
}

export default function ConfigConsole() {
  const [activeTab, setActiveTab] = useState<"configure" | "conversations">("configure");
  const [tools, setTools] = useState<Tool[]>(INITIAL_TOOLS);
  const [testOpen, setTestOpen] = useState(false);
  const [traceVisible, setTraceVisible] = useState<TraceStep[]>([]);
  const [running, setRunning] = useState(false);

  const runTest = () => {
    setTestOpen(true);
    setRunning(true);
    setTraceVisible([]);
    setTools(INITIAL_TOOLS);

    DEMO_TRACE.forEach((step, i) => {
      setTimeout(() => {
        setTraceVisible((prev) => [...prev, step]);
        if (step.speaker === "tool") {
          const toolId = step.text.split("(")[0];
          setTools((prev) =>
            prev.map((t) =>
              t.id === toolId ? { ...t, lastCalled: "just now" } : t
            )
          );
        }
        if (i === DEMO_TRACE.length - 1) setRunning(false);
      }, i * 850);
    });
  };

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b border-border bg-surface">
        <div className="max-w-6xl mx-auto px-6 py-5 flex flex-col gap-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="font-mono text-[11px] uppercase tracking-widest text-amber mb-1">
                Dealership Voice Agent
              </p>
              <h1 className="text-xl font-semibold text-foreground">
                Sales &amp; Service Console
              </h1>
            </div>
            <nav className="flex gap-1 bg-surface-raised border border-border rounded-lg p-1">
              <button
                onClick={() => setActiveTab("configure")}
                className={`px-4 py-1.5 text-sm rounded-md transition-colors ${
                  activeTab === "configure"
                    ? "bg-amber text-background font-medium"
                    : "text-muted hover:text-foreground"
                }`}
              >
                Configure
              </button>
              <button
                onClick={() => setActiveTab("conversations")}
                className={`px-4 py-1.5 text-sm rounded-md transition-colors ${
                  activeTab === "conversations"
                    ? "bg-amber text-background font-medium"
                    : "text-muted hover:text-foreground"
                }`}
              >
                Conversations
              </button>
            </nav>
          </div>
          <GaugeStrip />
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-6 py-8">
        {activeTab === "configure" ? (
          <div className="flex flex-col gap-6">
            <OutboundDemoCall />

            <SectionCard
              icon={<MessagesSquare size={16} />}
              title="Identity & Behavior"
              subtitle="How the agent sounds, thinks, and responds"
            >
              <Field label="Personality / Behavior">
                <textarea
                  rows={4}
                  className="bg-background border border-border rounded-md px-3 py-2 text-sm text-foreground placeholder:text-muted-dim focus:outline-none focus:ring-1 focus:ring-amber resize-none"
                  defaultValue="You are a warm, efficient front-desk assistant for a multi-brand dealership. You handle sales, service, and parts questions. Keep responses short and natural for voice, confirm details before booking anything."
                />
              </Field>
              <Field label="Voice Behavior Instructions">
                <textarea
                  rows={3}
                  className="bg-background border border-border rounded-md px-3 py-2 text-sm text-foreground placeholder:text-muted-dim focus:outline-none focus:ring-1 focus:ring-amber resize-none"
                  defaultValue="Speak at a natural, unhurried pace. If interrupted, stop immediately and listen. If the caller goes silent for 4+ seconds, gently check in."
                />
              </Field>
              <Field label="Language" hint="Multi-language mode active">
                <div className="flex items-center gap-2">
                  <span className="px-3 py-1.5 bg-signal-green-dim text-signal-green text-xs font-mono rounded-md border border-signal-green-dim">
                    English
                  </span>
                  <span className="px-3 py-1.5 bg-signal-green-dim text-signal-green text-xs font-mono rounded-md border border-signal-green-dim">
                    Español
                  </span>
                  <button className="px-3 py-1.5 border border-border text-muted text-xs font-mono rounded-md hover:border-border-bright">
                    + Add language
                  </button>
                </div>
              </Field>
            </SectionCard>

            <SectionCard
              icon={<Mic size={16} />}
              title="Voice & Recognition"
              subtitle="Speech recognition and voice output settings"
            >
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <Field label="ASR Provider">
                  <div className="relative">
                    <select className="w-full appearance-none bg-background border border-border rounded-md px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-1 focus:ring-amber">
                      <option>Deepgram Nova-3 (Turn detection: sensitive)</option>
                      <option>ElevenLabs native ASR</option>
                    </select>
                    <ChevronDown size={14} className="absolute right-3 top-1/2 -translate-y-1/2 text-muted pointer-events-none" />
                  </div>
                </Field>
                <Field label="ElevenLabs Voice">
                  <div className="relative">
                    <select className="w-full appearance-none bg-background border border-border rounded-md px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-1 focus:ring-amber">
                      <option>Rosa — warm, bilingual</option>
                      <option>Marcus — steady, formal</option>
                    </select>
                    <ChevronDown size={14} className="absolute right-3 top-1/2 -translate-y-1/2 text-muted pointer-events-none" />
                  </div>
                </Field>
              </div>
            </SectionCard>

            <SectionCard
              icon={<Wrench size={16} />}
              title="Tools & Knowledge"
              subtitle="What the agent can actually do, backed by the MCP tool server"
            >
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                {tools.map((tool) => (
                  <div
                    key={tool.id}
                    className={`border rounded-md px-3.5 py-3 flex flex-col gap-1 transition-colors ${
                      tool.lastCalled
                        ? "border-signal-green-dim bg-signal-green-dim/10"
                        : "border-border bg-background"
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-mono text-xs text-foreground">{tool.name}</span>
                      {tool.lastCalled && (
                        <span className="font-mono text-[10px] text-signal-green">
                          called {tool.lastCalled}
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-muted leading-snug">{tool.description}</p>
                  </div>
                ))}
              </div>
              <Field label="Knowledge Base" hint="Upload dealership FAQ content, hours, department contacts">
                <div className="border border-dashed border-border rounded-md px-4 py-5 flex items-center justify-center gap-2 text-muted text-sm">
                  <FileText size={16} />
                  <span>Drop a file or click to upload</span>
                </div>
              </Field>
            </SectionCard>

            <SectionCard
              icon={<ShieldAlert size={16} />}
              title="Pit Stop Protocol"
              subtitle="When the agent hands off to a human, and how it avoids getting stuck"
            >
              <Field label="Handoff Triggers">
                <div className="flex flex-col gap-2">
                  {[
                    "Caller explicitly asks for a human",
                    "Repeated failed clarification (loop threshold hit)",
                    "Out-of-scope request (legal, warranty dispute, complaint)",
                    "Detected frustration or negative sentiment",
                    "Ambiguous multi-intent request the agent can't confidently parse",
                  ].map((rule) => (
                    <label key={rule} className="flex items-center gap-2.5 text-sm text-foreground">
                      <input
                        type="checkbox"
                        defaultChecked
                        className="w-4 h-4 rounded accent-amber"
                      />
                      {rule}
                    </label>
                  ))}
                </div>
              </Field>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <Field label="Loop Threshold" hint="Fallback triggers after this many repeated clarifications">
                  <input
                    type="number"
                    defaultValue={3}
                    className="bg-background border border-border rounded-md px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-1 focus:ring-amber w-24"
                  />
                </Field>
                <Field label="Max Turns" hint="Session forces fallback past this many unresolved turns">
                  <input
                    type="number"
                    defaultValue={10}
                    className="bg-background border border-border rounded-md px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-1 focus:ring-amber w-24"
                  />
                </Field>
              </div>
            </SectionCard>

            <div className="flex items-center justify-end gap-3 pb-8">
              <button className="px-4 py-2 text-sm text-muted border border-border rounded-md hover:border-border-bright hover:text-foreground transition-colors flex items-center gap-2">
                <X size={14} /> Cancel
              </button>
              <button
                onClick={runTest}
                className="px-4 py-2 text-sm text-foreground border border-border rounded-md hover:border-amber-dim transition-colors flex items-center gap-2"
              >
                <Play size={14} /> Test
              </button>
              <button className="px-4 py-2 text-sm bg-amber text-background rounded-md font-medium hover:brightness-110 transition-all flex items-center gap-2">
                <Save size={14} /> Save
              </button>
            </div>
          </div>
        ) : (
          <div className="flex flex-col gap-3">
            {CONVERSATIONS.map((c) => (
              <div
                key={c.id}
                className="border border-border rounded-lg bg-surface px-5 py-4 flex items-center justify-between hover:border-border-bright transition-colors cursor-pointer"
              >
                <div className="flex items-center gap-4">
                  <div className="w-9 h-9 rounded-full bg-surface-raised border border-border flex items-center justify-center text-amber">
                    <PhoneCall size={15} />
                  </div>
                  <div>
                    <p className="text-sm text-foreground">{c.useCase}</p>
                    <p className="text-xs text-muted-dim font-mono mt-0.5">{c.time}</p>
                  </div>
                </div>
                <div className="flex items-center gap-6">
                  <span className="font-mono text-xs text-muted">{c.duration}</span>
                  <span
                    className={`text-xs font-mono px-2.5 py-1 rounded-full border ${
                      c.status === "Completed"
                        ? "text-signal-green border-signal-green-dim bg-signal-green-dim/10"
                        : "text-amber border-amber-dim bg-amber-dim/10"
                    }`}
                  >
                    {c.status}
                  </span>
                  <ArrowRight size={14} className="text-muted-dim" />
                </div>
              </div>
            ))}
            <p className="text-xs text-muted-dim text-center pt-4">
              Click a call to view transcript, recording, and the grounding trace behind each response.
            </p>
          </div>
        )}
      </main>

      {testOpen && (
        <div className="fixed inset-0 bg-black/60 flex items-end sm:items-center justify-center z-50 p-0 sm:p-6">
          <div className="bg-surface border border-border rounded-t-lg sm:rounded-lg w-full sm:max-w-2xl max-h-[85vh] flex flex-col">
            <div className="flex items-center justify-between px-5 py-4 border-b border-border">
              <div className="flex items-center gap-2">
                <span className={`w-2 h-2 rounded-full ${running ? "bg-signal-green animate-pulse-dot" : "bg-muted-dim"}`} />
                <h3 className="text-sm font-medium text-foreground">
                  {running ? "Test call in progress" : "Test call complete"}
                </h3>
              </div>
              <button onClick={() => setTestOpen(false)} className="text-muted hover:text-foreground">
                <X size={16} />
              </button>
            </div>
            <div className="flex-1 overflow-y-auto px-5 py-4 flex flex-col gap-2.5">
              {traceVisible.map((step, i) => (
                <div
                  key={i}
                  className={
                    step.speaker === "tool"
                      ? "font-mono text-xs text-amber bg-amber-dim/10 border border-amber-dim rounded-md px-3 py-2"
                      : `max-w-[85%] rounded-md px-3.5 py-2.5 text-sm ${
                          step.speaker === "caller"
                            ? "self-start bg-surface-raised text-foreground"
                            : "self-end bg-signal-green-dim/20 text-foreground border border-signal-green-dim"
                        }`
                  }
                >
                  {step.speaker !== "tool" && (
                    <p className="text-[10px] uppercase tracking-wide text-muted-dim mb-1">
                      {step.speaker === "caller" ? "Caller" : "Agent"}
                    </p>
                  )}
                  {step.text}
                </div>
              ))}
              {traceVisible.length === 0 && (
                <p className="text-sm text-muted-dim text-center py-8">Connecting test call…</p>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
