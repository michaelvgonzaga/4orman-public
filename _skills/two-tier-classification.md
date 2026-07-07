# Two-Tier Classification

**Works well for:** Any system with multiple specialist handlers where routing accuracy matters — AI diagnosis tools, support ticket routing, document processing pipelines, code review systems, multi-agent orchestration
**Confidence:** High — clean separation between routing and processing; graceful degradation validated in critic review

## The pattern

**Tier 1 — Classifier:** A single small call whose only job is to return a domain key. Prompt is extremely constrained: list of valid keys, "respond with one word, no explanation." Fast and cheap.

**Tier 2 — Specialist:** The full processing call, using a system prompt composed of `base_prompt + domain_addendum`. The domain addendum adds expertise for the classified domain without changing the core instructions.

```python
def classify(self, content: str) -> str:
    user_prompt = CLASSIFICATION_TEMPLATE.format(content=content[:3000])
    try:
        result = self.complete(CLASSIFICATION_SYSTEM, user_prompt).strip().lower()
        if result not in VALID_KEYS:
            print(f"Warning: unrecognized domain '{result}'. Falling back to default.", file=sys.stderr)
            return DEFAULT_KEY
        return result
    except Exception as e:
        print(f"Warning: classification failed ({e}). Falling back to default. Use --domain to set manually.", file=sys.stderr)
        return DEFAULT_KEY

def build_system_prompt(domain_key: str) -> str:
    addendum = DOMAINS[domain_key].get("addendum", "")
    return BASE_PROMPT + ("\n\n---\n\n" + addendum if addendum else "")
```

### Key rules

1. **Classifier prompt must be maximally constrained.** List every valid key. Say "one word only, no punctuation, no explanation." Any ambiguity produces verbose output that fails the `result in VALID_KEYS` check.

2. **Always truncate input for classification.** The classifier doesn't need the full context — `content[:3000]` is enough to identify domain. Full input is passed to the specialist tier only.

3. **Fallback must be visible, not silent.** When classification fails or returns an unrecognized key, print a warning to stderr and tell the user how to override manually (`--framework`, `--domain`, etc.). Silent fallback to a generic handler misleads users debugging routing issues.

4. **Manual override flag is required.** Users must be able to bypass auto-classification (`--framework wordpress`). Auto-classification is a convenience, not a constraint.

5. **Domain addendums extend the base prompt, they don't replace it.** `base + addendum` keeps core behavior (output format, guardrails, quality checks) consistent across all domains. A domain that fully replaces the base prompt risks losing safety constraints.

6. **Keep the domain list small and stable.** Classification accuracy degrades as the number of keys grows. 5–8 domains is manageable; 20+ requires a different approach (hierarchical classification or embeddings).

### Classification system prompt template

```
You are a [type] classifier. Classify the submitted [input] into exactly one domain.

Respond with exactly one word from this list:
- key-a   (description of when this applies)
- key-b   (description of when this applies)
- key-c   (description of when this applies)
- default (anything that does not clearly fit the above)

One word only. No punctuation. No explanation.
```

## When to use it

- Input can belong to one of several distinct specialist domains
- Each domain benefits from different background knowledge or instructions
- Routing must be automated (user shouldn't have to specify the domain every time)
- The number of domains is small enough to enumerate (≤8)

## When NOT to use it

- There is only one domain — the classification tier adds latency with no benefit
- Domains are not mutually exclusive — overlapping domains need a different routing strategy (e.g., multi-label classification, ranked handlers)
- Classification accuracy is safety-critical — a misclassified medical or legal query routed to the wrong specialist could cause real harm; use explicit user confirmation instead of auto-routing
- Input is so short that the classifier has no reliable signal (< 50 tokens)

## Results

- **Support-bot** — 5 domains (billing, technical, account, feedback, general); all test inputs routed correctly on first attempt; critic caught silent fallback bug, fixed before shipping.
