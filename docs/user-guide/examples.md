# Examples gallery

A small set of Mermaid sources to paste into the Atlantis editor. The diagrams below render in the live preview — this docs site shows them as code blocks for reference.

## Flowchart

```mermaid
flowchart TD
  A[Start] --> B{Is it Tuesday?}
  B -- Yes --> C[Drink tea]
  B -- No --> D[Drink coffee]
  C --> E[Get on with it]
  D --> E
```

## Sequence diagram

```mermaid
sequenceDiagram
  participant U as User
  participant A as Atlantis
  participant W as WebEngine
  U->>A: Type Mermaid source
  A->>A: Debounce 500 ms
  A->>W: bridge.render(source)
  W-->>A: report_svg(svg)
  A-->>U: Preview updates
```

## Class diagram

```mermaid
classDiagram
  class WebEngineMermaidBridge {
    +render(source)
    +set_theme(theme)
    -timeout_ms
  }
  class PreviewPane {
    +render_source(source, on_done)
    +last_svg
  }
  PreviewPane --> WebEngineMermaidBridge : owns
```

These three diagram families (`flowchart`, `sequenceDiagram`, `classDiagram`) exercise the main code paths in the WebEngine bridge. If you can render all three locally, the bridge is healthy.
