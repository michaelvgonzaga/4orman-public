Suppress 4orman-tools hook activity from the terminal.

```bash
echo 1 > ~/.4orman/4orman-quiet && echo "4orman-tools hook activity: silent"
```

Hooks still run and inject ground-truth context into compaction — only the terminal notification is suppressed.

Use `/4orman-watch` to make hook activity visible again.
