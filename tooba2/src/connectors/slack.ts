
import { WebClient } from "@slack/web-api";

type SlackClient = Pick<WebClient, "users" | "conversations">;

export class SlackConnector {
  private readonly client: SlackClient;
  private readonly maxRetries = 5;
  private readonly baseDelayMs = 1000;

  constructor(tokenOrClient: string | WebClient) {
    this.client =
      typeof tokenOrClient === "string"
        ? new WebClient(tokenOrClient)
        : tokenOrClient;
  }

  async withRetry<T>(
    operation: () => Promise<T>
  ): Promise<T> {
    for (let attempt = 0; ; attempt++) {
      try {
        return await operation();
      } catch (error: unknown) {
        const err = error as {
          code?: string;
          statusCode?: number;
          retryAfter?: number;
          data?: { retry_after?: number };
          headers?: Record<string, string | number | undefined>;
      };

        const isRateLimited =
          err.statusCode === 429 ||
          err.code === "slack_webapi_rate_limited_error";

        if (!isRateLimited || attempt >= this.maxRetries) {
          throw error;
        }

        const headerDelay = Number(err.headers?.["retry-after"]);
        const retryAfter =
          err.retryAfter ??
          err.data?.retry_after ??
          (Number.isFinite(headerDelay) && headerDelay > 0
            ? headerDelay
            : undefined);

        const delayMs =
          retryAfter !== undefined && retryAfter > 0
            ? retryAfter * 1000
            : this.baseDelayMs * 2 ** attempt;

        await new Promise<void>((resolve) =>
          setTimeout(resolve, delayMs)
        );
      }
    }
  }

  async fetchUsers() {
    const all: NonNullable<
      Awaited<ReturnType<WebClient["users"]["list"]>>["members"]
    > = [];

    let cursor: string | undefined;

    do {
      const response = await this.withRetry(() =>
        this.client.users.list({
          ...(cursor ? { cursor } : {}),
          limit: 200,
        })
      );

      all.push(...(response.members ?? []));
      cursor = response.response_metadata?.next_cursor || undefined;
    } while (cursor);

    return all;
  }

  async fetchChannels() {
    const all: NonNullable<
      Awaited<ReturnType<WebClient["conversations"]["list"]>>["channels"]
    > = [];

    let cursor: string | undefined;

    do {
      const response = await this.withRetry(() =>
        this.client.conversations.list({
          ...(cursor ? { cursor } : {}),
          limit: 200,
          types: "public_channel,private_channel",
          exclude_archived: true,
        })
      );

      all.push(...(response.channels ?? []));
      cursor = response.response_metadata?.next_cursor || undefined;
    } while (cursor);

    return all;
  }

  async fetchChannelMembers(channelId: string) {
    const all: NonNullable<
      Awaited<ReturnType<WebClient["conversations"]["members"]>>["members"]
    > = [];

    let cursor: string | undefined;

    do {
      const response = await this.withRetry(() =>
        this.client.conversations.members({
          channel: channelId,
          ...(cursor ? { cursor } : {}),
          limit: 200,
        })
      );

      all.push(...(response.members ?? []));
      cursor = response.response_metadata?.next_cursor || undefined;
    } while (cursor);

    return all;
  }
}
