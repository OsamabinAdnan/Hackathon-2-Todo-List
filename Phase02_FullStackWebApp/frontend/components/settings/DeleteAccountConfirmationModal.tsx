'use client';

import { AlertTriangleIcon, CheckIcon, XIcon } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

interface DeleteAccountConfirmationModalProps {
  isOpen: boolean;
  onConfirm: () => void;
  onCancel: () => void;
}

export function DeleteAccountConfirmationModal({
  isOpen,
  onConfirm,
  onCancel,
}: DeleteAccountConfirmationModalProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-2 xs:p-4">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-background/80 backdrop-blur-xl animate-in fade-in duration-200"
        onClick={onCancel}
      />

      {/* Modal */}
      <div className="relative w-full max-w-md bg-card border border-border/50 rounded-2xl xs:rounded-3xl shadow-2xl p-4 xs:p-6 animate-in zoom-in-95 duration-200">
        {/* Warning Icon */}
        <div className="flex justify-center mb-4 xs:mb-6">
          <div className="w-16 h-16 xs:w-20 xs:h-20 rounded-full bg-danger/10 flex items-center justify-center border border-danger/20">
            <AlertTriangleIcon className="h-8 w-8 xs:h-10 xs:w-10 text-danger" />
          </div>
        </div>

        {/* Title */}
        <h2 className="text-xl xs:text-2xl font-extrabold text-foreground text-center mb-2 tracking-tight">
          Delete Account?
        </h2>

        {/* Disclaimer */}
        <div className="bg-destructive/5 border border-destructive/20 rounded-xl p-3 xs:p-4 mb-4 xs:mb-6">
          <p className="text-sm text-destructive font-medium text-center">
            This action cannot be undone. This will permanently delete your account and remove all your data.
          </p>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-2 xs:gap-3">
          <Button
            onClick={onCancel}
            variant="outline"
            className="flex-1 py-2.5 xs:py-3 rounded-xl border-border/50 hover:bg-accent transition-all font-bold text-sm"
          >
            <XIcon className="h-4 w-4 mr-2" />
            No, Keep It
          </Button>
          <Button
            onClick={onConfirm}
            className="flex-1 py-2.5 xs:py-3 rounded-xl bg-danger text-danger-foreground hover:bg-danger/90 transition-all font-bold text-sm shadow-lg shadow-danger/20"
          >
            <CheckIcon className="h-4 w-4 mr-2" />
            Yes, Delete
          </Button>
        </div>
      </div>
    </div>
  );
}
