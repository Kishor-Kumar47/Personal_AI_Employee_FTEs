---
type: email
source: gmail
message_id: 19c514e4541badf6
from: Google Cloud <CloudPlatform-noreply@google.com>
subject: [Action Advised] Review Google Cloud credential security best practices
date: Thu, 12 Feb 2026 02:03:29 -0800
received: 2026-03-01T22:56:00.244382
priority: high
status: pending
snippet: Secure service account and API keys to prevent unauthorized access. MY CONSOLE Hello Mr, We&#39;re writing to provide you with security best practices regarding the management of service account keys
---

# Email: [Action Advised] Review Google Cloud credential security best practices

## Sender
**From:** Google Cloud <CloudPlatform-noreply@google.com>

## Date
Thu, 12 Feb 2026 02:03:29 -0800

## Preview
Secure service account and API keys to prevent unauthorized access. MY CONSOLE Hello Mr, We&#39;re writing to provide you with security best practices regarding the management of service account keys

## Content
Secure service account and API keys to prevent unauthorized access.




MY CONSOLE




Hello Mr,

We're writing to provide you with security best practices regarding the  
management of service account keys and API keys within your Google Cloud  
environment.

Recent security trends indicate that long-lived credentials without proper  
security best practices remain a top security risk for unauthorized access.  
To ensure your environment remains secure, and to modernize your  
authentication strategy, we strongly advise implementing the unified  
security framework outlined below.

What you need to do

Action advised:

Secure the credential lifecycle: Apply standard security hygiene by  
following these best practices:


Zero-Code Storage: Never commit keys to source code or version control. Use  
Secret Manager to inject credentials at runtime.
Disable Dormant Keys: Audit your active keys and decommission any that show  
no activity over the last 30 days.
Enforce API Restrictions: Never leave an API key unrestricted. Limit keys  
to specific APIs (eg, Maps Java Script only) and apply environmental  
restrictions (IP addresses, HTTP referrers, or bundle IDs).
Apply Least Privilege: Never give full permissions to a service account.  
Use the IAM recommender to prune unused permissions for service accounts,  
ensuring only the absolute minimum access required for their function.
Mandatory Rotation: Implement the iam.serviceAccountKeyExpiryHours policy  
to enforce a maximum lifespan for all user-managed service account keys. If  
service account keys are not needed, implement  
iam.managed.disableServiceAccountKeyCreation to disable the creation of new  
service account keys.

Improve operational safeguards: Ensure a rapid response to security  
incidents by completing the following:


Set Essential Contacts: Verify that your Essential Contacts are up to date  
to ensure critical security notifications reach the right people during an  
incident.
Set Billing Anomaly and Budget Alerts: Ensure billing anomaly and budget  
alerts notifications are acted on. A sudden spike in consumption is often  
the first indicator of a compromised credential.

We're here to help

We are committed to helping you maintain a secure environment. If you have  
any questions or require assistance, please contact Google Cloud Support.

Thanks for choosing Google Cloud.





– The Google Cloud Team





DOCUMENTATION



SUPPORT




Was this information helpful?

Yes Neutral No


© 2026 Google LLC 1600 Amphitheatre Parkway, Mountain View, CA 94043

You've received this mandatory service announcement to update you about  
important changes to Google Cloud or your account.



Visit Google Cloud blog Visit GCP on GitHub Visit Google Cloud on LinkedIn  
Visit Google Cloud on Twitter






## Suggested Actions
- [ ] Read and understand the email
- [ ] Determine required response
- [ ] Check Company_Handbook.md for response rules
- [ ] Draft reply or take action
- [ ] Create approval request if needed
- [ ] Mark email as read when done
- [ ] Move to /Done when complete

## Notes
_Add your notes here_

---
*Processed by Gmail Watcher v1.0 (Silver Tier)*
