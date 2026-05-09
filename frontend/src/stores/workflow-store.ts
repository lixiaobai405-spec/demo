import { create } from "zustand";

interface WorkflowState {
  activeTab: "student" | "instructor";
  setActiveTab: (t: "student" | "instructor") => void;
}

export const useWorkflowStore = create<WorkflowState>((set) => ({
  activeTab: "student",
  setActiveTab: (t) => set({ activeTab: t }),
}));
