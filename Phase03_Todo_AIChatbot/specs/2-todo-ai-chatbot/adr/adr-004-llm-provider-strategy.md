# ADR-004: LLM Provider Strategy

## Status
Proposed

## Date
2026-01-13

## Context
The AI chatbot requires a Large Language Model (LLM) to process natural language inputs and generate responses. We must decide which LLM provider and model to use, considering factors like cost, performance, availability, and model capabilities. This decision impacts system costs, response quality, and potential vendor dependencies.

## Decision
We will use OpenRouter with "mistralai/devstral-2512:free" as the default model for the AI chatbot. This provides a cost-effective solution with reasonable performance characteristics for the prototype phase. The model can be confirmed or changed later as requirements evolve.

The LLM strategy will:
- Use OpenRouter as the LLM provider for flexibility and competitive pricing
- Start with the free "mistralai/devstral-2512:free" model to minimize initial costs
- Implement configurable model selection to allow easy switching later
- Follow the example code pattern provided in the specification

## Alternatives
- **OpenAI GPT models**: Use OpenAI's GPT-4 or newer models for potentially better performance but at higher cost
- **Anthropic Claude models**: Use Claude models for different strengths in reasoning and safety, with different pricing
- **Self-hosted open-source models**: Deploy models like Llama, Mistral, or other open-source models for full control but higher infrastructure costs
- **Google Gemini models**: Use Google's models for different capabilities and pricing model
- **Azure OpenAI Service**: Use Microsoft's Azure-hosted OpenAI for enterprise features and compliance

## Consequences
**Positive:**
- Cost-effective solution with free tier for development and prototyping
- Flexibility to switch models later without major code changes
- Good performance characteristics for the intended use case
- Competitive pricing for production usage
- Access to variety of models through same provider

**Negative:**
- Potential limitations in model capabilities compared to premium models
- Vendor dependency on OpenRouter
- Possible rate limits or availability constraints with free models
- Need to validate model performance for the specific use case
- Potential model changes or deprecation affecting stability

## References
- specs/2-todo-ai-chatbot/plan.md
- specs/2-todo-ai-chatbot/spec.md
- specs/2-todo-ai-chatbot/contracts.md