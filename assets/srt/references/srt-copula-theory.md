# SRT Copula Theory

Guidance: conceptual theory only. In this workflow the Gaussian copula is a
report-only correlation exhibit. The mark comes from the cash-flow DCF in
`Srt dcf.xlsm`; the copula does not set or override the price. Pricing
execution, market calibration, and automation are open for others.

## Mechanism

The one-factor Gaussian copula models each reference name with a latent variable:

```text
X_i = sqrt(rho) * M + sqrt(1 - rho) * Z_i
```

`M` is the common market factor, `Z_i` is idiosyncratic noise, and `rho` is asset
correlation. A name defaults by horizon `t` when `X_i` falls below its PD-implied
threshold. Conditional on `M`, defaults are independent; integrating over `M`
produces the portfolio loss distribution.

## Tranche Directionality

Higher correlation pushes probability into both tails: more very-low-default
states and more very-high-default states.

- Equity / first-loss: benefits from more zero/few-default states. Equity is
  long correlation.
- Senior: suffers when the many-default tail reaches attachment. Senior is
  short correlation.
- Mezzanine: usually less sensitive; sign can depend on subordination and tenor.

## Value Drivers

Explain tranche value through PD/spreads, correlation level and skew, recovery,
spread dispersion, granularity, attachment/detachment, and maturity/WAL. Recovery
and severity remain SRT model inputs; the copula is only a conceptual exhibit.

## Base, Compound, And Smile

Compound correlation is the single `rho` that matches one tranche price. Different
tranches imply different compound correlations. Base correlation maps each
detachment point and is more useful for interpolation. The resulting smile/skew
shows the single Gaussian copula is a diagnostic, not a perfect pricing model.

## Report Language

Use language like:

```text
The DCF mark does not consume the copula. The copula exhibit is a report-only
correlation sensitivity: higher default correlation benefits the equity tranche
but hurts senior tranches, all else equal.
```

Hard boundary: do not present copula output as a live mark or approval basis.
