# Spec Delta: Quiz Generation

## ADDED Requirements

### Requirement: Web Search Toggle

The system SHALL support a web search switch for quiz generation that controls whether Tavily tools are available to the AI context-gathering step.

#### Scenario: Search disabled

- GIVEN `webSearchEnabled=false`
- WHEN the user requests quiz generation
- THEN the backend SHALL not expose Tavily Search or Tavily Extract
- AND use an empty tool context.

#### Scenario: Search enabled

- GIVEN `webSearchEnabled=true`
- WHEN the user requests quiz generation
- THEN the backend SHALL expose Tavily Search and Tavily Extract to the AI tool-use step with configured timeout and result limits.

### Requirement: Tavily Tool Selection

The system SHALL allow the AI context-gathering step to choose Tavily Search, Tavily Extract, both, or neither based on user input.

#### Scenario: Keyword input

- WHEN the user input is a topic or keyword without URL
- THEN the AI MAY call Tavily Search.

#### Scenario: URL input

- WHEN the user input contains a URL
- THEN the AI SHOULD call Tavily Extract for that URL.

### Requirement: Tavily Tool Formatting

The system SHALL format successful Tavily Search and Tavily Extract results into concise prompt context.

#### Scenario: Tavily returns results

- WHEN Tavily returns search results
- THEN the backend SHALL format title, URL, and summary/snippet with length limits
- AND include the formatted search context in the DeepSeek quiz prompt.

#### Scenario: Tavily extracts URL content

- WHEN Tavily Extract returns page content
- THEN the backend SHALL format URL, title if available, and relevant content chunks with length limits
- AND include the formatted extract context in the DeepSeek quiz prompt.

### Requirement: Tavily Search And Extract Providers

The system SHALL support Tavily Search and Tavily Extract as the first real tools for fresh-knowledge retrieval and URL page extraction.

#### Scenario: Tavily is configured

- GIVEN `SEARCH_PROVIDER=tavily`
- AND `TAVILY_API_KEY` is configured on the backend
- WHEN the system needs fresh external sources
- THEN the backend SHALL make Tavily Search and Tavily Extract available to the tool-use step.

#### Scenario: Tavily is not configured

- GIVEN Tavily is selected but `TAVILY_API_KEY` is missing
- WHEN the system needs external search or URL extraction
- THEN the backend SHALL log a warning and continue quiz generation with empty search context in development mode.

### Requirement: Dynamic Tavily Parameters

The system SHALL dynamically choose Tavily parameters based on input complexity, user region intent, and requested source constraints.

#### Scenario: Simple knowledge topic

- WHEN the topic is simple and broad
- THEN the system SHOULD use fewer search results, basic depth, and snippets only.

#### Scenario: Complex or fresh knowledge topic

- WHEN the topic is complex, fresh, niche, or ambiguous
- THEN the system MAY increase result count, use advanced search depth, request richer content, or use Extract on high-value URLs.

#### Scenario: Domestic or international context

- WHEN the user implies a country or region
- THEN the system MAY set Tavily country preference, such as `china`, `united states`, or `united kingdom`, where supported.

### Requirement: Search Failure Degradation

Tavily Search or Extract failure SHALL NOT block quiz generation in the first version.

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

The system SHALL record generation metadata including web search switch, Tavily tool calls, Tavily status, warning message, model, and source count.

#### Scenario: Search enabled but failed

- WHEN a quiz is generated after Tavily Search or Extract fails
- THEN the generation log SHALL include `webSearchEnabled=true`, tool name, Tavily failure status, warning message, and model name.

## MODIFIED Requirements

### Requirement: Quiz JSON Output

The existing quiz JSON output SHALL remain backward compatible with `title`, `summary`, and `questions`, while allowing optional search metadata later.

#### Scenario: Existing frontend reads quiz

- GIVEN the frontend only reads `title`, `summary`, and `questions`
- WHEN backend returns source metadata
- THEN the frontend SHALL still render the quiz normally.

### Requirement: AI Failure Handling

The existing AI failure handling SHALL distinguish between Tavily tool failure and DeepSeek generation failure.

#### Scenario: DeepSeek technical failure

- WHEN model timeout or JSON parsing fails
- THEN the system SHALL show retry guidance.

#### Scenario: Search technical failure

- WHEN Tavily Search or Extract fails or times out
- THEN the system SHALL continue generation with empty search context and not show a generic AI failure.
