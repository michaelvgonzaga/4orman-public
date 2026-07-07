Toggle autopilot for the rest of this terminal session.

`4orman-ai` already asked once at launch and set the mode for this session (`$FOREMAN_MODE`, shown in the splash). This command flips it mid-session without needing a new terminal.

Check the current value, flip it, and confirm to the user in one line:

- If `$FOREMAN_MODE` is `autopilot` (or unset — default is autopilot): switch to **gate mode** — from now on, surface a proposal and wait for explicit yes/no before acting, instead of deciding and building silently.
- If `$FOREMAN_MODE` is `gate`: switch to **autopilot** — go back to deciding and announcing in one sentence, then building, per the standing autopilot preference.

This only affects the running conversation — it is not written to disk, and closing the terminal resets it to asking again next launch. Say `/gate` again to flip back.
