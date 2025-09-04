# Model configuration examples

# Small test set
QUICK_TEST = [
    "google/gemini-2.5-pro",
    "qwen/qwen-2.5-7b-instruct"
]

# Medium benchmark 
MEDIUM_BENCHMARK = [
    "google/gemini-2.5-pro",
    "qwen/qwen-2.5-7b-instruct", 
    "anthropic/claude-3-5-sonnet",
    "meta/llama-3.1-70b-instruct"
]

# Large tournament
LARGE_TOURNAMENT = [
    "google/gemini-2.5-pro",
    "google/gemini-2.5-flash", 
    "qwen/qwen-2.5-7b-instruct",
    "qwen/qwen-2.5-14b-instruct",
    "anthropic/claude-3-5-sonnet",
    "anthropic/claude-3-5-haiku",
    "meta/llama-3.1-70b-instruct",
    "meta/llama-3.1-8b-instruct",
    "mistral/mistral-large",
    "mistral/mistral-small"
]
CHEAP_MODELS = [
    "google/gemini-2.5-flash", 
    "moonshotai/kimi-k2",
    "qwen/qwen3-235b-a22b-2507",
    "meta-llama/llama-4-maverick",
    "openai/gpt-4o-mini",
    "x-ai/grok-3-mini"
]
CHEAP_MODELS_TEST = [
    "google/gemini-2.5-flash", 
    "qwen/qwen3-235b-a22b-2507",
    "meta-llama/llama-4-maverick",
]
# Specialized categories
GOOGLE_MODELS = [
    "google/gemini-2.5-pro",
    "google/gemini-2.5-flash",
    "google/gemini-1.5-pro"
]

OPEN_SOURCE = [
    "qwen/qwen-2.5-7b-instruct",
    "meta/llama-3.1-70b-instruct", 
    "mistral/mistral-7b-instruct"
]
