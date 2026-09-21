# Chart selection and visual encoding

## Evidence base
Cleveland and McGill (JASA 1984) ran controlled experiments (55 subjects for
position–length, 54 for position–angle) and ordered ten elementary perceptual tasks from
most to least accurate:

1. Position along a common scale
2. Position along non-aligned scales
3. Length, direction, angle
4. Area
5. Volume, curvature
6. Shading, colour saturation

Position judgements were more accurate than length by factors of 1.4 to 2.5, and 1.96×
as accurate as angle, all statistically significant. The authors concluded that
"radical surgery on these popular graphs is needed" and offered dot charts, grouped dot
charts and framed-rectangle charts as replacements for bar charts, divided bars, pies and
shaded maps. Curve-difference judgements were shown to be inaccurate compared with
plotting the difference on its own axis.

Heer and Bostock (CHI 2010) replicated these results via crowdsourcing and extended them
to rectangular-area perception (treemaps, cartograms) and to chart size and gridline
spacing.

## Practical hierarchy
| Priority | Encoding | Use for |
|---|---|---|
| 1 | Aligned position (dot plot, bar, line on a shared axis) | Exact comparison |
| 2 | Length (bars without a shared baseline) | Where aligned position is unavailable |
| 3 | Angle, area (pie, bubble, treemap) | Sparingly; part-of-whole only when precision is not needed |
| — | Table | When exact lookup matters more than pattern recognition |
| — | Difference series | Whenever the message is a gap between two series |

## Chart by executive question
| Executive question | Preferred display | Notes |
|---|---|---|
| Actual vs target | Bullet chart, dot plot, variance bar | Show the variance as its own mark |
| Trend and turning point | Line chart with target or forecast line | Annotate the turning point |
| Ranking | Sorted horizontal bar or dot plot | Sort by value, largest first |
| Contribution to variance | Waterfall | Start = plan, end = actual, bridges = drivers |
| Relationship between two variables | Scatterplot with caveats | State n, period, and that correlation ≠ cause |
| Scenario range | Line or bars with interval / band | Central estimate + range; label the P-values or bounds used |
| Multiple options and trade-offs | Decision table | Options × criteria; BAU as a column |
| Precise values across categories | Compact table with conditional emphasis | Emphasis by weight/icon, not colour alone |

## Anti-charts (fail VIS-01 unless justified)
- Pie / donut for more than 3 parts, or for any comparison of parts to each other.
- Stacked bars where the message is about a non-bottom segment.
- Dual-axis lines (implied relationship the scales do not support).
- Bubble size for a decision-relevant magnitude.
- 3D of any kind.
- Gauge / speedometer for anything with a target (use a bullet chart).

## Design rules
| Rule | Detail | Check |
|---|---|---|
| Annotate the insight | Label the turning point, exception or threshold directly on the chart | VIS-03 |
| Always supply a comparator | Target, forecast, baseline or prior period drawn on the chart | CMP-01 |
| Draw to scale | Zero baseline for any length encoding; no truncated bars | VIS-02 |
| Direction | Time left → right; rankings sorted by value | VIS-05 |
| Colour is never the only cue | Icon, text or pattern in addition to colour; ≥3:1 contrast where lightness is the second cue (WCAG 2.2 SC 1.4.1, Level A) | VIS-04 |
| Show uncertainty | Central estimate with range / confidence interval / P90; sensitivity and switching values on key assumptions | FWD-02 |
| No decorative 3D | 3D bars look appealing and mislead about encoded values | VIS-06 |
| No chartjunk | Prune non-data ink; one message per chart | VIS-06 |
| Plot differences directly | Do not force the reader to subtract between curves | CMP-02 |

## Emphasis policy (resolves the minimalism vs embellishment tension)

| Policy | Applies to | Allowed | Forbidden |
|---|---|---|---|
| `minimal` (default) | Every dashboard, decision paper, QBR, brief, customer-facing pack, board pack | Grey for context series, one accent colour for the message series, direct labels, IBCS / ISO 24896 notation (consistent scenario patterns: actual solid, plan outlined, forecast hatched) | Decorative imagery, gradients, multiple accent colours, icons as data |
| `keynote` (opt-in) | Keynote or strategic presentation intended to be remembered, **and** user confirms | Larger type, a memorable visual metaphor around (not inside) the chart, one highlighted number | Any change to axis, scale, baseline or proportion; any encoding that alters perceived value |

Reasoning: the evidence is unambiguous on scale, proportion, orientation and colour, and
divided on whether restrained embellishment aids memory. The skill therefore defaults to
minimal wherever speed and comparability dominate, and allows emphasis only where
memorability is the explicit goal — never at the cost of value integrity.

## Status palette (for dashboards and scorecards)
Use with `scripts/contrast_check.py`. Every status has an icon and a text label.

| Status | Icon | Text | Suggested colour | Notes |
|---|---|---|---|---|
| On track | ● | "On track" | #1B7F3B | |
| At risk | ▲ | "At risk" | #B8860B | |
| Off track | ■ | "Off track" | #B02A2A | |
| No data | ○ | "No data" | #6B6B6B | Value absent. Never leave a KPI blank |
| No target | ◇ | "No target" | #6B6B6B | Value present, nothing to judge it against. Never show "No data" when a value exists |

Colours here are defaults; the tokens block in `design-system.md` is authoritative.

## Notation consistency (IBCS 2.0 / ISO 24896:2026)
- Same measure → same colour, same pattern, same position on every page.
- Actual = solid fill; plan/budget = outline; forecast = hatched; prior year = grey.
- Variance to plan on its own axis, positive up/right, negative down/left.
- Units and periods stated once per chart, not per label.
