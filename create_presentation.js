const pptxgen = require("pptxgenjs");

const prs = new pptxgen();
prs.layout = "LAYOUT_WIDE"; // 13.33 x 7.5 inches

// ── Color palette ──────────────────────────────────────────────
const NAVY       = "1B2A4A";
const WHITE      = "FFFFFF";
const STEEL_BLUE = "2E6DB4";
const LIGHT_NAVY = "E8EDF5";
const DARK_GRAY  = "333333";
const MID_GRAY   = "666666";
const GOLD       = "C9A84C";
const F_TITLE    = "Georgia";
const F_BODY     = "Calibri";

const MEDIA = "C:/Users/hrwan/fin427/fin427report/report_latex/media/media";
const W = 13.33;
const H = 7.5;

// ── Helper: standard content slide header + footer ─────────────
function contentSlide(title) {
  const slide = prs.addSlide();
  // Navy header bar
  slide.addShape(prs.ShapeType.rect, {
    x: 0, y: 0, w: W, h: 1.05,
    fill: { color: NAVY }, line: { color: NAVY }
  });
  // Gold accent line
  slide.addShape(prs.ShapeType.rect, {
    x: 0, y: 1.05, w: W, h: 0.04,
    fill: { color: GOLD }, line: { color: GOLD }
  });
  slide.addText(title, {
    x: 0.4, y: 0, w: W - 0.8, h: 1.05,
    fontSize: 26, bold: true, color: WHITE, fontFace: F_TITLE,
    valign: "middle", align: "left"
  });
  // Footer
  slide.addText("FIN 427  |  Machine Learning Stock Selection  |  April 2026", {
    x: 0.4, y: 7.18, w: W - 0.8, h: 0.28,
    fontSize: 9, color: MID_GRAY, fontFace: F_BODY, align: "right"
  });
  return slide;
}

// ── Helper: metric stat box ────────────────────────────────────
function addMetricBox(slide, x, label, value, highlight = false) {
  slide.addShape(prs.ShapeType.rect, {
    x, y: 1.2, w: 3.0, h: 0.85,
    fill: { color: highlight ? NAVY : LIGHT_NAVY },
    line: { color: highlight ? NAVY : STEEL_BLUE, pt: 1 }
  });
  slide.addText(label, {
    x: x + 0.1, y: 1.25, w: 2.8, h: 0.28,
    fontSize: 9.5, color: highlight ? "A8C0D6" : MID_GRAY, fontFace: F_BODY
  });
  slide.addText(value, {
    x: x + 0.1, y: 1.5, w: 2.8, h: 0.47,
    fontSize: 18, bold: true, color: highlight ? WHITE : NAVY, fontFace: F_BODY
  });
}

// ── Helper: model slide (left bullets + right figure) ──────────
function modelSlide(title, metrics, bullets, figPath, figCaption) {
  const slide = contentSlide(title);
  metrics.forEach(({ label, value, highlight }, i) =>
    addMetricBox(slide, 0.4 + i * 3.2, label, value, highlight)
  );
  slide.addText("Key Findings", {
    x: 0.4, y: 2.25, w: 5.6, h: 0.38,
    fontSize: 13.5, bold: true, color: STEEL_BLUE, fontFace: F_BODY
  });
  slide.addText(bullets, {
    x: 0.4, y: 2.72, w: 5.6, h: 3.9,
    fontSize: 12, color: DARK_GRAY, fontFace: F_BODY
  });
  slide.addText(figCaption, {
    x: 6.25, y: 2.25, w: 6.7, h: 0.33,
    fontSize: 10.5, italic: true, color: MID_GRAY, fontFace: F_BODY
  });
  slide.addImage({ path: figPath, x: 6.25, y: 2.62, w: 6.7, h: 4.55 });
}

// ════════════════════════════════════════════════════════════════
// SLIDE 1 – Title
// ════════════════════════════════════════════════════════════════
{
  const slide = prs.addSlide();
  slide.addShape(prs.ShapeType.rect, {
    x: 0, y: 0, w: W, h: H, fill: { color: NAVY }, line: { color: NAVY }
  });
  // Gold left bar
  slide.addShape(prs.ShapeType.rect, {
    x: 0, y: 0, w: 0.09, h: H, fill: { color: GOLD }, line: { color: GOLD }
  });
  // Gold divider under title
  slide.addShape(prs.ShapeType.rect, {
    x: 0.55, y: 3.35, w: 5.0, h: 0.06, fill: { color: GOLD }, line: { color: GOLD }
  });
  slide.addText("Machine Learning\nStock Selection", {
    x: 0.55, y: 0.9, w: 9.0, h: 2.2,
    fontSize: 46, bold: true, color: WHITE, fontFace: F_TITLE,
    align: "left", lineSpacingMultiple: 1.15
  });
  slide.addText("Household and Personal Products Sector  |  FIN 427", {
    x: 0.55, y: 3.5, w: 10.0, h: 0.55,
    fontSize: 18, color: "A8C0D6", fontFace: F_BODY, align: "left"
  });
  slide.addText(
    "Harry Wang   \u2022   Vincent Antonio   \u2022   Kepler Huntress   \u2022   Matthew Meilinger",
    { x: 0.55, y: 4.25, w: 11.0, h: 0.42, fontSize: 13, color: "7A9AB8", fontFace: F_BODY }
  );
  slide.addText(
    "whrui@umich.edu  |  antonvin@umich.edu  |  keplerh@umich.edu  |  mattmeil@umich.edu",
    { x: 0.55, y: 4.68, w: 11.0, h: 0.33, fontSize: 10, color: "4F7090", fontFace: F_BODY }
  );
  slide.addText("April 7, 2026", {
    x: 0.55, y: 6.9, w: 4.0, h: 0.32, fontSize: 11, color: "4F7090", fontFace: F_BODY
  });
}

// ════════════════════════════════════════════════════════════════
// SLIDE 2 – Introduction
// ════════════════════════════════════════════════════════════════
{
  const slide = contentSlide("Introduction");
  // Research question banner
  slide.addShape(prs.ShapeType.rect, {
    x: 0.4, y: 1.18, w: W - 0.8, h: 1.0,
    fill: { color: LIGHT_NAVY }, line: { color: STEEL_BLUE, pt: 1 }
  });
  slide.addText(
    "Research Question: Using machine learning, which stock in the Household and Personal Products sector (GICS 3030) will deliver the highest industry-adjusted return in November 2024?",
    {
      x: 0.6, y: 1.22, w: W - 1.2, h: 0.9,
      fontSize: 13, color: NAVY, fontFace: F_BODY, bold: true,
      align: "left", valign: "middle"
    }
  );
  // Left col: Dataset
  slide.addText("Dataset", {
    x: 0.4, y: 2.38, w: 5.9, h: 0.38,
    fontSize: 14, bold: true, color: STEEL_BLUE, fontFace: F_BODY
  });
  slide.addText(
    "\u2022  1,053,738 stock-month observations (Jan 2001 \u2013 Nov 2024)\n\u2022  All GICS sectors; prediction restricted to 38 sector stocks\n\u2022  15 winsorized predictor variables\n\u2022  Target: industry-adjusted monthly return (indadjret)",
    {
      x: 0.4, y: 2.82, w: 5.9, h: 2.1,
      fontSize: 12, color: DARK_GRAY, fontFace: F_BODY
    }
  );
  // Right col: Six models
  slide.addText("Six Models Evaluated", {
    x: 6.9, y: 2.38, w: 6.0, h: 0.38,
    fontSize: 14, bold: true, color: STEEL_BLUE, fontFace: F_BODY
  });
  slide.addText(
    "1.  Ordinary Least Squares (OLS)\n2.  LASSO Penalized Regression\n3.  Vanilla Decision Tree\n4.  Random Forest\n5.  Gradient Boosting (XGBoost)\n6.  Simple Neural Network (MLP)",
    {
      x: 6.9, y: 2.82, w: 6.0, h: 2.5,
      fontSize: 12, color: DARK_GRAY, fontFace: F_BODY
    }
  );
  // Recommendation callout
  slide.addShape(prs.ShapeType.rect, {
    x: 0.4, y: 5.55, w: W - 0.8, h: 0.72,
    fill: { color: NAVY }, line: { color: NAVY }
  });
  slide.addText(
    "\u2605  Recommendation: NAII (Natural Alternatives International Inc.) \u2014 top-3 under OLS and XGBoost; top-8 under four of six models",
    {
      x: 0.6, y: 5.58, w: W - 1.2, h: 0.65,
      fontSize: 12.5, color: WHITE, fontFace: F_BODY, bold: true,
      align: "left", valign: "middle"
    }
  );
}

// ════════════════════════════════════════════════════════════════
// SLIDE 3 – Data Overview
// ════════════════════════════════════════════════════════════════
{
  const slide = contentSlide("Data Overview");
  // Left: scope + variable categories
  slide.addText("Dataset Scope", {
    x: 0.4, y: 1.22, w: 5.9, h: 0.38,
    fontSize: 14, bold: true, color: STEEL_BLUE, fontFace: F_BODY
  });
  slide.addText(
    "\u2022  Panel: January 2001 \u2013 November 2024\n\u2022  Universe: All GICS sectors (~1.05 M observations)\n\u2022  Prediction universe: 38 stocks (GICS sector 30 / group 3030)\n\u2022  Sources: CRSP, Compustat, WRDS Financial Ratios, OptionsMetrics, BoardEx",
    { x: 0.4, y: 1.65, w: 5.9, h: 1.8, fontSize: 11.5, color: DARK_GRAY, fontFace: F_BODY }
  );
  slide.addText("Predictor Variable Categories (15 variables)", {
    x: 0.4, y: 3.55, w: 5.9, h: 0.38,
    fontSize: 14, bold: true, color: STEEL_BLUE, fontFace: F_BODY
  });
  const cats = [
    ["Size",            "Log real market capitalization"],
    ["Value",           "Book-to-market equity"],
    ["Momentum",        "12-month & 11-month momentum"],
    ["Profitability",   "Net profit margin, ROIC, \u0394ROA"],
    ["Governance",      "Board age diversity, % male directors"],
    ["Risk / Liquidity","Beta, Amihud illiquidity, current ratio"],
    ["Capital Structure","Net WC/assets, log share change, O/S ratio"],
  ];
  cats.forEach(([cat, desc], i) => {
    const y = 4.0 + i * 0.38;
    slide.addShape(prs.ShapeType.rect, {
      x: 0.4, y, w: 2.1, h: 0.34,
      fill: { color: NAVY }, line: { color: NAVY }
    });
    slide.addText(cat, {
      x: 0.45, y, w: 2.0, h: 0.34,
      fontSize: 10.5, bold: true, color: WHITE, fontFace: F_BODY, valign: "middle"
    });
    slide.addText(desc, {
      x: 2.55, y, w: 3.7, h: 0.34,
      fontSize: 10.5, color: DARK_GRAY, fontFace: F_BODY, valign: "middle"
    });
  });
  // Right: Spearman correlation matrix
  slide.addText("Spearman Correlation Matrix of Predictors (Training Set)", {
    x: 6.7, y: 1.22, w: 6.3, h: 0.33,
    fontSize: 10.5, italic: true, color: MID_GRAY, fontFace: F_BODY
  });
  slide.addImage({ path: `${MEDIA}/image2.png`, x: 6.7, y: 1.6, w: 6.3, h: 5.55 });
}

// ════════════════════════════════════════════════════════════════
// SLIDE 4 – Variable of Interest: Net Profit Margin
// ════════════════════════════════════════════════════════════════
{
  const slide = contentSlide("Variable of Interest: Net Profit Margin");
  slide.addText("Why Net Profit Margin?", {
    x: 0.4, y: 1.22, w: 6.2, h: 0.38,
    fontSize: 14, bold: true, color: STEEL_BLUE, fontFace: F_BODY
  });
  slide.addText(
    "Net profit margin (net income \u00f7 total sales) captures how efficiently a firm converts revenue into earnings \u2014 a fundamental profitability signal in a sector driven by brand equity and operational efficiency.\n\n\u2022  Sustained margins signal durable competitive advantages\n\u2022  Supported by Novy-Marx (2013): profitable firms earn significantly higher returns\n\u2022  Winsorized at 1st\u201399th percentile; two sequential trimming passes removed ~2.2% of extreme observations\n\u2022  Final distribution: median 0.036; range [\u221222.14, 0.36]",
    { x: 0.4, y: 1.68, w: 6.2, h: 3.35, fontSize: 12, color: DARK_GRAY, fontFace: F_BODY }
  );
  // Stats box
  slide.addShape(prs.ShapeType.rect, {
    x: 0.4, y: 5.15, w: 6.2, h: 0.82,
    fill: { color: LIGHT_NAVY }, line: { color: STEEL_BLUE, pt: 1 }
  });
  slide.addText(
    "Full sample: 1,053,738 obs.  |  Missingness: ~5%  |  Variable code: finnpm",
    { x: 0.6, y: 5.2, w: 5.8, h: 0.72, fontSize: 11.5, color: NAVY, fontFace: F_BODY, valign: "middle" }
  );
  // Right: two stacked figures
  slide.addText("Distribution of finnpm (Sector 3030)", {
    x: 6.9, y: 1.22, w: 6.1, h: 0.3, fontSize: 10.5, italic: true, color: MID_GRAY, fontFace: F_BODY
  });
  slide.addImage({ path: `${MEDIA}/fig_voi_distribution.png`, x: 6.9, y: 1.57, w: 6.1, h: 2.65 });
  slide.addText("Mean Industry-Adjusted Return by Decile of Net Profit Margin", {
    x: 6.9, y: 4.28, w: 6.1, h: 0.3, fontSize: 10.5, italic: true, color: MID_GRAY, fontFace: F_BODY
  });
  slide.addImage({ path: `${MEDIA}/fig_voi_return_scatter.png`, x: 6.9, y: 4.63, w: 6.1, h: 2.55 });
}

// ════════════════════════════════════════════════════════════════
// SLIDE 5 – Data Splits
// ════════════════════════════════════════════════════════════════
{
  const slide = contentSlide("Data Splits & Methodology");
  slide.addImage({
    path: `${MEDIA}/fig_train_test_timeline.png`,
    x: 0.4, y: 1.18, w: 12.5, h: 3.3
  });
  const splits = [
    { label: "Training",   period: "Jan 2001 \u2013 Dec 2018", detail: "Fit all model parameters\n18 years, multiple business cycles",     dark: false },
    { label: "Validation", period: "Jan 2019 \u2013 Dec 2021", detail: "Hyperparameter tuning\nIncludes COVID-19 structural break",        dark: false },
    { label: "Test",       period: "Jan 2022 \u2013 Oct 2024", detail: "Out-of-sample performance\n(R\u00b2, RMSE, Spearman \u03c1)",       dark: false },
    { label: "Prediction", period: "November 2024",             detail: "Features as of Oct 31, 2024\nindadjret never used in training",    dark: true  },
  ];
  splits.forEach(({ label, period, detail, dark }, i) => {
    const x = 0.4 + i * 3.23;
    slide.addShape(prs.ShapeType.rect, {
      x, y: 4.63, w: 3.05, h: 2.55,
      fill: { color: dark ? NAVY : LIGHT_NAVY },
      line: { color: dark ? GOLD : STEEL_BLUE, pt: dark ? 2 : 1 }
    });
    slide.addText(label, {
      x: x + 0.12, y: 4.7, w: 2.8, h: 0.38,
      fontSize: 14, bold: true, color: dark ? WHITE : NAVY, fontFace: F_BODY
    });
    slide.addText(period, {
      x: x + 0.12, y: 5.1, w: 2.8, h: 0.38,
      fontSize: 11, bold: true, color: dark ? GOLD : STEEL_BLUE, fontFace: F_BODY
    });
    slide.addText(detail, {
      x: x + 0.12, y: 5.52, w: 2.8, h: 1.45,
      fontSize: 10.5, color: dark ? "A8C0D6" : DARK_GRAY, fontFace: F_BODY
    });
  });
}

// ════════════════════════════════════════════════════════════════
// SLIDE 6 – OLS
// ════════════════════════════════════════════════════════════════
modelSlide(
  "OLS Regression",
  [
    { label: "R\u00b2 (Test)",    value: "\u22120.0012" },
    { label: "RMSE",              value: "0.1852"       },
    { label: "MAE",               value: "0.1078"       },
    { label: "Spearman \u03c1",   value: "\u22120.0441" },
  ],
  "\u2022  Predictive accuracy is near zero \u2014 consistent with the empirical difficulty of forecasting cross-sectional returns\n\n\u2022  Momentum (Mom11, Mom12), size (log market cap), and book-to-market equity have the largest standardized coefficient magnitudes\n\n\u2022  Positive predictors: Mom11, Mom12, B/M\n\n\u2022  Negative predictors: Log Market Cap, Amihud illiquidity, O/S ratio",
  `${MEDIA}/fig_ols_coefficients.png`,
  "Standardized coefficient estimates (|coef| sorted, blue = positive, red = negative)"
);

// ════════════════════════════════════════════════════════════════
// SLIDE 7 – LASSO
// ════════════════════════════════════════════════════════════════
modelSlide(
  "LASSO Penalized Regression",
  [
    { label: "R\u00b2 (Test)",      value: "\u22120.0012" },
    { label: "Optimal \u03b1",      value: "0.00450"      },
    { label: "Predictors Zeroed",   value: "13 of 15",  highlight: true },
    { label: "Spearman \u03c1",     value: "\u22120.0576" },
  ],
  "\u2022  LASSO variable selection: only 2 of 15 predictors survive with non-zero coefficients\n\n\u2022  Surviving predictors: Log Market Cap and Book-to-Market equity only\n\n\u2022  Performance virtually identical to OLS \u2014 additional features contribute mostly noise\n\n\u2022  Stark result: 87% of predictors are irrelevant under regularization",
  `${MEDIA}/fig_lasso_path.png`,
  "LASSO regularization path \u2014 dashed line marks cross-validated optimal \u03b1"
);

// ════════════════════════════════════════════════════════════════
// SLIDE 8 – Decision Tree
// ════════════════════════════════════════════════════════════════
modelSlide(
  "Vanilla Decision Tree",
  [
    { label: "R\u00b2 (Test)",  value: "\u22120.0095" },
    { label: "Optimal Depth",   value: "3"            },
    { label: "Val. R\u00b2",    value: "0.0032"       },
    { label: "Top Splitter",    value: "Mom12"        },
  ],
  "\u2022  Max depth = 3 selected via validation-set grid search \u2014 prevents severe overfitting\n\n\u2022  12-month momentum (finmom12) is the most important splitting feature across all branches\n\n\u2022  Worst out-of-sample R\u00b2 among all models, but the simple structure reveals momentum\u2019s dominance clearly\n\n\u2022  Shallow depth limits ability to capture complex variable interactions",
  `${MEDIA}/fig_tree_importance.png`,
  "Feature importances (mean decrease in impurity) \u2014 only features assigned non-zero importance shown"
);

// ════════════════════════════════════════════════════════════════
// SLIDE 9 – Random Forest
// ════════════════════════════════════════════════════════════════
modelSlide(
  "Random Forest",
  [
    { label: "R\u00b2 (Test)",  value: "\u22120.0090" },
    { label: "Trees",           value: "200"          },
    { label: "Max Depth",       value: "10"           },
    { label: "Max Features",    value: "\u221an"      },
  ],
  "\u2022  Optimal hyperparameters via grid search: n=200 trees, depth=10, features=\u221an\n\n\u2022  Validation R\u00b2 = 0.0054 \u2014 best among tree-based methods during tuning\n\n\u2022  Ensemble averaging reduces variance vs. single tree, but out-of-sample improvement is marginal\n\n\u2022  Momentum (finmom12) again dominates feature importance; B/M and size are secondary",
  `${MEDIA}/fig_rf_importance.png`,
  "Feature importances (mean decrease in impurity, top 15, normalized to sum to 1)"
);

// ════════════════════════════════════════════════════════════════
// SLIDE 10 – XGBoost
// ════════════════════════════════════════════════════════════════
modelSlide(
  "Gradient Boosting (XGBoost)",
  [
    { label: "R\u00b2 (Test)",     value: "\u22120.0041", highlight: true },
    { label: "Best R\u00b2 (All)", value: "#1 of 6",      highlight: true },
    { label: "Stopped At",         value: "Iter 79"                       },
    { label: "Spearman \u03c1",    value: "+0.0014"                       },
  ],
  "\u2022  Best out-of-sample R\u00b2 among all six models (R\u00b2 = \u22120.0041), though improvement is marginal\n\n\u2022  Early stopping halted training at iteration 79 of 1,000 \u2014 the predictive signal is quickly exhausted\n\n\u2022  Only model with a positive (near-zero) Spearman \u03c1 = 0.0014, though not statistically significant (p = 0.605)\n\n\u2022  Momentum and book-to-market dominate gain-based feature importance",
  `${MEDIA}/fig_xgb_importance.png`,
  "Feature importances by gain (total improvement in loss attributed to each feature)"
);

// ════════════════════════════════════════════════════════════════
// SLIDE 11 – Neural Network
// ════════════════════════════════════════════════════════════════
modelSlide(
  "Neural Network (MLP)",
  [
    { label: "R\u00b2 (Test)",  value: "\u22120.0059"  },
    { label: "Architecture",    value: "128\u219264\u219232" },
    { label: "Early Stop",      value: "Epoch 30"       },
    { label: "Parameters",      value: "12,417"         },
  ],
  "\u2022  3-layer MLP: hidden layers (128, 64, 32), ReLU activations, Adam optimizer (\u03b7 = 0.001), L2 weight decay (\u03b1 = 0.001)\n\n\u2022  Inputs standardized with a StandardScaler fitted on the training set only\n\n\u2022  Loss curves show no signs of severe overfitting \u2014 regularization and early stopping are working\n\n\u2022  Spearman \u03c1 = \u22120.0027 (p = 0.304, not statistically significant)",
  `${MEDIA}/fig_nn_loss.png`,
  "Training vs. validation loss curves \u2014 dashed line marks early-stopping epoch"
);

// ════════════════════════════════════════════════════════════════
// SLIDE 12 – Interesting & Unusual Findings
// ════════════════════════════════════════════════════════════════
{
  const slide = contentSlide("Interesting & Unusual Findings");
  const findings = [
    {
      title: "All Six Models Produce Near-Zero or Negative R\u00b2",
      body: "Every model fails to beat a naive mean predictor on the 2022\u20132024 test set. Even the best model (XGBoost) achieves only R\u00b2 = \u22120.0041. This confirms the well-established empirical result that cross-sectional stock returns are extremely difficult to predict.",
      color: NAVY
    },
    {
      title: "LASSO Eliminates 87% of Predictors",
      body: "At the optimal penalty \u03b1 = 0.00450, only Log Market Cap and Book-to-Market survive. 13 of 15 carefully constructed predictors \u2014 including governance, profitability, and liquidity variables \u2014 are shrunk exactly to zero. The signal is concentrated in just two classic factors.",
      color: STEEL_BLUE
    },
    {
      title: "Cross-Model Consensus Despite Poor Individual Fit",
      body: "Despite near-zero R\u00b2 across all models, NAII ranks in the top tier consistently. Models with essentially no predictive power still agree on relative ordering \u2014 suggesting the top picks are driven by strong factor signals (particularly momentum) rather than noise.",
      color: "1A6B3C"
    },
    {
      title: "XGBoost Exhausts Signal at Iteration 79 of 1,000",
      body: "With a patience of 50 and up to 1,000 boosting rounds, XGBoost stopped at just iteration 79. The predictable content of 15 firm characteristics for monthly return prediction is exhausted almost immediately, consistent with near-random cross-sectional returns in this sector.",
      color: "7B4000"
    },
  ];
  findings.forEach(({ title, body, color }, i) => {
    const col = i % 2;
    const row = Math.floor(i / 2);
    const x = 0.4 + col * 6.5;
    const y = 1.18 + row * 3.1;
    slide.addShape(prs.ShapeType.rect, {
      x, y, w: 6.2, h: 2.9,
      fill: { color: WHITE }, line: { color: color, pt: 2 }
    });
    slide.addShape(prs.ShapeType.rect, {
      x, y, w: 0.1, h: 2.9, fill: { color }, line: { color }
    });
    slide.addText(title, {
      x: x + 0.25, y: y + 0.1, w: 5.8, h: 0.48,
      fontSize: 13, bold: true, color, fontFace: F_BODY
    });
    slide.addText(body, {
      x: x + 0.25, y: y + 0.63, w: 5.8, h: 2.15,
      fontSize: 11.5, color: DARK_GRAY, fontFace: F_BODY
    });
  });
}

// ════════════════════════════════════════════════════════════════
// SLIDE 13 – Model Comparison & Rankings
// ════════════════════════════════════════════════════════════════
{
  const slide = contentSlide("Model Comparison & Stock Rankings");
  // Left figure: metrics
  slide.addText("Out-of-Sample R\u00b2 & RMSE by Model", {
    x: 0.4, y: 1.18, w: 6.1, h: 0.32,
    fontSize: 10.5, italic: true, color: MID_GRAY, fontFace: F_BODY
  });
  slide.addImage({ path: `${MEDIA}/fig_metrics_comparison.png`, x: 0.4, y: 1.55, w: 6.1, h: 3.1 });
  // Right figure: rankings
  slide.addText("Average Rank Across 6 Models \u2014 All 38 Sector Stocks (Nov 2024)", {
    x: 6.8, y: 1.18, w: 6.2, h: 0.32,
    fontSize: 10.5, italic: true, color: MID_GRAY, fontFace: F_BODY
  });
  slide.addImage({ path: `${MEDIA}/fig_sector_predictions.png`, x: 6.8, y: 1.55, w: 6.2, h: 3.1 });

  // Bottom performance table
  slide.addText("Out-of-Sample Performance Summary", {
    x: 0.4, y: 4.82, w: 12.5, h: 0.35,
    fontSize: 12.5, bold: true, color: STEEL_BLUE, fontFace: F_BODY
  });
  const colW = [2.3, 1.7, 1.55, 1.8, 1.55, 2.7];
  const headers = ["Model", "R\u00b2 (Test)", "RMSE", "Spearman \u03c1", "p-value", "Nov 2024 Top Pick"];
  const rows = [
    ["OLS",           "\u22120.0012", "0.1852", "\u22120.0441", "0.0000", "\u2014"],
    ["LASSO",         "\u22120.0012", "0.1852", "\u22120.0576", "0.0000", "\u2014"],
    ["Decision Tree", "\u22120.0095", "0.1860", "\u22120.0469", "0.0000", "\u2014"],
    ["Random Forest", "\u22120.0090", "0.1860", "\u22120.0278", "0.0000", "\u2014"],
    ["XGBoost",       "\u22120.0041", "0.1855", "+0.0014",      "0.6047", "NAII (rank 1)"],
    ["Neural Net",    "\u22120.0059", "0.1857", "\u22120.0027", "0.3041", "\u2014"],
  ];
  const tY = 5.22;
  const rowH = 0.295;
  // Header
  let cx = 0.4;
  headers.forEach((h, j) => {
    slide.addShape(prs.ShapeType.rect, {
      x: cx, y: tY, w: colW[j], h: rowH,
      fill: { color: NAVY }, line: { color: NAVY }
    });
    slide.addText(h, {
      x: cx + 0.05, y: tY, w: colW[j] - 0.1, h: rowH,
      fontSize: 9.5, bold: true, color: WHITE, fontFace: F_BODY, valign: "middle"
    });
    cx += colW[j];
  });
  // Rows
  rows.forEach((row, ri) => {
    cx = 0.4;
    const isXGB = ri === 4;
    row.forEach((cell, j) => {
      slide.addShape(prs.ShapeType.rect, {
        x: cx, y: tY + rowH * (ri + 1), w: colW[j], h: rowH,
        fill: { color: isXGB ? LIGHT_NAVY : (ri % 2 === 0 ? WHITE : "F5F6F8") },
        line: { color: "CCCCCC", pt: 0.5 }
      });
      slide.addText(cell, {
        x: cx + 0.05, y: tY + rowH * (ri + 1), w: colW[j] - 0.1, h: rowH,
        fontSize: 9.5, bold: isXGB, color: isXGB ? NAVY : DARK_GRAY,
        fontFace: F_BODY, valign: "middle"
      });
      cx += colW[j];
    });
  });
}

// ════════════════════════════════════════════════════════════════
// SLIDE 14 – Conclusion
// ════════════════════════════════════════════════════════════════
{
  const slide = prs.addSlide();
  slide.addShape(prs.ShapeType.rect, {
    x: 0, y: 0, w: W, h: H, fill: { color: NAVY }, line: { color: NAVY }
  });
  slide.addShape(prs.ShapeType.rect, {
    x: 0, y: 0, w: 0.09, h: H, fill: { color: GOLD }, line: { color: GOLD }
  });
  slide.addText("Conclusion", {
    x: 0.5, y: 0.45, w: 12.0, h: 0.75,
    fontSize: 38, bold: true, color: WHITE, fontFace: F_TITLE
  });
  slide.addShape(prs.ShapeType.rect, {
    x: 0.5, y: 1.28, w: 3.5, h: 0.06, fill: { color: GOLD }, line: { color: GOLD }
  });
  // Recommendation banner
  slide.addShape(prs.ShapeType.rect, {
    x: 0.5, y: 1.48, w: 12.5, h: 1.08,
    fill: { color: GOLD }, line: { color: GOLD }
  });
  slide.addText("Buy Recommendation:  NAII \u2014 Natural Alternatives International Inc.", {
    x: 0.7, y: 1.52, w: 12.1, h: 0.52,
    fontSize: 21, bold: true, color: NAVY, fontFace: F_TITLE, valign: "middle"
  });
  slide.addText(
    "Top-3 under OLS and XGBoost   \u2022   Top-8 under 4 of 6 models   \u2022   Strong 12-month momentum signal",
    {
      x: 0.7, y: 2.0, w: 12.1, h: 0.42,
      fontSize: 12.5, color: NAVY, fontFace: F_BODY, bold: false, valign: "middle"
    }
  );
  // Supporting points
  const points = [
    {
      n: "1",
      text: "All six models produce near-zero or slightly negative out-of-sample R\u00b2 on the 2022\u20132024 test period \u2014 consistent with the well-established empirical result that individual stock returns are very difficult to predict."
    },
    {
      n: "2",
      text: "12-month momentum is the most consistently important predictor across all six methods. LASSO further reduced the feature set to just market cap and book-to-market, eliminating 87% of predictors."
    },
    {
      n: "3",
      text: "Cross-model consensus provides additional confidence: even weak directional signals, when aggregated across many stocks and methods, improve rank stability and support the NAII recommendation."
    },
    {
      n: "4",
      text: "Future work: ensemble stacking, alternative targets (sector-relative rank), richer feature sets including sentiment from earnings calls, and longer prediction horizons."
    },
  ];
  points.forEach(({ n, text }, i) => {
    const y = 2.72 + i * 1.08;
    slide.addShape(prs.ShapeType.ellipse, {
      x: 0.5, y: y + 0.02, w: 0.4, h: 0.4,
      fill: { color: GOLD }, line: { color: GOLD }
    });
    slide.addText(n, {
      x: 0.5, y: y + 0.02, w: 0.4, h: 0.4,
      fontSize: 13, bold: true, color: NAVY, fontFace: F_BODY,
      align: "center", valign: "middle"
    });
    slide.addText(text, {
      x: 1.05, y, w: 11.9, h: 0.5,
      fontSize: 11.5, color: "C5D5E8", fontFace: F_BODY
    });
  });
  slide.addText("FIN 427  |  University of Michigan  |  April 2026", {
    x: 0.5, y: 7.1, w: 12.0, h: 0.3,
    fontSize: 10, color: "4F7090", fontFace: F_BODY, align: "center"
  });
}

// ════════════════════════════════════════════════════════════════
// Save
// ════════════════════════════════════════════════════════════════
prs.writeFile({ fileName: "C:/Users/hrwan/fin427/fin427report/FIN427_Presentation.pptx" })
  .then(() => console.log("Saved: FIN427_Presentation.pptx"))
  .catch(err => { console.error(err); process.exit(1); });
