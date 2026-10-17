# SupportLens — Intent Classification and Annotation Policy

## 1. Purpose

This document defines the authoritative rules for assigning intent labels to Apple Support customer messages.

It serves as the common specification for:

1. Creating and reviewing the human-annotated golden set.
2. Implementing the LLM intent-classification prompt.
3. Adjudicating disagreements between existing annotations and model predictions.
4. Evaluating classifier performance consistently across model and prompt versions.

## 2. Core classification principles

### 2.1 Classify the primary intent

Assign exactly one label representing the customer's primary support issue or request.

When a message contains several symptoms, identify the main complaint and the context that best explains why the customer is contacting support.

Do not assign multiple labels merely because a message mentions multiple products, symptoms, or services.

### 2.2 Interpret natural language reasonably

Customers are not required to describe a problem in technically precise language.

For example:

- "Ever since updating, my phone keeps freezing."
- "iOS 11 has ruined my battery."
- "My phone keeps restarting after the update."

These messages provide enough contextual evidence to identify an update-related complaint even though the customer does not explain the technical mechanism.

Do not use `unknown_or_insufficient_context` simply because a message lacks technical detail when its primary intent remains reasonably identifiable.

### 2.3 Do not invent missing information

Reasonable interpretation is permitted; unsupported assumptions are not.

For example:

- A password error does not automatically mean the customer has an Apple ID problem.
- A Wi-Fi complaint does not automatically mean the router is defective.
- A disappearing photo does not automatically establish that iCloud Backup failed.
- Mentioning an iPhone model does not establish hardware failure.

Use the information actually provided and any relevant conversation context available to the annotator.

### 2.4 Distinguish a symptom from a stated trigger

A symptom describes what is wrong. A trigger describes when or under what circumstances the problem appeared.

Examples:

- Symptom: battery drains quickly.
- Trigger: the customer reports that the drain started after an iOS update.
- Symptom: applications crash.
- Trigger: the customer says the crashes began immediately after updating.

The stated trigger can determine the appropriate intent when the taxonomy explicitly prioritizes update-related regressions.

### 2.5 Preserve evidence and historical annotations

Never overwrite original annotations during review.

Store the original label and notes separately from the proposed V2 label, rationale, confidence, and adjudication result. A model prediction is evidence to evaluate, not an authoritative answer.

---

## 3. Allowed intent labels

The classifier must return exactly one of these ten labels:

1. `software_update_issue`
2. `battery_and_charging`
3. `device_hardware_issue`
4. `icloud_backup_data`
5. `apple_id_account_security`
6. `app_store_purchase_billing`
7. `connectivity_and_communication`
8. `settings_and_how_to`
9. `unknown_or_insufficient_context`
10. `other_or_out_of_scope`

The first eight are defined support intents. The final two distinguish an issue that cannot be identified from an identifiable issue outside the supported taxonomy.

---

## 4. Intent definitions and inclusion rules

### 4.1 `software_update_issue`

**Definition:** Problems involving installing, downloading, applying, upgrading, or rolling back an operating system, as well as problems the customer explicitly associates with an OS update.

Include:

- Failed or interrupted iOS/macOS installation.
- An operating-system upgrade that will not complete.
- A failed rollback or an update stuck in progress.
- Crashes, freezing, sluggishness, battery drain, or other regressions that the customer explicitly associates with an OS update.
- Complaints that clearly identify an OS update as the source or context of the reported regression, even when the precise symptom is described informally.
- Vague but interpretable complaints whose primary subject is an OS update.

Examples:

| Customer message | Label |
|---|---|
| "My iOS update is stuck at 80%." | `software_update_issue` |
| "Ever since updating, my phone keeps freezing." | `software_update_issue` |
| "Battery life has become terrible since iOS 11." | `software_update_issue` |
| "After updating macOS, none of my apps work properly." | `software_update_issue` |
| "Why is iOS 11 so bad?" | `software_update_issue`, when the complaint is clearly about the OS |

**Exclusion rules:**

- A mere OS-version mention is insufficient if no identifiable update issue or complaint is established.
- A question about how to configure a feature is `settings_and_how_to`.
- App Store application updates are not OS updates; classify them according to the application download/update problem or the actual primary issue.
- A problem that predates an update and is merely mentioned alongside it should not automatically receive this label.
- Do not assume an update caused a problem when the message provides no meaningful connection between the update and the complaint.

**Key rule:** When the customer explicitly says a problem started, appeared, or has continued since an OS update, prefer `software_update_issue` if the update-related regression is the primary framing of the complaint. Technical proof of causation is not required.

### 4.2 `battery_and_charging`

**Definition:** Problems whose primary subject is battery behavior or charging.

Include:

- Rapid battery drain without a meaningful OS-update-related framing.
- Battery capacity or battery health concerns.
- A device that will not charge.
- Charging that starts and stops unexpectedly.
- Charger, cable, or charging-accessory problems.
- Unexpected battery percentage changes.
- Battery-related shutdowns when battery behavior is the primary complaint.

Examples:

| Customer message | Label |
|---|---|
| "My battery drops from 80% to 20% in an hour." | `battery_and_charging` |
| "My iPhone won't charge with my cable." | `battery_and_charging` |
| "Battery health has fallen to 75%." | `battery_and_charging` |
| "My battery drains rapidly." | `battery_and_charging` |

**Precedence:** If the customer explicitly frames battery drain as a regression that started after an OS update, use `software_update_issue` under the update-related regression rule.

Do not classify every battery complaint as an update issue merely because an update is mentioned incidentally.

### 4.3 `device_hardware_issue`

**Definition:** Physical damage or device-level hardware malfunction that is the primary complaint and does not fit the battery/charging category.

Include:

- Broken screens.
- Physical damage to the device.
- Buttons that fail mechanically.
- Speakers, microphones, cameras, or other hardware components that malfunction.
- Hardware failures that are identifiable from the message.
- Device-level failures where hardware is clearly the reported issue.

Examples:

| Customer message | Label |
|---|---|
| "My iPhone screen cracked when I dropped it." | `device_hardware_issue` |
| "The physical volume button is stuck." | `device_hardware_issue` |
| "The rear camera produces no image." | `device_hardware_issue` |

**Exclusion rules:**

- Battery and charging problems belong to `battery_and_charging` unless an explicit update-related regression takes priority.
- A symptom alone does not prove a hardware failure.
- A software malfunction is not automatically a hardware issue just because it occurs on a physical device.
- If the customer explicitly frames the malfunction as a post-update regression, apply the update rule unless the update mention is incidental or the primary request is clearly different.

### 4.4 `icloud_backup_data`

**Definition:** Problems involving iCloud, backups, restoration, device-to-device transfer, or personal data storage, recovery, and access.

Include:

- iCloud backup failures.
- Restoring data from a backup.
- Moving data between devices.
- Missing or inaccessible photos, contacts, messages, or other personal data when the data problem is identifiable.
- iCloud synchronization or storage problems.
- Personal data loss during a restore or transfer.

Examples:

| Customer message | Label |
|---|---|
| "My iCloud backup will not complete." | `icloud_backup_data` |
| "My photos disappeared after restoring my iPhone." | `icloud_backup_data` |
| "How do I transfer everything to my new iPhone?" | `icloud_backup_data` |
| "My contacts are not syncing through iCloud." | `icloud_backup_data` |

**Exclusion rules:**

- Do not assume iCloud is responsible for missing data unless the message supports that interpretation.
- An Apple ID authentication problem belongs to `apple_id_account_security` when account access is the primary issue.
- A generic application malfunction belongs to the category that best represents the actual complaint.

### 4.5 `apple_id_account_security`

**Definition:** Problems primarily involving Apple ID access, authentication, account recovery, or account security.

Include:

- Apple ID sign-in failures.
- Apple ID password or account-recovery problems.
- Two-factor authentication failures.
- Account lockouts explicitly related to Apple ID.
- Unauthorized access to an Apple account.
- Account security alerts involving an identifiable Apple account.
- Account compromise or recovery requests.

Examples:

| Customer message | Label |
|---|---|
| "I cannot sign in to my Apple ID." | `apple_id_account_security` |
| "My Apple account has been locked." | `apple_id_account_security` |
| "I cannot receive my Apple ID verification code." | `apple_id_account_security` |

**Exclusion rules:**

- A password error in a third-party email application does not automatically imply an Apple ID issue.
- A general scam, phishing email, or suspicious telephone call is not automatically an Apple ID issue. Use this category when Apple account security is the primary identifiable concern; otherwise, assess whether the message belongs in `other_or_out_of_scope`.
- An iCloud data problem is classified under `icloud_backup_data` when data access or recovery, rather than account authentication, is primary.

### 4.6 `app_store_purchase_billing`

**Definition:** Problems primarily involving App Store downloads, application updates, purchases, refunds, subscriptions, or billing.

Include:

- App downloads that fail or remain pending.
- App Store download verification failures.
- Application updates that cannot be downloaded through the App Store.
- Failed or duplicate purchases.
- Refund requests.
- Subscription billing or cancellation problems.
- Charges for applications or services purchased through the App Store.

Examples:

| Customer message | Label |
|---|---|
| "My App Store download is stuck on waiting." | `app_store_purchase_billing` |
| "I was charged twice for an application." | `app_store_purchase_billing` |
| "I need a refund for an App Store purchase." | `app_store_purchase_billing` |
| "My application update will not download from the App Store." | `app_store_purchase_billing` |

**Exclusion rules:**

- A malfunction within an application is not automatically an App Store problem.
- An operating-system update problem belongs to `software_update_issue`.
- If the customer explicitly frames an App Store download failure as a regression caused by an OS update, apply the update rule when the OS-update-related regression is the primary framing.

### 4.7 `connectivity_and_communication`

**Definition:** Problems primarily involving network connectivity or communication services.

Include:

- Wi-Fi connection failures.
- Bluetooth pairing or connectivity failures.
- Cellular signal, mobile data, or network connection problems.
- Calls that cannot connect or unexpectedly disconnect.
- iMessage activation or sending/receiving failures.
- FaceTime connection failures.
- Other identifiable connection problems within the supported scope.

Examples:

| Customer message | Label |
|---|---|
| "My iPhone will not connect to Wi-Fi." | `connectivity_and_communication` |
| "Bluetooth keeps disconnecting from my headphones." | `connectivity_and_communication` |
| "I cannot activate iMessage." | `connectivity_and_communication` |
| "My calls keep dropping." | `connectivity_and_communication` |

**Exclusion rules:**

- Do not infer a specific service or network cause without evidence.
- A page that does not open may represent connectivity, an application failure, or an unspecified problem. Use the available context to distinguish them.
- If a connectivity failure is explicitly framed as a regression following an OS update, apply the update rule when that framing is primary.

### 4.8 `settings_and_how_to`

**Definition:** Requests for instructions or assistance configuring, enabling, disabling, or using a device or software feature when the customer is not primarily reporting a malfunction.

Include:

- How to enable or disable a setting.
- Questions about using a device feature.
- Instructions for configuring notifications, display settings, or other options.
- Questions about how to perform a supported operation.
- Requests for guidance that do not describe a direct technical failure.

Examples:

| Customer message | Label |
|---|---|
| "How do I enable rotation lock?" | `settings_and_how_to` |
| "How can I disable notifications for this application?" | `settings_and_how_to` |
| "How do I make these files available offline?" | `settings_and_how_to`, if the referenced item and task are sufficiently clear |

**Exclusion rules:**

- Do not use this category for a direct malfunction that requires troubleshooting.
- A request to fix a setting that will not save is a technical failure, not merely a how-to question.
- If the requested operation or referenced object cannot be identified, use `unknown_or_insufficient_context`.

### 4.9 `unknown_or_insufficient_context`

**Definition:** The available message and relevant context do not provide enough information to identify the customer's primary support intent.

Use this category when:

- The customer refers to "this," "it," or "that problem" without enough recoverable context.
- A reply only confirms an OS version or says a restart was attempted, without identifying the underlying issue.
- The message is too fragmentary to determine what the customer needs.
- The customer references an image or attachment that is unavailable and that image is essential to understanding the issue.
- Several interpretations remain plausible and the available evidence does not support choosing one.

Examples:

| Customer message | Label |
|---|---|
| "It is still happening." | `unknown_or_insufficient_context`, if prior context is unavailable |
| "I'm using version 11.0.3." | `unknown_or_insufficient_context` |
| "I tried restarting too." | `unknown_or_insufficient_context`, if the original problem is unknown |
| "Why does this happen?" | `unknown_or_insufficient_context`, if the referenced event cannot be identified |

**Exclusion rules:**

- Do not use this label just because the customer communicates informally.
- Do not require a detailed technical diagnosis when the primary intent is recognizable.
- A vague complaint can still be classified if it clearly communicates the subject of the complaint.
- If the issue is identifiable but falls outside the supported taxonomy, use `other_or_out_of_scope` instead.

### 4.10 `other_or_out_of_scope`

**Definition:** The customer's issue or request is understandable, but it does not belong to any of the eight defined support intents.

Include:

- Order delivery or shipping complaints outside the supported categories.
- Standalone complaints about support procedures or service quality.
- Identifiable issues that do not fit the defined technical support categories.
- General service complaints whose subject is clear but unsupported by the taxonomy.

Examples:

| Customer message | Label |
|---|---|
| "My order still has not been delivered." | `other_or_out_of_scope` |
| "Customer support transferred me five times without resolving my complaint." | `other_or_out_of_scope` |
| "I want to complain about the way my repair appointment was handled." | `other_or_out_of_scope`, if the primary issue is the service process |

**Exclusion rules:**

- Do not use this label as a fallback for unfamiliar wording.
- Do not use it when a supported intent is identifiable.
- Do not confuse an unclear issue with an out-of-scope issue.
- A complaint about an application, operating system, or device should still be classified under a supported intent when the available evidence supports one.

---

## 5. Precedence and tie-breaking rules

These rules are necessary because a single customer message may fit more than one category.

### Rule 1: OS-update-related regressions

If the customer explicitly associates a problem with an OS update and frames that regression as the primary complaint, prefer `software_update_issue` over the corresponding symptom category.

For example:

> "My battery has been terrible ever since I installed iOS 11."

Label: `software_update_issue`.

However:

> "My battery drains quickly. Also, I installed iOS 11 last month."

Label: `battery_and_charging`, unless the surrounding context establishes a meaningful relationship between the update and the battery problem.

The distinction is between an update-related complaint and an incidental update mention.

### Rule 2: Battery and charging take precedence over generic hardware

When the primary complaint is battery life, battery behavior, or charging, use `battery_and_charging` rather than `device_hardware_issue`, unless the update-related regression rule applies.

### Rule 3: Application problems versus App Store problems

A problem with an application itself is not automatically an App Store problem.

- Application crashes or broken application features: classify according to the primary problem and available taxonomy.
- App downloads, application updates, purchases, or billing: `app_store_purchase_billing`.
- Application malfunction explicitly framed as an OS-update regression: `software_update_issue` when the update-related regression is the primary framing.

### Rule 4: Account access versus data access

- Apple ID authentication, recovery, or account security: `apple_id_account_security`.
- Backup, restoration, transfer, or missing personal data: `icloud_backup_data`.

Choose the category that represents the actual primary issue, not merely a service name mentioned in the message.

### Rule 5: Settings requests versus technical failures

- Asking how to perform an operation: `settings_and_how_to`.
- Reporting that the operation fails, a setting will not save, or a feature malfunctions: classify according to the primary technical issue.

### Rule 6: Unknown versus out of scope

Ask two questions in order:

1. Can the customer's primary issue be reasonably identified?
2. If yes, does that issue fit a supported intent?

If the answer to the first question is no, use `unknown_or_insufficient_context`.

If the answer to the first question is yes but the second is no, use `other_or_out_of_scope`.

