# Domain Research

**Works well for:** Getting smart about an unfamiliar field before building for it — legal, healthcare, trades, retail, or any domain you haven't worked in before
**Confidence:** High — standard research methodology, not domain-specific

## The pattern

Before writing any code or detailed spec for a domain you don't know well, run this research sequence:

1. **Map the workflow** — How does a professional in this field actually spend their day? What are the recurring tasks, handoffs, and pain points?

2. **Identify the vocabulary** — Every domain has terms of art. Legal has "discovery", "pleadings", "retainer". Plumbing has "rough-in", "P-trap", "GPM". Healthcare has "SOAP notes", "intake", "prior auth".

3. **Find the regulations** —
   - Legal: unauthorized practice of law, jurisdiction-specific rules
   - Healthcare: HIPAA, state licensing, scope of practice
   - Finance: SOC2, PCI-DSS, fiduciary rules
   - Trades: local codes, bonding/insurance requirements

4. **Identify what already exists** — What tools do professionals in this field already use? What are they forced to use vs. what do they hate? Don't replace something they love; find the gaps.

5. **Validate one assumption** — Before writing the full spec, identify the single biggest assumption you're making about how this domain works. Validate it by: asking the user directly if they're present, checking `_knowledgebase/` for existing research, or flagging it as a Risk in the spec if it can't be validated before building.

## When to use it

- The user is from a domain you haven't worked in before
- The spec has domain-specific compliance risks flagged
- The user says "people in my field do X" without explaining why

## When NOT to use it

- The user is the domain expert and is present to answer questions — ask them directly; their answers are more reliable than external research
- The domain is already well-represented in `_knowledgebase/` — read those files instead of re-researching from scratch
