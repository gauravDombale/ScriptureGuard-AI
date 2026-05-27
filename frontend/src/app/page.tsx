"use client";

import { CheckCircle2, FileText, ImageIcon, ShieldCheck, Sparkles, type LucideIcon } from "lucide-react";
import { ChatWindow } from "@/components/ChatWindow";
import { DenominationPicker } from "@/components/DenominationPicker";
import { InputBar } from "@/components/InputBar";
import { Badge } from "@/components/ui/Badge";
import { Card, SoftCard } from "@/components/ui/Card";
import { useChat } from "@/lib/hooks/useChat";
import { useSession } from "@/lib/hooks/useSession";

export default function Home() {
  const sessionId = useSession();
  const chat = useChat(sessionId);
  const verifiedCount = chat.messages.reduce(
    (count, message) => count + message.citations.filter((citation) => citation.verified).length,
    0,
  );

  return (
    <main className="min-h-screen bg-white text-[#111111]">
      <div className="mx-auto flex min-h-screen w-full max-w-[1200px] flex-col px-4 sm:px-6">
        <header className="sticky top-0 z-20 flex min-h-16 flex-col gap-3 border-b border-[#e5e7eb] bg-white py-4 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex items-center gap-3">
            <div className="grid h-10 w-10 place-items-center rounded-md bg-[#111111] text-white">
              <ShieldCheck aria-hidden="true" size={22} />
            </div>
            <div>
              <h1 className="display-title text-xl">ScriptureGuard AI</h1>
              <p className="text-sm text-[#6b7280]">Grounded answers with verified KJV citations</p>
            </div>
          </div>
          <DenominationPicker value={chat.denomination} onChange={chat.setDenomination} />
        </header>

        <section className="grid min-h-0 flex-1 gap-6 py-6 lg:grid-cols-[minmax(0,1fr)_320px]">
          <Card className="flex min-h-[calc(100vh-128px)] flex-col overflow-hidden rounded-xl shadow-[0_4px_12px_rgba(0,0,0,0.08)]">
            <div className="flex flex-col gap-3 border-b border-[#e5e7eb] p-4 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <div className="display-title text-2xl">Ask with citations</div>
                <p className="mt-1 text-sm text-[#6b7280]">
                  Answers stream live and cited verses are validated before display.
                </p>
              </div>
              <Badge className="w-fit gap-2">
                <CheckCircle2 aria-hidden="true" size={14} />
                {verifiedCount} verified
              </Badge>
            </div>
            <ChatWindow messages={chat.messages} isLoading={chat.isLoading} error={chat.error} />
            <div className="border-t border-[#e5e7eb] p-4">
              <InputBar
                mode={chat.mode}
                onModeChange={chat.setMode}
                onSend={chat.send}
                isLoading={chat.isLoading}
              />
            </div>
          </Card>

          <aside className="hidden min-h-0 lg:block">
            <div className="sticky top-24 flex flex-col gap-4">
              <SoftCard className="p-5">
                <div className="mb-4 flex items-center justify-between">
                  <div className="display-title text-lg">Session</div>
                  <Badge>{chat.mode === "text" ? "Text" : "Image"}</Badge>
                </div>
                <div className="grid gap-3">
                  <StatusRow icon={FileText} label="Messages" value={String(chat.messages.length)} />
                  <StatusRow icon={CheckCircle2} label="Verified citations" value={String(verifiedCount)} />
                  <StatusRow icon={Sparkles} label="Lens" value={chat.denomination.replace("_", " ")} />
                </div>
              </SoftCard>

              <Card className="p-5">
                <div className="mb-4 flex items-center gap-2">
                  <ImageIcon aria-hidden="true" size={18} />
                  <div className="display-title text-lg">Image workflow</div>
                </div>
                <div className="rounded-lg bg-[#f5f5f5] p-4">
                  <div className="grid grid-cols-3 gap-2">
                    {["Prompt", "Guard", "Render"].map((step) => (
                      <div
                        key={step}
                        className="rounded-md bg-white px-2 py-3 text-center text-xs font-medium text-[#374151]"
                      >
                        {step}
                      </div>
                    ))}
                  </div>
                  <div className="mt-4 h-2 overflow-hidden rounded-full bg-white">
                    <div className="h-full w-2/3 rounded-full bg-[#111111]" />
                  </div>
                </div>
              </Card>
            </div>
          </aside>
        </section>
      </div>
    </main>
  );
}

function StatusRow({
  icon: Icon,
  label,
  value,
}: {
  icon: LucideIcon;
  label: string;
  value: string;
}) {
  return (
    <div className="flex items-center justify-between rounded-md bg-white px-3 py-2">
      <div className="flex items-center gap-2 text-sm text-[#6b7280]">
        <Icon aria-hidden="true" size={16} />
        <span>{label}</span>
      </div>
      <span className="text-sm font-semibold capitalize text-[#111111]">{value}</span>
    </div>
  );
}
