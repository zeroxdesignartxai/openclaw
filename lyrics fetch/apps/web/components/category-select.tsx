"use client";
import { useState } from "react";

type Props = { onChange: (val: string | null) => void };

export default function CategorySelect({ onChange }: Props) {
  const [value, setValue] = useState<string | null>(null);
  return (
    <select
      className="rounded border border-gray-700 bg-gray-900 px-3 py-2 text-sm"
      value={value || ""}
      onChange={(e) => {
        const v = e.target.value || null;
        setValue(v);
        onChange(v);
      }}
    >
      <option value="">Auto-detect</option>
      <option value="software">Software</option>
      <option value="electronics">Electronics</option>
      <option value="service-providers">Service providers</option>
    </select>
  );
}
