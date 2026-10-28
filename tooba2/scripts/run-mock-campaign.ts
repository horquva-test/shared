
import { readFile } from "node:fs/promises";
import { resolve } from "node:path";
import {
  createConfirmationResponse,
  launchConfirmationCampaign,
  saveCampaignResults,
  type CampaignAsset,
  type ConfirmationQuestions,
} from "../src/campaign/confirmation.js";

const assetsPath = resolve("data/campaign-assets.json");
const resultsPath = resolve("data/campaign-results.json");

async function main(): Promise<void> {
  const fileContent = await readFile(assetsPath, "utf-8");
  const assets = JSON.parse(fileContent) as CampaignAsset[];

  // Create campaign requests with "don't know" as the initial answers.
  const requests = launchConfirmationCampaign(assets);

  // Mock only: these are synthetic records, not real owner responses.
  const mockAnswers: ConfirmationQuestions = {
    backup: "don't know",
    criticality: "don't know",
    documented: "don't know",
    fallback: "don't know",
  };

  const responses = requests.map((request, index) =>
    createConfirmationResponse(
      request,
      mockAnswers,
      {},
      new Date(Date.UTC(2026, 9, 23, 12, index, 0))
    )
  );

  await saveCampaignResults(resultsPath, responses);

  console.log(`Mock campaign requests created: ${requests.length}`);
  console.log(`Synthetic result records saved to: ${resultsPath}`);
  console.log("No Slack messages or emails were sent.");
}

main().catch((error: unknown) => {
  console.error("Mock campaign failed:", error);
  process.exitCode = 1;
});
