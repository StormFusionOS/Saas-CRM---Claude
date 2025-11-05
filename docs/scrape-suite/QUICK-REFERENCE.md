# Scrape Suite - Quick Reference Card

**One-page cheat sheet for power users**

---

## Common Actions

### Keywords
```
Add Keyword       → Keywords → Add Keyword → Fill form → Save
Edit Keyword      → Keywords → Click keyword → Edit → Save
Deactivate        → Keywords → Toggle switch → Confirm
Export Keywords   → Keywords → Export → Download CSV
```

### Competitors
```
Add Competitor    → Competitors → Add Competitor → Fill form → Save
View Changes      → Competitors → Filter: "Changed Only"
Crawl Now         → Jobs & Logs → Run Competitor Crawl → Select → Run
Delete Competitor → Competitors → Click ⋮ → Delete → Confirm
```

### SERP Tracking
```
View Rankings     → SERP Explorer → Select keyword → View snapshot
Export SERP       → SERP Explorer → Export → Download CSV
Compare Snapshots → SERP Explorer → Select dates → Compare
Manual Capture    → Jobs & Logs → Run SERP Snapshot → Wait
```

### Backlinks
```
View Backlinks    → Backlinks & Citations → Backlinks tab
Filter DoFollow   → Backlinks → Toggle "DoFollow only"
Export Links      → Backlinks → Export Backlinks → CSV
Check Domain      → Referring Domains tab → Search domain
```

### Audits
```
View Issues       → Page Audits → Select audit → Expand
Filter Critical   → Page Audits → Severity: Critical
Mark Fixed        → Page Audits → Checkbox → Mark as Fixed
Run New Audit     → Jobs & Logs → Run Site Audit → URL
```

---

## Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Search/Filter | `/` |
| New Item | `Ctrl/Cmd + N` |
| Save | `Ctrl/Cmd + S` |
| Export | `Ctrl/Cmd + E` |
| Refresh Data | `Ctrl/Cmd + R` |
| Close Modal | `Esc` |

---

## Status Indicators

### Keyword Status
- 🟢 **Green**: Ranking improved
- 🔴 **Red**: Ranking dropped
- ⚪ **Gray**: No change
- ⚫ **Black**: Not ranking (100+)

### Competitor Status
- 🟢 **Active**: Being monitored
- 🔴 **Inactive**: Monitoring paused
- 🟡 **Changed**: Updates detected
- ⚪ **No Changes**: Static this week

### Backlink Status
- 🟢 **Active**: Link still present
- 🔴 **Lost**: Link removed
- 🔵 **DoFollow**: Passes SEO value
- ⚪ **NoFollow**: No SEO value

### Job Status
- 🔵 **Queued**: Waiting to run
- 🟡 **Running**: In progress
- 🟢 **Completed**: Finished successfully
- 🔴 **Failed**: Error occurred

---

## Priority Levels

### Competitors
- **Critical**: Top 3 direct competitors
- **High**: Direct competitors
- **Medium**: Indirect competitors
- **Low**: Market monitoring

### Audit Issues
- **Critical**: Breaks site functionality
- **Error**: Significant SEO impact
- **Warning**: Minor SEO impact
- **Info**: Best practice suggestions

---

## Automated Schedules

| Task | Frequency | Time (UTC) |
|------|-----------|-----------|
| SERP Snapshots | Daily | 03:00 |
| Competitor Crawls | Weekly | Sun 02:00 |
| Site Audits | Monthly | 1st, 01:00 |
| Backlink Refresh | Configurable | 7 days default |
| Citation Check | Configurable | 30 days default |

---

## Data Limits

| Item | Limit | Notes |
|------|-------|-------|
| Keywords | 500 | Per account |
| Competitors | 50 | Per account |
| Pages per Crawl | 1000 | Configurable (1-1000) |
| SERP History | 365 days | Auto-archived after |
| Backlinks | Unlimited | External API limits apply |
| Job History | 90 days | Older logs archived |

---

## Export Formats

All exports are CSV format with headers:

**Keywords Export**
```
id, keyword_text, target_domain, current_rank, previous_rank, 
best_rank, impressions, clicks, ctr, last_checked_at
```

**SERP Results Export**
```
rank, domain, url, title, is_ours
```

**Backlinks Export**
```
source_domain, source_url, target_url, anchor_text, 
is_dofollow, is_inbody, first_seen, last_seen
```

**Citations Export**
```
platform, listing_url, is_listed, name_found, address_found,
phone_found, nap_match, last_checked
```

---

## API Rate Limits

| Endpoint | Limit | Window |
|----------|-------|--------|
| SERP Snapshots | 60 | Per hour |
| Competitor Crawls | 10 | Per hour |
| Backlink Checks | 20 | Per hour |
| API Calls | 1000 | Per hour |

**Tip:** Enable "Proxy Pool" in Settings to increase limits.

---

## Common Filters

### Keywords Page
- Active/Inactive
- Search Intent (informational, commercial, transactional)
- Ranking position (top 10, top 20, not ranking)

### Competitors Page
- Active/Inactive
- Category
- Priority level
- Changed in last 7 days

### Backlinks Page
- Domain
- DoFollow/NoFollow
- Active/Lost

### Audits Page
- Severity (critical, error, warning, info)
- Fixed/Unfixed
- Date range

---

## Troubleshooting Quick Fixes

| Problem | Solution |
|---------|----------|
| Rankings not updating | Jobs & Logs → Run SERP Snapshot |
| Competitor not crawling | Check Jobs & Logs for errors |
| Backlinks not loading | Trigger manual refresh |
| Export not downloading | Check pop-up blocker |
| Changes not saving | Check network connection |
| Page loading slowly | Clear browser cache |

---

## Settings Quick Config

**Minimal Setup** (Low volume)
```
Daily SERP: ✓ Enabled
Weekly Crawl: ✓ Enabled
Monthly Audit: ✗ Disabled
Backlinks: 30 days
Citations: 90 days
Max Pages: 50
Proxy Pool: ✗ Disabled
```

**Recommended Setup** (Medium volume)
```
Daily SERP: ✓ Enabled
Weekly Crawl: ✓ Enabled
Monthly Audit: ✓ Enabled
Backlinks: 14 days
Citations: 30 days
Max Pages: 100
Proxy Pool: ✗ Disabled
```

**Aggressive Setup** (High volume)
```
Daily SERP: ✓ Enabled
Weekly Crawl: ✓ Enabled (consider daily)
Monthly Audit: ✓ Enabled (consider weekly)
Backlinks: 7 days
Citations: 14 days
Max Pages: 500
Proxy Pool: ✓ Enabled
```

---

## Support Quick Links

- 📧 Email: support@yourcompany.com
- 💬 Live Chat: Click bottom-right icon
- 📚 Full Docs: [docs/scrape-suite](./README.md)
- 🎥 Videos: youtube.com/yourcompany
- 🐛 Report Bug: Profile → Report Issue

---

**Print this page for quick reference at your desk!**

Last Updated: January 2025
