======================================================================
NAIVE vs ENHANCED RAG DEMO
======================================================================

# Naive vs Enhanced RAG — Findings

## Q1: Slack Connection (Key Win)
Query transformation directly fixed the Day 44 retrieval failure.
- Original: "How do I connect TechFlow to Slack?"
- Transformed: "How do I integrate TechFlow with Slack for communication and notifications?"
- Naive answer: partial refusal
- Enhanced answer: correct, complete answer
- Cause: expansion of "connect" to "integrate...for communication and notifications"
  pulled the correct chunk into retrieval.

## Hybrid Spotlight
BM25 did not produce visible wins on the four test queries — vector embeddings
were already strong enough to retrieve the correct documents for exact codes
like TF-429 and specific figures like $1,500. Hybrid search provides insurance
for cases where vector similarity fails on exact-match terms; this dataset's
documents are short enough that semantic overlap is high regardless.
BM25's value is more pronounced on longer documents where exact terms are
sparse relative to surrounding context.

## Regression: Q12 (Asana Import)
- Original: "Can I import projects from Asana?" — clear, specific query
- Transformed: "Is it possible to import project data from Asana into this software?"
- Naive answer: complete (included attachment size limit detail)
- Enhanced answer: truncated (attachment detail dropped)
- Cause: transformer replaced "TechFlow" with "this software" — a vaguer phrase
  that slightly shifted retrieval. The transformer prompt instructs it to leave
  clear queries unchanged, but the model transformed it anyway.
- Fix: add a stricter instruction in the transformer prompt, or add a confidence
  gate — only apply transformation if the query contains vague terms.

## Overall Assessment
Enhanced RAG outperforms naive on ambiguous or underspecified queries.
For clear, specific queries it performs equivalently or slightly worse due
to unnecessary transformation. Production recommendation: apply query
transformation conditionally — run a classifier first to detect vague queries,
transform only those, pass specific queries directly to retrieval.

======================================================================

## Results

[Q1] How do I connect TechFlow to Slack?
  → Transformed: How do I integrate TechFlow with Slack for communication and notifications?

  NAIVE:    The context does not provide specific instructions on how to connect TechFlow to Slack. It only mentions that TechFlow connects to Slack via OAuth 2.0 and sends automated notifications to chosen Slack...

  ENHANCED: To integrate TechFlow with Slack for communication and notifications, you need to connect TechFlow to Slack via OAuth 2.0. Once connected, TechFlow will send automated notifications for task updates, ...


[Q2] What are the remote work hours policy?
  → Transformed: What is the policy regarding remote work hours?

  NAIVE:    TechFlow employees may work remotely up to 3 days per week. The core hours are from 10am to 3pm in the employee's local time zone. Attendance at the weekly all-hands meeting on Thursdays at 10am PT is...

  ENHANCED: TechFlow employees may work remotely up to 3 days per week, with core hours being from 10am to 3pm in the employee's local time zone. Attendance at the weekly all-hands meeting on Thursdays at 10am PT...


[Q3] How much does the Business plan cost per user?
  → Transformed: What is the cost per user for the Business subscription plan?

  NAIVE:    The Business plan costs $28 per user per month when billed monthly, or $22 per user per month when billed annually [Source: Pricing Page | Category: pricing_info]....

  ENHANCED: The cost per user for the Business subscription plan is $28 per user per month when billed monthly, or $22 per user per month when billed annually [Source: Pricing Page | Category: pricing_info]....


[Q4] I'm getting error code TF-401, what does it mean?
  → Transformed: I am encountering error code TF-401; can you explain its meaning and possible solutions?

  NAIVE:    Error code TF-401 means your session has expired or your account lacks permission to perform the action. To resolve this, log out and log back in to refresh your session. If the error persists after r...

  ENHANCED: Error code TF-401 means your session has expired or your account lacks permission to perform the action you are trying to execute. To resolve this issue, you should log out and then log back in to ref...


[Q5] Can I export my data if I cancel?
  → Transformed: Can I export my data after I cancel my subscription?

  NAIVE:    Yes, you can export your data if you cancel your TechFlow subscription. Your data is retained for 90 days after cancellation, during which you can export everything. After 90 days, the data is permane...

  ENHANCED: Yes, you can export your data after you cancel your subscription, as your data is retained for 90 days after cancellation. During this period, you can export everything [Source: FAQ | Category: produc...


[Q6] How many PTO days do new employees get?
  → Transformed: What is the number of paid time off days that new employees receive?

  NAIVE:    New employees at TechFlow accrue 15 days of Paid Time Off (PTO) per year in the first two years of employment [Source: Employee Handbook | Category: company_policy]....

  ENHANCED: New employees receive 15 days of paid time off (PTO) per year in the first two years of their employment [Source: Employee Handbook | Category: company_policy]....


[Q7] Does TechFlow support SSO and which identity providers?
  → Transformed: Does TechFlow support Single Sign-On, and which identity providers are compatible with it?

  NAIVE:    Yes, TechFlow supports single sign-on (SSO) via SAML 2.0 and OIDC on Business and Enterprise plans. The supported identity providers include Okta, Azure Active Directory, Google Workspace, and OneLogi...

  ENHANCED: Yes, TechFlow supports Single Sign-On (SSO) via SAML 2.0 and OIDC on Business and Enterprise plans. The compatible identity providers include Okta, Azure Active Directory, Google Workspace, and OneLog...


[Q8] What happens when I exceed my storage limit?
  → Transformed: What are the consequences of exceeding my data storage limit?

  NAIVE:    When you exceed your storage limit, TechFlow sends email warnings at 80% and 95% of your storage limit. If you reach 100%, you can no longer upload new attachments until you free up space or upgrade y...

  ENHANCED: When you exceed your storage limit, TechFlow sends email warnings at 80% and 95% of your limit. If you reach 100%, you can no longer upload new attachments until you either free up space or upgrade yo...


[Q9] How do I set up two-factor authentication?
  → Transformed: How do I configure two-factor authentication for my account?

  NAIVE:    To set up two-factor authentication (2FA), go to Profile > Security > Two-Factor Authentication. Click 'Enable 2FA'. Then, scan the QR code with an authenticator app (such as Google Authenticator, Aut...

  ENHANCED: To configure two-factor authentication (2FA) for your account, go to Profile > Security > Two-Factor Authentication. Click 'Enable 2FA', then scan the QR code with an authenticator app (such as Google...


[Q10] What is the refund policy for annual plans?
  → Transformed: What is the refund policy for annual subscription plans?

  NAIVE:    For annual plans, a full refund is available within 14 days of the initial purchase or annual renewal. After 14 days, no refunds are issued, but you may cancel to prevent future charges, and your acce...

  ENHANCED: For annual subscription plans, a full refund is available within 14 days of the initial purchase or annual renewal. After 14 days, no refunds are issued, but you may cancel to prevent future charges, ...


[Q11] How does AI task auto-assignment decide who to assign work to?
  → Transformed: How does artificial intelligence for task auto-assignment determine the appropriate individual for work assignments?

  NAIVE:    TechFlow's AI task auto-assignment decides who to assign work to by analyzing each task's required skills, estimated effort, and priority. It then matches the task to the best available team member ba...

  ENHANCED: TechFlow's AI for task auto-assignment determines the appropriate individual for work assignments by analyzing each task's required skills, estimated effort, and priority. It then matches the task to ...


[Q12] Can I import projects from Asana?
  → Transformed: Is it possible to import project data from Asana into this software?

  NAIVE:    Yes, you can import projects from Asana into TechFlow using the one-click import wizard, which automatically maps projects, tasks, subtasks, due dates, and assignees. Attachments under 100MB each are ...

  ENHANCED: Yes, it is possible to import project data from Asana into TechFlow using the one-click import wizard [Source: FAQ | Category: product_faq]....


[Q13] What integrations are available on the free Starter plan?
  → Transformed: What software integrations are included in the free Starter subscription plan?

  NAIVE:    The free Starter plan does not include integrations. It does not support AI features, integrations, or API access [Source: Pricing Page | Category: pricing_info]....

  ENHANCED: The free Starter plan does not include integrations, as it specifically states that it does not include AI features, integrations, or API access [Source: Pricing Page]....


[Q14] How do I invite someone to my workspace?
  → Transformed: How do I send an invitation to someone to join my collaborative workspace?

  NAIVE:    To invite someone to your workspace, go to Settings > Team > Invite Members. Enter the email addresses (comma-separated for bulk invites), assign a role (Admin, Member, or Viewer), and click Send Invi...

  ENHANCED: To send an invitation to someone to join your collaborative workspace in TechFlow, go to Settings > Team > Invite Members. Enter the email addresses (comma-separated for bulk invites), assign a role (...


[Q15] What is the API rate limit on the Business plan?
  → Transformed: What is the application programming interface rate limit for the Business subscription plan?

  NAIVE:    The API rate limit on the Business plan is 1,000 requests per minute [Source: Help Center | Category: support_article]....

  ENHANCED: The application programming interface (API) rate limit for the Business subscription plan is 1,000 requests per minute [Source: Help Center | Category: support_article]....


[Q16] How does billing work if I add a user mid-month?
  → Transformed: What is the billing process if I add a new user in the middle of the month?

  NAIVE:    When you add a user mid-cycle, you are charged a prorated amount for the remainder of the current billing period [Source: Pricing Page | Category: pricing_info]....

  ENHANCED: When you add a new user in the middle of the month, you will be charged a prorated amount for the remainder of the current billing period [Source: Pricing Page | Category: pricing_info]....


[Q17] What are the parental leave benefits?
  → Transformed: What are the benefits associated with parental leave policies?

  NAIVE:    TechFlow provides 16 weeks of fully paid parental leave for primary caregivers and 8 weeks for secondary caregivers, regardless of gender. Leave may begin up to 4 weeks before the expected birth or ad...

  ENHANCED: The benefits associated with parental leave policies at TechFlow include 16 weeks of fully paid parental leave for primary caregivers and 8 weeks for secondary caregivers, regardless of gender. Additi...


[Q18] How do I recover a deleted task?
  → Transformed: How can I restore a deleted task in the software application?

  NAIVE:    To recover a deleted task, go to the Trash, which is accessible from the left sidebar under Archive > Trash. Find the task you want to restore and click 'Restore'. Restored tasks will return to their ...

  ENHANCED: To restore a deleted task in the software application, go to the Trash, which is accessible from the left sidebar under Archive > Trash. Find the task you want to restore and click 'Restore'. The rest...


[Q19] Does TechFlow have a startup discount program?
  → Transformed: Does TechFlow offer a discount program for startups or new businesses?

  NAIVE:    Yes, TechFlow has a startup program that offers startups under 3 years old with fewer than 20 employees 6 months of the Business plan at no cost. Acceptance into the program is at TechFlow's discretio...

  ENHANCED: Yes, TechFlow offers a startup program for startups under 3 years old with fewer than 20 employees, which includes 6 months of the Business plan at no cost. However, acceptance into the program is at ...


[Q20] What AI features can I turn off if I don't want them?
  → Transformed: Which artificial intelligence features can I disable if I do not want to use them?

  NAIVE:    You can toggle off the following AI features in TechFlow if you don't want them: automatic task assignment, deadline risk prediction, sprint velocity forecasting, meeting summary generation, and natur...

  ENHANCED: You can disable the following AI features in TechFlow if you do not want to use them: automatic task assignment, deadline risk prediction, sprint velocity forecasting, meeting summary generation, and ...


======================================================================
HYBRID SEARCH SPOTLIGHT — Exact-match queries
======================================================================

[Query] TF-429 error
  NAIVE:    Error code TF-429 means you have exceeded the API rate limit for your plan. Business plans allow 1,000 API requests per minute. To resolve this issue, you should reduce your request frequency or imple
  ENHANCED: To troubleshoot and resolve the TF-429 error code, which indicates that you have exceeded the API rate limit for your plan, follow these steps:

1. **Reduce Request Frequency**: Decrease the number of

[Query] What is the rate limit for Enterprise plans?
  NAIVE:    The rate limit for Enterprise plans is unlimited API access [Source: Help Center | Category: support_article].
  ENHANCED: The Enterprise subscription plans have unlimited API access, meaning there is no request rate limit [Source: FAQ | Category: product_faq].

[Query] How much storage does the Pro plan include?
  NAIVE:    The Pro plan includes 50GB of storage per workspace [Source: Pricing Page | Category: pricing_info].
  ENHANCED: The total storage capacity included in the TechFlow Pro Plan is 50GB per workspace [Source: Pricing Page | Category: pricing_info].

[Query] What is the L&D budget amount?
  NAIVE:    The annual L&D budget for all full-time employees is $1,500 for courses, conferences, books, and certifications [Source: Employee Handbook | Category: company_policy].
  ENHANCED: The budget amount for Learning and Development is $1,500 annually for all full-time employees [Source: Employee Handbook].