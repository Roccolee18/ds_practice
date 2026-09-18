# 9-day plan — Capital One OA, due Sept 27

**Format:** 90 minutes, "complete as many tasks as possible."
**Time available:** 2–4 hrs/day.
**Standing:** pandas = close, debugging syntax not concepts · SQL = recall gap · ML = attempted, scored poorly.

---

## The single most important thing on this page

> **"As many tasks as possible" means you are not expected to finish.**
> Scoring is per task. A task you half-solve scores more than a task you never open.
> **Triage is a graded skill, and it's the cheapest thing on this list to improve.**

### Triage protocol — rehearse this until it's reflex

1. **Minute 0–4: read every task before writing anything.** Rank them easy / medium / hard.
   Four minutes spent reading is not lost time; it's the highest-return four minutes of the test.
2. **Do them in your order, not theirs.** Task order is not difficulty order.
3. **Hard time-box.** 12 minutes on a task with nothing working → leave a comment saying what you'd
   do and move on. Come back only if time remains.
4. **Never leave a task blank.** Partial credit is real. A groupby that returns the right shape with
   one wrong column beats an empty cell.
5. **Reserve the last 8 minutes** to revisit skipped tasks and sanity-check outputs you rushed.

Practise this on Day 8. Untrained, everyone sinks 25 minutes into the hardest task and leaves two
easy ones untouched.

---

## Where the hours go

Effort is ranked by **points per hour**, not by how weak you feel:

| priority | area | why |
|---|---|---|
| 1 | **ML section knowledge** | You can already write sklearn. What you're missing is a *checklist*, not fluency. 3 hours converts "poor" to "solid" — the best return available. |
| 2 | **Triage rehearsal** | Free. Just a rule that needs one rehearsal under the clock. |
| 3 | **SQL patterns** | Real work, but 6 patterns cover most of what appears. |
| 4 | **pandas** | You're close. Protect these points; don't over-invest. |
| — | **MCQ review** | Cheap, high-density, and possible free points. Fits in dead time — do it in 15-min chunks, not in a study block. |

**Do not spend nine days on SQL.** It's your weakest area, which makes it the most tempting and the
worst trade. A section you'd score near zero on sinks you harder than a merely weak one.

---

## Day by day

### Day 1–2 (Fri 18 – Sat 19) — ML section · ~3 hrs/day

Highest return on the board. Your M1–M3 failures are knowledge gaps, not coding gaps.

- Read `SOLUTIONS.md` sections M1–M3 slowly. Then **rebuild M1 from scratch in a blank notebook**,
  no copying. Get a passing `check("M1", m1)`.  
- Do the same for M2 and M3.
- Internalize the checklist below until you can recite it.
- **Write M4 in your own words.** Six answers, 3–5 sentences each, graded against the rubric.
  Capital One is a regulated lender and weights this reasoning heavily. It is also the cheapest
  section to improve, because it's the only one where preparation is literally just having thought
  about it once before.

**Daily, in dead time:** 10–15 minutes on the MCQ bank (interactive quiz, or `MCQ_BANK.md`).
This does not come out of your study block — do it on your phone while waiting for something.
Use **Missed** mode after the first pass so you only re-see what you got wrong.

### Day 3–5 (Sun 20 – Tue 22) — SQL · ~3 hrs/day

- **Day 3:** drills D01–D08 (`sql_drills.ipynb`). Read → break → close → rewrite loop.
- **Day 4:** rewrite D01–D08 cold from memory first (20 min), then drills D09–D14.
- **Day 5:** rewrite D09–D14 cold, then D15–D18. D18 is gaps-and-islands — the capstone.
- Each day, start by rewriting the *previous* day's drills cold. That spacing is what makes them stick.

### Day 6 (Wed 23) — pandas · ~2 hrs

- Redo Section 1 (P1–P4) cold, timed at 20 minutes. You've debugged these; now do them fluently.
- Then re-sit **Section 2 (S1–S5)** cold. This is the real test of whether the drills transferred.

### Day 7 (Thu 24) — patch the gaps · ~3 hrs

- Whatever failed on Day 6, in the loop.
- Re-read your `NOTES.md` and `PROGRESS.md` "patterns I want automatic" checklist.
- **Full MCQ pass, all 40, in one sitting.** Then read every explanation you got wrong, and re-run
  **Hard only** (6 questions) plus **Missed**. If the assessment has any multiple-choice items, this is
  where those points live and they're the cheapest on the board.

### Day 8 (Fri 25) — dress rehearsal · ~2 hrs

```bash
./sets/capital-one-ds/bootstrap.sh 99   # fresh numbers
./new-attempt.sh capital-one-ds
```

Full 90 minutes, strict triage protocol, no peeking, no pausing. Treat it as the real thing.
Then score it and read only what you got wrong.

### Day 9 (Sat 26) — take the real assessment

Morning: 30 minutes skimming your pattern list. Nothing new.
**Take it Saturday, not Sunday.** Never leave a timed online assessment to the deadline day —
technical problems on the 27th with no buffer would be an avoidable way to lose this.

---

## The ML checklist — the thing that fixes your M1–M3 score

Run this top to bottom on any modelling task. It is most of the marks.

**Before modelling**
- [ ] For every column ask: *could I have known this value on the decision date?* If no → drop it.
      Leakage is the single highest-signal thing you catch.
- [ ] Profile numerics for sentinel values: `-1`, `999`, `-9999`, `1900-01-01`. `df.describe()` plus
      `value_counts()` on suspicious columns. Imputers sail straight past these.
- [ ] Check the class balance. It decides your metric.

**Splitting**
- [ ] Is there a date column? Then **split by time**, never randomly. Train on the past, test on the
      future, because that's what production does.
- [ ] All preprocessing inside a `Pipeline`, so scalers and imputers never see the test set.

**Metrics**
- [ ] Imbalanced? Report **PR-AUC alongside ROC-AUC**. Baseline PR-AUC is the base rate.
- [ ] Never report accuracy on an imbalanced problem.
- [ ] **An implausibly high score is a bug report, not a result.** AUC > 0.95 on a credit problem
      means leakage until proven otherwise.

**Decisions**
- [ ] Convert the score into a decision using the stated costs. Break-even probability is
      `gain / (gain + loss)`.
- [ ] Never assume a 0.5 threshold. `class_weight="balanced"` distorts probabilities; calibrate or
      drop the weighting if the cutoff must mean something.
- [ ] State the business case in one sentence: *"approving everyone loses \$X/application; the model
      at a Y% approval rate makes \$Z."*

**Always say out loud**
- [ ] What you'd do with more time.
- [ ] That the threshold was tuned on the test set and is therefore optimistic.
- [ ] Any fairness exposure — protected characteristics (age), proxies (ZIP), and that dropping them
      isn't sufficient without disparate-impact testing.

---

## If you only get through half of this

In priority order: **ML checklist → triage protocol → MCQ bank → drills D13–D18 → everything else.**

The first three are a few hours combined and they're worth more than every remaining hour of SQL.

---

## The MCQ bank

40 scenario questions, weighted the way CodeSignal's published Data Science Framework weights it:
roughly 6 ML-fundamentals items to every 2 probability/statistics items.

| mode | what it's for |
|---|---|
| **All** | First pass. Do it once cold to find your gaps. |
| **ML fundamentals** (26) | Bias-variance, regularization, leakage, imbalance, metrics, ensembles, calibration, monitoring, fair lending. |
| **Probability & stats** (14) | Bayes, binomial, selection bias, p-values, CIs, Simpson's paradox, A/B testing. |
| **Hard only** (6) | Reject inference, calibration, SMOTE and calibration, ZIP as a proxy, model choice under ECOA, outcome lag. |
| **Missed** | Everything you've got wrong, remembered across sessions. This is the mode you live in after day 1. |

Read the explanations even when you're right — several of them carry the exact sentence you'd want to
say out loud in the open-ended section (break-even threshold, reject inference, the outcome-lag
monitoring problem).

`MCQ_BANK.md` in the set folder is the same content as a reference sheet, with answers inline.
