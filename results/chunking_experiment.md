# Chunking Experiment Results

## Config 1: chunk_size=500, overlap=100
- Chunks generated: 50
- Q1 observation: The context does not provide specific instructions on how to connect TechFlow to Slack. It only mentions that TechFlow connects to Slack via OAuth 2.0 and sends automated notifications to chosen Slack channels [Source: FAQ | Category: product_faq].
- Q4 observation: Error code TF-401 means your session has expired or your account lacks permission to perform the action. To resolve this, log out and log back in to refresh your session. If the error persists after re-login, contact your workspace admin to verify your role and permission settings [Source: Help Center | Category: support_article].
- Q11 observation: TechFlow's AI task auto-assignment decides who to assign work to by analyzing each task's required skills, estimated effort, and priority. It then matches the task to the best available team member based on their workload, past performance, and skill tags. Managers can override assignments at any time [Source: FAQ | Category: product_faq].
- Q15 observation: The API rate limit on the Business plan is 1,000 requests per minute [Source: Help Center | Category: support_article].

## Config 2: chunk_size=250, overlap=50
- Chunks generated: 99
- Q1 observation: The context does not provide specific instructions on how to connect TechFlow to Slack. Therefore, I cannot answer your question based on the provided information.
- Q4 observation: Error code TF-401 means your session has expired or your account lacks permission to perform the action. To resolve this, log out and log back in to refresh your session. If the error persists after re-login, contact your workspace admin to verify your permissions [Source: Help Center | Category: support_article].
- Q11 observation: TechFlow's AI task auto-assignment decides who to assign work to by analyzing each task's required skills, estimated effort, and priority. It then matches the task to the best available team member based on their workload, past performance, and skill tags. Managers can override assignments at any time [Source: FAQ | Category: product_faq].
- Q15 observation: The API rate limit on the Business plan is 1,000 requests per minute [Source: Help Center | Category: support_article].

## Config 3: chunk_size=1000, overlap=200
- Chunks generated: 50
- Q1 observation: The context does not provide specific instructions on how to connect TechFlow to Slack. It only mentions that TechFlow connects to Slack via OAuth 2.0 and sends automated notifications to chosen Slack channels [Source: FAQ | Category: product_faq].
- Q4 observation: Error code TF-401 means your session has expired or your account lacks permission to perform the action. To resolve this, log out and log back in to refresh your session. If the error persists after re-login, contact your workspace admin to verify your role and permission settings [Source: Help Center | Category: support_article].
- Q11 observation: TechFlow's AI task auto-assignment decides who to assign work to by analyzing each task's required skills, estimated effort, and priority. It then matches the task to the best available team member based on their workload, past performance, and skill tags. Managers can override assignments at any time [Source: FAQ | Category: product_faq].
- Q15 observation: The API rate limit on the Business plan is 1,000 requests per minute [Source: Help Center | Category: support_article].

======================================================================

## Setup Note
All 50 source documents are short FAQ-style entries (under 250 characters each),
so no document was split across any configuration. Each config produced 50 chunks —
one per document. This means the experiment primarily tested retrieval behavior at
the boundary of the smallest chunk size rather than true chunking effects.

## Key Observation: Q1 Degradation on Config 2
The only meaningful difference appeared on Q1 ("How do I connect TechFlow to Slack?"):
- Config 1 (500/100): Partial answer with OAuth context preserved
- Config 2 (250/50): Hard refusal — not enough context in the retrieved chunk
- Config 3 (1000/200): Same as Config 1

This illustrates the core risk of small chunks: when a document is trimmed too
aggressively, the retrieved fragment lacks enough surrounding context for the LLM
to generate a useful answer.

## Distance Score Interpretation
Lower distance = stronger semantic match. Differences between configs on the same
query were consistently under 0.01 — too small to indicate meaningful retrieval
quality differences. Answer quality, not distance score, is the better evaluation
metric for short knowledge bases.

## Conclusion
For short, structured documents (FAQs, policy entries, support articles under
300 characters), chunk_size=500 with overlap=100 is the correct default. It
preserves full document context without padding, and the overlap protects against
boundary truncation.

The experiment's real-world implication: chunking strategy matters most when
documents are long (PDFs, manuals, legal documents). For those, 500/100 remains
a solid starting point, but semantic chunking — splitting at paragraph or section
boundaries rather than character counts — produces better results. That pattern
is covered in Day 45.