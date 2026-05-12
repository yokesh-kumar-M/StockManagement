import { cva, type VariantProps } from "class-variance-authority";
import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";

const badgeVariants = cva(
  "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold transition-colors",
  {
    variants: {
      variant: {
        default: "bg-cyan-500/20 text-cyan-400 border border-cyan-500/30",
        success: "bg-green-500/20 text-green-400 border border-green-500/30",
        destructive: "bg-red-500/20 text-red-400 border border-red-500/30",
        warning: "bg-yellow-500/20 text-yellow-400 border border-yellow-500/30",
        outline: "border border-gray-600 text-gray-300",
      },
    },
    defaultVariants: { variant: "default" },
  }
);

interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

export function Badge({ className, variant, ...props }: BadgeProps) {
  return <div className={twMerge(clsx(badgeVariants({ variant }), className))} {...props} />;
}
