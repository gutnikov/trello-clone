---
name: setup-slack
description: Configure Slack bot for chat-first interaction with Orca
dependencies: []
docs:
  - docs/guides/workflow-customization.md
---

# Setup: Slack Bot

## Detect

Check for existing Slack configuration:

- `slack:` section in WORKFLOW.md frontmatter
- `SLACK_BOT_TOKEN` and `SLACK_APP_TOKEN` in `.env`

Report "configured" if both tokens are present and the config section exists. Report "not configured" otherwise.

## Propose

Guide the user through creating and configuring a Slack app. Present each section one at a time and wait for confirmation before moving on.

### Step 1: Create the Slack App

1. Open https://api.slack.com/apps in your browser
2. Click **Create New App**
3. Choose **From an app manifest**
4. Select the workspace you want to install the bot in
5. Switch to the **YAML** tab and paste this manifest:

```yaml
display_information:
  name: Orca
  description: AI orchestration assistant for your development team
  background_color: "#1a1a2e"
features:
  bot_user:
    display_name: Orca
    always_online: true
oauth_config:
  scopes:
    bot:
      - chat:write
      - app_mentions:read
      - im:history
      - im:read
      - im:write
      - channels:history
      - channels:read
      - groups:history
      - groups:read
settings:
  event_subscriptions:
    bot_events:
      - message.im
      - app_mention
  interactivity:
    is_enabled: false
  org_deploy_enabled: false
  socket_mode_enabled: true
```

6. Click **Next**, review the summary, then click **Create**

### Step 2: Understand the Permissions

The manifest requests these bot token scopes. Explain each to the user:

| Scope | Why Orca Needs It |
|-------|-------------------|
| `chat:write` | Send messages and replies in threads |
| `app_mentions:read` | Detect when someone @mentions the bot in a channel |
| `im:history` | Read DM conversation history (for thread context) |
| `im:read` | Know when a DM channel is opened with the bot |
| `im:write` | Send DMs back to users |
| `channels:history` | Read messages in public channels where the bot is mentioned |
| `channels:read` | See which public channels the bot has been added to |
| `groups:history` | Read messages in private channels where the bot is invited |
| `groups:read` | See which private channels the bot has been added to |

And these event subscriptions:

| Event | What It Does |
|-------|-------------|
| `message.im` | Fires when someone sends a DM to the bot |
| `app_mention` | Fires when someone @mentions the bot in any channel |

**Socket Mode** is enabled so the bot connects via WebSocket — no public URL needed. This is ideal for running Orca locally on your machine.

### Step 3: Install to Workspace

1. In the app settings, go to **Install App** in the left sidebar
2. Click **Install to Workspace**
3. Review the permissions and click **Allow**
4. You should see a green checkmark confirming installation

### Step 4: Get the Bot Token

1. After installing, you'll be on the **OAuth & Permissions** page
2. Copy the **Bot User OAuth Token** — it starts with `xoxb-`
3. Save this somewhere safe (you'll need it in a moment)

This token lets Orca send and receive messages as the bot.

### Step 5: Enable Socket Mode and Get the App Token

1. Go to **Settings** > **Basic Information** in the left sidebar
2. Scroll down to **App-Level Tokens**
3. Click **Generate Token and Scopes**
4. Name: `orca-socket`
5. Click **Add Scope** and select `connections:write`
6. Click **Generate**
7. Copy the token — it starts with `xapp-`
8. Save this alongside the bot token

This token lets Orca establish the WebSocket connection to Slack.

### Step 6: Verify Socket Mode is On

1. Go to **Settings** > **Socket Mode** in the left sidebar
2. Confirm the toggle is **ON** (it should be if you used the manifest)
3. If it's off, turn it on

### Step 7: Verify Event Subscriptions

1. Go to **Features** > **Event Subscriptions** in the left sidebar
2. Confirm the toggle is **ON**
3. Under **Subscribe to bot events**, confirm both are listed:
   - `message.im`
   - `app_mention`
4. If either is missing, click **Add Bot User Event** and add it, then click **Save Changes**

### Step 8: Invite the Bot to Channels (Optional)

The bot automatically works in DMs. For channel @mentions to work:

1. Go to the Slack channel where you want to use the bot
2. Type `/invite @Orca` or click the channel name > **Integrations** > **Add apps** > search "Orca"
3. The bot can now respond to @mentions in that channel

Ask the user to provide both tokens (the `xoxb-` bot token and the `xapp-` app token) before proceeding.

## Configure

Once the user provides both tokens:

### 1. Add Slack config to WORKFLOW.md

Add the `slack:` section to the YAML frontmatter, before the closing `---`:

```yaml
slack:
  bot_token: $SLACK_BOT_TOKEN
  app_token: $SLACK_APP_TOKEN
  session_timeout_ms: 1800000       # 30 min idle timeout per thread
  max_sessions_per_user: 5          # max concurrent threads per user
```

The `$SLACK_BOT_TOKEN` and `$SLACK_APP_TOKEN` are resolved from environment variables at startup.

### 2. Store tokens in `.env`

Write the actual token values to the `.env` file in the project root:

```
SLACK_BOT_TOKEN=xoxb-your-actual-token-here
SLACK_APP_TOKEN=xapp-your-actual-token-here
```

**Never commit tokens to git.** The `.env` file must stay local.

### 3. Ensure `.env` is gitignored

Check `.gitignore` for a `.env` entry. If missing, add it:

```
.env
```

## Verify

### 1. Start Orca

```bash
orca WORKFLOW.md
```

Look for these log lines:
- `MCP tool server started on port XXXXX` — MCP tools are available
- `Slack bot connected` — Socket Mode WebSocket is active

If you see `Slack bot connected`, the bot is live.

### 2. Test DM

1. Open Slack
2. Find the **Orca** bot in your DM list (search "Orca" in the sidebar)
3. Send a message like "hello"
4. You should see a `_Thinking..._` reply that updates with the response

### 3. Test Channel Mention

1. Go to a channel where the bot is invited
2. Type `@Orca what can you do?`
3. The bot should reply in a thread

### 4. Test Orca Tools

In a DM with the bot, try:
- "Show me the current orchestrator status" — tests `orca_status` tool
- "List all issues in Scoping state" — tests `orca_list_issues` tool
- "Create an issue titled 'Test issue'" — tests `orca_create_issue` tool

### Troubleshooting

| Problem | Fix |
|---------|-----|
| No "Slack bot connected" log | Check `SLACK_BOT_TOKEN` and `SLACK_APP_TOKEN` in `.env`. Verify Socket Mode is enabled in the app settings. |
| Bot doesn't respond to DMs | Check **Event Subscriptions** has `message.im`. Reinstall the app if events were added after initial install. |
| Bot doesn't respond to @mentions | Invite the bot to the channel with `/invite @Orca`. Check `app_mention` event subscription. |
| "Slack API error: invalid_auth" | The bot token is wrong or expired. Generate a new one from **OAuth & Permissions**. |
| "Slack API error: not_allowed_token_type" | You're using the app token where the bot token is expected (or vice versa). `xoxb-` = bot token, `xapp-` = app token. |

## Docs Update

Update `docs/guides/workflow-customization.md` — add a Slack section:

```markdown
### Slack Bot

Orca includes an optional Slack bot for chat-first interaction. Configure it with `/orca setup-slack`.

The bot supports:
- **DMs:** Message the Orca bot directly for private conversations
- **Channel mentions:** @Orca in any channel for shared context
- **Full Orca integration:** Create issues, check status, trigger dispatches via natural language

Configuration is in the `slack:` section of WORKFLOW.md. Tokens are stored in `.env`.
```

## Definition of Done

- [ ] Slack app created at api.slack.com with correct scopes and Socket Mode
- [ ] `slack:` section present in WORKFLOW.md
- [ ] Tokens stored in `.env` (not committed to git)
- [ ] `.env` is in `.gitignore`
- [ ] Orca starts with "Slack bot connected" in logs
- [ ] Bot responds to DMs
- [ ] `docs/guides/workflow-customization.md` has Slack section
