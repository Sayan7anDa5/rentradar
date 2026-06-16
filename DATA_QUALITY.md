# Data Quality Report — RentRadar

Handling real, messy rental data honestly was a core part of this project. This document records every data-quality issue encountered and the decision made for each. Transparency about cleaning decisions is essential for a trustworthy analysis.

## Source selection

The first dataset considered had a `price` column but **no clearly labeled rent field**, plus an empty `priceSqFt` column. On inspection, `price` was contaminated: values ranged from ₹3,000 (clearly monthly rent) up to ₹30,00,000 (clearly sale prices), with blocks of suspicious repeating values (e.g. ₹4,10,202 appearing four times) indicating junk data. Because rent and sale prices could not be reliably separated, this source was rejected.

The final dataset was selected specifically because it has a **labeled `rent` column**, sane value ranges, and no missing values across key fields.

## Final dataset overview

- **~7,700 rows** across 5 cities: Mumbai, New Delhi, Bangalore, Pune, Nagpur
- **Key fields:** house_type, locality, city, area, beds, bathrooms, balconies, furnishing, area_rate, rent
- **Missing values:** none in the columns used for analysis

## Cleaning decisions

### 1. Outlier removal — high end
A small number of listings had rents above ₹5 lakh/month, up to ₹27 lakh. Inspection showed these were a thin tail of ultra-luxury or mislabeled listings, not representative of the typical rental market.

**Decision:** capped rent at ₹3,00,000, removing 153 rows (~2% of data). These were dropped not because all were errors, but because rare ultra-luxury rentals would skew a model intended for typical flats.

### 2. Outlier check — low end
The smallest rents (₹1,000–₹3,000) were inspected and judged to be legitimate — cheap single rooms exist in this range, particularly in smaller cities. No low-end rows were removed.

### 3. Sparse categories — bedroom count
Bedroom counts of 5+ had very few samples (6-bed: 6 flats, 7-bed: 3, 8-bed: 3, 10-bed: 6) and produced unreliable, non-monotonic averages (e.g. 6-bed appeared cheaper than 4-bed).

**Decision:** restricted bedroom-based analysis and statistical tests to **1–4 BHK**, where each category has hundreds to thousands of samples.

### 4. High cardinality — locality
The `locality` field contains hundreds of distinct neighborhoods. One-hot encoding for the model produced 1,762 feature columns, some backed by only 1–2 listings.

**Decision:** retained all localities for the current model (it still beats baseline by 33%), but flagged grouping of sparse localities as a future improvement to reduce dimensionality.

## Known limitations

- The model is least accurate on high-end rentals (₹1 lakh+) due to their sparsity.
- Statistical findings establish association, not causation; bedroom and city effects partly reflect flat size and location.
- Analysis reflects the snapshot in the source data and is not live/real-time.
