import { ShieldAlert } from "lucide-react";

type Props = {
  message: string;
};

export function SafetyBanner({ message }: Props) {
  return (
    <div className="flex gap-2 rounded-md border border-[#d29b70] bg-[#fff4e8] p-3 text-sm text-[#5f3518]">
      <ShieldAlert aria-hidden="true" className="mt-0.5 shrink-0" size={18} />
      <p>{message}</p>
    </div>
  );
}
