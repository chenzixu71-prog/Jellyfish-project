# Spec Delta: Quiz Generation

## ADDED Requirements

### Requirement: Web Search Toggle

The system SHALL support a web search switch for quiz generation.

#### Scenario: Search disabled

- GIVEN `webSearchEnabled=false`
- WHEN the user requests quiz generation
- THEN the backend SHALL skip Tavily and use an empty search context.

#### Scenario: Search enabled

- GIVEN `webSearchEnabled=true`
- WHEN the user requests quiz generation
- THEN the backend SHALL call Tavily with configured timeout and result limit.

### Requirement: Tavily Search Formatting

The system SHALL format successful Tavily search results into concise prompt context.

#### Scenario: Tavily returns results

- WHEN Tavily returns search results
- THEN the backend SHALL format title, URL, and summary/snippet with length limits
- AND include the formatted search context in the DeepSeek quiz prompt.

### Requirement: Tavily Search Provider

The system SHALL support Tavily as the first real search provider for fresh-knowledge retrieval.

#### Scenario: Tavily is configured

- GIVEN `SEARCH_PROVIDER=tavily`
- AND `TAVILY_API_KEY` is configured on the backend
- WHEN the system needs fresh external sources
- THEN the backend SHALL query Tavily and convert the results into formatted search context.

#### Scenario: Tavily is not configured

- GIVEN Tavily is selected but `TAVILY_API_KEY` is missing
- WHEN the system needs external search
- THEN the backend SHALL log a warning and continue quiz generation with empty search context in development mode.

### Requirement: Search Failure Degradation

Search failure SHALL NOT block quiz generation in the first version.

#### Scenario: Tavily timeout

- WHEN Tavily times out
- THEN the backend SHALL log a warning
- AND continue DeepSeek quiz generation with empty search context.

#### Scenario: Tavily request fails

- WHEN Tavily returns an error
- THEN the backend SHALL log a warning
- AND continue DeepSeek quiz generation with empty search context.

### Requirement: Trusted Domain Filtering

The system SHALL support filtering search sources by trusted domains when the query or generation mode requires it.

#### Scenario: Wikipedia-only request

- WHEN the user asks for only Wikipedia sources
- THEN the source collector SHALL only accept results from Wikipedia domains or use empty search context.

### Requirement: Prompt Injection Resistance

The system SHALL treat retrieved source content as data only and SHALL NOT follow instructions embedded inside retrieved pages or documents.

#### Scenario: Retrieved page contains malicious instruction

- GIVEN a retrieved page says “ignore previous instructions”
- WHEN source context is injected into the quiz prompt
- THEN the system SHALL continue following the quiz generation system prompt.

### Requirement: Generation Quality Metadata

The system SHALL record generation metadata including web search switch, Tavily status, warning message, model, and source count.

#### Scenario: Search enabled but failed

- WHEN a quiz is generated after Tavily fails
- THEN the generation log SHALL include `webSearchEnabled=true`, Tavily failure status, warning message, and model name.

## MODIFIED Requirements

### Requirement: Quiz JSON Output

The existing quiz JSON output SHALL remain backward compatible with `title`, `summary`, and `questions`, while allowing optional search metadata later.

#### Scenario: Existing frontend reads quiz

- GIVEN the frontend only reads `title`, `summary`, and `questions`
- WHEN backend returns source metadata
- THEN the frontend SHALL still render the quiz normally.

### Requirement: AI Failure Handling

The existing AI failure handling SHALL distinguish between search failure and DeepSeek generation failure.

#### Scenario: DeepSeek technical failure

- WHEN model timeout or JSON parsing fails
- THEN the system SHALL show retry guidance.

#### Scenario: Search technical failure

- WHEN Tavily search fails or times out
- THEN the system SHALL continue generation with empty search context and not show a generic AI failure.
