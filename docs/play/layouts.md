# Agent Layouts

The Play city adapts to the number of agents declared by the running crew.

## Rules

- If the crew declares `n` agents, the UI shows exactly `n` agents.
- Empty placeholders are not shown.
- Agents receive distinct colors, up to 20 agents.
- Names appear under avatars.
- Thought bubbles stay above avatars.
- Positions are spaced to reduce overlap between names, avatars, and bubbles.

## Layout Scale

| Agent count | Behavior |
| --- | --- |
| 1-4 | Agents use separated primary zones |
| 5 | Adds the top-center Ops zone |
| 6-8 | Adds side corridor houses around the Tool Hub |
| 9-10 | Uses the full city layout |
| 11+ | Keeps the first 10 city positions and places extras around the map |

## Design Intent

The current design uses one coherent city rather than completely separate worlds per agent count. Each count activates a different set of occupied positions inside that city.

This keeps the environment stable while still avoiding empty slots.

## Known Improvement

The next step is to create more distinct compositions for small crews:

| Crew size | Better future environment |
| --- | --- |
| 1 agent | Focused desk or small office |
| 2 agents | Two-room collaboration space |
| 3 agents | Triangle work hub |
| 4 agents | Four district layout |
| 5-10 agents | Full city expansion |

That would make each `n` feel more intentionally designed, not only progressively activated.
