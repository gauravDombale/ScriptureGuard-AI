export type Denomination =
  | "protestant"
  | "catholic"
  | "orthodox"
  | "evangelical"
  | "non_denominational";

export type VerseCitation = {
  reference: string;
  text: string;
  verified: boolean;
};

export type ChatRequest = {
  session_id: string;
  message: string;
  denomination: Denomination;
  mode: "text" | "image";
};

export type ChatResponse = {
  session_id: string;
  response: string;
  citations: VerseCitation[];
  image_url: string | null;
  safety_blocked: boolean;
  block_reason: string | null;
  denomination_notes: string | null;
  retrieval_score: number | null;
};

export type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
  citations: VerseCitation[];
  imageUrl?: string | null;
  blocked?: boolean;
  isStreaming?: boolean;
  streamStatus?: string;
  isImageLoading?: boolean;
  prompt?: string;
};
