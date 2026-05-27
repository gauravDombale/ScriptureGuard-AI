import type { Denomination } from "@/types";

const OPTIONS: { value: Denomination; label: string }[] = [
  { value: "protestant", label: "Protestant" },
  { value: "catholic", label: "Catholic" },
  { value: "orthodox", label: "Orthodox" },
  { value: "evangelical", label: "Evangelical" },
  { value: "non_denominational", label: "Non-denominational" },
];

type Props = {
  value: Denomination;
  onChange: (value: Denomination) => void;
};

export function DenominationPicker({ value, onChange }: Props) {
  return (
    <label className="flex items-center gap-2 text-sm text-[#3c3933]">
      <span>Lens</span>
      <select
        value={value}
        onChange={(event) => onChange(event.target.value as Denomination)}
        className="h-10 rounded-md border border-[#bdb3a2] bg-white px-3 text-sm text-[#1c1b18] outline-none focus:border-[#2f6f61]"
      >
        {OPTIONS.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </label>
  );
}
