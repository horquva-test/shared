
import { mkdir, writeFile } from "node:fs/promises";
import { dirname } from "node:path";

export type ConfirmationAnswer = "yes" | "no" | "don't know";

export interface ConfirmationQuestions {
  backup: ConfirmationAnswer;
  criticality: ConfirmationAnswer;
  documented: ConfirmationAnswer;
  fallback: ConfirmationAnswer;
}

export interface ConfirmationRequest {
  asset_id: string;
  owner_email: string;
  questions: ConfirmationQuestions;
}

export interface ConfirmationResponse {
  asset_id: string;
  owner_email: string;
  answered_at: string;
  answers: ConfirmationQuestions;
  prior_values: Partial<ConfirmationQuestions>;
}

export interface CampaignAsset {
  asset_id: string;
  owner_name: string;
  owner_email: string;
}

export function createConfirmationResponse(
  request: ConfirmationRequest,
  answers: ConfirmationQuestions,
  prior_values: Partial<ConfirmationQuestions>,
  answeredAt: Date = new Date()
): ConfirmationResponse {
  if (!request.asset_id.trim()) {
    throw new Error("asset_id is required");
  }

  if (!request.owner_email.trim()) {
    throw new Error("owner_email is required");
  }

  return {
    asset_id: request.asset_id,
    owner_email: request.owner_email,
    answered_at: answeredAt.toISOString(),
    answers: { ...answers },
    prior_values: { ...prior_values },
  };
}

export function launchConfirmationCampaign(
  assets: CampaignAsset[]
): ConfirmationRequest[] {
  return assets.map((asset) => ({
    asset_id: asset.asset_id,
    owner_email: asset.owner_email,
    questions: {
      backup: "don't know",
      criticality: "don't know",
      documented: "don't know",
      fallback: "don't know",
    },
  }));
}

export async function saveCampaignResults(
  filePath: string,
  responses: ConfirmationResponse[]
): Promise<void> {
  await mkdir(dirname(filePath), { recursive: true });

  await writeFile(
    filePath,
    JSON.stringify(responses, null, 2),
    "utf-8"
  );
}
