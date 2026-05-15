import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { Button } from "@/components/ui/button";

describe("Button", () => {
  it("keeps loading buttons visually active instead of dimming them as disabled", () => {
    render(
      <Button loading variant="default">
        生成差异化竞争力分析
      </Button>,
    );

    const button = screen.getByRole("button", {
      name: "生成差异化竞争力分析",
    });

    expect(button).toHaveAttribute("aria-busy", "true");
    expect(button).toHaveAttribute("aria-disabled", "true");
    expect(button).not.toHaveAttribute("disabled");
    expect(button.className).not.toContain("opacity-50");
  });
});
