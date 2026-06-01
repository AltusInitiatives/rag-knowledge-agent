# Embedding Model Comparison: small vs large

| Query | Small Top-1 Distance | Large Top-1 Distance | Same Top Result? |
|-------|---------------------|---------------------|-----------------|
| How do I integrate with third-party tools? | 0.4916 | 0.5431 | ✅ |
| What is the cancellation policy? | 0.5758 | 0.5894 | ✅ |
| I can't log in to my account | 0.5016 | 0.5342 | ✅ |
| How does pricing scale with team size? | 0.5509 | 0.4983 | ✅ |
| What data does TechFlow store about me? | 0.3784 | 0.3741 | ❌ |
| How do I set up automated workflows? | 0.381 | 0.4029 | ✅ |
| Can I customize notification settings? | 0.3127 | 0.3653 | ✅ |
| What happens to my data if I cancel? | 0.3926 | 0.3881 | ✅ |
| How do I upgrade my plan? | 0.574 | 0.5785 | ✅ |
| Does TechFlow support SSO? | 0.1481 | 0.1408 | ✅ |

## Cost Reference
- text-embedding-3-small: $0.02 / 1M tokens
- text-embedding-3-large: $0.13 / 1M tokens (6.5x more expensive)

## Conclusion
Across 10 test queries, text-embedding-3-large produced the same top result as text-embedding-3-small in 9 out of 10 cases (90%). The single divergence occurred on the ambiguous query "What data does TechFlow store about me?" — a query with no direct match in the knowledge base, which is precisely where a stronger model might show its advantage.

Distance scores tell a similar story: neither model consistently outperformed the other. small returned a lower (better) distance on 6 queries; large returned a lower distance on 4. The differences were marginal in most cases — rarely more than 0.05.

Recommendation: For a knowledge base of this type — short, structured documents with clear topical coverage — text-embedding-3-small is the correct choice. It delivers equivalent retrieval quality at 6.5x lower cost. text-embedding-3-large is worth evaluating when queries are semantically complex, documents are long and nuanced, or when marginal retrieval improvements have measurable downstream impact (e.g., a medical or legal knowledge base where a wrong retrieval has real consequences). For most client automation projects, small is the default until proven otherwise.