"""
Build FIN427_Report.docx from Template.docx, mirroring the LaTeX report content.
Run from the report_docx folder or any location — paths are absolute.
"""

from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from lxml import etree
import copy, os

TEMPLATE = r'c:\Users\hrwan\fin427\fin427report\report_docx\Template.docx'
MEDIA    = r'c:\Users\hrwan\fin427\fin427report\report_latex\media\media'
OUTPUT   = r'c:\Users\hrwan\fin427\fin427report\report_docx\FIN427_Report.docx'

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def clear_body(doc):
    """Remove every element from the document body, leaving styles and sectPr intact."""
    body = doc.element.body
    # Preserve the sectPr (section/page layout) element
    sectPr = body.find(qn('w:sectPr'))
    for child in list(body):
        body.remove(child)
    # Re-add sectPr so page layout is preserved
    if sectPr is not None:
        body.append(sectPr)

def p(doc, text, style='Normal'):
    para = doc.add_paragraph(style=style)
    para.add_run(text)
    return para

def h(doc, text, level):
    return doc.add_heading(text, level=level)

def bold_p(doc, text, style='Normal'):
    para = doc.add_paragraph(style=style)
    para.add_run(text).bold = True
    return para

def caption(doc, text):
    para = doc.add_paragraph(style='Caption')
    para.add_run(text)
    return para

def fig(doc, filename, caption_text, width=5.5):
    path = os.path.join(MEDIA, filename)
    if os.path.exists(path):
        doc.add_picture(path, width=Inches(width))
        last = doc.paragraphs[-1]
        last.alignment = WD_ALIGN_PARAGRAPH.CENTER
    caption(doc, caption_text)

def bullet(doc, text, level=0):
    style = 'List Paragraph'
    para = doc.add_paragraph(style=style)
    para.paragraph_format.left_indent = Inches(0.25 * (level + 1))
    para.style.paragraph_format.first_line_indent = Inches(-0.25)
    run = para.add_run(text)
    # Add bullet formatting via numPr
    pPr = para._p.get_or_add_pPr()
    numPr = OxmlElement('w:numPr')
    ilvl = OxmlElement('w:ilvl')
    ilvl.set(qn('w:val'), str(level))
    numId = OxmlElement('w:numId')
    numId.set(qn('w:val'), '1')
    numPr.append(ilvl)
    numPr.append(numId)
    pPr.append(numPr)
    return para

def mixed_run(para, parts):
    """parts = list of (text, bold, italic) tuples"""
    for text, bold, italic in parts:
        run = para.add_run(text)
        run.bold = bold
        run.italic = italic


# ---------------------------------------------------------------------------
# Table builders
# ---------------------------------------------------------------------------

def add_variable_table(doc):
    """Table 1 — Variable names, labels and constraints (16 rows + header)."""
    caption(doc, 'Table 1. Variable names, labels and constraints')
    rows = [
        ('Real market capitalization',                            'lag1mcreal',   'J',  '0.00'),
        ('Natural logarithm of real market capitalization',       'lnlag1mcreal', 'J',  '0.00'),
        ('Book-to-market equity',                                 'bm',           'J',  '0.50'),
        ('Option volume/stock volume',                            'os',           '1',  '0.05'),
        ('Momentum12 (12 mth ret ending 1 mth prior to port)',   'mom12',        '2',  '1.00'),
        ('Net profit margin (Net profit/Sales)',                  'npm',          '3',  '1.00'),
        ('Standard deviation of board members\u2019 age',        'sdage',        '4',  '0.00'),
        ('Percentage male board members',                         'gender',       '4',  '0.00'),
        ('Systematic risk',                                       'beta',         '5',  '1.00'),
        ('Net working capital/Assets',                            'nwca',         '6',  '0.50'),
        ('Amihud liquidity \u00d7 1,000,000',                    'illiq',        '7',  '2.50'),
        ('Current ratio (Current assets/Current liabilities)',   'cr',           '8',  '1.00'),
        ('Natural logarithm of the change in issued shares',     'lnshchg',      '9',  '0.50'),
        ('Momentum 11 (11 mth ret ending 1 mth prior to port)',  'mom11',        '10', '1.00'),
        ('Change in return on assets',                           'chgroa',       '11', '2.50'),
        ('Return on invested capital',                           'roic',         '12', '2.50'),
    ]
    table = doc.add_table(rows=1 + len(rows), cols=4)
    table.style = 'Table Grid'
    hdr = table.rows[0].cells
    for i, hd in enumerate(['Name', 'Label', 'Group', 'Constraint']):
        hdr[i].text = hd
        hdr[i].paragraphs[0].runs[0].bold = True
    for r_idx, (name, label, grp, const) in enumerate(rows, start=1):
        row_cells = table.rows[r_idx].cells
        row_cells[0].text = name
        row_cells[1].text = label
        row_cells[2].text = grp
        row_cells[3].text = const
    doc.add_paragraph()  # spacing


def add_desc_stats_table(doc):
    """Table 2 — Descriptive statistics on the whole sample."""
    caption(doc, 'Table 2. Descriptive statistics on the whole sample')
    headers = ['Variable', 'N', 'Mean', 'Std', 'p1', 'p25', 'p50', 'p75', 'p99', '%Miss']
    data = [
        ('Log Market Cap',        '1,053,738', '13.6486', '2.1184',  '9.0592',   '12.1470',  '13.6252', '15.0681', '18.7068', '0.0'),
        ('Book-to-Market',        '1,053,738',  '0.5637', '0.6363',  '0.0000',   ' 0.1263',   '0.4239',  '0.7860',  '3.2579', '18.9'),
        ('Chg in ROA',            '1,053,738',  '0.0002', '0.1394', '-0.5519',  '-0.0063',   '0.0000',  '0.0056',  '0.5814', '30.5'),
        ('Amihud Illiquidity',    '1,053,738',  '1.2648', '5.6545',  '0.0001',   '0.0007',   '0.0059',  '0.0911', '42.1305',  '0.0'),
        ('Std Dev Board Age',     '1,053,738',  '6.2181', '3.8834',  '0.0000',   '4.3000',   '6.8000',  '8.8000', '14.4000', '20.4'),
        ('Pct Male Board',        '1,053,738',  '0.6869', '0.3659',  '0.0000',   '0.6360',   '0.8330',  '1.0000',  '1.0000', '20.4'),
        ('Net Profit Margin',     '1,053,738', '-0.4015', '2.8284', '-20.2819',  '0.0000',   '0.0250',  '0.0950',  '0.3770', '17.7'),
        ('Momentum 12m',          '1,053,738',  '0.1156', '0.5292', '-0.8424',  '-0.1756',   '0.0376',  '0.3066',  '2.4969',  '5.1'),
        ('Current Ratio',         '1,053,738',  '2.4912', '3.8439',  '0.0000',   '0.0500',   '1.5341',  '2.8528', '21.8429', '24.9'),
        ('Option/Stock Vol',      '1,053,738',  '0.0005', '0.0015',  '0.0000',   '0.0000',   '0.0001',  '0.0005',  '0.0061', '37.2'),
        ('Beta',                  '1,053,738',  '0.5794', '0.7244', '-0.1409',   '0.0000',   '0.1755',  '1.0668',  '2.8688', '45.7'),
        ('NWC/Assets',            '1,053,738',  '0.1739', '0.2548', '-0.2023',   '0.0000',   '0.0572',  '0.3091',  '0.8975', '33.2'),
        ('Ln Share Issuance Chg', '1,053,738',  '0.0017', '0.0216', '-0.0072',   '0.0000',   '0.0000',  '0.0000',  '0.0502', '75.5'),
        ('Momentum 11m',          '1,053,738',  '0.1062', '0.5057', '-0.8307',  '-0.1715',   '0.0359',  '0.2914',  '2.3624',  '4.7'),
        ('ROIC',                  '1,053,738',  '0.0051', '0.2097', '-0.9830',   '0.0000',   '0.0000',  '0.0960',  '0.3870', '17.4'),
        ('indadjret',             '1,053,738',  '0.0035', '0.1567', '-0.3590',  '-0.0613',  '-0.0038',  '0.0544',  '0.4960',  '0.0'),
    ]
    table = doc.add_table(rows=1 + len(data), cols=len(headers))
    table.style = 'Table Grid'
    for i, hd in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = hd
        cell.paragraphs[0].runs[0].bold = True
    for r_idx, row_data in enumerate(data, start=1):
        for c_idx, val in enumerate(row_data):
            table.rows[r_idx].cells[c_idx].text = val
    doc.add_paragraph()


def add_voi_table(doc):
    """Table — Descriptive statistics for Net Profit Margin (variable of interest)."""
    caption(doc, 'Table. Descriptive statistics for Net Profit Margin (variable of interest)')
    headers = ['Variable', 'N', 'Mean', 'Std', 'p1', 'p5', 'p25', 'p50', 'p75', 'p95', 'p99', '%Miss']
    data = [
        ('Net Profit Margin', '1,053,738', '-0.4015', '2.8284',
         '-20.2819', '-0.8800', '0.0000', '0.0250', '0.0950', '0.2400', '0.3770', '17.7'),
    ]
    table = doc.add_table(rows=1 + len(data), cols=len(headers))
    table.style = 'Table Grid'
    for i, hd in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = hd
        cell.paragraphs[0].runs[0].bold = True
    for r_idx, row_data in enumerate(data, start=1):
        for c_idx, val in enumerate(row_data):
            table.rows[r_idx].cells[c_idx].text = val
    doc.add_paragraph()


def add_splits_table(doc):
    """Table — Data splits."""
    caption(doc, 'Table. Data splits')
    headers = ['Split', 'Start', 'End', 'N Rows', 'N Stocks', 'N Months']
    data = [
        ('Training',   'January 2001',  'December 2018', '776,610', '9,163', '216'),
        ('Validation', 'January 2019',  'December 2021', '133,199', '4,753',  '36'),
        ('Test',       'January 2022',  'October 2024',  '143,929', '5,223',  '34'),
        ('Prediction', 'November 2024', 'November 2024',      '38',    '38',   '1'),
    ]
    table = doc.add_table(rows=1 + len(data), cols=6)
    table.style = 'Table Grid'
    for i, hd in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = hd
        cell.paragraphs[0].runs[0].bold = True
    for r_idx, row_data in enumerate(data, start=1):
        for c_idx, val in enumerate(row_data):
            table.rows[r_idx].cells[c_idx].text = val
    doc.add_paragraph()


def add_ols_coef_table(doc):
    caption(doc, 'Table. OLS coefficient estimates (sorted by |standardised coef|)')
    headers = ['Feature', 'Coefficient', 'Std Coef']
    data = [
        ('Momentum 12m',          '-0.008384', '-0.004461'),
        ('Momentum 11m',           '0.008443',  '0.004292'),
        ('Log Market Cap',        '-0.002026', '-0.004238'),
        ('Book-to-Market',         '0.006195',  '0.003961'),
        ('NWC/Assets',             '0.008014',  '0.001998'),
        ('Current Ratio',         '-0.000429', '-0.001573'),
        ('Pct Male Board',        '-0.004090', '-0.001543'),
        ('Ln Share Issuance Chg',  '0.067220',  '0.001264'),
        ('Beta',                   '0.001172',  '0.000831'),
        ('Amihud Illiquidity',    '-0.000131', '-0.000784'),
        ('ROIC',                   '0.002222',  '0.000452'),
        ('Chg in ROA',             '0.003365',  '0.000449'),
        ('Net Profit Margin',      '0.000121',  '0.000314'),
        ('Std Dev Board Age',     '-0.000073', '-0.000286'),
        ('Option/Stock Vol',       '0.064712',  '0.000087'),
    ]
    table = doc.add_table(rows=1 + len(data), cols=3)
    table.style = 'Table Grid'
    for i, hd in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = hd
        cell.paragraphs[0].runs[0].bold = True
    for r_idx, row_data in enumerate(data, start=1):
        for c_idx, val in enumerate(row_data):
            table.rows[r_idx].cells[c_idx].text = val
    doc.add_paragraph()


def add_lasso_coef_table(doc):
    caption(doc, 'Table. LASSO coefficient estimates (\u03b1 = 4.50e\u221203, 13 features zeroed)')
    headers = ['Feature', 'Coefficient', 'Zeroed']
    data = [
        ('Log Market Cap',        '-0.000670', 'No'),
        ('Book-to-Market',         '0.000356', 'No'),
        ('Chg in ROA',             '0.000000', 'Yes'),
        ('Amihud Illiquidity',     '0.000000', 'Yes'),
        ('Std Dev Board Age',     '-0.000000', 'Yes'),
        ('Pct Male Board',        '-0.000000', 'Yes'),
        ('Net Profit Margin',      '0.000000', 'Yes'),
        ('Momentum 12m',          '-0.000000', 'Yes'),
        ('Current Ratio',         '-0.000000', 'Yes'),
        ('Option/Stock Vol',      '-0.000000', 'Yes'),
        ('Beta',                  '-0.000000', 'Yes'),
        ('NWC/Assets',             '0.000000', 'Yes'),
        ('Ln Share Issuance Chg',  '0.000000', 'Yes'),
        ('Momentum 11m',          '-0.000000', 'Yes'),
        ('ROIC',                  '-0.000000', 'Yes'),
    ]
    table = doc.add_table(rows=1 + len(data), cols=3)
    table.style = 'Table Grid'
    for i, hd in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = hd
        cell.paragraphs[0].runs[0].bold = True
    for r_idx, row_data in enumerate(data, start=1):
        for c_idx, val in enumerate(row_data):
            table.rows[r_idx].cells[c_idx].text = val
    doc.add_paragraph()


def add_reconciliation_table(doc):
    """Table 3 — Stock rankings under different estimation techniques."""
    caption(doc, 'Table 3. Stock rankings under different estimation techniques')

    # 2 header rows + Panel A label + 10 data rows + Panel B label + 10 data rows = 24 rows
    # cols: Rank | OLS | LASSO | Vanilla | Random Forest | Gradient Boosting | Neural Networks
    panel_a_stocks = [
        ('1',  'NAII', 'NAII', 'SKIN', 'UPXI', 'UPXI', 'NUS'),
        ('2',  'UG',   'UPXI', 'MED',  'SKIN', 'SKIN', 'SKIN'),
        ('3',  'HNST', 'MTEX', 'UPXI', 'MED',  'UG',   'UG'),
        ('4',  'NUS',  'AXIL', 'UG',   'NUS',  'NUS',  'NAII'),
        ('5',  'MED',  'NHTC', 'NHTC', 'UG',   'NAII', 'MED'),
        ('6',  'NHTC', 'NUS',  'DSY',  'NAII', 'MED',  'HNST'),
        ('7',  'OLPX', 'UG',   'LFVN', 'WALD', 'WALD', 'DSY'),
        ('8',  'MTEX', 'MED',  'NAII', 'HNST', 'LFVN', 'NHTC'),
        ('9',  'SKIN', 'SNYR', 'AXIL', 'DSY',  'HNST', 'LFVN'),
        ('10', 'USNA', 'LFVN', 'NATR', 'LFVN', 'ODC',  'ODC'),
    ]
    panel_b_returns = [
        ('1',  '2.21', '0.65', '6.67', '18.05', '7.59', '4.44'),
        ('2',  '1.57', '0.61', '6.67',  '3.42', '3.28', '3.12'),
        ('3',  '1.25', '0.58', '6.67',  '1.99', '1.43', '2.07'),
        ('4',  '1.21', '0.54', '0.66',  '1.54', '1.41', '1.67'),
        ('5',  '1.07', '0.52', '0.66',  '1.03', '1.09', '1.20'),
        ('6',  '1.04', '0.52', '0.66',  '0.79', '0.93', '0.85'),
        ('7',  '0.92', '0.52', '0.66',  '0.73', '0.68', '0.34'),
        ('8',  '0.91', '0.51', '0.66',  '0.56', '0.49', '0.33'),
        ('9',  '0.89', '0.50', '0.66',  '0.38', '0.33', '0.27'),
        ('10', '0.85', '0.49', '0.66',  '0.34', '0.28', '0.27'),
    ]

    total_rows = 2 + 1 + 10 + 1 + 10  # header1 + header2 + panelA_label + 10 + panelB_label + 10
    table = doc.add_table(rows=total_rows, cols=7)
    table.style = 'Table Grid'

    # Row 0: category headers (merged cells conceptually via text)
    row0 = table.rows[0].cells
    row0[0].text = ''
    row0[1].text = 'Regression'
    row0[2].text = 'Regression'
    row0[3].text = 'Decision Trees'
    row0[4].text = 'Decision Trees'
    row0[5].text = 'Decision Trees'
    row0[6].text = 'Neural Networks'
    for cell in row0:
        if cell.text:
            cell.paragraphs[0].runs[0].bold = True

    # Row 1: column sub-headers
    row1 = table.rows[1].cells
    for i, hd in enumerate(['Rank', 'OLS', 'LASSO', 'Vanilla', 'Random Forest', 'Gradient Boosting', 'Neural Networks']):
        row1[i].text = hd
        row1[i].paragraphs[0].runs[0].bold = True

    # Row 2: Panel A label
    row2 = table.rows[2].cells
    row2[0].text = 'Panel A: Stock'
    row2[0].paragraphs[0].runs[0].bold = True
    for c in row2[1:]:
        c.text = ''

    # Rows 3-12: Panel A data
    for ri, row_data in enumerate(panel_a_stocks, start=3):
        cells = table.rows[ri].cells
        for ci, val in enumerate(row_data):
            cells[ci].text = val

    # Row 13: Panel B label
    row13 = table.rows[13].cells
    row13[0].text = 'Panel B: Predicted Return (%)'
    row13[0].paragraphs[0].runs[0].bold = True
    for c in row13[1:]:
        c.text = ''

    # Rows 14-23: Panel B data
    for ri, row_data in enumerate(panel_b_returns, start=14):
        cells = table.rows[ri].cells
        for ci, val in enumerate(row_data):
            cells[ci].text = val

    doc.add_paragraph()


# ---------------------------------------------------------------------------
# Main build
# ---------------------------------------------------------------------------

doc = Document(TEMPLATE)
clear_body(doc)

# ---- Title page / header -------------------------------------------------
doc.core_properties.title = 'Machine Learning Stock Selection: Household and Personal Products Sector'

h(doc, 'Machine Learning Stock Selection: Household and Personal Products Sector', level=0)

# Abstract
p(doc, (
    'This paper applies six machine learning models to predict industry-adjusted monthly returns '
    'for stocks in the Household and Personal Products sector (GICS sector 30, group 3030) and '
    'uses those predictions to recommend one stock to buy in November 2024. '
    'The dataset spans January 2001 through November 2024 and contains approximately 1.05 million '
    'stock-month observations across all GICS sectors. Fifteen winsorized predictor variables '
    'capture size, value, momentum, profitability, liquidity, governance, and risk characteristics. '
    'Models are trained on data from January 2001 through December 2018, tuned on a validation '
    'window (January 2019\u2013December 2021), and evaluated on a held-out test set '
    '(January 2022\u2013October 2024); November 2024 serves as the pure prediction month. '
    'The six methods are: ordinary least squares (OLS) regression, LASSO penalized regression, '
    'a vanilla decision tree, a random forest, gradient boosting (XGBoost), and a simple '
    'three-layer neural network. Out-of-sample R\u00b2 values are near zero or slightly negative '
    'for all models, consistent with the well-documented difficulty of predicting cross-sectional '
    'stock returns. Despite limited predictive power in aggregate, the models exhibit '
    'meaningful agreement in their top-ranked picks for November 2024. '
    'NAII (Natural Alternatives International Inc.) appears in the top three rankings under '
    'two of six models and is our recommended buy. Net profit margin (finnpm) is our '
    'variable of interest, capturing how efficiently firms in this sector convert revenue '
    'into earnings.'
))
doc.add_paragraph()

# Author / date placeholder
para = doc.add_paragraph()
para.add_run('[Student Name 1]').bold = False
para.add_run(' | [email@umich.edu] | [phone]')
doc.add_paragraph('[Student Name 2] | [email@umich.edu] | [phone]')
doc.add_paragraph('[Month Day, Year]')
doc.add_paragraph()

# ---- Table of Contents placeholder -------------------------------------
h(doc, 'Contents', level=1)
p(doc, '[Update this table of contents field before submission]')
doc.add_paragraph()

h(doc, 'Tables', level=1)
p(doc, 'Table 1. Variable names, labels and constraints')
p(doc, 'Table 2. Descriptive statistics on the whole sample')
p(doc, 'Table 3. Stock rankings under different estimation techniques')
doc.add_paragraph()

h(doc, 'Figures', level=1)
p(doc, 'Figure 1. Spearman correlation matrix of the 15 predictor variables')
p(doc, 'Figure 2. Distribution of net profit margin (finnpm)')
p(doc, 'Figure 3. Mean industry-adjusted return by decile of net profit margin')
p(doc, 'Figure 4. Chronological data splits')
p(doc, 'Figure 5. OLS standardised coefficient estimates')
p(doc, 'Figure 6. LASSO regularization path')
p(doc, 'Figure 7. Vanilla decision tree structure')
p(doc, 'Figure 8. Vanilla decision tree feature importances')
p(doc, 'Figure 9. Random forest feature importances')
p(doc, 'Figure 10. XGBoost feature importances')
p(doc, 'Figure 11. Neural network training and validation loss curves')
p(doc, 'Figure 12. Average rank across six models for all 38 sector stocks')
p(doc, 'Figure 13. Out-of-sample R\u00b2 and RMSE for each model')
doc.add_paragraph()

# ---- Introduction -------------------------------------------------------
h(doc, 'Introduction', level=1)

h(doc, 'Research Question and Overview', level=2)
p(doc, (
    'Can machine learning models trained on publicly observable stock characteristics '
    'identify which stock in the Household and Personal Products sector (GICS 3030) '
    'will deliver the highest industry-adjusted return in November 2024? '
    'We address this question by fitting six distinct models \u2014 OLS, LASSO, a vanilla '
    'decision tree, a random forest, XGBoost, and a simple neural network \u2014 on a '
    'large cross-sectional panel spanning more than two decades, then generating '
    'out-of-sample predictions for the 38 sector stocks observed at the October 2024 '
    'portfolio formation date. The stock that scores highest most consistently across '
    'methods is our recommended investment: '
    'NAII (Natural Alternatives International Inc.).'
))

h(doc, 'Report Structure', level=2)
p(doc, (
    'Section 2 describes the dataset, variable construction, and the chronological '
    'train/validation/test/prediction split. Section 3 presents results for each model '
    'together with out-of-sample performance metrics and feature importances. '
    'Section 4 reconciles the six sets of predictions and justifies the final stock pick. '
    'Section 5 concludes. An appendix provides detailed descriptions of each predictor variable.'
))

# ---- Data ---------------------------------------------------------------
h(doc, 'Data', level=1)

h(doc, 'Variable Names, Labels and Descriptions', level=2)
p(doc, (
    'The name and label for each independent variable are presented in Table 1, '
    'along with the group that compiled each variable and the constraint applied to '
    'each variable to mitigate the potential for outliers to have an outsized influence '
    'on results. For example, 0.50 for Book-to-market equity means the variable was '
    'constrained at the 0.5th percentile and the 99.5th percentile. '
    'A description for each variable is provided in the Appendix.'
))
doc.add_paragraph()
add_variable_table(doc)

h(doc, 'Descriptive Statistics on the Whole Sample', level=2)
p(doc, (
    'The dataset covers the period January 2001 to October 2024, comprising 1,053,738 '
    'stock-month observations across all GICS sectors. Table 2 reports summary statistics '
    'for all 15 predictor variables and the target variable (industry-adjusted return, '
    'indadjret), computed on the full sample excluding November 2024. The fin* columns are '
    'winsorized at the percentile constraints listed in Table 1; the percentage missing '
    'reflects the fraction of raw observations that required imputation. lnshchg (log change '
    'in shares issued) has the highest missingness at approximately 75%, while illiquidity '
    'and momentum are nearly complete.'
))
doc.add_paragraph()
add_desc_stats_table(doc)

fig(doc, 'fig_desc_stats.png',
    'Figure 1. Spearman correlation matrix of the 15 predictor variables computed '
    'on the training set (January 2001 \u2013 December 2018). Values shown are Spearman rank '
    'correlations. The momentum variables (finmom11, finmom12) are highly correlated '
    'with each other, as expected.', width=5.5)

h(doc, 'Descriptive Statistics on Your Variable of Interest', level=2)
p(doc, (
    'We select net profit margin (finnpm) as our variable of interest. '
    'Net profit margin \u2014 defined as net income divided by total sales \u2014 is a '
    'fundamental profitability measure that captures how efficiently a firm converts '
    'revenue into earnings after all costs, taxes, and interest. In the Household and '
    'Personal Products sector, where firms compete on brand equity and operational '
    'efficiency, sustained profit margins signal durable competitive advantages that '
    'may be rewarded by the market.'
))
p(doc, (
    'The variable is winsorized at the 1st and 99th percentiles (constraint 1.00), '
    'which preserves large profitability signals while eliminating extreme data errors. '
    'Descriptive statistics for the full sample (excluding November 2024) are presented '
    'in the table below. Figure 2 shows the distribution of finnpm within our sector, '
    'and Figure 3 shows the relationship between net profit margin decile and mean '
    'industry-adjusted return in the training set.'
))
doc.add_paragraph()
add_voi_table(doc)

fig(doc, 'fig_voi_distribution.png',
    'Figure 2. Distribution of net profit margin (finnpm) for Household & Personal '
    'Products stocks (sector 30, group 3030).', width=5.0)

fig(doc, 'fig_voi_return_scatter.png',
    'Figure 3. Mean industry-adjusted return by decile of net profit margin, '
    'training set (January 2001 \u2013 December 2018), Household & Personal Products sector.',
    width=5.0)

h(doc, 'Training, Test, Validation Samples and the Last Month', level=2)
p(doc, (
    'We partition the data chronologically to prevent look-ahead bias. All models are '
    'trained on the full cross-sectional universe (all GICS sectors) to maximise the number '
    'of observations available for learning the relationship between stock characteristics '
    'and industry-adjusted returns; predictions are then restricted to the 38 Household '
    'and Personal Products stocks present in November 2024.'
))

for text in [
    'Training set (January 2001 \u2013 December 2018): Used to fit all model parameters. '
    'The 18-year window captures multiple full business cycles including the dot-com bust, '
    'the 2008 financial crisis, and the subsequent recovery.',

    'Validation set (January 2019 \u2013 December 2021): Used for hyperparameter selection '
    '(LASSO penalty, tree depth, forest grid, XGBoost early stopping). This window includes '
    'the COVID-19 shock of 2020, testing model robustness to structural breaks.',

    'Test set (January 2022 \u2013 October 2024): Used for final out-of-sample performance '
    'reporting (R\u00b2, RMSE, Spearman \u03c1). Models are refit on training + validation '
    'combined before test evaluation.',

    'Prediction month (November 2024): Features are observed as of October 31, 2024 '
    '(the portfolio formation date). The indadjret for November 2024 is never used '
    'during modelling; it serves only for ex-post verification of the recommendation.',
]:
    bullet(doc, text, level=0)

doc.add_paragraph()
add_splits_table(doc)

fig(doc, 'fig_train_test_timeline.png',
    'Figure 4. Chronological data splits. Models are trained on the full cross-sectional '
    'universe; the prediction is restricted to 38 Household & Personal Products stocks '
    'in November 2024.', width=5.5)

# ---- Results ------------------------------------------------------------
h(doc, 'Results', level=1)

h(doc, 'Regression', level=2)

h(doc, 'Ordinary Least Squares Regression', level=3)
p(doc, (
    'The OLS model achieves an out-of-sample R\u00b2 of \u22120.0012 on the test set '
    '(January 2022 \u2013 October 2024), with RMSE of 0.1852, MAE of 0.1078, and '
    'Spearman rank correlation of \u22120.0441 (p-value 0.0000). '
    'Although the predictive accuracy is slightly negative relative to a na\u00efve mean '
    'forecast, the estimated coefficients provide useful signals about which characteristics '
    'are associated with higher returns. Momentum (both 11- and 12-month), size, and '
    'book-to-market receive the largest standardised coefficient magnitudes.'
))
doc.add_paragraph()
add_ols_coef_table(doc)

fig(doc, 'fig_ols_coefficients.png',
    'Figure 5. OLS standardised coefficient estimates. Blue bars indicate a positive '
    'relationship with industry-adjusted returns; red bars indicate a negative relationship. '
    'Sorted by absolute magnitude.', width=5.5)

h(doc, 'Penalized Regression', level=3)
p(doc, (
    'The optimal regularization parameter selected via LassoCV with 5-fold time-series '
    'cross-validation is \u03b1 = 4.50e\u221203. At this penalty level, 13 of 15 predictors '
    'are shrunk exactly to zero, demonstrating the variable-selection property of LASSO. '
    'Only Log Market Cap and Book-to-Market survive regularization with non-zero coefficients.'
))
p(doc, (
    'The LASSO model achieves an out-of-sample R\u00b2 of \u22120.0012 on the test set '
    '(January 2022 \u2013 October 2024), with RMSE of 0.1852, MAE of 0.1075, and '
    'Spearman rank correlation of \u22120.0576 (p-value 0.0000). Performance is '
    'essentially identical to OLS, suggesting the signal is concentrated in the two '
    'surviving predictors and that additional features contribute mostly noise.'
))
doc.add_paragraph()
add_lasso_coef_table(doc)

fig(doc, 'fig_lasso_path.png',
    'Figure 6. LASSO regularization path. Each coloured line shows how a coefficient '
    'evolves as the penalty decreases (right). The dashed vertical line marks the '
    'cross-validation-selected \u03b1.', width=5.5)

h(doc, 'Decision Trees', level=2)

h(doc, 'Vanilla Decision Tree', level=3)
p(doc, (
    'The optimal tree depth selected via validation-set R\u00b2 grid search is 3 '
    '(validation R\u00b2 = 0.0032). The most important splitting feature is Momentum 12m.'
))
p(doc, (
    'The vanilla decision tree model achieves an out-of-sample R\u00b2 of \u22120.0095 '
    'on the test set (January 2022 \u2013 October 2024), with RMSE of 0.1860, MAE of '
    '0.1083, and Spearman rank correlation of \u22120.0469 (p-value 0.0000). The shallow '
    'depth constraint (max depth = 3) prevents severe overfitting but limits the '
    'model\u2019s ability to capture non-linear interactions beyond the top-level splits.'
))

fig(doc, 'fig_tree_structure.png',
    'Figure 7. Vanilla decision tree structure (best depth = 3). '
    'Shading intensity indicates the predicted value in each leaf.', width=5.5)

fig(doc, 'fig_tree_importance.png',
    'Figure 8. Vanilla decision tree feature importances (mean decrease in impurity). '
    'Only features assigned non-zero importance are split upon.', width=4.5)

h(doc, 'Random Forest', level=3)
p(doc, (
    'Grid search over {n_estimators \u2208 {100, 200}, max_depth \u2208 {5, 10}, '
    'max_features \u2208 {sqrt, 0.5}} (8 combinations) selects 200 trees, max depth 10, '
    'max features sqrt (validation R\u00b2 = 0.0054). The ensemble averages over many '
    'decorrelated trees, reducing variance relative to the single decision tree.'
))
p(doc, (
    'The random forest model achieves an out-of-sample R\u00b2 of \u22120.0090 on the '
    'test set (January 2022 \u2013 October 2024), with RMSE of 0.1860, MAE of 0.1089, '
    'and Spearman rank correlation of \u22120.0278 (p-value 0.0000).'
))

fig(doc, 'fig_rf_importance.png',
    'Figure 9. Random forest feature importances (mean decrease in impurity, top 15 features). '
    'Values are normalised to sum to 1 across all features.', width=5.0)

h(doc, 'Gradient Boosting', level=3)
p(doc, (
    'XGBoost is configured with n_estimators=1000, learning_rate=0.05, max_depth=5, '
    'subsample=0.8, colsample_bytree=0.8, and early stopping with patience 50 evaluated '
    'on the validation set. Training halted at iteration 79.'
))
p(doc, (
    'The XGBoost gradient boosting model achieves an out-of-sample R\u00b2 of \u22120.0041 '
    'on the test set (January 2022 \u2013 October 2024), with RMSE of 0.1855, MAE of '
    '0.1084, and Spearman rank correlation of 0.0014 (p-value 0.6047). This is the best '
    'R\u00b2 among all six models, though the improvement over the regression baselines '
    'is marginal.'
))

fig(doc, 'fig_xgb_importance.png',
    'Figure 10. XGBoost feature importances measured by gain (total improvement in the '
    'loss function attributed to each feature across all splits). Features absent from '
    'the figure received zero gain during training.', width=5.0)

h(doc, 'Neural Networks', level=2)
p(doc, (
    'The neural network architecture is a 3-layer multi-layer perceptron (MLP) with '
    'hidden layers of sizes (128, 64, 32), ReLU activations, Adam optimiser '
    '(\u03b7 = 0.001), and L2 weight decay \u03b1 = 0.001 (12,417 trainable parameters '
    'total). Input features are standardised using a StandardScaler fitted on the '
    'training set. Early stopping monitors validation loss with patience 20; '
    'training stopped at epoch 30.'
))
p(doc, (
    'The neural network model achieves an out-of-sample R\u00b2 of \u22120.0059 on the '
    'test set (January 2022 \u2013 October 2024), with RMSE of 0.1857, MAE of 0.1087, '
    'and Spearman rank correlation of \u22120.0027 (p-value 0.3041). The network converges '
    'quickly and its loss curves (Figure 11) show no signs of severe overfitting, suggesting '
    'the regularization and early stopping are working as intended.'
))

fig(doc, 'fig_nn_loss.png',
    'Figure 11. Neural network training and validation loss curves. The dashed vertical '
    'line marks the early-stopping epoch.', width=5.0)

h(doc, 'Reconciliation of Results Based Upon Different Estimation Techniques', level=2)
p(doc, (
    'Table 3 presents the top-10 predicted industry-adjusted return rankings for November '
    '2024 across all six estimation methods. Panel A reports the stock ticker at each rank; '
    'Panel B reports the corresponding predicted industry-adjusted return expressed as a '
    'percentage.'
))
p(doc, (
    'Test-set performance varies across methods: '
    'OLS: R\u00b2 = \u22120.001 | LASSO: R\u00b2 = \u22120.001 | Vanilla Tree: R\u00b2 = \u22120.009 | '
    'Random Forest: R\u00b2 = \u22120.009 | Gradient Boosting: R\u00b2 = \u22120.004 | '
    'Neural Network: R\u00b2 = \u22120.006. '
    'Despite this variation, the rankings show meaningful consistency for the top-ranked '
    'stocks. NAII (Natural Alternatives International Inc.) appears in the top 3 under '
    '2 of 6 models and is our recommended buy for November 2024.'
))

fig(doc, 'fig_sector_predictions.png',
    'Figure 12. Average rank across six models for all 38 Household & Personal Products '
    'stocks in November 2024. Lower average rank indicates a more consistent buy '
    'recommendation. Crimson bars denote the top-3 consensus picks.', width=5.5)

fig(doc, 'fig_metrics_comparison.png',
    'Figure 13. Out-of-sample R\u00b2 and RMSE for each model evaluated on the test set '
    '(January 2022 \u2013 October 2024).', width=5.5)

doc.add_paragraph()
add_reconciliation_table(doc)

# ---- Conclusion ---------------------------------------------------------
h(doc, 'Conclusion', level=1)
p(doc, (
    'We applied six machine learning models to predict industry-adjusted monthly stock '
    'returns for the Household and Personal Products sector and recommend NAII '
    '(Natural Alternatives International Inc.) as the stock to buy in November 2024. '
    'The recommendation is supported by NAII\u2019s appearance in the top-3 under OLS '
    'and XGBoost, its top-8 placement under four of the remaining four models, and its '
    'strong 12-month momentum signal \u2014 the most consistently important predictor '
    'across all six methods.'
))
p(doc, (
    'All six models produce near-zero or slightly negative out-of-sample R\u00b2 values '
    'on the 2022\u20132024 test period, consistent with the well-established empirical '
    'result that individual stock returns are very difficult to predict. Nevertheless, '
    'even weak directional signals can be valuable when aggregated across many stocks, '
    'and the cross-model consensus provides additional confidence in the top-ranked names.'
))
p(doc, (
    'Future work could explore alternative targets (e.g., sector-relative rank instead of '
    'a continuous return), longer prediction horizons, and richer feature sets including '
    'text-based sentiment from earnings calls. Ensemble stacking across the six models '
    'may also improve rank stability.'
))

# ---- References ---------------------------------------------------------
h(doc, 'References', level=1)
p(doc, (
    'Fama, E.F., and K.R. French, 1992. The cross-section of expected stock returns, '
    'Journal of Finance, 47, 427\u2013465.'
))
p(doc, (
    'Jegadeesh, N., and S. Titman, 1993. Returns to buying winners and selling losers: '
    'Implications for stock market efficiency, Journal of Finance, 48, 65\u201391.'
))

# ---- Appendix -----------------------------------------------------------
h(doc, 'Appendix: Description of Each Variable', level=1)

appendix_vars = [
    ('Real Market Capitalization and Its Natural Logarithm',
     'Real market capitalization is the market value of the stock, adjusted to purchasing '
     'power of November 2025 using the Consumer Price Index. There is a substantial body '
     'of evidence that small stocks have historically earned higher returns than large stocks '
     '(for example, Fama and French, 1992). This is most likely because small stocks are '
     'riskier than large stocks. Compared to large-capitalization companies, small '
     'capitalization companies are likely to have less analyst coverage, less chance their '
     'debt is rated by ratings agencies like S&P, Moody\u2019s and Fitch, less institutional '
     'investment and lower liquidity. Market capitalization is compiled from the CRSP database '
     'accessed via WRDS. The natural logarithm of real market capitalization is a '
     'transformation for regression analysis to allow for a more realistic linear relationship '
     'between industry-adjusted stock returns and the market value of equity.'),

    ('Book-to-Market Equity',
     'The book-to-market equity ratio is the ratio of the company\u2019s book value of equity '
     'from the balance sheet to its market capitalization. There is a substantial body of '
     'evidence that stocks with high book-to-market ratios have historically earned higher '
     'returns than stocks with low book-to-market ratios (Fama and French, 1992). Whether '
     'this result is due to mispricing or increased risk exposure is a subject of debate, '
     'but prior to the last two decades there was no disputing the empirical result. '
     'The book-to-market equity ratio was obtained from the Financial Ratios Suite of WRDS.'),

    ('Option Volume/Stock Volume',
     '[Insert text]'),

    ('Momentum12 (12 mth ret ending 1 mth prior to port formation)',
     '[Insert text]'),

    ('Net Profit Margin (Net profit/Sales)',
     '[Insert text]'),

    ('Standard Deviation of Board Members\u2019 Age',
     '[Insert text]'),

    ('Percentage Male Board Members',
     '[Insert text]'),

    ('Systematic Risk',
     '[Insert text]'),

    ('Net Working Capital/Assets',
     '[Insert text]'),

    ('Amihud Liquidity \u00d7 1,000,000',
     '[Insert text]'),

    ('Current Ratio (Current Assets/Current Liabilities)',
     '[Insert text]'),

    ('Natural Logarithm of the Change in Issued Shares',
     '[Insert text]'),

    ('Momentum 11 (11 mth ret ending 1 mth prior to port formation)',
     '[Insert text]'),

    ('Change in Return on Assets',
     '[Insert text]'),

    ('Return on Invested Capital',
     '[Insert text]'),
]

for var_name, var_desc in appendix_vars:
    doc.add_heading(var_name, level=5)
    p(doc, var_desc)

# ---- Save ---------------------------------------------------------------
doc.save(OUTPUT)
print(f'Saved: {OUTPUT}')
