"use client";

import { useState } from "react";
import { PhoneCall, ShieldCheck, Loader2 } from "lucide-react";

const DEMO_API_URL = process.env.NEXT_PUBLIC_DEMO_API_URL || "";

type Step = "phone" | "code" | "calling" | "done" | "error";

// Strips spaces/dashes/parens so "(984) 388-9822" and "+1 984-388-9822"
// both work. Does not guess a missing country code -- that would risk
// silently sending to the wrong country -- but only errors on that
// specific case, with a message telling the visitor what to add.
function normalizePhone(raw: string): { value: string; error: string | null } {
  const stripped = raw.replace(/[\s\-().]/g, "");
  if (!stripped.startsWith("+")) {
    return {
      value: stripped,
      error: "Add your country code with a + in front, e.g. +19843889822 or +50432964465.",
    };
  }
  return { value: stripped, error: null };
}

export default function OutboundDemoCall() {
  const [step, setStep] = useState<Step>("phone");
  const [phone, setPhone] = useState("+");
  const [code, setCode] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const apiConfigured = Boolean(DEMO_API_URL);

  const sendCode = async () => {
    const { value: normalized, error } = normalizePhone(phone);
    if (error) {
      setErrorMessage(error);
      setStep("error");
      return;
    }

    setLoading(true);
    setErrorMessage("");
    try {
      const res = await fetch(`${DEMO_API_URL}/verify/send`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ phone_number: normalized }),
      });
      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.detail || "Could not send verification code.");
      }
      setStep("code");
    } catch (err) {
      setErrorMessage(err instanceof Error ? err.message : "Something went wrong.");
      setStep("error");
    } finally {
      setLoading(false);
    }
  };

  const verifyAndCall = async () => {
    setLoading(true);
    setErrorMessage("");
    setStep("calling");
    try {
      const res = await fetch(`${DEMO_API_URL}/verify/check`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ phone_number: normalizePhone(phone).value, code }),
      });
      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.detail || "Could not verify that code.");
      }
      setStep("done");
    } catch (err) {
      setErrorMessage(err instanceof Error ? err.message : "Something went wrong.");
      setStep("error");
    } finally {
      setLoading(false);
    }
  };

  const reset = () => {
    setStep("phone");
    setPhone("+");
    setCode("");
    setErrorMessage("");
  };

  return (
    <div className="border border-border rounded-lg bg-surface">
      <div className="flex items-center gap-3 px-5 py-4 border-b border-border">
        <div className="w-8 h-8 rounded-md bg-surface-raised border border-amber-dim flex items-center justify-center text-amber shrink-0">
          <PhoneCall size={16} />
        </div>
        <div>
          <h2 className="text-sm font-medium text-foreground">
            Try the AI voice Agent-Outbound Live Demo call
          </h2>
          <p className="text-xs text-muted mt-0.5">
            Real outbound call, real agent — verify your number and it calls you
          </p>
        </div>
      </div>

      <div className="p-5 flex flex-col gap-4">
        {!apiConfigured && (
          <p className="text-xs text-signal-red">
            Demo call API not configured — set NEXT_PUBLIC_DEMO_API_URL.
          </p>
        )}

        {step === "phone" && (
          <div className="flex flex-col gap-3">
            <label className="text-xs font-medium text-muted uppercase tracking-wide">
              Your phone number
            </label>
            <div className="flex gap-2">
              <input
                type="tel"
                placeholder="+1 555 123 4567"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                className="flex-1 bg-background border border-border rounded-md px-3 py-2 text-sm text-foreground placeholder:text-muted-dim focus:outline-none focus:ring-1 focus:ring-amber"
              />
              <button
                onClick={sendCode}
                disabled={loading || phone.replace(/\D/g, "").length < 7 || !apiConfigured}
                className="px-4 py-2 text-sm bg-amber text-background rounded-md font-medium hover:brightness-110 transition-all disabled:opacity-40 disabled:cursor-not-allowed flex items-center gap-2"
              >
                {loading ? <Loader2 size={14} className="animate-spin" /> : <ShieldCheck size={14} />}
                Send code
              </button>
            </div>
            <p className="text-xs text-muted-dim">
              Use E.164 format with country code, e.g. +50432964465. We text a
              one-time code to confirm it&apos;s really your number before
              calling it.
            </p>
          </div>
        )}

        {step === "code" && (
          <div className="flex flex-col gap-3">
            <label className="text-xs font-medium text-muted uppercase tracking-wide">
              Enter the code we texted you
            </label>
            <div className="flex gap-2">
              <input
                type="text"
                inputMode="numeric"
                placeholder="123456"
                value={code}
                onChange={(e) => setCode(e.target.value)}
                className="flex-1 bg-background border border-border rounded-md px-3 py-2 text-sm text-foreground placeholder:text-muted-dim focus:outline-none focus:ring-1 focus:ring-amber"
              />
              <button
                onClick={verifyAndCall}
                disabled={loading || !code}
                className="px-4 py-2 text-sm bg-amber text-background rounded-md font-medium hover:brightness-110 transition-all disabled:opacity-40 disabled:cursor-not-allowed flex items-center gap-2"
              >
                {loading ? <Loader2 size={14} className="animate-spin" /> : <PhoneCall size={14} />}
                Verify &amp; call me
              </button>
            </div>
          </div>
        )}

        {step === "calling" && (
          <div className="flex items-center gap-3 py-4">
            <Loader2 size={16} className="animate-spin text-amber" />
            <p className="text-sm text-foreground">Placing your call now…</p>
          </div>
        )}

        {step === "done" && (
          <div className="flex flex-col gap-2 py-2">
            <p className="text-sm text-signal-green">
              Your phone should be ringing. That&apos;s the real agent, live.
            </p>
            <button
              onClick={reset}
              className="self-start text-xs text-muted hover:text-foreground underline"
            >
              Try another number
            </button>
          </div>
        )}

        {step === "error" && (
          <div className="flex flex-col gap-2 py-2">
            <p className="text-sm text-signal-red">{errorMessage}</p>
            <button
              onClick={reset}
              className="self-start text-xs text-muted hover:text-foreground underline"
            >
              Try again
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
