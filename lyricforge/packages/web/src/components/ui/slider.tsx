import { cn } from "@/lib/utils";

type SliderProps = React.InputHTMLAttributes<HTMLInputElement> & { label?: string };

export function Slider({ label, className, ...props }: SliderProps) {
  return (
    <label className="block space-y-2">
      {label && <span className="text-xs text-white/70">{label}</span>}
      <input
        type="range"
        className={cn(
          "w-full h-2 bg-white/10 rounded-lg appearance-none cursor-pointer",
          "accent-primary",
          className
        )}
        {...props}
      />
    </label>
  );
}
