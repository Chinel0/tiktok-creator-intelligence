# Deployment & Testing Checklist

**Timeline:** Tuesday (today) → Friday (presentation)  
**Status:** Datasets ready, now deploy and test

---

## TODAY (Tuesday) & WEDNESDAY

### Step 1: Deploy to Streamlit Cloud ✓ NEXT
- [ ] Go to [streamlit.io](https://streamlit.io)
- [ ] Sign up / log in with GitHub
- [ ] Click "Create App"
- [ ] Connect your GitHub repo (tiktok-creator-intelligence)
- [ ] Select branch: `main`
- [ ] App file path: `app/main.py`
- [ ] Click Deploy
- **Takes:** 3-5 minutes
- **Result:** You get a public URL like `https://your-username-appname.streamlit.app`

### Step 2: Test the App Locally (Optional but Recommended)
```bash
cd tiktok-creator-intelligence
streamlit run app/main.py
```
- [ ] Test login/register flow
- [ ] Test CSV upload tab (it should work)
- [ ] Upload one test dataset (e.g., TERA_synthetic_data.csv)
- [ ] Check Dashboard loads
- [ ] Check Insights page
- [ ] Check Recommendations page
- **Takes:** 10 minutes

### Step 3: Share Dataset Files with Testers
- [ ] Email each tester their personalized CSV
  - Tera → `TERA_synthetic_data.csv`
  - Yetunde → `YETUNDE_synthetic_data.csv`
  - Denzel → `DENZEL_synthetic_data.csv`
  - Wudh → `WUDH_synthetic_data.csv`
  - Esther → `ESTHER_synthetic_data.csv`
  - Basti → `BASTI_synthetic_data.csv`
  - Judith → `JUDITH_synthetic_data.csv`
  - Paul → `PAUL_synthetic_data.csv`
- [ ] Include: `data/TESTING_README.md` (instructions)
- [ ] Include: Your app's public URL
- **Takes:** 5 minutes

### Step 4: Testing Schedule (Wednesday)
- [ ] Set a time window (e.g., 2-4 PM) when testers can access the app
- [ ] Tell testers to:
  1. Download their CSV
  2. Sign up on your app
  3. Upload CSV → Run Analysis
  4. Explore all 3 pages
  5. Send you feedback
- [ ] You stay available to help if they hit issues
- **Takes:** 2-3 hours (mostly waiting for feedback)

### Step 5: Collect Feedback (Wednesday Evening)
- [ ] Create a simple Google Form or Slack thread
- [ ] Ask questions:
  - Did the sentiment % seem accurate?
  - Were the keywords relevant?
  - Did recommendations make sense?
  - Any bugs or crashes?
  - Overall: helpful or not?
- [ ] Compile feedback for Friday presentation
- **Takes:** 30 minutes

---

## THURSDAY

### Step 6: Fix Any Critical Bugs (If Needed)
- [ ] Review tester feedback
- [ ] If there are crashes/errors:
  - Fix the bug in your code
  - Commit to GitHub
  - Streamlit Cloud auto-redeployes (2-3 minutes)
- [ ] If all good: skip this step
- **Takes:** 0-1 hour depending on bugs

### Step 7: Prepare Friday Presentation
- [ ] Record a demo (5 min):
  - Show login → upload CSV → dashboard → insights → recommendations
  - Or demo live if you prefer
- [ ] Prepare talking points:
  - What the app does
  - What feedback you got
  - What works well
  - What you'd improve next
  - How it solves the creator problem
- **Takes:** 30 minutes

---

## FRIDAY (Presentation)

### Step 8: Present
- [ ] Live demo OR recorded demo
- [ ] Show the app working with sample data
- [ ] Show real tester feedback
- [ ] Explain the NLP pipeline (VADER + TF-IDF)
- [ ] Demo the recommendations
- [ ] Mention: "For production, we'd use official TikTok API or CSV upload flow"
- **Takes:** 10-15 minutes

---

## Important Notes

### ⚠️ About the Browser Scraper
- **Don't advertise** the "Connect TikTok" live scraper as a feature
- It will show in the app, but won't work on cloud deployment
- For beta testing: use the CSV upload flow (which works perfectly)
- For presentation: demo the scraper locally on your laptop OR mention it separately

### ✅ What WILL Work on Streamlit Cloud
- Login/Register
- CSV Upload
- Full NLP Pipeline (preprocessing, sentiment, keywords)
- All 3 pages (Dashboard, Insights, Recommendations)
- Real-time analysis
- User profile & history

### ❌ What WON'T Work on Streamlit Cloud
- Live TikTok browser scraping (no X11 display, no browser)
- This is fine because you have synthetic data for testing

---

## Success Criteria

By Friday, you should be able to:
- ✅ Share a working app link with testers
- ✅ Have 8 testers use it with their personalized data
- ✅ Collect real feedback on NLP quality
- ✅ Demo it live or with a recording
- ✅ Explain how it solves the creator problem
- ✅ Answer: "Does the sentiment/keyword analysis actually help creators?"

That's the real test. Not whether the scraper works (that's secondary). But whether the NLP insights are actually useful.

---

## Files Ready to Use

```
data/
├── TERA_synthetic_data.csv              (627 comments)
├── YETUNDE_synthetic_data.csv           (309 comments)
├── DENZEL_synthetic_data.csv            (1,145 comments)
├── WUDH_synthetic_data.csv              (895 comments)
├── ESTHER_synthetic_data.csv            (1,285 comments)
├── BASTI_synthetic_data.csv             (1,574 comments)
├── JUDITH_synthetic_data.csv            (1,268 comments)
├── PAUL_synthetic_data.csv              (1,163 comments)
├── TESTING_README.md                    (instructions for testers)
└── videos_merged.csv                    (your real data, for reference)
```

All files are in `data/` and ready to go.

---

## Questions?

- **App not deploying?** Check that `app/main.py` exists and `requirements.txt` has all deps
- **Testers can't upload CSV?** Make sure they have the right columns: `Comment Text`, `Comment Language`, `Comment Like Count`, `Author Nickname`
- **NLP analysis looks wrong?** That's great feedback — document it for your presentation
- **Need to add a feature?** Wait until Monday. Focus on testing what you have.

---

**Next Action:** Deploy to Streamlit Cloud (5 min). You've got this! 🚀
