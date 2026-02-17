# Compliance Implementation Reference

Detailed compliance requirements for GDPR, CCPA, FERPA, and COPPA.

---

## GDPR (EU General Data Protection Regulation)

### Consent Management
- Explicit opt-in for conversation history storage (Tier 1+)
- Clear privacy policy link in widget footer
- "Do Not Track" mode (browser-local only, no server sync)

### User Rights Implementation
- **Right to Access**: Export conversation history (JSON/CSV) via `/api/v1/user/export`
- **Right to Deletion**: One-click account deletion (Article 17) via `/api/v1/user/delete`
- **Right to Portability**: Download all user data in machine-readable format

### Configuration
```json
{
  "gdpr_controls": {
    "consent_banner": true,
    "privacy_policy_link": "/privacy",
    "data_export_endpoint": "/api/v1/user/export",
    "data_deletion_endpoint": "/api/v1/user/delete",
    "retention_policy": "30_days_inactive_anonymous"
  }
}
```

---

## CCPA (California Consumer Privacy Act)

### "Do Not Sell My Data" Opt-Out
- Widget footer includes "Do Not Sell My Personal Information" link
- Opt-out applies retroactively (existing data not sold)
- No account required to opt-out (global setting)

### Configuration
```json
{
  "ccpa_controls": {
    "do_not_sell_link": "/ccpa-opt-out",
    "opt_out_applies_retroactively": true,
    "third_party_sharing": false
  }
}
```

---

## FERPA (Family Educational Rights and Privacy Act)

### Student Privacy Protection
- No PII shared with third parties without parental consent (if <18)
- Educational records (progress, quiz scores) encrypted at rest
- Instructor access limited to authorized personnel

### Configuration
```json
{
  "ferpa_controls": {
    "age_gate": 13,
    "parental_consent_required_under": 18,
    "educational_records_encryption": "AES-256",
    "third_party_sharing": "parental_consent_only"
  }
}
```

---

## COPPA (Children's Online Privacy Protection Act)

### Age Gating (<13 years)
- Age verification before account creation
- Parental consent modal (email verification to parent)
- Limited data collection (no behavioral tracking for <13)

### Configuration
```json
{
  "coppa_controls": {
    "minimum_age": 13,
    "age_verification_method": "date_of_birth",
    "parental_consent_flow": "email_verification",
    "under_13_features_disabled": ["social_sharing", "public_profiles", "third_party_analytics"]
  }
}
```

---

## Privacy Consent Modal Template

```json
{
  "consent_modal": {
    "title": "Save Your Conversation?",
    "message": "We'll securely store your conversation history so you can access it from any device. You can delete it anytime.",
    "actions": [
      {"label": "Yes, Save My Conversation", "event": "consent_granted"},
      {"label": "No, Keep It Local Only", "event": "consent_denied"}
    ]
  }
}
```

## External References

| Regulation | Official Resource |
|------------|------------------|
| GDPR | https://gdpr.eu/ |
| CCPA | https://oag.ca.gov/privacy/ccpa |
| FERPA | https://www2.ed.gov/policy/gen/guid/fpco/ferpa/index.html |
| COPPA | https://www.ftc.gov/legal-library/browse/rules/childrens-online-privacy-protection-rule-coppa |
