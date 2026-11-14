# Crypto Hunter AI 7.2 — Test deployment

## What is new
- Eight-language interface, Bitcoin public address lookup, puzzle catalog, recovery guidance and commission simulation.
- Optional email/password sign-in using Supabase Auth, with per-user puzzle and case records in PostgreSQL protected by Row Level Security (RLS).
- No Supabase settings: public demo mode, temporary puzzle list; recovery case storage disabled.

## Upgrade the existing public Streamlit test app
1. Upload/replace `app_v7.py` and `requirements.txt` in `AGHFerreira/crypto-hunter-ai-v7-test`. Do not upload `schema_supabase.sql` as a requirement for Streamlit; it is only a setup script.
2. Check the Streamlit test app displays version 7.2. It works in demo mode without database configuration.
3. For private, persistent storage: create your own Supabase project; open **SQL Editor** and execute `schema_supabase.sql` **once** on a fresh project. Verify RLS policies in the dashboard.
4. In Streamlit Community Cloud **App settings → Secrets**, set:

```toml
SUPABASE_URL = "https://YOUR_PROJECT.supabase.co"
SUPABASE_ANON_KEY = "YOUR_SUPABASE_PUBLISHABLE_OR_ANON_KEY"
```

Use the public/publishable/anon key only; **never** put a service-role key in Streamlit or GitHub. Do not commit credentials to GitHub. For Supabase projects that use newer publishable key formats, confirm their compatibility with the Auth REST endpoint; the legacy anon JWT is the most straightforward for this prototype.
5. Enable email authentication in Supabase Auth; configure email confirmation and production-safe rate limits. Test with **two distinct test accounts** to verify neither can view the other's puzzles or cases.

## Security and scope
This is an **experimental prototype**, not a production customer portal. Authentication is stored in Streamlit session state; it does not implement robust refresh-token management, email-verification workflows, account recovery, audit logging, consent records, abuse prevention, encryption policy, or an administrative case-review backend. Do **not** onboard real customers or enter personal/confidential data yet. Do not enter seed phrases, private keys, wallet passwords, wallet files, or recovery credentials. RLS must remain enabled. Case authorization is self-declared, not independently verified.

Only investigate public Bitcoin data and puzzles whose organizers explicitly authorize participation. Inactive Bitcoin addresses are not evidence of abandonment and are not a source of permission to access funds.
