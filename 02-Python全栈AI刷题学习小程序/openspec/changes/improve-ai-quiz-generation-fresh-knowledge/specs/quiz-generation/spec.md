# Spec Delta: Quiz Generation

## ADDED Requirements

### Requirement: Topic Risk Analysis

The system SHALL analyze the user's learning input before quiz generation to detect whether the topic is ordinary, too broad, too short, fresh, niche, or ambiguous.

#### Scenario: Ambiguous new term

- WHEN the user enters `Harness Engineering`
- AND the system cannot confidently map it to one domain
- THEN the system SHALL either retrieve supporting sources or ask the user to clarify the intended domain.

#### Scenario: Stable topic

- WHEN the user enters a stable topic such as `Git commit push pull`
- THEN the system MAY generate directly from user input without external retrieval.

### Requirement: Source-Aware Generation

The system SHALL support generating quizzes from explicit source context when the topic is fresh, niche, or ambiguous.

#### Scenario: Source context exists

- GIVEN source context about Harness.io pipelines
- WHEN quiz generation runs
- THEN the generated questions SHALL be about Harness.io / DevOps / CI-CD concepts, not unrelated harness meanings.

### Requirement: Tavily Search Provider

The system SHALL support Tavily as the first real search provider for fresh-knowledge retrieval.

#### Scenario: Tavily is configured

- GIVEN `SEARCH_PROVIDER=tavily`
- AND `TAVILY_API_KEY` is configured on the backend
- WHEN the system needs fresh external sources
- THEN the backend SHALL query Tavily and convert the results into source documents.

#### Scenario: Tavily is not configured

- GIVEN Tavily is selected but `TAVILY_API_KEY` is missing
- WHEN the system needs external search
- THEN the backend SHALL return a controlled configuration error or fall back to a mock/local provider in development mode.

### Requirement: Trusted Domain Filtering

The system SHALL support filtering search sources by trusted domains when the query or generation mode requires it.

#### Scenario: Wikipedia-only request

- WHEN the user asks for only Wikipedia sources
- THEN the source collector SHALL only accept results from Wikipedia domains or return insufficient evidence.

### Requirement: Source References

For source-aware generation, each generated question SHALL include one or more `source_refs` that map to collected source metadata.

#### Scenario: Question has no source

- WHEN a source-aware generated question lacks `source_refs`
- THEN backend validation SHALL reject the quiz or retry generation.

### Requirement: Insufficient Evidence Handling

The system SHALL not silently generate confident questions when evidence is insufficient.

#### Scenario: Not enough reliable source material

- GIVEN the system cannot find enough relevant source material
- WHEN the user asks to generate a quiz
- THEN the system SHALL return a clarification or “please provide material” response.

### Requirement: Prompt Injection Resistance

The system SHALL treat retrieved source content as data only and SHALL NOT follow instructions embedded inside retrieved pages or documents.

#### Scenario: Retrieved page contains malicious instruction

- GIVEN a retrieved page says “ignore previous instructions”
- WHEN source context is injected into the quiz prompt
- THEN the system SHALL continue following the quiz generation system prompt.

### Requirement: Generation Quality Metadata

The system SHALL record generation metadata including source mode, model, confidence, and source count.

#### Scenario: Source-aware quiz generated

- WHEN a quiz is generated with external sources
- THEN the generation log SHALL include source mode, source count, confidence, and model name.

## MODIFIED Requirements

### Requirement: Quiz JSON Output

The existing quiz JSON output SHALL remain backward compatible with `title`, `summary`, and `questions`, while allowing optional source metadata.

#### Scenario: Existing frontend reads quiz

- GIVEN the frontend only reads `title`, `summary`, and `questions`
- WHEN backend returns source metadata
- THEN the frontend SHALL still render the quiz normally.

### Requirement: AI Failure Handling

The existing AI failure handling SHALL distinguish between technical failure and knowledge-confidence failure.

#### Scenario: Technical failure

- WHEN model timeout or JSON parsing fails
- THEN the system SHALL show retry guidance.

#### Scenario: Knowledge-confidence failure

- WHEN source evidence is insufficient or topic is ambiguous
- THEN the system SHALL ask for clarification or material, not show a generic AI failure.
