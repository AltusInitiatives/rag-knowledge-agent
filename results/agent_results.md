======================================================================
LANGGRAPH AGENT DEMO — TechFlow Support Agent
======================================================================
Note: The escalation query will pause and ask for your approval.


[Q1] What integrations does TechFlow support?
--------------------------------------------------
/Users/itsshinetam/rag-knowledge-agent/src/langchain_rag.py:64: LangChainDeprecationWarning: The class `Chroma` was deprecated in LangChain 0.2.9 and will be removed in 1.0. An updated version of the class exists in the `langchain-chroma package and should be used instead. To use it run `pip install -U `langchain-chroma` and import as `from `langchain_chroma import Chroma``.
  return Chroma(
TechFlow supports integrations with the following tools:

- Slack
- Microsoft Teams
- GitHub
- GitLab
- Jira
- Asana
- Google Workspace
- Salesforce
- Zapier

Additionally, TechFlow can connect with over 200 other tools via its REST API and native connectors.

[Q2] What is the refund policy for annual plans?
--------------------------------------------------
The refund policy for annual plans allows for a full refund within 14 days of the initial purchase or annual renewal. After 14 days, no refunds are issued, but you can cancel to prevent future charges, and your access will continue until the end of the paid period.

[Q3] How does AI task auto-assignment work?
--------------------------------------------------
AI task auto-assignment in TechFlow analyzes each task's required skills, estimated effort, and priority. It matches tasks to the best available team member based on their workload, past performance, and skill tags. Managers can override these assignments at any time.

[Q4] Can you pull up the account for customer C001?
--------------------------------------------------
The account details for customer C001 are as follows:

- **Name:** Alice Chen
- **Plan:** Business
- **Status:** Active
- **Joined:** March 15, 2024
- **Seats:** 12
- **Storage Used:** 47 GB

[Q5] What plan is customer C002 on?
--------------------------------------------------
Customer C002, Bob Martinez, is on the Pro plan.

[Q6] How much would 15 seats on the Business plan cost monthly?
--------------------------------------------------
The cost for 15 seats on the Business plan would be $420 per month.

[Q7] What's the annual cost for 8 Pro plan seats?
--------------------------------------------------
The annual cost for 8 Pro plan seats is $1,152. This is based on a rate of $12 per user per month, totaling $96 per month.

[Q8] Look up customer C001 and tell me how much they'd save switching to annual billing.
--------------------------------------------------
Alice Chen, with customer ID C001, would save $864 by switching to annual billing for the Business plan. 

- **Monthly Billing**: $336/month
- **Annual Billing**: $264/month

Let me know if you need any further assistance!

[Q9] Customer C003 says their account was suspended by mistake and they need it restored immediately.
--------------------------------------------------

⚠️  APPROVAL REQUIRED
Pending action: escalate_issue({'customer_id': 'C003', 'issue_summary': 'Account suspended by mistake, needs immediate restoration.', 'priority': 'high'})
Approve? (yes/no): yes
I've created a support ticket for customer C003 regarding the mistaken account suspension. The ticket ID is TKT-2033, and a support specialist will follow up within 1 hour.

[Q10] What plan is customer C999 on?
--------------------------------------------------
It seems that there is no customer found with the ID C999. Please double-check the customer ID and try again.

[Q11] How much does the Enterprise plan cost for 50 seats?
--------------------------------------------------
The Enterprise plan pricing is custom, and you'll need to contact sales at sales@techflow.io for a quote.

[Q12] What is the L&D budget for employees?
--------------------------------------------------
The annual Learning and Development (L&D) budget for full-time employees at TechFlow is $1,500. This budget can be used for courses, conferences, books, and certifications. Please note that budget requests must be submitted under the L&D category, and any unused budget does not roll over to the next year.

[Q13] How do I set up SSO with Okta?
--------------------------------------------------
To set up single sign-on (SSO) with Okta, you need to be on a Business or Enterprise plan, as SSO via SAML 2.0 and OIDC is available for those plans. Unfortunately, the specific steps for the setup are not detailed in the available resources. I recommend checking the TechFlow documentation or reaching out to your account administrator for detailed instructions on integrating with Okta.

[Q14] Calculate the price for 100 business seats annually.
--------------------------------------------------
The price for 100 business seats annually is $26,400. This includes a rate of $22 per user per month, totaling $2,200 per month. You save $7,200 compared to monthly billing.

[Q15] Does TechFlow have a startup program?
--------------------------------------------------
Yes, TechFlow has a startup program designed for startups that are under 3 years old and have fewer than 20 employees. It offers 6 months of the Business plan at no cost. To apply, startups can visit [techflow.io/startup](https://techflow.io/startup) and provide their company's founding date and LinkedIn page. Acceptance into the program is at TechFlow's discretion, and only one application per company is allowed.