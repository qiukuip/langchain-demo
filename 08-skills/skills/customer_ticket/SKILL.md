---
name: Customer Ticket
description: Use this skill to process the tickets from customers
---

#  Customer Ticket

## Overview

This skill explains how to process customer's ticket.

## Instructions

### 1. Update status

Use update_ticket_status tool to update the status of the ticket from "New" to "Processing" first.

If the status of the ticket is "Complete" or "Complete but reject", ignore it directly!

### 2. Classify

Use the classify_ticket tool to classify ticket, the class maybe is:
- Customer Inquiry
- Product Feedback
- Order Status
- Refund
- Other

### 3. Process

Process tickets by the description below:

| Ticket Class | How to process                                                                                                                                                                                                                   |
| --- |----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Customer Inquiry | Use pass_ticket tool to pass it to Customer Service Group, update ticket status to "Pending CSG"                                                                                                                                 |
| Product Feedback | Use pass_ticket tool to pass it to Product Development Group, update ticket status to "Pending PDG"                                                                                                                              |
| Order Status | Use query_order tool to query the order status, update ticket status to "Complete"                                                                                                                                               |
| Refund | Request approval, if get approval, use refund tool to process the ticket and update ticket status to "Complete", if rejected, update ticket status to "Complete but reject", otherwise, update ticket status to "Pending refund" |
| Other | Pass it to Customer Service Group, update ticket status to "Pending CSG"                                                                                                                                                          |

Important note: If the ticket class is "Refund", must request approval!

When ticket process complete, use update_ticket_status to update the ticket status to "Complete".
