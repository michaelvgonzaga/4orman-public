# Vendor-Neutral Adapter Pattern

**Works well for:** CLI tools, APIs, or agents that call an external service (AI provider, payment processor, SMS gateway, etc.) where the provider may change, multiple providers need to coexist, or lock-in is a design risk
**Confidence:** High — clean extension point; OpenAI support added in M3 with zero changes to the rest of the codebase

## The pattern

```python
class [Service]Adapter:
    DEFAULT_MODELS = {
        "provider-a": "model-name-a",
        "provider-b": "model-name-b",
    }

    def __init__(self, provider: str, model: str | None, api_key: str):
        self.provider = provider.lower()
        self.model = model or self.DEFAULT_MODELS.get(self.provider)
        self.api_key = api_key

    def [operation](self, *args) -> [return_type]:
        if self.provider == "provider-a":
            return self._[operation]_provider_a(*args)
        if self.provider == "provider-b":
            return self._[operation]_provider_b(*args)
        raise ValueError(
            f"Unsupported provider '{self.provider}'. Supported: provider-a, provider-b"
        )

    def _[operation]_provider_a(self, *args) -> [return_type]:
        # import SDK lazily so missing package gives a clear error, not an ImportError at startup
        try:
            import provider_a_sdk
        except ImportError:
            raise RuntimeError("provider-a package not installed. Run: pip install provider-a-sdk")
        # ... call SDK

    def _[operation]_provider_b(self, *args) -> [return_type]:
        # Stub for a future milestone — raises NotImplementedError with a clear message
        raise NotImplementedError(
            "Provider B support is planned for [milestone]. Use provider=provider-a for now."
        )
```

### Key rules

1. **Default models live in the adapter, not in the prompt layer.** If you hardcode a model name in a prompt template or config file, you've created hidden coupling. `DEFAULT_MODELS` is the one place.

2. **Lazy imports.** Import the SDK inside the provider method, not at the top of the file. This means a missing SDK gives a clear `RuntimeError` at call time with an install hint — not a cryptic `ImportError` when the module loads.

3. **`NotImplementedError` stubs, not empty branches.** Future providers get a stub immediately so the dispatch table is complete and the error message tells the user what to do. A `pass` or `return None` silently fails.

4. **Config priority: CLI flag → env var → default.** Never accept credentials (API keys, tokens) as CLI flags — they end up in shell history. Accept them only via environment variable.

   ```
   provider = cli_arg or os.environ.get("SERVICE_PROVIDER", "default-provider")
   api_key  = os.environ.get(f"{provider.upper()}_API_KEY")
   ```

5. **The adapter is the only place that knows about providers.** Callers (CLI, tests, other modules) construct the adapter and call its public method. They never branch on `provider` themselves.

## When to use it

- The project calls an external service and "we might switch providers later" is a real possibility
- Multiple providers need to coexist (e.g., different teams use different AI models)
- The external service has an API key or credential that must be kept out of CLI args and logs

## When NOT to use it

- There is exactly one provider and switching is explicitly out of scope — the abstraction adds complexity for no benefit
- The provider is internal infrastructure you control — an adapter is overkill; just call it directly

## Results

- **Internal project M1** — Anthropic implemented; OpenAI stub in place with `NotImplementedError`. Adapter dispatch and lazy imports working as designed.
- **Internal project M3** — update when OpenAI support ships.
