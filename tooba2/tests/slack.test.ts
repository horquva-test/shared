
import { describe, it, expect, vi } from "vitest";
import { SlackConnector } from "../src/connectors/slack.js";

describe("SlackConnector", () => {
  it("returns an empty list when there are no users", async () => {
    const mockClient = {
      users: {
        list: vi.fn().mockResolvedValue({
          members: [],
          response_metadata: { next_cursor: "" },
        }),
      },
      conversations: {
        list: vi.fn(),
        members: vi.fn(),
      },
    };

    const connector = new SlackConnector(mockClient as never);
    const users = await connector.fetchUsers();

    expect(users).toEqual([]);
    expect(mockClient.users.list).toHaveBeenCalledTimes(1);
  });

  it("returns users from multiple pages", async () => {
    const mockClient = {
      users: {
        list: vi
          .fn()
          .mockResolvedValueOnce({
            members: [{ id: "U001" }],
            response_metadata: { next_cursor: "next-page" },
          })
          .mockResolvedValueOnce({
            members: [{ id: "U002" }],
            response_metadata: { next_cursor: "" },
          }),
      },
      conversations: {
        list: vi.fn(),
        members: vi.fn(),
      },
    };

    const connector = new SlackConnector(mockClient as never);
    const users = await connector.fetchUsers();

    expect(users.map((user) => user.id)).toEqual(["U001", "U002"]);
    expect(mockClient.users.list).toHaveBeenCalledTimes(2);
  });

  it("returns channels from multiple pages", async () => {
    const mockClient = {
      users: { list: vi.fn() },
      conversations: {
        list: vi
          .fn()
          .mockResolvedValueOnce({
            channels: [{ id: "C001" }],
            response_metadata: { next_cursor: "next-page" },
          })
          .mockResolvedValueOnce({
            channels: [{ id: "C002" }],
            response_metadata: { next_cursor: "" },
          }),
        members: vi.fn(),
      },
    };

    const connector = new SlackConnector(mockClient as never);
    const channels = await connector.fetchChannels();

    expect(channels.map((channel) => channel.id)).toEqual([
      "C001",
      "C002",
    ]);
    expect(mockClient.conversations.list).toHaveBeenCalledTimes(2);
  });

  it("returns channel members from multiple pages", async () => {
    const mockClient = {
      users: { list: vi.fn() },
      conversations: {
        list: vi.fn(),
        members: vi
          .fn()
          .mockResolvedValueOnce({
            members: ["U001"],
            response_metadata: { next_cursor: "next-page" },
          })
          .mockResolvedValueOnce({
            members: ["U002"],
            response_metadata: { next_cursor: "" },
          }),
      },
    };

    const connector = new SlackConnector(mockClient as never);
    const members = await connector.fetchChannelMembers("C001");

    expect(members).toEqual(["U001", "U002"]);
    expect(mockClient.conversations.members).toHaveBeenCalledTimes(2);
  });

  it("retries when Slack returns a rate-limit error", async () => {
    const connector = new SlackConnector({} as never);

    const rateLimitError = Object.assign(
      new Error("Rate limited"),
      {
        statusCode: 429,
        retryAfter: 0.001,
      }
    );

    const operation = vi
      .fn()
      .mockRejectedValueOnce(rateLimitError)
      .mockResolvedValueOnce("success");

    const result = await connector.withRetry(operation);

    expect(result).toBe("success");
    expect(operation).toHaveBeenCalledTimes(2);
  });
});
