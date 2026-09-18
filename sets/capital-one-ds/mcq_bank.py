"""
Multiple-choice bank: probability/statistics and ML fundamentals.

Weighted the way CodeSignal's published Data Science Framework weights it -- roughly
6 ML-fundamentals items to every 2 probability/statistics items -- and written as
scenario questions in a lending / fraud / marketing context.

`answer` is the 0-based index of the correct option.
"""

QUESTIONS = [

# ======================================================================
# PROBABILITY & STATISTICS
# ======================================================================
{
"id": "Q01", "topic": "Probability", "subtopic": "Bayes' theorem", "difficulty": "medium",
"q": """A fraud model flags 1% of all transactions for review. 0.2% of transactions are genuinely
fraudulent, and the model catches 90% of those.

A transaction has just been flagged. What is the probability it is actually fraudulent?""",
"options": ["90%", "18%", "2%", "About 50% — flagged and not-flagged are roughly equally likely"],
"answer": 1,
"why": """P(fraud) = 0.002 and P(flag | fraud) = 0.90, so true positives are 0.002 x 0.90 = 0.0018 of
all transactions. The model flags 0.01 of all transactions. So P(fraud | flag) = 0.0018 / 0.01 = **18%**.

This is the base-rate fallacy, and it is the single most-tested probability idea in DS screens. A model
with 90% sensitivity still produces mostly false positives when the condition is rare, because the
enormous negative class contributes far more false positives than the tiny positive class contributes
true ones. It is also why fraud and default teams care about precision at a given alert volume, not
sensitivity alone."""},

{
"id": "Q02", "topic": "Probability", "subtopic": "Binomial distribution", "difficulty": "medium",
"q": """A portfolio contains 20 accounts. Each defaults independently with probability 0.05.

What is the probability that **exactly 2** of them default?""",
"options": ["5.0%", "18.9%", "25.0%", "9.5%"],
"answer": 1,
"why": """Binomial: C(20,2) x 0.05^2 x 0.95^18 = 190 x 0.0025 x 0.3972 = **0.189**.

Watch for the trap of answering 0.05 x 2 = 10% or similar. Also note the independence assumption —
in a real credit portfolio defaults are correlated through the macro cycle, which is exactly why
stress testing exists. Saying that out loud is worth marks in an interview."""},

{
"id": "Q03", "topic": "Statistics", "subtopic": "Selection bias", "difficulty": "hard",
"q": """You build a default-risk model using historical data on **approved** applicants only, since
those are the only ones with a known repayment outcome. It performs well in backtesting.

What is the most serious problem with using it to score new applications?""",
"options": [
 "Nothing — approved applicants are the only ones with labels, so this is the correct training set",
 "The training population was already filtered by the existing approval policy, so the model never sees the riskiest part of the applicant distribution it will be asked to score",
 "The sample is too small to be representative",
 "Approved applicants will have more missing data than rejected ones"],
"answer": 1,
"why": """This is **selection bias**, and in lending it has its own name: the **reject inference**
problem. Your training data is a censored sample — the incumbent policy already removed the applicants
it judged riskiest, so the model learns the relationship between features and default only within the
approved region. Applied to the full applicant pool it extrapolates into a region it has no evidence
about.

Standard mitigations: reject inference techniques (parcelling, augmentation), or deliberately approving
a small random holdout below policy cutoff to generate unbiased labels. Naming reject inference in a
Capital One interview is a strong signal."""},

{
"id": "Q04", "topic": "Statistics", "subtopic": "Confidence intervals", "difficulty": "medium",
"q": """A 95% confidence interval for mean customer income is [\\$48,000, \\$52,000].

Which statement is correct?""",
"options": [
 "There is a 95% probability the true mean income lies between \\$48,000 and \\$52,000",
 "95% of customers have incomes between \\$48,000 and \\$52,000",
 "If we repeated this sampling procedure many times, about 95% of the intervals constructed this way would contain the true mean",
 "We are 95% confident the sample mean lies in this interval"],
"answer": 2,
"why": """The confidence level is a property of the **procedure**, not of this one interval. Under the
frequentist framing the true mean is a fixed constant — it is either in this interval or it is not, so
assigning it a 95% probability is a category error.

Option B confuses a confidence interval with a prediction interval (which describes individual values
and would be far wider). Option D is trivially wrong: the sample mean is the centre of the interval by
construction."""},

{
"id": "Q05", "topic": "Statistics", "subtopic": "p-values", "difficulty": "medium",
"q": """An A/B test on a new application flow returns p = 0.03.

What does this mean?""",
"options": [
 "There is a 3% probability the null hypothesis is true",
 "There is a 97% probability the new flow is better",
 "If the null hypothesis were true, there would be a 3% probability of observing a result at least as extreme as this one",
 "The new flow improves conversion by 3%"],
"answer": 2,
"why": """A p-value is **P(data at least this extreme | null is true)** — not P(null | data), which is
what options A and B claim. Inverting that conditional is the most common statistical error in industry.

Also worth saying unprompted: statistical significance is not practical significance. With a large
enough sample, a 0.01% lift is significant and worthless. Always ask for the effect size and its
confidence interval alongside the p-value."""},

{
"id": "Q06", "topic": "Statistics", "subtopic": "Simpson's paradox", "difficulty": "hard",
"q": """Segment A has a higher approval rate than Segment B for **every individual card product**. But
looking at the portfolio overall, Segment A's approval rate is **lower** than Segment B's.

What is the most likely explanation?""",
"options": [
 "There is an error in the aggregation",
 "Segment A applies disproportionately for products that have low approval rates overall",
 "The products have different sample sizes, which invalidates the comparison",
 "This is statistically impossible"],
"answer": 1,
"why": """**Simpson's paradox.** The aggregate is a weighted average, and the two segments have
different weights across products. If Segment A concentrates in a hard-to-approve product, its overall
rate can fall below Segment B's despite winning within every product.

The practical lesson: always ask what the confounding variable is before trusting an aggregate
comparison. In fair-lending analysis this matters enormously — an apparent disparity in overall
approval rates can be driven entirely by product mix, and a real disparity can be masked by it."""},

{
"id": "Q07", "topic": "Statistics", "subtopic": "Central limit theorem", "difficulty": "easy",
"q": """Customer income in your portfolio is strongly right-skewed.

What does the Central Limit Theorem let you conclude?""",
"options": [
 "With enough data, the income distribution itself becomes approximately normal",
 "The sampling distribution of the sample mean becomes approximately normal as sample size grows, even though income itself stays skewed",
 "You should log-transform income before any analysis",
 "The median is a better estimator than the mean for skewed data"],
"answer": 1,
"why": """The CLT is about the **sampling distribution of a statistic**, not about the raw data. Income
stays skewed no matter how much of it you collect; it is the distribution of *sample means* that
approaches normality (given finite variance and adequate n).

That is what licenses the usual t-tests and confidence intervals on the mean even for non-normal data.
Option D is reasonable advice in its own right, but it is not what the CLT says."""},

{
"id": "Q08", "topic": "Statistics", "subtopic": "Descriptive statistics", "difficulty": "easy",
"q": """You are reporting a typical customer's annual income. The distribution is right-skewed with a
few very high earners.

Which is the more appropriate summary, and why?""",
"options": [
 "The mean, because it uses all the data",
 "The median, because it is not pulled upward by the extreme high incomes",
 "The mode, because it is the most common value",
 "The mean, because the CLT makes it unbiased"],
"answer": 1,
"why": """The mean is dragged toward the tail by a small number of very high earners, so it overstates
what a typical customer earns. The median is robust to that.

Report both when you can — the **gap between mean and median is itself a measure of skew**, and
volunteering that reads as fluency. The mean is not wrong, it just answers a different question
("what is the total divided by the count?", which is the right question for revenue forecasting)."""},

{
"id": "Q09", "topic": "Probability", "subtopic": "Expected value", "difficulty": "medium",
"q": """Approving a non-defaulting applicant earns \\$300. Approving one who defaults costs \\$1,200.
Declining earns \\$0.

Above what predicted default probability should you decline?""",
"options": ["0.20", "0.25", "0.50", "0.80"],
"answer": 0,
"why": """Approve while expected value is positive: (1-p)(300) - p(1200) > 0, so 300 > 1500p, giving
p < **0.20**.

The general formula is worth memorising: **break-even p = gain / (gain + loss)** = 300 / (300 + 1200)
= 0.20. Note how far this is from the default 0.5 threshold — whenever the costs are asymmetric, 0.5 is
arbitrary. And the probabilities have to be **calibrated** for this to mean anything, which is why
`class_weight="balanced"` quietly breaks it."""},

{
"id": "Q10", "topic": "Statistics", "subtopic": "Multiple comparisons", "difficulty": "medium",
"q": """You test 20 candidate features for association with default, each at the α = 0.05 level. Two
come back significant.

What should you conclude?""",
"options": [
 "Both features are genuinely associated with default",
 "Testing 20 independent nulls at α = 0.05 is expected to produce about one false positive by chance, so these findings need correction or validation",
 "You should lower α to 0.01 and rerun the same tests on the same data",
 "The sample size is too small"],
"answer": 1,
"why": """With 20 independent tests at α = 0.05, the expected number of false positives under the null
is 20 x 0.05 = 1, and the probability of at least one is 1 - 0.95^20 ≈ 64%. Finding two significant
results is barely more than chance.

Fixes: Bonferroni (conservative), Benjamini-Hochberg FDR (usually more appropriate for screening), or
— best — validate on held-out data. Option C is wrong because rerunning on the same data does not create
new evidence."""},

{
"id": "Q11", "topic": "Statistics", "subtopic": "Correlation and confounding", "difficulty": "easy",
"q": """Customers who enrol in autopay default at half the rate of those who don't. A colleague
proposes enrolling everyone in autopay to halve losses.

What is the flaw?""",
"options": [
 "Autopay has no causal effect on anything",
 "Enrolment is self-selected: customers who opt in are likely more financially organised and lower-risk to begin with, so the correlation confounds the treatment with the type of person who chooses it",
 "The sample of autopay users is too small",
 "Default rates cannot be compared across groups"],
"answer": 1,
"why": """Classic confounding by self-selection. The observed gap mixes any genuine effect of autopay
with the pre-existing difference between people who choose it and people who don't.

To isolate the causal effect you would need a randomised trial (randomly offer an incentive to enrol)
or a quasi-experimental design. Note the answer is not "autopay does nothing" — it may well help; the
point is that this evidence cannot tell you how much."""},

{
"id": "Q12", "topic": "Statistics", "subtopic": "Hypothesis testing errors", "difficulty": "medium",
"q": """Your fraud model's alert threshold is **lowered**, so more transactions get flagged.

What happens to precision and recall?""",
"options": [
 "Both increase",
 "Recall increases, precision typically decreases",
 "Precision increases, recall decreases",
 "Both decrease"],
"answer": 1,
"why": """Lowering the threshold flags more transactions, so you catch more of the true fraud
(**recall up**) while also sweeping in more legitimate transactions (**precision down**).

This trade-off is the entire content of a precision-recall curve. In practice the threshold is set by
operational capacity — how many alerts the review team can actually work per day — not by a statistical
criterion."""},

{
"id": "Q13", "topic": "Statistics", "subtopic": "Sampling", "difficulty": "easy",
"q": """You need a 5,000-customer sample for a survey, and you need reliable estimates for the Student
segment, which is only 3% of the portfolio.

Which sampling approach is most appropriate?""",
"options": [
 "Simple random sampling across the whole portfolio",
 "Stratified sampling, oversampling the Student segment, with weights applied when computing portfolio-level estimates",
 "Convenience sampling from customers who respond to email",
 "Cluster sampling by state"],
"answer": 1,
"why": """Simple random sampling would give roughly 150 Students — too few for a precise segment-level
estimate. **Stratified sampling** lets you oversample the small stratum for precision where you need it,
then reweight so portfolio-level numbers remain unbiased.

The reweighting step is the part people forget: without it, your portfolio estimates are skewed toward
the oversampled group."""},

{
"id": "Q14", "topic": "Statistics", "subtopic": "A/B testing", "difficulty": "medium",
"q": """An A/B test on a marketing offer has been running for three days. The treatment is ahead and
just crossed p < 0.05. Your colleague wants to stop the test and ship.

What is the main concern?""",
"options": [
 "Three days is always too short regardless of sample size",
 "Repeatedly checking significance and stopping as soon as it is crossed inflates the false-positive rate well above 5%",
 "p < 0.05 is not a strong enough threshold for a business decision",
 "The treatment group is probably contaminated"],
"answer": 1,
"why": """This is **peeking**, or optional stopping. If you monitor continuously and stop at the first
significant result, the actual Type I error rate is far above the nominal 5% — random walks cross any
fixed boundary eventually.

Fixes: fix the sample size in advance from a power calculation, or use a method designed for continuous
monitoring (sequential testing, always-valid p-values, Bayesian stopping rules). Also relevant here:
three days may not cover a full weekly cycle, and novelty effects distort early results."""},

# ======================================================================
# ML FUNDAMENTALS
# ======================================================================
{
"id": "Q15", "topic": "ML", "subtopic": "Bias-variance", "difficulty": "easy",
"q": """Your model achieves 0.98 AUC on training data and 0.71 AUC on held-out validation data.

What is the diagnosis, and the appropriate response?""",
"options": [
 "High bias (underfitting) — increase model complexity",
 "High variance (overfitting) — add regularization, reduce complexity, or get more training data",
 "The validation set is corrupted — re-split the data",
 "The model is well-calibrated and ready to ship"],
"answer": 1,
"why": """A large train-validation gap is the signature of **high variance**. The model has memorised
noise specific to the training set.

Remedies, roughly in order of what to try first: stronger regularization, fewer/simpler features, less
model capacity (shallower trees, fewer estimators), early stopping, and more training data. Contrast
with high bias, where train and validation scores are both poor **and close together** — there, more
data will not help at all."""},

{
"id": "Q16", "topic": "ML", "subtopic": "Regularization", "difficulty": "medium",
"q": """You have 400 candidate features and want a model that automatically discards the useless ones.

Which regularization should you reach for, and why?""",
"options": [
 "L2 (Ridge), because it shrinks coefficients toward zero",
 "L1 (Lasso), because its penalty drives some coefficients to exactly zero, performing feature selection",
 "Either — they produce equivalent results",
 "Neither; regularization does not affect feature selection"],
"answer": 1,
"why": """**L1 produces exact zeros; L2 does not.** The geometric intuition: L1's constraint region is a
diamond with corners on the axes, so the optimum frequently lands on a corner where some coefficients
are exactly 0. L2's region is a sphere with no corners — coefficients shrink toward zero but essentially
never reach it.

Elastic Net combines both, and is the usual choice when features are correlated, because L1 alone picks
one feature arbitrarily from a correlated group and zeroes the rest."""},

{
"id": "Q17", "topic": "ML", "subtopic": "Data leakage", "difficulty": "medium",
"q": """You are predicting whether a credit application will default within 12 months. Which of these
features is **leakage**?""",
"options": [
 "The applicant's FICO score at the time of application",
 "The number of credit inquiries in the 6 months before applying",
 "The total amount recovered by the collections department on the account",
 "The applicant's stated annual income"],
"answer": 2,
"why": """Collections recoveries only exist **after** an account has already defaulted. It could not
possibly be known at the moment the application is decided, so including it lets the model see the
answer.

The general test, which is the one to state in an interview: **"could this value have been known on the
decision date?"** If no, drop it. The tell-tale symptom is an implausibly high score — an AUC above ~0.95
on a credit problem where 0.75 is the industry norm is a leakage investigation, not a win."""},

{
"id": "Q18", "topic": "ML", "subtopic": "Class imbalance", "difficulty": "easy",
"q": """Your default prediction dataset is 3% positive. A model achieves 97% accuracy.

What should you conclude?""",
"options": [
 "The model is excellent and should be deployed",
 "97% accuracy is exactly what predicting 'no default' for every single applicant would achieve, so accuracy tells you nothing here",
 "The model is overfitting",
 "The dataset needs to be rebalanced before any model can be trained"],
"answer": 1,
"why": """With a 3% positive rate, the trivial all-negative classifier scores 97%. **Accuracy is
uninformative on imbalanced problems** and reporting it signals inexperience.

Use PR-AUC (whose baseline is the base rate, 0.03 here), ROC-AUC, recall at a fixed precision, or —
best — a business metric in dollars. Option D overstates things: rebalancing is one tool among several,
and it is often unnecessary at 3%, especially when calibrated probabilities matter downstream."""},

{
"id": "Q19", "topic": "ML", "subtopic": "Evaluation metrics", "difficulty": "medium",
"q": """Comparing two models on a dataset with a 2% positive rate: Model A has ROC-AUC 0.89, Model B
has ROC-AUC 0.87. Their PR-AUCs are 0.21 and 0.34 respectively.

Which model is more useful, and why the discrepancy?""",
"options": [
 "Model A — ROC-AUC is the standard metric",
 "Model B — under heavy imbalance, ROC-AUC is inflated because the false-positive rate has an enormous denominator, while PR-AUC reflects performance on the rare class you actually care about",
 "They are equivalent; the metrics just disagree randomly",
 "Neither is usable until the classes are balanced"],
"answer": 1,
"why": """ROC-AUC's x-axis is FPR = FP / (FP + TN). When negatives are 98% of the data, TN is huge, so
even a large number of false positives barely moves FPR. ROC curves therefore look flattering under
heavy imbalance.

Precision = TP / (TP + FP) has no such cushion — every false positive hurts directly. When the positive
class is what you care about and it is rare, **PR-AUC is the more honest metric**, and Model B is the
better model."""},

{
"id": "Q20", "topic": "ML", "subtopic": "Cross-validation", "difficulty": "medium",
"q": """You are building a model on transactions spanning 2022-2024, to be deployed scoring new
transactions going forward.

Which validation scheme is correct?""",
"options": [
 "5-fold cross-validation with shuffling",
 "Stratified k-fold on the target",
 "Time-based split — train on earlier periods, validate on later ones (e.g. TimeSeriesSplit)",
 "Leave-one-out cross-validation"],
"answer": 2,
"why": """Random folds let the model train on future data and test on past data, which production will
never allow. That interleaving produces an **optimistic** estimate — the model sees the recent regime
during training when it never will in deployment.

Whenever the data has a time dimension and the model predicts forward, split by time. In credit
specifically, holding out the most recent vintage entirely ("out-of-time validation") is standard
practice and a model-risk reviewer will ask for it by name."""},

{
"id": "Q21", "topic": "ML", "subtopic": "KNN", "difficulty": "easy",
"q": """In k-nearest-neighbours, you increase k from 1 to 50.

What happens to bias and variance?""",
"options": [
 "Bias decreases, variance increases",
 "Bias increases, variance decreases — the decision boundary smooths out and becomes less sensitive to individual noisy points",
 "Both increase",
 "Both decrease"],
"answer": 1,
"why": """k = 1 fits the training data perfectly (zero training error) with a jagged boundary that
chases every noisy point — low bias, high variance. Larger k averages over more neighbours, smoothing
the boundary: **higher bias, lower variance**.

This is the bias-variance trade-off made unusually visible, which is why it is a favourite exam
question. k is chosen by cross-validation. Note also that KNN requires feature scaling, since it is
distance-based."""},

{
"id": "Q22", "topic": "ML", "subtopic": "Ensembles", "difficulty": "medium",
"q": """What is the key difference between bagging (e.g. random forest) and boosting (e.g. gradient
boosting)?""",
"options": [
 "Bagging uses decision trees; boosting uses linear models",
 "Bagging trains learners independently in parallel on bootstrap samples and averages them, primarily reducing variance; boosting trains them sequentially with each correcting its predecessor's errors, primarily reducing bias",
 "Boosting is always more accurate than bagging",
 "Bagging requires feature scaling; boosting does not"],
"answer": 1,
"why": """**Bagging = parallel + averaging = variance reduction.** Each tree is grown deep (low bias,
high variance) on a bootstrap sample, and averaging cancels the independent errors.

**Boosting = sequential + error correction = bias reduction.** Each weak learner (typically a shallow
tree, high bias) focuses on what the ensemble got wrong so far.

Consequence: random forests are hard to overfit by adding trees, whereas boosting **will** overfit with
too many rounds — hence early stopping and learning-rate tuning."""},

{
"id": "Q23", "topic": "ML", "subtopic": "Feature scaling", "difficulty": "easy",
"q": """Which of these models is **not** sensitive to the scale of input features?""",
"options": [
 "K-nearest neighbours",
 "Support vector machine with an RBF kernel",
 "Gradient-boosted decision trees",
 "Logistic regression with L2 regularization"],
"answer": 2,
"why": """Tree-based models split on thresholds within a single feature at a time (`income > 50000`),
so any monotonic rescaling produces identical splits. **Trees need no scaling.**

Everything else listed does. KNN and RBF-SVM compute distances, so a feature measured in dollars would
dominate one measured in years. Regularized linear models penalise coefficient magnitude, so the
penalty would fall unevenly across differently-scaled features."""},

{
"id": "Q24", "topic": "ML", "subtopic": "Categorical encoding", "difficulty": "medium",
"q": """You have a `merchant_id` feature with 40,000 distinct values.

What is the main risk of using target encoding (replacing each merchant with the mean default rate of
its transactions)?""",
"options": [
 "It produces too many columns",
 "Leakage and overfitting — a merchant appearing a handful of times gets an encoding computed partly from its own target values, which does not generalize",
 "Target encoding cannot handle categorical data",
 "It requires the target to be continuous"],
"answer": 1,
"why": """Target encoding uses the label, so unless it is computed **inside** the cross-validation fold
(out-of-fold encoding) each row's encoding is partly derived from its own target. Rare categories are
worst: a merchant seen twice gets an encoding that is essentially just its own outcome.

Mitigations: out-of-fold encoding, smoothing toward the global mean by category frequency, and grouping
rare categories into an "other" bucket. Option A is the problem with **one-hot** encoding on high
cardinality, which is a real issue too — just not the one asked about."""},

{
"id": "ML25", "id_": "Q25",
"topic": "ML", "subtopic": "Multicollinearity", "difficulty": "medium",
"q": """Two features in your logistic regression are correlated at 0.95.

What is the primary consequence?""",
"options": [
 "The model's predictions will be badly wrong",
 "Individual coefficient estimates become unstable and hard to interpret, though overall predictive performance may be fine",
 "The model will fail to converge",
 "The correlated features must always be removed"],
"answer": 1,
"why": """Multicollinearity inflates coefficient standard errors — the fit cannot tell which of the two
correlated features deserves the credit, so their coefficients swing wildly (sometimes flipping sign)
with small changes in the data. **Predictions are typically fine; interpretation is not.**

That distinction decides whether you care. For a pure prediction task you may ignore it. For a credit
model requiring adverse-action reason codes, unstable coefficients are unacceptable — which is one
reason lenders use WOE binning and variable clustering. L2 regularization also stabilises the estimates."""},

{
"id": "Q26", "topic": "ML", "subtopic": "Logistic regression", "difficulty": "medium",
"q": """In a logistic regression predicting default, the coefficient on `num_inquiries_6m` is 0.35.

What does that mean?""",
"options": [
 "Each additional inquiry raises the probability of default by 35%",
 "Each additional inquiry raises the probability of default by 0.35",
 "Each additional inquiry raises the log-odds of default by 0.35, i.e. multiplies the odds by e^0.35 ≈ 1.42",
 "Inquiries explain 35% of the variance in default"],
"answer": 2,
"why": """Logistic regression is linear **in the log-odds**, not in probability. A coefficient β means a
one-unit increase multiplies the odds by e^β — here about a 42% increase in odds.

The effect on *probability* is not constant: it depends on where you start. Going from 1% to 1.4% and
from 40% to 48.6% are both consistent with the same coefficient. Confusing odds with probability is a
standard trap."""},

{
"id": "Q27", "topic": "ML", "subtopic": "Calibration", "difficulty": "hard",
"q": """Your model has excellent ROC-AUC (0.88), but when you bucket predictions, applicants assigned a
predicted probability of 0.10 actually default about 25% of the time.

What is the problem, and does it matter?""",
"options": [
 "Nothing is wrong — high AUC means the model is good",
 "The model ranks well but is poorly calibrated. It matters whenever the predicted probability is used as a number rather than a ranking — for example setting a cost-based cutoff or estimating expected loss",
 "The model is overfitting and must be retrained",
 "AUC was computed incorrectly"],
"answer": 1,
"why": """**AUC measures ranking only.** Apply any monotonic transformation to every prediction and AUC
is unchanged, while calibration is destroyed. A model can order applicants perfectly and still have
probabilities that mean nothing.

It matters the moment you use the number: expected loss calculations, dollar-based thresholds, risk-based
pricing, capital reserving. Fixes: Platt scaling or isotonic regression via `CalibratedClassifierCV`, and
avoid `class_weight="balanced"` when calibration matters, since it deliberately distorts the base rate."""},

{
"id": "Q28", "topic": "ML", "subtopic": "Learning curves", "difficulty": "medium",
"q": """You plot training and validation error against training set size. Both curves have plateaued,
they sit close together, and both are at a high error level.

What should you do?""",
"options": [
 "Collect more training data",
 "Increase model capacity or add better features — this is high bias, and more data will not help",
 "Add stronger regularization",
 "Use a different train/test split"],
"answer": 1,
"why": """Converged curves with a small gap and high error mean **high bias**: the model is too simple
to capture the signal, and it is already extracting everything it can from the data it has. More rows
of the same thing will not move either curve.

Do the opposite of the overfitting playbook: richer features, more capacity, less regularization. The
mirror case — a large persistent gap between the curves — is high variance, and *that* is when more
data helps."""},

{
"id": "Q29", "topic": "ML", "subtopic": "Hyperparameter search", "difficulty": "medium",
"q": """You have a limited compute budget and 8 hyperparameters to tune.

Why is random search generally preferred over grid search here?""",
"options": [
 "Random search always finds a better optimum",
 "In practice only a few hyperparameters matter much, and random search explores more distinct values of each important one for the same number of trials, whereas grid search wastes evaluations on redundant combinations",
 "Grid search cannot handle more than 3 hyperparameters",
 "Random search is less likely to overfit the validation set"],
"answer": 1,
"why": """With a grid, every trial repeats the same few values along each axis — if only 2 of your 8
hyperparameters actually matter, a 3^8 grid tests just 3 distinct values of each of those. The same
budget spent randomly tests a different value of every parameter on every trial.

Bayesian optimization (Optuna, scikit-optimize) does better still by using past trials to choose the
next. Note that under real time pressure, sensible defaults plus a small random search beats an elaborate
tuning setup almost every time."""},

{
"id": "Q30", "topic": "ML", "subtopic": "Train/validation/test", "difficulty": "easy",
"q": """Why keep a separate test set on top of a validation set?""",
"options": [
 "To have more data available for training",
 "Because the validation set is used repeatedly for model and hyperparameter selection, performance on it becomes optimistic; the test set gives an unbiased estimate because it is touched only once",
 "The test set is for checking data quality",
 "Test and validation sets are interchangeable terms"],
"answer": 1,
"why": """Every decision you make by looking at validation performance — model family, hyperparameters,
feature set, threshold — fits you a little more to that particular sample. After a few dozen such
decisions, validation score is no longer an unbiased estimate of generalization.

The test set is spent **once**, at the very end. If you look at it, tweak, and look again, it has become
a validation set and you no longer have an honest estimate."""},

{
"id": "Q31", "topic": "ML", "subtopic": "Missing data", "difficulty": "medium",
"q": """A column `months_since_last_delinquency` is missing for 60% of applicants — specifically, for
everyone who has never been delinquent.

What is the best treatment?""",
"options": [
 "Drop the column; 60% missing is too much",
 "Impute with the median",
 "The missingness is itself informative — add a binary 'never delinquent' indicator and impute the numeric column with a sentinel or the median, so the model can use both signals",
 "Drop all rows with missing values"],
"answer": 2,
"why": """This is **missing not at random**, and the pattern carries the signal: missing means "never
delinquent", which is strongly predictive of low risk. Median imputation alone discards that by making
these applicants look like average-risk ones.

Adding a missingness indicator preserves it. Option D would delete 60% of your data and, worse,
systematically remove the lowest-risk applicants — destroying the sample. Some implementations
(HistGradientBoosting, XGBoost, LightGBM) handle NaN natively and learn the split direction themselves."""},

{
"id": "Q32", "topic": "ML", "subtopic": "Resampling", "difficulty": "hard",
"q": """A colleague proposes SMOTE to fix an 8% positive class rate before fitting a model whose
probabilities will be used to set a dollar-based approval cutoff.

What is the strongest objection?""",
"options": [
 "SMOTE only works for image data",
 "Resampling changes the base rate, so the model's output probabilities no longer reflect the real-world prior — which breaks any cutoff derived from actual costs unless you recalibrate afterwards",
 "SMOTE always causes overfitting",
 "8% is too balanced for SMOTE to have any effect"],
"answer": 1,
"why": """Training on a rebalanced sample shifts the intercept, so predicted probabilities are inflated
relative to reality. If your threshold comes from `gain / (gain + loss)`, it is now meaningless.

Secondary objections worth raising: SMOTE interpolates between neighbours, which is poorly defined for
one-hot and mixed-type features, and it can synthesise points inside the majority region and amplify
noise. At 8% positive, resampling is usually unnecessary — class weights or simply leaving it alone and
choosing the right metric normally works better."""},

{
"id": "Q33", "topic": "ML", "subtopic": "Dimensionality", "difficulty": "medium",
"q": """What does PCA do, and what is the main caveat when using it before a supervised model?""",
"options": [
 "It selects the features most correlated with the target; the caveat is that it can overfit",
 "It finds orthogonal linear combinations of features that maximise retained variance; the caveat is that it ignores the target entirely, so a low-variance direction that happens to be highly predictive can be discarded",
 "It removes correlated features; the caveat is that it requires categorical inputs",
 "It clusters similar observations; the caveat is that k must be chosen in advance"],
"answer": 1,
"why": """PCA is **unsupervised** — it never looks at y. High variance and high predictive value are not
the same thing, so PCA can throw away exactly the direction you needed.

Second major caveat in a regulated context: principal components are linear combinations of all the
original features, so they are not interpretable and cannot support adverse-action reason codes. That
alone rules PCA out of most credit underwriting models. It also requires scaling first, since it is
variance-based."""},

{
"id": "Q34", "topic": "ML", "subtopic": "Neural networks", "difficulty": "medium",
"q": """Why did ReLU largely replace sigmoid as the hidden-layer activation in deep networks?""",
"options": [
 "ReLU is bounded, which stabilises training",
 "Sigmoid saturates at both extremes, where its gradient approaches zero — in a deep network these small gradients multiply through backpropagation and the vanishing-gradient problem stalls learning in early layers. ReLU has a constant gradient of 1 for positive inputs",
 "ReLU produces probabilistic outputs",
 "Sigmoid cannot represent non-linear functions"],
"answer": 1,
"why": """The sigmoid's derivative peaks at 0.25 and approaches 0 in the tails. Backpropagation
multiplies these derivatives layer by layer, so gradients shrink exponentially with depth and early
layers barely update.

ReLU's gradient is exactly 1 wherever the unit is active, so the signal propagates. Its own failure mode
is "dying ReLU" — a unit stuck at negative input has zero gradient forever — which Leaky ReLU and ELU
address. Sigmoid remains correct in the **output** layer for binary classification."""},

{
"id": "Q35", "topic": "ML", "subtopic": "Regularization in NNs", "difficulty": "easy",
"q": """What does dropout do during training, and what happens at inference time?""",
"options": [
 "It removes unimportant features permanently; at inference the reduced network is used",
 "It randomly zeroes a fraction of activations each training step, preventing units from co-adapting; at inference all units are active with activations scaled to match the expected training-time magnitude",
 "It drops the worst-performing training examples",
 "It reduces the learning rate over time"],
"answer": 1,
"why": """Dropout stops units from relying on the presence of specific other units, which forces
redundant, more robust representations. It is loosely an ensemble over exponentially many sub-networks.

The inference behaviour matters and is often asked: **dropout is off at test time**, with scaling
applied so expected activation magnitudes match (frameworks use "inverted dropout", scaling up during
training instead). Forgetting to switch to eval mode is a real and common bug."""},

{
"id": "Q36", "topic": "ML", "subtopic": "Gradient descent", "difficulty": "easy",
"q": """Your training loss oscillates wildly and sometimes increases from epoch to epoch.

What is the most likely cause?""",
"options": [
 "The learning rate is too high, so updates overshoot the minimum",
 "The learning rate is too low",
 "The model has too few parameters",
 "The training set is too large"],
"answer": 0,
"why": """Too large a step size overshoots, bouncing across the loss surface instead of descending it —
sometimes diverging outright. A learning rate that is too **low** produces the opposite signature: smooth
but painfully slow convergence, often plateauing early.

Standard responses: lower the learning rate, add a schedule (cosine, step decay), use warmup, or apply
gradient clipping. Unscaled input features are a frequent underlying cause, since they make the loss
surface badly conditioned."""},

{
"id": "Q37", "topic": "ML", "subtopic": "Interpretability", "difficulty": "hard",
"q": """A gradient-boosting model ranks `zip3` as its second most important feature for default
prediction.

What is the correct response in a lending context?""",
"options": [
 "Keep it — feature importance shows it is predictive, and predictive accuracy is the goal",
 "Geography is a well-documented proxy for race and national origin. High importance on ZIP is a fair-lending red flag: it should be escalated to compliance, tested for disparate impact, and a less discriminatory alternative sought",
 "Replace zip3 with full ZIP code for more granularity",
 "Feature importance is unreliable, so nothing should be concluded"],
"answer": 1,
"why": """A model that learns "this ZIP defaults more" is implementing redlining regardless of intent,
and ECOA/Reg B liability does not depend on intent. High importance on a geographic proxy is a
compliance escalation, not a modelling win.

The expected process: disparate impact testing (adverse impact ratio across proxied demographic groups),
a documented business justification, and a search for a **less discriminatory alternative** that achieves
comparable performance — that search is itself a regulatory expectation. Note that simply dropping ZIP is
not sufficient either, since other permitted variables can carry the same proxy signal."""},

{
"id": "Q38", "topic": "ML", "subtopic": "Model selection", "difficulty": "medium",
"q": """For a credit underwriting decision at a regulated lender, which consideration most strongly
favours logistic regression on WOE-binned features over gradient boosting?""",
"options": [
 "Logistic regression is always more accurate on tabular data",
 "Every declined applicant must receive specific principal reasons for the decision under ECOA, and a linear model on monotonic bins yields exact, stable per-applicant reason codes rather than a post-hoc approximation",
 "Gradient boosting cannot handle categorical features",
 "Logistic regression trains faster"],
"answer": 1,
"why": """The binding constraint is **adverse action notices**. A linear model on monotonic bins gives
reason codes that are exact, stable, and explainable to a regulator; SHAP on a GBM is a post-hoc
approximation with its own assumptions, and it takes far more work to defend in model risk review.

Option A is false — GBM usually edges out logistic regression on tabular accuracy, and a good answer
names that as the real cost of the choice. GBM is often fine for lower-stakes uses: line increases,
marketing prioritisation, fraud triage."""},

{
"id": "Q39", "topic": "ML", "subtopic": "Monitoring", "difficulty": "hard",
"q": """Your 12-month default model has been live for two months. What is the fundamental monitoring
challenge, and how do you handle it?""",
"options": [
 "There is no challenge — compute AUC monthly",
 "The target takes 12 months to observe, so you cannot measure actual performance yet. You monitor leading indicators instead: score and feature distribution drift (PSI), approval rates, and early performance proxies such as first-payment default and 30-DPD at 3 and 6 months",
 "Retrain the model every month regardless",
 "Wait 12 months before monitoring anything"],
"answer": 1,
"why": """The **outcome lag** is the defining problem in credit model monitoring: by the time you can
measure what you actually care about, the model has been making decisions for a year.

So you monitor what is observable now. Input drift (PSI > 0.10 investigate, > 0.25 escalate) catches
population shift and broken pipelines within days. Early delinquency proxies correlate with the eventual
outcome and arrive in months rather than a year. A champion/challenger setup running in shadow lets you
compare alternatives without waiting for full maturity."""},

{
"id": "Q40", "topic": "ML", "subtopic": "Ensembles", "difficulty": "medium",
"q": """You average the predictions of five models. When does this help most?""",
"options": [
 "When all five models are the same algorithm with the same hyperparameters",
 "When the models are individually reasonably accurate **and** make errors that are not strongly correlated with each other",
 "When one model is much better than the rest",
 "Ensembling always improves performance by a fixed amount"],
"answer": 1,
"why": """Averaging cancels errors only to the extent that they are **independent**. Five copies of the
same model make the same mistakes, and averaging them changes nothing. Diversity is the active
ingredient — different algorithms, feature subsets, or bootstrap samples.

The other condition is that the base learners be better than random; averaging in a bad model drags the
ensemble down. And when one model clearly dominates, a weighted blend or stacking beats a plain average."""},
]

# tidy up the one entry that carried a stray key
for _qq in QUESTIONS:
    if "id_" in _qq:
        _qq["id"] = _qq.pop("id_")

TOPICS = sorted({q["topic"] for q in QUESTIONS})


def summary():
    from collections import Counter
    print(f"{len(QUESTIONS)} questions")
    for t, n in Counter(q["topic"] for q in QUESTIONS).most_common():
        print(f"  {t:12s} {n:3d}")
    for d, n in Counter(q["difficulty"] for q in QUESTIONS).most_common():
        print(f"  {d:12s} {n:3d}")
    ids = [q["id"] for q in QUESTIONS]
    assert len(set(ids)) == len(ids), "duplicate ids"
    for q in QUESTIONS:
        assert 0 <= q["answer"] < len(q["options"]), f"{q['id']} bad answer index"
        assert len(q["options"]) == 4, f"{q['id']} needs 4 options"
        assert q["why"].strip(), f"{q['id']} missing explanation"
    print("all structural checks passed")


if __name__ == "__main__":
    summary()
