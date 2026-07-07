Show 4orman-tools hook activity in the terminal.

```bash
echo 0 > ~/.4orman/4orman-quiet && echo "4orman-tools hook activity: visible"
```

After running this, each compaction shows a terminal notification:
`4orman-tools session-snapshot v<version> — next: <current step>`

Use `/4orman-quiet` to suppress it.
