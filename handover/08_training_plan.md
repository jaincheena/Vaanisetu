# VaaniSetu — Training Plan

---

## Session 1 — Staff Training (2 Hours)

**Audience:** Training officers, field coordinators, content reviewers  
**Format:** Hands-on workshop with the live system  
**Ideal Group Size:** 4–8 participants

### Agenda

| Time | Activity | Notes |
|------|----------|-------|
| 0:00–0:15 | Welcome & why VaaniSetu | Show impact numbers; compare to manual translation cost |
| 0:15–0:30 | Tour of the interface | Sidebar navigation, top banner (RAM, disk, model status) |
| 0:30–0:55 | Live demo: submit a job | Use a real 5-min training video; watch all 7 stages |
| 0:55–1:15 | Understanding confidence badges | Explain green/amber/red with examples |
| 1:15–1:40 | Review Queue walkthrough | Approve, edit, reject — each participant reviews one segment |
| 1:40–1:50 | Reverse Bridge mode | Demo: upload a short farmer recording |
| 1:50–2:00 | Q&A + Quick Reference Card | Hand out printed Quick Reference Card |

### Competency Checklist — Staff

After training, each participant should be able to:
- [ ] Open VaaniSetu from any office device
- [ ] Submit a translation job with correct source and target languages
- [ ] Interpret confidence badges and take appropriate action
- [ ] Review and approve/edit amber segments in the Review Queue
- [ ] Download the output ZIP and identify file formats
- [ ] Use Reverse Bridge mode for farmer recordings
- [ ] Know who to contact if the system is slow or unresponsive

---

## Session 2 — IT Admin Training (1 Hour)

**Audience:** IT staff who will maintain the server  
**Format:** Hands-on with the server PC

### Agenda

| Time | Activity |
|------|----------|
| 0:00–0:10 | System overview — what's installed where |
| 0:10–0:20 | Starting and stopping the server (`.bat` scripts) |
| 0:20–0:35 | Running the weekly backup |
| 0:35–0:45 | Disk management — cleanup of uploads/workspace |
| 0:45–0:55 | Troubleshooting table walkthrough |
| 0:55–1:00 | Emergency procedures (power cut, crash) |

### Competency Checklist — IT Admin

After training, the admin should be able to:
- [ ] Start and stop the VaaniSetu server
- [ ] Explain the directory structure under `C:\VaaniSetu\`
- [ ] Run backup to external drive
- [ ] Identify and clear disk space when needed
- [ ] Restart a failed job
- [ ] Set up Windows Firewall rule for port 8765
- [ ] Add a new user (tell them the LAN URL and provide the shared login string)
- [ ] Identify when to call for developer support

---

## 90-Day Adoption Plan

| Week | Milestone | Owner |
|------|-----------|-------|
| Week 1 | Hardware check + setup + model download | IT Admin |
| Week 2 | Staff training session with 2 pilot jobs | Training Officer |
| Week 3–4 | Submit 5–10 real jobs; review all amber segments | Training Officers |
| Week 5–6 | Review Queue established as daily routine | Content Reviewer |
| Week 7–8 | Check Glossary — validate recurring terms | Senior Staff |
| Week 9–10 | First Impact Ledger export — share with management | Programme Manager |
| Week 11–12 | Identify any gaps; adjust language list if needed | IT Admin + Staff |
| Month 3 | Full adoption — VaaniSetu part of standard workflow | All |

---

1. **Never skip the Review Queue** — amber segments must be reviewed before distribution
2. **Check disk periodically** — automatic workspace cleanup is active, but outputs accumulate over time
3. **The system gets smarter** — Translation Memory improves the more it is used and corrected
4. **Queue management is RAM-aware** — submitting multiple files schedules them safely across worker pools
5. **No internet needed** — reassure staff that the system works entirely offline
