import { cn } from "@/lib/utils";
import { type ButtonHTMLAttributes, forwardRef } from "react";

export type ButtonVariant = "primary" | "ghost" | "outline";

export const Button = forwardRef<HTMLButtonElement, ButtonHTMLAttributes<HTMLButtonElement> & { variant?: ButtonVariant }>(
  ({ className, variant = "primary", ...props }, ref) => {
    const styles: Record<ButtonVariant, string> = {
      primary: "bg-primary text-white hover:bg-primary/90",
      ghost: "bg-white/5 hover:bg-white/10 text-white",
      outline: "border border-white/20 text-white hover:border-white/50"
    };
    return <button ref={ref} className={cn("px-4 py-2 rounded-lg text-sm transition", styles[variant], className)} {...props} />;
  }
);
Button.displayName = "Button";
