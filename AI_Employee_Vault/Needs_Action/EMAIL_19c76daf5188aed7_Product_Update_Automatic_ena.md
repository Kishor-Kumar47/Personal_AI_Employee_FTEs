---
type: email
source: gmail
message_id: 19c76daf5188aed7
from: Google Cloud <CloudPlatform-noreply@google.com>
subject: [Product Update] Automatic enablement of new OpenTelemetry ingestion API
date: Thu, 19 Feb 2026 09:03:06 -0800
received: 2026-03-01T22:55:59.468492
priority: normal
status: pending
snippet: We&#39;re enabling a new OTLP ingestion API starting Mar 23, 2026. MY CONSOLE Hello Mr, You may have previously received a notification regarding this update. If so, please disregard this message. We
---

# Email: [Product Update] Automatic enablement of new OpenTelemetry ingestion API

## Sender
**From:** Google Cloud <CloudPlatform-noreply@google.com>

## Date
Thu, 19 Feb 2026 09:03:06 -0800

## Preview
We&#39;re enabling a new OTLP ingestion API starting Mar 23, 2026. MY CONSOLE Hello Mr, You may have previously received a notification regarding this update. If so, please disregard this message. We

## Content
Hello Mr,

We’re writing to let you know that Cloud Observability has launched a new  
OpenTelemetry (OTel) ingestion API[1] that supports native OpenTelemetry  
Protocol (OTLP) logs, trace spans, and metrics. Starting March 4, 2026,  
this API will be added as a dependency for the current Cloud Logging, Cloud  
Trace, and Cloud Monitoring ingestion APIs. This change ensures a seamless  
transition as collection tools migrate to this new unified endpoint.

What you need to know

Key changes:

    - The existing Cloud Observability ingestion APIs  
(logging.googleapis.com, cloudtrace.googleapis.com, and  
monitoring.googleapis.com) are automatically activated when you create a  
Google Cloud project using the Google Cloud console or gcloud CLI. The  
behavior remains unchanged for projects created via API, which do not have  
these ingestion APIs enabled by default. Starting March 4, 2026, the new  
OTel ingestion endpoint telemetry.googleapis.com will automatically  
activate when any of these specified APIs are enabled.
    - In addition, we will automatically enable this new endpoint for all  
existing projects that already have current ingestion APIs active.

What you need to do

No action is required from you for this API enablement change, and there  
will be no disruption to your existing services. You may disable the API at  
any time by following these instructions[2].

Refer to the attachment for a list of the projects that will automatically  
enable the new endpoint

We’re here to help

If you have any questions or require assistance, please contact Google  
Cloud Support[3].

Thanks for choosing Google Cloud Observability.

– The Google Cloud Team

[1]  
https://docs.cloud.google.com/stackdriver/docs/reference/telemetry/overview
[2] https://docs.cloud.google.com/service-usage/docs/enable-disable
[3] https://support.google.com/

© 2026 Google LLC 1600 Amphitheatre Parkway, Mountain View, CA 94043

You’ve received this mandatory service announcement to update you about  
important changes to Google Cloud or your account.


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
