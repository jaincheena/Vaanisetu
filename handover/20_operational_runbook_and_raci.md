# VaaniSetu — Operational Runbook & RACI Governance

> **Target Audience:** BAIF Executive Leadership, Regional Directors, IT Administrators, and Training Leads  
> **Purpose:** Ensure long-term organizational ownership, zero-friction support, and structured adoption across all 12 BAIF state centers without requiring developer intervention.

---

## 1. RACI Governance & Ownership Matrix

| Operational Function | IT Systems Admin | Extension Trainer | Bilingual Reviewer | Programme Manager | Regional Director |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Server Startup & Daily Health** | **A / R** | I | I | I | I |
| **Pre-Flight Hardware Check** | **A / R** | C | I | I | I |
| **Disaster Recovery & Rollback** | **A / R** | I | I | I | I |
| **Job Submission & Localization** | I | **A / R** | C | I | I |
| **Confidence Gate Review & Clearance** | I | C | **A / R** | I | I |
| **Translation Memory Curation** | I | C | **A / R** | C | I |
| **Impact Ledger & Donor Reporting** | I | I | I | **A / R** | C |
| **Regional Rollout & Resource Allocation**| C | C | C | C | **A / R** |

*Legend: **R** = Responsible, **A** = Accountable, **C** = Consulted, **I** = Informed.*

---

## 2. 24/7 Field Support Runbook & Troubleshooting Decision Trees

### Scenario 1: Server Not Accessible on Local WiFi
```
Issue: User navigates to http://192.168.x.x:8765 but page fails to load.
  │
  ├─► Check 1: Is host PC connected to office WiFi?
  │     └─► No: Reconnect host PC to office router.
  │
  ├─► Check 2: Is the server running?
  │     └─► Run scripts\health_check.bat on the host PC.
  │     └─► If offline, double click scripts\start_vaanisetu.bat.
  │
  └─► Check 3: Is Windows Defender Firewall blocking port 8765?
        └─► Open PowerShell (Admin) and run:
            netsh advfirewall firewall add rule name="VaaniSetu" dir=in action=allow protocol=TCP localport=8765
```

---

### Scenario 2: Job Status Stuck in "Translating" or "Extracting"
```
Issue: Progress bar has not updated for > 20 minutes on a low-memory laptop.
  │
  ├─► Check 1: Did the laptop enter sleep or hibernate mode?
  │     └─► Prevent Windows sleep in Power & Battery settings during long runs.
  │
  ├─► Check 2: Check server logs:
  │     └─► Open C:\VaaniSetu\logs\vaanisetu.log and scroll to the bottom.
  │
  └─► Resolution:
        1. Run scripts\stop_vaanisetu.bat
        2. Run scripts\start_vaanisetu.bat
        3. Submit job using ⚡ Draft Mode or enable "Resource Saver Mode".
```

---

### Scenario 3: Database or Translation Memory Corruption
```
Issue: SQLite error or missing historical job entries.
  │
  └─► One-Click Remediation:
        1. Run scripts\rollback.bat
        2. Enter the path to your latest backup (e.g. E:\VaaniSetu_Backup\backup_2026-08-15_1800)
        3. Type YES to restore database and verify table schema automatically.
```

---

## 3. 30-60-90 Day Phased Organizational Adoption Roadmap

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                             BAIF 30-60-90 DAY ADOPTION ROADMAP                                   │
├───────────────────────────────┬───────────────────────────────┬──────────────────────────────────┤
│ 📅 PHASE 1: DAYS 1 - 30       │ 📅 PHASE 2: DAYS 31 - 60      │ 📅 PHASE 3: DAYS 61 - 90         │
│ Core Pilot (Maharashtra HQ)   │ Regional Expansion (4 States) │ Enterprise Scale (All 12 Centers)│
├───────────────────────────────┼───────────────────────────────┼──────────────────────────────────┤
│ • Staging at Pune Central HQ  │ • Air-gapped USB deployment   │ • Full deployment across all     │
│ • Train 15 HQ extension staff │   to Gujarat, MP, Rajasthan,    12 BAIF state centers            │
│   via in-app Training Academy │   and Karnataka regional hubs │ • 100% of video/audio training   │
│ • Localize top 25 core crop   │ • Train 60 field coordinators   localized into 22 languages      │
│   and livestock modules into  │ • Establish daily Review Queue│ • Monthly Impact Ledger exports  │
│   Marathi and Hindi           │   protocols in local dialects │   integrated into donor reports  │
│ • Build first 500 validated   │ • Scale outbound 8kHz IVR     │ • Zero recurring translation     │
│   Translation Memory terms    │   voice broadcast to farmers  │   costs permanently achieved     │
└───────────────────────────────┴───────────────────────────────┴──────────────────────────────────┘
```

---

## 4. Operational Self-Sufficiency & Knowledge Handover

1. **Zero External Dependencies:** VaaniSetu operates completely offline without internet or cloud subscriptions.
2. **Self-Healing Storage:** Intermediate workspace files are automatically purged after every run, ensuring disk space never fills up silently.
3. **Compound Learning Asset:** Every correction made by BAIF field officers permanently trains the local Translation Memory, making the system progressively more accurate for BAIF's specific dialect regions over time.
