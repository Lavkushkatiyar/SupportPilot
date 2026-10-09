# SupportLens Intent Taxonomy

The taxonomy defines the support intent assigned to an incoming customer
message.

## Classification Principle

Assign the intent based on the customer's primary support problem.

A message may mention multiple topics, but the classifier should select the
intent that best represents the issue the customer is asking Apple Support
to resolve.

---

## 1. software_update_issue

### Definition

Problems directly related to installing, updating, upgrading, or rolling
back iOS or macOS.

### Includes

- iOS or macOS update failures
- Update installation problems
- Updates getting stuck
- Problems clearly caused by an operating-system update
- Requests to downgrade or roll back an OS update

### Excludes

- Battery problems where battery drain is the primary complaint
- Wi-Fi or Bluetooth problems where connectivity is the primary complaint
- Hardware problems where physical/device failure is the primary complaint

### Examples

- "My iOS update won't install."
- "My Mac is stuck while updating."
- "How can I downgrade my iPhone after this update?"

---

## 2. battery_and_charging

### Definition

Problems where battery life or charging is the customer's primary concern.

### Includes

- Rapid battery drain
- Battery not holding charge
- Charging problems
- Charger-related problems
- Battery-related hardware symptoms

### Excludes

- General device performance problems where battery is not the main issue
- Connectivity problems
- OS update problems where updating itself is the main issue

### Examples

- "My battery dies within a few hours."
- "My iPhone won't charge."
- "The battery drains extremely fast."

---

## 3. device_hardware_issue

### Definition

Physical or device-level failures where hardware malfunction is the
primary support problem.

### Includes

- Broken or cracked screens
- Broken buttons
- Display failures
- Device not powering on
- Physical device damage
- Other clearly hardware-related failures

### Excludes

- Battery or charging problems when those are the primary issue
- OS update problems
- Software/settings problems

### Examples

- "I cracked my iPhone screen."
- "My power button doesn't work."
- "My MacBook screen stays black."

---

## 4. icloud_backup_data

### Definition

Problems involving iCloud, backups, restoring data, or loss/access to
personal data.

### Includes

- iCloud problems
- iCloud backup failures
- Restoring from backup
- Missing or lost photos
- Missing or lost messages
- Data transfer or recovery problems

### Excludes

- General photo/app problems unrelated to backup or data storage
- Apple ID authentication problems where account access is the primary issue

### Examples

- "My iCloud backup won't complete."
- "I can't restore my photos from iCloud."
- "My messages disappeared after restoring my phone."

---

## 5. apple_id_account_security

### Definition

Problems involving Apple ID access, authentication, passwords, account
security, or unauthorized access.

### Includes

- Forgotten Apple ID passwords
- Locked accounts
- Apple ID recovery
- Unauthorized account access
- Suspicious account activity
- Stolen-device account security

### Excludes

- App purchases or refunds where billing is the primary issue
- General device problems
- iCloud data problems where data recovery is the primary issue

### Examples

- "I forgot my Apple ID password."
- "My Apple ID is locked."
- "I think someone accessed my account."

---

## 6. app_store_purchase_billing

### Definition

Problems involving the App Store, purchases, subscriptions, refunds, or
billing.

### Includes

- App Store download problems
- App Store update problems
- Purchases
- Refund requests
- Subscription problems
- Unexpected charges
- Billing information problems

### Excludes

- Problems inside a specific application unrelated to purchasing
- Apple ID problems where account access is the primary issue

### Examples

- "I can't download an app from the App Store."
- "I was charged twice for my subscription."
- "How can I get a refund for this purchase?"

---

## 7. connectivity_and_communication

### Definition

Problems where connectivity or communication functionality is the primary
support issue.

### Includes

- Wi-Fi
- Bluetooth
- Cellular connectivity
- Phone calls
- iMessage
- FaceTime
- Connection failures

### Excludes

- Settings questions where configuration is the primary issue
- OS update problems where the update itself is the primary issue

### Examples

- "My iPhone keeps disconnecting from Wi-Fi."
- "Bluetooth won't connect to my car."
- "I can't make or receive calls."

---

## 8. settings_and_how_to

### Definition

Questions primarily asking how to configure, enable, disable, or use a
device or feature.

### Includes

- Settings questions
- Configuration questions
- "How do I..." questions
- "How can I..." questions
- Enabling or disabling features
- Navigation/help with device settings

### Excludes

- A direct technical failure where the customer is asking for troubleshooting
  rather than configuration instructions
- Hardware failures
- Account/security problems

### Examples

- "How do I turn off this feature?"
- "How can I change this setting?"
- "How do I enable this option?"

---

## Unknown / Insufficient Context

Messages that do not contain enough information to reliably determine an
intent should not be forced into one of the eight support intents.

Examples:

- "It's so annoying."
- "Why?????"
- "Please fix this."

These messages may require additional conversation context before they can
be classified reliably.