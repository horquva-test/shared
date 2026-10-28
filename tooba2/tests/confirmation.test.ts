
import { describe, it, expect } from "vitest";
import {
  createConfirmationResponse,
  launchConfirmationCampaign,
  type ConfirmationRequest,
  type ConfirmationQuestions,
  type CampaignAsset,
} from "../src/campaign/confirmation.js";

describe("Confirmation Campaign", () => {
  const request: ConfirmationRequest = {
    asset_id: "ASSET-001",
    owner_email: "owner@example.test",
    questions: {
      backup: "yes",
      criticality: "yes",
      documented: "no",
      fallback: "don't know",
    },
  };

  const answers: ConfirmationQuestions = {
    backup: "yes",
    criticality: "no",
    documented: "yes",
    fallback: "don't know",
  };

  it("creates a response with owner, asset and timestamp", () => {
    const response = createConfirmationResponse(
      request,
      answers,
      {},
      new Date("2026-10-23T10:00:00.000Z")
    );

    expect(response.asset_id).toBe("ASSET-001");
    expect(response.owner_email).toBe("owner@example.test");
    expect(response.answered_at).toBe("2026-10-23T10:00:00.000Z");
  });

  it("supports don't know answers", () => {
    const response = createConfirmationResponse(
      request,
      answers,
      {}
    );

    expect(response.answers.fallback).toBe("don't know");
  });

  it("preserves prior values", () => {
    const priorValues = {
      backup: "no" as const,
      documented: "yes" as const,
    };

    const response = createConfirmationResponse(
      request,
      answers,
      priorValues
    );

    expect(response.prior_values).toEqual(priorValues);
  });

  it("rejects an empty asset ID", () => {
    expect(() =>
      createConfirmationResponse(
        { ...request, asset_id: " " },
        answers,
        {}
      )
    ).toThrow("asset_id is required");
  });

  it("rejects an empty owner email", () => {
    expect(() =>
      createConfirmationResponse(
        { ...request, owner_email: "" },
        answers,
        {}
      )
    ).toThrow("owner_email is required");
  });

  it("creates confirmation requests for all five assets", () => {
    const assets: CampaignAsset[] = [
      {
        asset_id: "ASSET-001",
        owner_name: "Natasha Khan",
        owner_email: "natasha.khan@example.test",
      },
      {
        asset_id: "ASSET-002",
        owner_name: "Kia Vang",
        owner_email: "kia.vang@example.test",
      },
      {
        asset_id: "ASSET-003",
        owner_name: "Imaan Siddiqui",
        owner_email: "imaan.siddiqui@example.test",
      },
      {
        asset_id: "ASSET-004",
        owner_name: "Affan Ahmed Khan",
        owner_email: "affan.ahmed.khan@example.test",
      },
      {
        asset_id: "ASSET-005",
        owner_name: "Muhammad Ibrahim Shaikh",
        owner_email: "muhammad.ibrahim.shaikh@example.test",
      },
    ];

    const requests = launchConfirmationCampaign(assets);

    expect(requests).toHaveLength(5);
    expect(requests.map((item) => item.asset_id)).toEqual([
      "ASSET-001",
      "ASSET-002",
      "ASSET-003",
      "ASSET-004",
      "ASSET-005",
    ]);

    expect(requests[0]?.questions.backup).toBe("don't know");
  });
});
