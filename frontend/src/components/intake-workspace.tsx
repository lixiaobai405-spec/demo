"use client";

import { IntakeImportSection } from "@/components/intake-import-section";
import { IntakeSessionRecall } from "@/components/intake-session-recall";
import { IntakePrefillDisplay } from "@/components/intake-prefill-display";
import { IntakeConfirmationForm } from "@/components/intake-confirmation-form";

export function IntakeWorkspace() {
  return (
    <section className="grid gap-6 xl:grid-cols-[1.05fr_0.95fr]">
      <div className="flex flex-col gap-6">
        <IntakeImportSection />
        <IntakeSessionRecall />
      </div>
      <div className="flex flex-col gap-6">
        <IntakePrefillDisplay />
        <IntakeConfirmationForm />
      </div>
    </section>
  );
}
