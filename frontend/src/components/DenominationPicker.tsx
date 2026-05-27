import type { Denomination } from "@/types";
import { Select } from "./ui/Select";

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
    <label className="flex items-center gap-2 text-sm font-medium text-[#374151]">
      <span className="text-[#6b7280]">Lens</span>
      <Select
        value={value}
        onChange={(event) => onChange(event.target.value as Denomination)}
        className="w-[190px]"
      >
        {OPTIONS.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </Select>
    </label>
  );
}
