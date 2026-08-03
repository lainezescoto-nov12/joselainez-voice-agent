"use client";

type GaugeStatus = "online" | "offline" | "warn";

function Gauge({
  label,
  value,
  status,
}: {
  label: string;
  value: string;
  status: GaugeStatus;
}) {
  const dotColor =
    status === "online"
      ? "bg-signal-green"
      : status === "warn"
      ? "bg-amber"
      : "bg-signal-red";

  const ringColor =
    status === "online"
      ? "border-signal-green-dim"
      : status === "warn"
      ? "border-amber-dim"
      : "border-signal-red";

  return (
    <div className="flex items-center gap-3 px-5 py-3 border-r border-border last:border-r-0">
      <div className={`relative w-9 h-9 rounded-full border ${ringColor} flex items-center justify-center shrink-0`}>
        <span className={`w-2 h-2 rounded-full ${dotColor} ${status === "online" ? "animate-pulse-dot" : ""}`} />
      </div>
      <div className="flex flex-col leading-tight">
        <span className="font-mono text-[10px] uppercase tracking-wider text-muted-dim">
          {label}
        </span>
        <span className="font-mono text-sm text-foreground">{value}</span>
      </div>
    </div>
  );
}

export default function GaugeStrip() {
  return (
    <div className="flex flex-wrap items-stretch border border-border rounded-lg bg-surface overflow-hidden">
      <Gauge label="Voice Link" value="ElevenLabs · Live" status="online" />
      <Gauge label="Tool Server" value="8 tools online" status="online" />
      <Gauge label="Telephony" value="Twilio · Connected" status="online" />
      <Gauge label="Automation" value="n8n · Idle" status="warn" />
    </div>
  );
}
