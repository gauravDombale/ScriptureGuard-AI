"use client";

import { useEffect, useState } from "react";

export function useSession(): string {
  const [sessionId, setSessionId] = useState("");

  useEffect(() => {
    const existing = localStorage.getItem("scriptureguard_session_id");
    if (existing) {
      setSessionId(existing);
      return;
    }
    const created = crypto.randomUUID();
    localStorage.setItem("scriptureguard_session_id", created);
    setSessionId(created);
  }, []);

  return sessionId;
}
