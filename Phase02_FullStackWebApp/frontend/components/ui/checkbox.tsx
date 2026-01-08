"use client"

import * as React from "react"
import * as CheckboxPrimitive from "@radix-ui/react-checkbox"
import { CheckIcon } from "lucide-react"

import { cn } from "@/lib/utils"

function Checkbox({
  className,
  ...props
}: React.ComponentProps<typeof CheckboxPrimitive.Root>) {
  return (
    <CheckboxPrimitive.Root
      data-slot="checkbox"
      className={cn(
        "peer h-4 w-4 shrink-0 rounded-[4px] border-2 border-gray-400 bg-white shadow-xs transition-all outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 dark:border-gray-500 dark:bg-gray-900 dark:focus-visible:ring-offset-gray-950 data-[state=checked]:border-[#6366F1] data-[state=checked]:bg-[#6366F1] data-[state=checked]:text-white dark:data-[state=checked]:border-[#4a5ab8] dark:data-[state=checked]:bg-[#4a5ab8] dark:data-[state=checked]:text-white focus-visible:ring-[#6366F1] dark:focus-visible:ring-[#4a5ab8] aria-invalid:border-destructive aria-invalid:ring-destructive/20 dark:aria-invalid:border-destructive dark:aria-invalid:ring-destructive/40",
        className
      )}
      {...props}
    >
      <CheckboxPrimitive.Indicator
        data-slot="checkbox-indicator"
        className="flex items-center justify-center text-current transition-none"
      >
        <CheckIcon className="h-3.5 w-3.5" />
      </CheckboxPrimitive.Indicator>
    </CheckboxPrimitive.Root>
  )
}

export { Checkbox }
