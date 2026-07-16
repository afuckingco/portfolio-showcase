# 🔧 INJI-CHO: Maintenance & Operations Guide

**Subtitle**: Keeping Your App Running Smoothly  
**Audience**: Developers, DevOps, Project Maintainers  
**Last Updated**: July 2026

---

## 📋 OVERVIEW

Maintenance adalah kegiatan **berkelanjutan** untuk menjaga aplikasi tetap:
- ✅ Online & accessible
- ✅ Performant (cepat)
- ✅ Secure (aman dari hacker)
- ✅ Reliable (data aman)
- ✅ Updated (bugless)

---

## 🚀 PHASE 1: IMMEDIATE MAINTENANCE (Week 1-4)

### Daily Tasks (5 minutes)

**Check Application Status**
```bash
# 1. Visit your deployed URL
https://yoursite.netlify.app

# 2. Test basic functionality
- Load page
- Click map
- Check database connection
- Try pick mode
- Export a temple

# 3. Check error logs
- DevTools Console (F12)
- Netlify logs dashboard
- Supabase error logs
```

**Respond to User Issues**
```
If users report bugs:
1. Try to reproduce
2. Check error logs
3. Document in GitHub Issues
4. Plan fix
5. Deploy fix
6. Notify user
```

---

### Weekly Tasks (30 minutes)

**Monitor Performance**
```bash
# Check Netlify Analytics
Dashboard → Analytics
- Page loads
- Errors
- Traffic patterns

# Check Supabase usage
Dashboard → API Usage
- Query count
- Storage used
- Bandwidth
```

**Backup Database**
```bash
# Supabase auto-backups daily
# Manual backup:
1. Go to Supabase Dashboard
2. Settings → Backups
3. Click "Create backup"
4. Download locally
```

**Review Recent Changes**
```bash
# Check git history
git log --oneline -10

# Review recent commits
git show <commit>

# Check deployment status
Netlify Dashboard → Deploys
```

---

### Monthly Tasks (2-3 hours)

**Full System Check**
```
□ All features working (map, pick, filter, export)
□ No console errors
□ Database responsive
□ Response times < 3 seconds
□ No broken links
□ Mobile responsive
□ Dark mode working
```

**Update Dependencies**
```bash
# Check for updates
npm outdated

# Update non-breaking changes
npm update

# Commit changes
git add package-lock.json
git commit -m "chore: update dependencies"
git push

# Monitor for issues in next 24 hours
```

**Review User Feedback**
```
□ GitHub issues reported
□ Feature requests received
□ Bugs discovered
□ Performance complaints
□ Security concerns

Action: Document and prioritize
```

---

## 🔒 SECURITY MAINTENANCE

### Weekly Security Check

**Dependency Vulnerabilities**
```bash
# Check for security issues
npm audit

# If vulnerabilities found:
npm audit fix

# If auto-fix unavailable:
# Update package.json manually
# Test thoroughly
# Deploy with caution
```

**Code Review for Security**
```javascript
// Check for common issues:

// ❌ NEVER commit secrets
// .env.local MUST be in .gitignore

// ❌ NEVER use eval()
eval(userInput)  // DANGER!

// ✅ Sanitize user input
const sanitized = sanitizeInput(userInput)

// ✅ Validate on backend (Supabase RLS)
// Frontend validation not enough
```

**API Key Rotation (Every 90 days)**
```bash
# Supabase security
1. Go to Settings → API
2. Create new anon key
3. Update .env in Netlify
4. Deploy
5. Revoke old key after 24 hours
6. Document rotation date
```

---

### Monthly Security Audit

**Check for Exposures**
```bash
# Scan git history for secrets
git log -p | grep -i "password\|token\|key\|secret"

# Use automated tools
npm install --save-dev secretlint
npm run secretlint

# Check if any secrets in repo
# If found: Remove from history with git-filter-branch
```

**SSL/HTTPS Verification**
```bash
# Check certificate validity
curl -I https://yoursite.netlify.app

# Should see: HTTP/2 200 and valid certificate
# Netlify auto-renews (every 30 days)
```

---

## 📊 MONITORING & ALERTS

### Setup Uptime Monitoring (Free)

**Use UptimeRobot**
```
1. Go to uptimerobot.com
2. Create account
3. Add monitor:
   - URL: https://yoursite.netlify.app
   - Interval: 5 minutes
4. Set alerts:
   - Down/Up email notifications
5. Done! Get alerts if site goes down
```

**Setup Error Tracking (Optional)**

```javascript
// Add to index.html for error tracking
<script>
  window.addEventListener('error', (e) => {
    // Log to error tracking service
    console.error('Error:', e.message)
    // Can send to Sentry, LogRocket, etc.
  })
</script>
```

---

### Real-time Monitoring Dashboard

**Netlify Built-in Analytics**
```
Go to: Netlify Dashboard → Analytics

Monitor:
├─ Unique visitors (by day/week)
├─ Page views
├─ Top pages
├─ Error rates
├─ Response times
└─ Top referrers
```

**Supabase Monitoring**
```
Go to: Supabase Dashboard → Database

Monitor:
├─ Database size (GB)
├─ Query count/second
├─ API usage (bandwidth)
├─ Active connections
└─ Slow queries
```

---

## 🐛 BUG TRACKING & FIXING

### When Bug Reported

**Step 1: Reproduce**
```bash
1. Try to reproduce bug locally
   npm run dev
   
2. Test in multiple browsers
   - Chrome
   - Firefox
   - Safari
   
3. Test on mobile
   - iPhone
   - Android
   
4. Check different conditions
   - Online/Offline
   - Light/Dark mode
   - Various screen sizes
```

**Step 2: Document**
```markdown
# Bug Report
Title: Map doesn't load on mobile
Severity: High
Browser: Safari iOS 14
Steps:
1. Open app on iPhone
2. Wait 5 seconds
3. Map blank, no errors

Expected: Map should load
Actual: Blank screen

Reproduction: Consistent (100%)
```

**Step 3: Fix**
```bash
# Create feature branch
git checkout -b fix/map-mobile-issue

# Make code changes
# Test locally
npm run dev

# Commit with clear message
git commit -m "fix: Fix map not loading on mobile Safari"

# Push and create PR (if team)
git push origin fix/map-mobile-issue
```

**Step 4: Test & Deploy**
```bash
# Full test cycle
npm run lint      # Code quality
npm run build     # Production build
npm run preview   # Test build locally

# Deploy
git push origin fix/map-mobile-issue

# Monitor in production
# Watch error logs for 24 hours
# Check performance metrics
```

**Step 5: Close Issue**
```markdown
# Close issue with message:
"Fixed in version 0.1.1
- Deploy at: 2026-07-15
- Changes: [link to commit]
- Tested on: Chrome, Firefox, Safari, Mobile"
```

---

## 📈 PERFORMANCE OPTIMIZATION

### Monthly Performance Review

**Measure Load Time**
```bash
# Test with Lighthouse (Chrome DevTools)
1. Open site
2. F12 → Lighthouse tab
3. Click "Analyze page load"
4. Review scores:
   - Performance (target: > 90)
   - Accessibility (target: > 90)
   - Best Practices (target: > 90)
   - SEO (target: > 90)
```

**Identify Bottlenecks**
```
If slow:

□ Map tiles slow?
  → Use WebP format
  → Add caching headers

□ JavaScript slow?
  → Check bundle size (npm run build)
  → Look for large dependencies
  → Consider code splitting

□ Database slow?
  → Check Supabase slow queries log
  → Add indexes if needed
  → Optimize SQL queries

□ Images slow?
  → Compress
  → Use WebP
  → Lazy load
```

**Check Bundle Size**
```bash
# After build
ls -lh dist/assets/

# Should be:
# main.*.js < 200KB
# main.*.css < 50KB
# If larger, investigate with:
npm install --save-dev webpack-bundle-analyzer
```

---

## 🔄 UPDATING DEPENDENCIES

### Safe Update Process

**Step 1: Check Outdated**
```bash
npm outdated
```

**Step 2: Read Changelogs**
```
For each major update:
1. Check CHANGELOG.md
2. Look for breaking changes
3. Check migration guide
4. Read deprecation warnings
```

**Step 3: Update Carefully**
```bash
# Minor/Patch updates (safe)
npm update

# Major updates (risky, needs testing)
npm install leaflet@latest
npm install @supabase/supabase-js@latest

# Then test thoroughly
npm run dev
npm run build
npm run preview
```

**Step 4: Test**
```bash
# Run all tests
npm run lint
npm run build

# Manual testing
npm run preview

# Test all features:
□ Map loads
□ Pick location works
□ Filter works
□ Export/Import works
□ Dark mode works
□ Mobile responsive
```

**Step 5: Deploy & Monitor**
```bash
git add package.json package-lock.json
git commit -m "chore: update dependencies to [version]"
git push

# Watch logs for 24 hours
# Check Netlify analytics
# Monitor error rates
```

---

## 📋 VERSION MANAGEMENT

### Semantic Versioning

```
Version Format: MAJOR.MINOR.PATCH (e.g., 0.1.0)

0.1.0
├─ 0 = MAJOR (breaking changes)
├─ 1 = MINOR (new features, backward compatible)
└─ 0 = PATCH (bug fixes)

Examples:
0.1.0 → 0.1.1 = Bug fix (patch)
0.1.1 → 0.2.0 = New feature (minor)
0.2.0 → 1.0.0 = Production release (major)
```

### Release Checklist

```markdown
# Release v0.2.0 - Photo Upload Feature

## Pre-Release
- [ ] All tests passing
- [ ] Documentation updated
- [ ] Changelog written
- [ ] No console errors
- [ ] Performance acceptable

## During Release
- [ ] Create release branch: release/0.2.0
- [ ] Update version in package.json
- [ ] Update CHANGELOG.md
- [ ] Update README.md if needed
- [ ] Create git tag: v0.2.0

## Post-Release
- [ ] Deploy to production
- [ ] Monitor error rates
- [ ] Check database migrations
- [ ] Notify users
- [ ] Archive release notes
```

---

## 💾 BACKUP & DISASTER RECOVERY

### Backup Strategy

**Database Backups**
```
Frequency: Daily (automatic)
Provider: Supabase
Retention: 7 days (free), 30 days (paid)

Manual backup:
1. Supabase Dashboard → Backups
2. Click "Create backup"
3. Download JSON export
4. Store locally + cloud storage
```

**Code Backups**
```
Frequency: On every commit
Provider: GitHub
Retention: Unlimited

What's backed up:
- All source code
- Configuration files
- Documentation
- Git history
```

**Daily Backup Checklist**
```bash
# Check database health
curl https://your-supabase.supabase.co/health

# Check code repo
git log -1 --oneline

# Verify recent deployments
# Check Netlify dashboard
```

---

### Disaster Recovery Plan

**If Database Corrupted**

```bash
# Step 1: Stop accepting writes (if possible)
# Maintenance mode in Netlify (redirects to status page)

# Step 2: Restore from backup
1. Supabase Dashboard → Backups
2. Select recent backup
3. Click "Restore"
4. Confirm (takes few minutes)

# Step 3: Verify data
SELECT COUNT(*) FROM temples;

# Step 4: Notify users
"Database issue resolved. All data intact."

# Step 5: Resume service
Remove maintenance mode
```

**If Code Broken**

```bash
# Step 1: Rollback to previous version
git revert <broken-commit>

# Step 2: Deploy rolled back code
git push origin main

# Step 3: Monitor for 1 hour
Check logs and error rates

# Step 4: Fix issue in new branch
git checkout -b fix/issue

# Step 5: Re-deploy when fixed
```

**If Site Hacked**

```bash
# Step 1: Immediate actions
1. Rotate API keys
2. Check Supabase RLS policies
3. Review recent database changes
4. Check git logs for unauthorized commits

# Step 2: Forensics
1. Review Netlify logs
2. Check Supabase audit logs
3. Scan code for vulnerabilities
4. Find vulnerability entry point

# Step 3: Patch
1. Fix vulnerability
2. Rotate all secrets
3. Deploy fix
4. Monitor for re-attack

# Step 4: Post-mortem
1. Document what happened
2. Update security measures
3. Add automated checks
4. Notify users if data compromised
```

---

## 📚 DOCUMENTATION MAINTENANCE

### Update Documentation When:

```
✅ New feature added
✅ Code structure changed
✅ API changed
✅ Environment variables added
✅ Database schema changed
✅ Deployment process changed
✅ Security procedure changed
✅ Bug discovered & fixed
```

### Documentation to Update

```
For each change, update:

1. README.md (if feature-level change)
2. ARCHITECTURE.md (if structure changes)
3. DEPLOYMENT.md (if deploy process changes)
4. Code comments (always!)
5. JSDoc comments (always!)
6. CHANGELOG.md (for releases)
7. GitHub Issues (if already reported)
```

---

## 📊 MAINTENANCE SCHEDULE

### Daily (5 minutes)
```
□ App accessible
□ No critical errors
□ Database responding
```

### Weekly (30 minutes)
```
□ Performance metrics
□ User feedback review
□ Security check
□ Backup verification
```

### Monthly (2-3 hours)
```
□ Full system test
□ Dependency updates
□ Performance optimization
□ Documentation review
□ Security audit
```

### Quarterly (4-6 hours)
```
□ Architecture review
□ Scaling assessment
□ Security penetration test
□ Cost optimization
□ Roadmap planning
```

### Yearly (1-2 days)
```
□ Major version evaluation
□ Technology stack review
□ User survey
□ Redesign consideration
□ Migration planning
```

---

## 🚨 INCIDENT RESPONSE

### Severity Levels

```
CRITICAL (Fix in 1 hour)
- App completely down
- Data loss
- Security breach
- All users affected

HIGH (Fix in 4 hours)
- App partially broken
- Some features don't work
- Performance severely degraded
- Many users affected

MEDIUM (Fix in 24 hours)
- Non-critical features broken
- Some users affected
- Workaround available
- Performance slightly slow

LOW (Fix in 1 week)
- Minor bugs
- UI inconsistencies
- Rare edge cases
- Few users affected
```

### Incident Response Steps

```
1. Declare Incident
   - Set severity level
   - Notify team
   - Start incident log

2. Assess Impact
   - How many users affected?
   - What functionality broken?
   - Data integrity compromised?

3. Implement Workaround (if possible)
   - Maintenance mode
   - Feature flag to disable feature
   - Temporary routing change

4. Root Cause Analysis
   - Check logs
   - Review recent changes
   - Identify failure point

5. Fix & Test
   - Write fix
   - Test thoroughly
   - Get code review

6. Deploy
   - Deploy to production
   - Monitor closely
   - Have rollback ready

7. Post-Incident
   - Document what happened
   - Update runbooks
   - Schedule post-mortem
   - Implement prevention measures
```

---

## 💰 COST OPTIMIZATION

### Monthly Cost Review

```
Netlify:     $0 (free tier) → $19+ (paid)
Supabase:    $0 (free tier) → $25+ (paid)
Domain:      $10-15/year
Total:       $10-50/month typical

Cost optimization:
□ Using free tiers efficiently?
□ Any unused services?
□ Database queries optimized?
□ Images compressed?
□ Build times reasonable?
```

### When to Upgrade

```
Upgrade Netlify when:
- Free tier limit exceeded (bandwidth/builds)
- Need more analytics
- Need team collaboration

Upgrade Supabase when:
- Database size > 5GB
- API rate limit exceeded
- Need priority support
- Need backups > 7 days
```

---

## 📞 USER SUPPORT

### Support Channels

```
GitHub Issues (for bugs)
- Users report bugs
- Developers assign/fix
- Track resolution

GitHub Discussions (for questions)
- Users ask questions
- Community helps
- Less formal than issues

Email (for critical issues)
- Direct contact
- Private discussions
- Security reports
```

### Support Response Times

```
Critical:    1 hour
High:        4 hours
Medium:      24 hours
Low:         1 week
Feature req: 1 month (review)
```

### Common Support Requests

```
Q: "My temples disappeared!"
A: 1. Check database backup
   2. Restore from Supabase backup
   3. Apologize & prevent future

Q: "App is slow"
A: 1. Check network tab
   2. Optimize queries
   3. Clear cache
   4. Contact provider if still slow

Q: "I found a security issue"
A: 1. Thank them
   2. Verify vulnerability
   3. Fix immediately
   4. Notify users (if data exposed)
   5. Reward if serious

Q: "Can you add feature X?"
A: 1. Document in GitHub Discussions
   2. Link to PHASE2_ROADMAP
   3. Add to backlog
   4. Notify when prioritized
```

---

## 🔍 MONITORING TOOLS

### Essential Monitoring

```
Tool              Purpose              Free?
─────────────────────────────────────────
Netlify Logs      Deployment logs      ✅
Supabase Logs     Database logs        ✅
Lighthouse        Performance          ✅
UptimeRobot       Uptime monitoring    ✅
GitHub Actions    CI/CD               ✅
```

### Optional Advanced Monitoring

```
Sentry            Error tracking       🟡 Free tier
LogRocket         Session replay       🟡 Free tier
Hotjar            User analytics       🟡 Free tier
Google Analytics  Visitor stats        ✅ Free
StatusPage.io     Status dashboard     🟡 Free tier
```

---

## 📝 MAINTENANCE CHECKLIST TEMPLATE

Copy & use weekly:

```markdown
# Maintenance Checklist - [DATE]

## Daily Checks
- [ ] App accessible
- [ ] No critical errors in console
- [ ] Database responding

## Performance
- [ ] Response time < 3s
- [ ] No 404 errors
- [ ] Images loading

## Security
- [ ] HTTPS working
- [ ] No suspicious logs
- [ ] API keys rotated? (N/A unless 90 days passed)

## User Issues
- [ ] GitHub issues reviewed
- [ ] User feedback addressed
- [ ] Support emails responded

## Data
- [ ] Database backup confirmed
- [ ] Recent commits verified
- [ ] No data corruption

## Notes
[Add any observations]

## Next Week's Tasks
- [ ] Task 1
- [ ] Task 2

Signed: _________ Date: _________
```

---

## 🎓 MAINTENANCE SKILLS

### Technical Skills Needed

```
Skill                Why
─────────────────────────────────
Git/GitHub          Version control, rollback
Bash/Terminal       Deployment scripts, logs
SQL/PostgreSQL      Database troubleshooting
JavaScript          Debug code issues
CSS                 UI/responsive issues
HTTP/HTTPS          Network troubleshooting
Linux basics        Server access (if self-hosted)
```

### Soft Skills Needed

```
Skill                Why
─────────────────────────────────
Documentation       Keep runbooks updated
Communication       Report to users
Problem-solving     Debug issues
Prioritization      Which bugs first?
On-call readiness   Handle incidents
```

---

## 📖 MAINTENANCE RESOURCES

**Keep These Handy**

```
□ Netlify Dashboard → https://app.netlify.com
□ Supabase Dashboard → https://app.supabase.com
□ GitHub Repo → https://github.com/you/inji-cho
□ Uptime Monitor → https://uptimerobot.com
□ Status Page → Create one for users
□ Runbook (this guide!)
□ Incident Log (spreadsheet or wiki)
```

---

## 🔗 HANDOFF DOCUMENT

### If Handing Off Maintenance

Create handoff document:

```markdown
# Inji-cho Maintenance Handoff

## Access Credentials
- Netlify: [email / password manager link]
- Supabase: [email / password manager link]
- GitHub: [username / SSH key location]
- Domain: [registrar / admin email]

## Critical Passwords
[Use password manager, NOT plaintext]

## Emergency Contacts
- Website owner: [name/email/phone]
- Database admin: [name/email/phone]
- Security contact: [name/email/phone]

## Common Issues & Solutions
1. App won't load → [steps]
2. Database slow → [steps]
3. Users can't login → [steps]

## Schedule
- Daily: [5 min check]
- Weekly: [30 min review]
- Monthly: [2-3 hour audit]

## Escalation
If unsure: Contact [owner name] at [contact]
```

---

## ✅ MAINTENANCE SIGN-OFF

```
When everything running smoothly:

✅ App accessible 24/7
✅ No critical bugs
✅ Performance acceptable
✅ Data secured & backed up
✅ Security up to date
✅ Documentation current
✅ Users happy
✅ Owner notified

Status: HEALTHY ✅
Last checked: [DATE]
Next check: [DATE + 7 days]

Signed: _______________
```

---

**Maintenance is ongoing, not a one-time task.**

Keep monitoring, keep updating, keep securing.

🏮 **Happy maintaining!**

---

*This guide should be updated quarterly as the app evolves.*
