# Sample Draft for style-guided-academic-writer Alignment Testing

This is a small illustrative draft used to exercise
`apply_style_to_draft.py`. Each paragraph deliberately mixes a different
canonical section so the alignment report has something to score against
the powered-descent / optimal-control corpus distilled by
`paper-style-distiller`.

## Introduction

Powered descent guidance is a classic optimal-control problem in which a
spacecraft must transition from a known orbital state to a soft touchdown
while satisfying thrust and glide-slope constraints. However, classical
convex formulations typically assume a constant gravity field, which
leaves a gap when landing on small bodies with strongly varying gravity.
Existing methods for planetary landing still suffer from high sensitivity
to initial state errors and from computational cost that prevents onboard
re-planning.

## Method

The proposed framework consists of three modules: an adaptive gravity
estimator, a sequential convexification kernel, and a constraint-consistent
control allocator. We propose to jointly optimize fuel consumption and
tracking robustness under bounded disturbance. The key idea is to embed
the gravity uncertainty into the convex subproblem as a bounded norm
constraint rather than treat it as an additive noise term.

## Results

On a representative Mars-landing benchmark, our method outperforms a
classical SOCP baseline in terms of fuel consumption and tracking error,
especially under large initial-state dispersion. The tracking error
converges to within 0.3 percent of the prescribed terminal accuracy. As
illustrated in Figure 4, performance gain mainly comes from the
adaptive gravity estimator rather than from parameter scaling.

## Discussion

The proposed scheme demonstrates robust tracking under bounded
disturbance, but it does not cover the case of unmodelled actuator
dynamics. A limitation of this work is that the convexification kernel
relies on a first-order gravity expansion, which may degrade accuracy
near the surface. Future work will incorporate higher-order gravity
terms and validate the framework in a high-fidelity simulation
environment.

## Conclusion

We have presented an adaptive guidance-control co-design that
explicitly aligns decision quality with tracking robustness. The results
suggest that embedding bounded uncertainty into the convex kernel is a
practical path toward reproducible onboard powered-descent guidance.