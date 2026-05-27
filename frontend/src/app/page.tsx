"use client";

import { ShieldCheck } from "lucide-react";
import { ChatWindow } from "@/components/ChatWindow";
import { DenominationPicker } from "@/components/DenominationPicker";
import { InputBar } from "@/components/InputBar";
import { useChat } from "@/lib/hooks/useChat";
import { useSession } from "@/lib/hooks/useSession";

export default function Home() {
  const sessionId = useSession();
  const chat = useChat(sessionId);

  return (
    <main className="min-h-screen bg-[#f7f4ed] text-[#1c1b18]">
      <div className="mx-auto flex min-h-screen w-full max-w-6xl flex-col px-4 py-4 sm:px-6">
        <header className="flex flex-col gap-3 border-b border-[#d8d0c2] pb-4 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex items-center gap-3">
            <div className="grid h-10 w-10 place-items-center rounded-md bg-[#173f35] text-white">
              <ShieldCheck aria-hidden="true" size={22} />
            </div>
            <div>
              <h1 className="text-xl font-semibold">ScriptureGuard AI</h1>
              <p className="text-sm text-[#625c52]">Grounded answers with verified KJV citations</p>
            </div>
          </div>
          <DenominationPicker value={chat.denomination} onChange={chat.setDenomination} />
        </header>

        <ChatWindow messages={chat.messages} isLoading={chat.isLoading} error={chat.error} />

        <InputBar
          mode={chat.mode}
          onModeChange={chat.setMode}
          onSend={chat.send}
          isLoading={chat.isLoading}
        />
      </div>
    </main>
  );
}
