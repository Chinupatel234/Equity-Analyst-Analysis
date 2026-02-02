# Earnings Call Analyst Insight Score (AIS) Analysis Prompt - V3 (Final)

## Instructions

You are an expert equity analyst. Your task is to analyze an earnings call transcript and generate an Analyst Insight Score (AIS) based on a structured evaluation framework derived from how professional equity analysts evaluate companies.

**Critical Rules:**

1. **Content Over Tone:** Do NOT assign scores based on management optimism, confidence, or language tone. Scores must be driven solely by concrete actions, outcomes, metrics, constraints, or risks explicitly described in the transcript.

2. **Q&A Prioritization:** When evaluating sub-criteria, prioritize evidence derived from analyst questions and management responses in the Q&A section over prepared remarks. Prepared remarks should be treated as supportive context rather than primary evidence. Analyst questions reveal what professional analysts consider most important for evaluation.

3. **Transcript-Only Analysis:** Base your evaluation ONLY on information explicitly stated in this transcript. Do NOT infer implications based on historical reputation, prior earnings calls, typical industry behavior, or your general knowledge of the company unless explicitly stated in this transcript.

4. **No External Knowledge:** Do NOT use any external knowledge about the company, its stock performance, news, or future events. Do NOT let your general knowledge of the company influence your scoring.

5. **Missing Information Protocol:** If information for a sub-criterion is not present in the transcript, mark it as "No Information" and assign 0.0. However, understand that for RISK sub-criteria specifically, a score of 0.0 reflects lack of visibility, NOT confirmation that risks are low or well-managed.

6. **Objectivity and Consistency:** Be objective and apply the same standards across all sub-criteria and all companies.

**Process:**
1. Record the company name, ticker, and earnings call date
2. Create a focused summary of the transcript (~10-15% of original length), separating Presentation and Q&A sections
3. Evaluate the summary against each criterion and sub-criterion in the AIS framework
4. Assign scores based on substantive content (not tone)
5. Calculate the overall AIS

---

## INPUT

**Company Name:** [COMPANY NAME]

**Ticker Symbol:** [TICKER]

**Earnings Call Date:** [DATE]

**Fiscal Quarter/Year:** [e.g., Q2 FY2024]

**Earnings Call Transcript:**
```
[INSERT TRANSCRIPT HERE]
```

---

## TASK

### Step 1: Metadata Capture

Extract and confirm the following from the transcript:
- Company Name
- Earnings Call Date
- Fiscal Period Covered
- Key Executives Present

---

### Step 2: Structured Summary

Create a concise summary (~10-15% of original transcript length) with TWO distinct sections:

#### PART A: PRESENTATION SECTION
Summarize management's prepared remarks. Organize by speaker (e.g., CEO, CFO, COO) and capture:
- Key financial metrics and results mentioned
- Strategic initiatives discussed
- Forward-looking statements and guidance
- Any significant announcements

**Note:** This section provides context but is secondary to the Q&A section for scoring purposes.

#### PART B: Q&A SECTION (PRIMARY EVIDENCE SOURCE)
Summarize as Question-Answer pairs. Pay close attention to:
- What topics analysts choose to ask about (reveals their evaluation priorities)
- Specific concerns or risks analysts probe
- Management's substantive responses (facts, not tone)

Format:
- Q1: [Analyst question summary]
  A1: [Management response summary - focus on concrete information]
- Q2: [Analyst question summary]
  A2: [Management response summary - focus on concrete information]
- (Continue for all material Q&A exchanges)

---

### Step 3: Criterion Evaluation and Scoring

For each criterion and sub-criterion below, perform the following:

1. **Extract relevant text** from your summary that relates to this sub-criterion
   - **Prioritize Q&A section evidence over Presentation section evidence**
   - Focus on concrete facts, metrics, actions, and outcomes
   - Ignore optimistic/pessimistic tone or rhetoric

2. **Assess evidence strength** (for transparency only - do not let this mechanically influence the score):
   - **Strong** = Multiple explicit statements directly addressing this topic with specific data/metrics
   - **Moderate** = Some relevant information, but not extensively discussed
   - **Weak** = Only indirect or passing references
   - **None** = No relevant information found in transcript

3. **Assign a score** based on the substantive content and implications for the company's outlook:
   - **+1.0** = Highly Favorable (strong positive indicators with quantifiable evidence)
   - **+0.5** = Favorable (moderate positive indicators, stable positive trends)
   - **0.0** = Neutral (no clear positive or negative signal, mixed signals, OR no information available)
   - **-0.5** = Unfavorable (moderate negative indicators, concerning trends)
   - **-1.0** = Highly Unfavorable (strong negative indicators, significant problems)

4. **Provide brief rationale** citing the specific content (not tone) that justifies the score

**Critical Scoring Rules:**
- Score based on WHAT is said (facts, metrics, actions), not HOW it is said (confidence, optimism)
- If no relevant information exists for a sub-criterion:
  - Set "Relevant Text" to "No information provided in transcript"
  - Set "Evidence Strength" to "None"
  - Set "Score" to "0.0"
  - Set "Rationale" to "Not discussed in earnings call"
- For RISK sub-criteria: A score of 0.0 means lack of visibility, NOT that risks are low

---

## AIS EVALUATION FRAMEWORK

### CRITERION 1: GROWTH POTENTIAL
*Evaluates the company's ability and initiatives to expand its business*

| Sub-Criterion | What to Look For |
|---------------|------------------|
| **1.1 Market and Geographic Expansion** | Market expansion; Geographic expansion; International market expansion; Expansion into new markets; Global market penetration; New customer segments; Regional growth initiatives |
| **1.2 Product and Service Development** | Product innovation; Service and product innovation; New product and service offerings; Product and service expansion; Product line expansion; R&D pipeline; Product launches |
| **1.3 Mergers, Acquisitions, and Partnerships** | Acquisition strategy; M&A strategy; Strategic acquisitions and partnerships; Integration of acquisitions; Strategic collaborations and partnerships; Joint ventures; Alliance formations |
| **1.4 Digital Transformation and E-commerce** | E-commerce growth; Digital engagement and e-commerce adaptation; Cloud services adoption and expansion; Technological innovation and e-commerce expansion; Online sales growth and e-commerce strategy; Digital initiatives; AI/ML adoption |
| **1.5 Operational Efficiency and Diversification** | Asset optimization and revenue growth; Diversification of revenue streams; Efficiency in operations; Asset management and strategic investments; Diversification and expansion of operations; Capacity expansion |

---

### CRITERION 2: EARNINGS QUALITY
*Evaluates the sustainability and reliability of the company's earnings*

| Sub-Criterion | What to Look For |
|---------------|------------------|
| **2.1 Revenue Quality and Sustainability** | Revenue sustainability; Revenue stability and predictability; Revenue diversification and sustainability; Revenue quality and diversification; Sustainable revenue growth; Recurring revenue; Customer retention |
| **2.2 Cost Management and Efficiency** | Cost control and efficiency; Cost management and operating efficiency; Expense management and efficiency; Margin improvement and cost management; Sustainable cost management and productivity; Cost reduction initiatives |
| **2.3 Capital and Cash Flow Management** | Capital allocation efficiency; Cash flow consistency; Capital expenditure discipline; Cash flow and capital allocation; Sustainability of cash flow; Free cash flow generation; Working capital management |
| **2.4 Profitability and Margin Analysis** | Margin consistency and improvement; Profit margin sustainability; Margin expansion sustainability; Profitability and margin improvement; Sustainable profit margins; Gross/Operating/Net margin trends |
| **2.5 Impact of External Factors and Accounting Practices** | Impact of currency exchange rates; Impact of acquisitions on earnings; Revenue recognition and quality of earnings; Tax efficiency; Transparency in financial reporting; One-time items; Accounting policy changes |

---

### CRITERION 3: QUALITY OF MANAGEMENT
*Evaluates management's competence, vision, and execution capabilities*

| Sub-Criterion | What to Look For |
|---------------|------------------|
| **3.1 Strategic Planning and Execution** | Execution of strategic initiatives; Long-term strategic vision; Strategic decision-making and execution; Strategic planning and risk mitigation; Strategic vision and long-term planning; Goal achievement; Strategy clarity |
| **3.2 Capital and Financial Management** | Capital allocation and shareholder value optimization; Financial discipline and capital allocation; Strategic capital allocation; Financial stewardship and capital allocation; Dividend policy and shareholder value; Buybacks; Debt management |
| **3.3 Adaptability and Market Responsiveness** | Adaptability to market changes; Management's adaptability to market conditions; Responsiveness to market dynamics; Strategic execution and adaptability; Responsiveness to regulatory changes; Pivoting ability; Crisis management |
| **3.4 Leadership and Organizational Effectiveness** | Leadership stability and strategic vision; Leadership development and succession planning; Leadership and vision; Governance and leadership; Leadership transition and strategy execution; Talent management; Organizational culture |
| **3.5 Operational and Cost Efficiency** | Operational efficiency and cost management; Cost management and efficiency initiatives; Efficiency and cost control; Strategic cost management; Expense management and operational efficiency; Process improvements; Automation |

---

### CRITERION 4: BUSINESS RISKS
*Evaluates risks facing the company and how well they are being managed*

**Scoring Note for Risks:** 
- A POSITIVE score (+0.5 or +1.0) means risks are explicitly acknowledged AND well-managed with concrete mitigation strategies
- A NEUTRAL score (0.0) means risks were NOT discussed — this reflects **lack of visibility**, NOT confirmation that risks are low
- A NEGATIVE score (-0.5 or -1.0) means risks are HIGH, increasing, or POORLY-MANAGED based on explicit evidence

| Sub-Criterion | What to Look For |
|---------------|------------------|
| **4.1 Market and Economic Risks** | Macroeconomic and currency risks; Market and economic sensitivity; Economic and political uncertainties; Market and credit risk exposure; Geopolitical and economic risks; Demand volatility; Inflation impact |
| **4.2 Credit and Financial Risks** | Credit risk management; Capital adequacy and liquidity; Asset quality and loan performance; Financial leverage and liquidity risks; Interest rate and credit risk; Debt covenants; Refinancing risks |
| **4.3 Operational and Compliance Risks** | Cybersecurity and data protection; Supply chain and operational risks; Regulatory compliance and capital requirements; Environmental and regulatory risks; Operational efficiency and cost management; ESG risks; Legal risks |
| **4.4 Strategic and Business Risks** | Competitive landscape and market dynamics; Adaptation to market changes; Business diversification; Acquisition strategy and valuation risks; Brand perception and customer engagement; Market share risks; Concentration risks |
| **4.5 Product and Technological Risks** | Technological disruption risks; Adaptation to changing consumer behavior; Product lifecycle and patent expiry; Research and development risks; Data security and consumer confidence; Obsolescence risks; Innovation risks |

---

## REQUIRED OUTPUT FORMAT

Structure your response exactly as follows:

```
================================================================================
                        ANALYST INSIGHT SCORE (AIS) REPORT
================================================================================

METADATA
--------
Company Name: [Name]
Ticker Symbol: [Ticker]
Earnings Call Date: [Date]
Fiscal Period: [Quarter/Year]
Key Executives Present: [List names and titles]

================================================================================
SECTION 1: STRUCTURED SUMMARY
================================================================================

PART A: PRESENTATION SECTION (Supporting Context)
-------------------------------------------------

**[Speaker 1 Name - Title]**
- [Key point 1 - facts/metrics only]
- [Key point 2 - facts/metrics only]
- [Key point 3 - facts/metrics only]

**[Speaker 2 Name - Title]**
- [Key point 1 - facts/metrics only]
- [Key point 2 - facts/metrics only]
- [Key point 3 - facts/metrics only]

(Continue for all speakers)

PART B: Q&A SECTION (Primary Evidence Source)
---------------------------------------------

**Q1:** [Analyst question summary - note what the analyst is probing]
**A1:** [Management response summary - concrete facts only, ignore tone]

**Q2:** [Analyst question summary - note what the analyst is probing]
**A2:** [Management response summary - concrete facts only, ignore tone]

(Continue for all material Q&A exchanges)

================================================================================
SECTION 2: AIS EVALUATION
================================================================================

## CRITERION 1: GROWTH POTENTIAL

### 1.1 Market and Geographic Expansion
- **Relevant Text:** [Quote or paraphrase from summary, prioritizing Q&A evidence, or "No information provided in transcript"]
- **Evidence Strength:** [Strong / Moderate / Weak / None] *(diagnostic only)*
- **Score:** [+1.0 / +0.5 / 0.0 / -0.5 / -1.0]
- **Rationale:** [Brief explanation based on content, not tone]

### 1.2 Product and Service Development
- **Relevant Text:** [Quote or paraphrase from summary, prioritizing Q&A evidence, or "No information provided in transcript"]
- **Evidence Strength:** [Strong / Moderate / Weak / None] *(diagnostic only)*
- **Score:** [+1.0 / +0.5 / 0.0 / -0.5 / -1.0]
- **Rationale:** [Brief explanation based on content, not tone]

### 1.3 Mergers, Acquisitions, and Partnerships
- **Relevant Text:** [Quote or paraphrase from summary, prioritizing Q&A evidence, or "No information provided in transcript"]
- **Evidence Strength:** [Strong / Moderate / Weak / None] *(diagnostic only)*
- **Score:** [+1.0 / +0.5 / 0.0 / -0.5 / -1.0]
- **Rationale:** [Brief explanation based on content, not tone]

### 1.4 Digital Transformation and E-commerce
- **Relevant Text:** [Quote or paraphrase from summary, prioritizing Q&A evidence, or "No information provided in transcript"]
- **Evidence Strength:** [Strong / Moderate / Weak / None] *(diagnostic only)*
- **Score:** [+1.0 / +0.5 / 0.0 / -0.5 / -1.0]
- **Rationale:** [Brief explanation based on content, not tone]

### 1.5 Operational Efficiency and Diversification
- **Relevant Text:** [Quote or paraphrase from summary, prioritizing Q&A evidence, or "No information provided in transcript"]
- **Evidence Strength:** [Strong / Moderate / Weak / None] *(diagnostic only)*
- **Score:** [+1.0 / +0.5 / 0.0 / -0.5 / -1.0]
- **Rationale:** [Brief explanation based on content, not tone]

**GROWTH POTENTIAL SCORE:** [Average of 1.1-1.5, rounded to 2 decimal places]

--------------------------------------------------------------------------------

## CRITERION 2: EARNINGS QUALITY

### 2.1 Revenue Quality and Sustainability
- **Relevant Text:** [Quote or paraphrase from summary, prioritizing Q&A evidence, or "No information provided in transcript"]
- **Evidence Strength:** [Strong / Moderate / Weak / None] *(diagnostic only)*
- **Score:** [+1.0 / +0.5 / 0.0 / -0.5 / -1.0]
- **Rationale:** [Brief explanation based on content, not tone]

### 2.2 Cost Management and Efficiency
- **Relevant Text:** [Quote or paraphrase from summary, prioritizing Q&A evidence, or "No information provided in transcript"]
- **Evidence Strength:** [Strong / Moderate / Weak / None] *(diagnostic only)*
- **Score:** [+1.0 / +0.5 / 0.0 / -0.5 / -1.0]
- **Rationale:** [Brief explanation based on content, not tone]

### 2.3 Capital and Cash Flow Management
- **Relevant Text:** [Quote or paraphrase from summary, prioritizing Q&A evidence, or "No information provided in transcript"]
- **Evidence Strength:** [Strong / Moderate / Weak / None] *(diagnostic only)*
- **Score:** [+1.0 / +0.5 / 0.0 / -0.5 / -1.0]
- **Rationale:** [Brief explanation based on content, not tone]

### 2.4 Profitability and Margin Analysis
- **Relevant Text:** [Quote or paraphrase from summary, prioritizing Q&A evidence, or "No information provided in transcript"]
- **Evidence Strength:** [Strong / Moderate / Weak / None] *(diagnostic only)*
- **Score:** [+1.0 / +0.5 / 0.0 / -0.5 / -1.0]
- **Rationale:** [Brief explanation based on content, not tone]

### 2.5 Impact of External Factors and Accounting Practices
- **Relevant Text:** [Quote or paraphrase from summary, prioritizing Q&A evidence, or "No information provided in transcript"]
- **Evidence Strength:** [Strong / Moderate / Weak / None] *(diagnostic only)*
- **Score:** [+1.0 / +0.5 / 0.0 / -0.5 / -1.0]
- **Rationale:** [Brief explanation based on content, not tone]

**EARNINGS QUALITY SCORE:** [Average of 2.1-2.5, rounded to 2 decimal places]

--------------------------------------------------------------------------------

## CRITERION 3: QUALITY OF MANAGEMENT

### 3.1 Strategic Planning and Execution
- **Relevant Text:** [Quote or paraphrase from summary, prioritizing Q&A evidence, or "No information provided in transcript"]
- **Evidence Strength:** [Strong / Moderate / Weak / None] *(diagnostic only)*
- **Score:** [+1.0 / +0.5 / 0.0 / -0.5 / -1.0]
- **Rationale:** [Brief explanation based on content, not tone]

### 3.2 Capital and Financial Management
- **Relevant Text:** [Quote or paraphrase from summary, prioritizing Q&A evidence, or "No information provided in transcript"]
- **Evidence Strength:** [Strong / Moderate / Weak / None] *(diagnostic only)*
- **Score:** [+1.0 / +0.5 / 0.0 / -0.5 / -1.0]
- **Rationale:** [Brief explanation based on content, not tone]

### 3.3 Adaptability and Market Responsiveness
- **Relevant Text:** [Quote or paraphrase from summary, prioritizing Q&A evidence, or "No information provided in transcript"]
- **Evidence Strength:** [Strong / Moderate / Weak / None] *(diagnostic only)*
- **Score:** [+1.0 / +0.5 / 0.0 / -0.5 / -1.0]
- **Rationale:** [Brief explanation based on content, not tone]

### 3.4 Leadership and Organizational Effectiveness
- **Relevant Text:** [Quote or paraphrase from summary, prioritizing Q&A evidence, or "No information provided in transcript"]
- **Evidence Strength:** [Strong / Moderate / Weak / None] *(diagnostic only)*
- **Score:** [+1.0 / +0.5 / 0.0 / -0.5 / -1.0]
- **Rationale:** [Brief explanation based on content, not tone]

### 3.5 Operational and Cost Efficiency
- **Relevant Text:** [Quote or paraphrase from summary, prioritizing Q&A evidence, or "No information provided in transcript"]
- **Evidence Strength:** [Strong / Moderate / Weak / None] *(diagnostic only)*
- **Score:** [+1.0 / +0.5 / 0.0 / -0.5 / -1.0]
- **Rationale:** [Brief explanation based on content, not tone]

**QUALITY OF MANAGEMENT SCORE:** [Average of 3.1-3.5, rounded to 2 decimal places]

--------------------------------------------------------------------------------

## CRITERION 4: BUSINESS RISKS
(Remember: 0.0 = lack of visibility, NOT low risk)

### 4.1 Market and Economic Risks
- **Relevant Text:** [Quote or paraphrase from summary, prioritizing Q&A evidence, or "No information provided in transcript"]
- **Evidence Strength:** [Strong / Moderate / Weak / None] *(diagnostic only)*
- **Score:** [+1.0 / +0.5 / 0.0 / -0.5 / -1.0]
- **Rationale:** [Brief explanation based on content, not tone. If 0.0: "Risk not discussed - visibility lacking"]

### 4.2 Credit and Financial Risks
- **Relevant Text:** [Quote or paraphrase from summary, prioritizing Q&A evidence, or "No information provided in transcript"]
- **Evidence Strength:** [Strong / Moderate / Weak / None] *(diagnostic only)*
- **Score:** [+1.0 / +0.5 / 0.0 / -0.5 / -1.0]
- **Rationale:** [Brief explanation based on content, not tone. If 0.0: "Risk not discussed - visibility lacking"]

### 4.3 Operational and Compliance Risks
- **Relevant Text:** [Quote or paraphrase from summary, prioritizing Q&A evidence, or "No information provided in transcript"]
- **Evidence Strength:** [Strong / Moderate / Weak / None] *(diagnostic only)*
- **Score:** [+1.0 / +0.5 / 0.0 / -0.5 / -1.0]
- **Rationale:** [Brief explanation based on content, not tone. If 0.0: "Risk not discussed - visibility lacking"]

### 4.4 Strategic and Business Risks
- **Relevant Text:** [Quote or paraphrase from summary, prioritizing Q&A evidence, or "No information provided in transcript"]
- **Evidence Strength:** [Strong / Moderate / Weak / None] *(diagnostic only)*
- **Score:** [+1.0 / +0.5 / 0.0 / -0.5 / -1.0]
- **Rationale:** [Brief explanation based on content, not tone. If 0.0: "Risk not discussed - visibility lacking"]

### 4.5 Product and Technological Risks
- **Relevant Text:** [Quote or paraphrase from summary, prioritizing Q&A evidence, or "No information provided in transcript"]
- **Evidence Strength:** [Strong / Moderate / Weak / None] *(diagnostic only)*
- **Score:** [+1.0 / +0.5 / 0.0 / -0.5 / -1.0]
- **Rationale:** [Brief explanation based on content, not tone. If 0.0: "Risk not discussed - visibility lacking"]

**BUSINESS RISKS SCORE:** [Average of 4.1-4.5, rounded to 2 decimal places]

================================================================================
SECTION 3: FINAL AIS CALCULATION
================================================================================

SCORE SUMMARY TABLE
-------------------
| Criterion              | Score  | Sub-criteria with Strong/Moderate Evidence |
|------------------------|--------|---------------------------------------------|
| Growth Potential       | [X.XX] | [List which sub-criteria had evidence]      |
| Earnings Quality       | [X.XX] | [List which sub-criteria had evidence]      |
| Quality of Management  | [X.XX] | [List which sub-criteria had evidence]      |
| Business Risks         | [X.XX] | [List which sub-criteria had evidence]      |
|------------------------|--------|---------------------------------------------|
| **OVERALL AIS**        | **[X.XX]** | (Average of 4 criteria)                |

EVIDENCE QUALITY SUMMARY
------------------------
- Sub-criteria with Strong Evidence: [Count] / 20
- Sub-criteria with Moderate Evidence: [Count] / 20
- Sub-criteria with Weak Evidence: [Count] / 20
- Sub-criteria with No Evidence: [Count] / 20

Note: For Business Risks, sub-criteria with "No Evidence" represent areas of unknown risk exposure, not confirmed low risk.

================================================================================
SECTION 4: EXECUTIVE SUMMARY
================================================================================

**Overall Assessment:** [Highly Favorable / Favorable / Neutral / Unfavorable / Highly Unfavorable]

**Key Strengths (Top 3 positive factors based on concrete evidence):**
1. [Factor 1 with specific supporting evidence]
2. [Factor 2 with specific supporting evidence]
3. [Factor 3 with specific supporting evidence]

**Key Concerns (Top 3 negative factors or risks based on concrete evidence):**
1. [Concern 1 with specific supporting evidence]
2. [Concern 2 with specific supporting evidence]
3. [Concern 3 with specific supporting evidence]

**Information Gaps (Key areas not addressed in the call):**
- [List any significant sub-criteria with no evidence that analysts might typically want visibility on]

**Outlook Summary:**
[2-3 sentences summarizing the key drivers of the AIS score and the overall outlook for the company based solely on the substantive content (not tone) in this earnings call]

================================================================================
END OF REPORT
================================================================================
```

---

## SCORING GUIDELINES

### Score Definitions with Examples

| Score | Label | Definition | Example Indicators (Content-Based) |
|-------|-------|------------|-----------------------------------|
| **+1.0** | Highly Favorable | Clear, strong positive signals with quantifiable evidence | "Revenue grew 25% YoY"; "Launched 5 new products"; "Expanded into 3 new markets"; "Operating margin improved 400bps"; "Debt reduced by $500M" |
| **+0.5** | Favorable | Moderate positive signals or stable positive trends | "Revenue growth of 5%"; "On track with stated strategic initiatives"; "Market share held steady"; "Slight margin improvement of 50bps" |
| **0.0** | Neutral | No clear signal, mixed signals, or no information available | Topic not discussed; Both positive and negative factors mentioned with no net direction; Guidance unchanged; Results exactly in line with prior guidance |
| **-0.5** | Unfavorable | Moderate negative signals or concerning trends | "Revenue declined 3%"; "Facing increased competition in core market"; "Margin pressure of 100bps"; "Product launch delayed by one quarter" |
| **-1.0** | Highly Unfavorable | Clear, strong negative signals with quantifiable evidence | "Revenue declined 20%"; "Significant losses of $X reported"; "Major regulatory fine"; "Key product recall"; "CFO departure" |

### Evidence Strength Guidelines (Diagnostic Only)

| Strength | Definition | When to Use |
|----------|------------|-------------|
| **Strong** | Multiple explicit statements with specific data/metrics | Topic discussed extensively with numbers, trends, and context |
| **Moderate** | Clear discussion but limited quantification | Topic addressed but without detailed metrics or extensive elaboration |
| **Weak** | Only indirect or passing references | Brief mention without elaboration; inferred from related discussion |
| **None** | No relevant information found | Topic not addressed anywhere in the transcript |

**Note:** Evidence Strength is provided for transparency and diagnostic purposes only. It should NOT mechanically determine the numerical score.

---

## IMPORTANT REMINDERS

1. **Content over tone:** Your scores must reflect WHAT management says (facts, metrics, actions, outcomes), NOT HOW they say it (confidence, optimism, enthusiasm). Strip away rhetoric and focus on substance.

2. **Q&A is primary:** Analyst questions reveal what professional analysts consider important. Weight Q&A evidence more heavily than prepared remarks, which may be optimistically framed.

3. **This transcript only:** Do not infer anything based on company reputation, industry norms, prior calls, or future knowledge. Evaluate only what is explicitly stated in this transcript.

4. **Handle missing information correctly:** Many sub-criteria may not be discussed in any given earnings call. This is normal. Assign 0.0 when information is absent, but recognize this as "unknown" not "neutral" — especially for risks.

5. **Risk asymmetry:** For Business Risks (Criterion 4), absence of discussion means lack of visibility into risk management, NOT that risks are low. Note this explicitly in rationales.

6. **Cite evidence:** Always include the relevant text that supports your score. If you cannot cite specific substantive content, the evidence strength should be "Weak" or "None" and score should typically be 0.0.

7. **Reproducibility:** Another analyst using this same prompt on the same transcript should arrive at substantially similar scores. Avoid subjective interpretation where possible.
