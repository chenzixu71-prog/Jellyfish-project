# ASCII Layout

## S04 Diagnose & Optimize - 1440x900

```text
┌──────┬───────────────────────────────────────────────────────────────────────┐
│ GEO  │ Project / Acme AI Knowledge Page            Saved        ⋯          │ 56
│      ├───────────────────────────────────────────────────────────────────────┤
│  +   │ USER INPUT · REAL · Provider · Model · Prompts v3 · 30/30 · HIGH    │ 44
│      ├───────────────┬───────────────────────────────────┬───────────────────┤
│  P   │ DIAGNOSIS     │ WORKING COPY                      │ EVIDENCE          │
│  R   │ 68.4 proxy    │ [Edit] [Diff]                     │ Rule: Support     │
│  F   │               │                                   │ Source paragraph  │
│      │ Critical  2   │ H1 ...                            │ Why it matters    │
│      │ Important 4   │ Paragraph with highlighted       │ Limit / N/A       │
│      │ Improve    3   │ evidence and accepted edits      │                   │
│      │               │                                   │ [Reject] [Apply]  │
│      │ Rule filters  │                                   │                   │
│      │ Evidence list │                                   │                   │
│      ├───────────────┴───────────────────────────────────┴───────────────────┤
│      │ 3 changes · 1 stale       [Reset]        [Confirm optimized version]│ 64
└──────┴───────────────────────────────────────────────────────────────────────┘
 72       256                   flexible min 560                  384
```

## S03 Running / Partial Success

```text
┌──────┬───────────────────────────────────────────────────────────────────────┐
│ GEO  │ Baseline evaluation                                      07:42       │
├──────┼───────────────────────────────────────────────────────────────────────┤
│      │ USER INPUT · REAL · ... · 22/30 VALID · LOW CONFIDENCE               │
├──────┼───────────────────────────────────────────────────────────────────────┤
│ Nav  │ 22 valid / 5 running / 3 failed       [Cancel request]               │
│      │ ████████████████████░░░░░░                                          │
│      │                                                                       │
│      │ Prompt rows: intent · status · mention · citation · duration · retry │
│      │ Inline error: timeout / retry failed item                             │
│      │                                                                       │
│      │ [Preview low-confidence diagnosis]   Formal comparison unavailable   │
└──────┴───────────────────────────────────────────────────────────────────────┘
```

## S05 Before / After

```text
┌──────┬───────────────────────────────────────────────────────────────────────┐
│ GEO  │ Comparison report                              Conditions compatible │
├──────┼───────────────────────────────────────────────────────────────────────┤
│      │ REAL · same model · prompt v3 · 3 repeats · rules-v1                 │
├──────┼───────────────────────────────────────────────────────────────────────┤
│ Nav  │ Rule score* 68.4 → 80.1  (+17.1%)  | Mention 40% → 50%              │
│      │ * proxy metric, not traffic/ranking                                  │
│      ├───────────────────────────────┬───────────────────────────────────────┤
│      │ BEFORE                        │ AFTER                                 │
│      │ Evidence and answers          │ Changed evidence and answers          │
│      ├───────────────────────────────┴───────────────────────────────────────┤
│      │ Per-prompt comparison · N/A reasons · limitations                    │
│      │ Was this useful?  [Yes] [Partly] [No]                                │
└──────┴───────────────────────────────────────────────────────────────────────┘
```

## Scroll And Stability

- 导航和顶部区域固定；主工作区独立滚动。
- S04 的诊断列、正文和证据检查器各自保持稳定宽度，选择建议不得导致布局跳动。
- 底部确认栏固定但预留内容内边距，不能遮挡最后一段正文。
- 长品牌名、20 个问题、长证据和 N/A 均需在 Figma 压力样本中验证。

## Structure Review

`structure-confirmed`：结构直接来自 PRD v1.0，无新增产品范围。视觉方向、色彩、字体和生图素材仍等待 GATE-2 用户确认。
