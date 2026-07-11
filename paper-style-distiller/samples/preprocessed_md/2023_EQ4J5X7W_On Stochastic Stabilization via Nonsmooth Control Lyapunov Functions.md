---
title: On Stochastic Stabilization via Nonsmooth Control Lyapunov Functions
publication: IEEE Transactions on Automatic Control
date: 2023-08-00 8/2023
key: EQ4J5X7W
---

Abstract—Control Lyapunov function is a central tool in stabilization. It generalizes an abstract energy function – a Lyapunov function – to the case of controlled systems. It is a known fact that most control Lyapunov functions are nonsmooth – so is the case in non-holonomic systems, like wheeled robots and cars. Frameworks for stabilization using non-smooth control Lyapunov functions exist, like Dini aiming and steepest descent. This work generalizes the related results to the stochastic case. As the groundwork, sampled control scheme is chosen in which control actions are computed at discrete moments in time using discrete measurements of the system state. In such a setup, special attention should be paid to the sample-to-sample behavior of the control Lyapunov function. A particular challenge here is a random noise acting on the system. The central result of this work is a theorem that states, roughly, that if there is a, generally non-smooth, control Lyapunov function, the given stochastic dynamical system can be practically stabilized in the sample-and-hold mode meaning that the control actions are held constant within sampling time steps. A particular control method chosen is based on Moreau-Yosida regularization, in other words, inf-convolution of the control Lyapunov function, but the overall framework is extendable to further control schemes. It is assumed that the system noise be bounded almost surely, although the case of unbounded noise is brieﬂy addressed.
## I. INTRODUCTION
arXiv:2205.13409v3  [math.OC]  7 Nov 2022 Stochastic stability theory can be traced back to the works of Khasminskii [1], Kushner [2], Mao [3] and Deng et al. [4] who extended the classical results and translated them into the language of K-functions of Khalil [5], convenient for control engineers. Stochastic stability analyses were applied to various types of systems including discrete systems [6], cascaded systems [7], delayed systems [8], systems with input saturation [9], systems with state-dependent switching [10], nonlinear stochastic dynamic systems with singular perturbations [11], hybrid systems [12], hybrid retarded systems [13], linear systems with randomly jumping parameters [14] etc. Practical stochastic stability was addressed in, e. g., [15], [16], [17].
When it comes to stochastic stabilization, most of the existing works assume continuous application of the control, whereas sampled control schemes were considered in rather speciﬁc contexts, e. g., based on approximate discrete-time models [18], [19] or in the event-triggered mode [20]. Stabilization of stochastic logical systems [21], [22] is yet another example of stochastic stabilization performed in discrete time, however the latter setting also implies a ﬁnite state-space, which is not suitable for certain applications, e. g., in robotics.
The authors are with Skolkovo of Science and Technology, emails: {p.osinenko,grigory.yaremenko,g.malaniya} @skoltech.ru. The experimental case study of this work was supported by Dmitry Dobriborsci and Ksenia Makarova.
The importance of sampled control frameworks is dictated by two facts. First, most modern controllers are implemented on digital media whence control actions are naturally computed at discrete moments in time, and based on discrete measurement of the state, rather than continuous. Second, the need for sampled controls is motivated by the fact that the majority of dynamical systems are not even stabilizable by means of feedback laws that depend continuously on the state [23], [24], [25], [26], [27], [28], [29]. There is an intimate connection between discontinuous feedback controls and nonsmooth control Lyapunov functions [30]. In particular, nonexistence of a smooth control Lyapunov function leads to non-existence of a continuous stabilizing feedback law. It should be noted here that not only do control Lyapunov functions appear mostly non-smooth, numerical routines for their calculation commonly produce non-smooth functions – for particular methods, refer, e. g., to [31], [32], [33], [34].
A major problem that arises under discontinuous feedback laws is deﬁning the system trajectory. But even resorting to such generalized notions of solutions as of Filippov does not remedy the situation. It was the prominent work by Clarke, Ledyaev, Sontag and Subbotin [25] which derived a general framework for stabilization by means of non-smooth control Lyapunov functions by means of sampled controls.
Stabilization here was meant as practical stabilization, i. e., the system state could be stabilized into any desirable vicinity of the equilibrium, provided that the sampling time be sufﬁciently small. In turn, the control law computation was based on the Moreau-Yosida regularization, in other words, inf-convolution of the control Lyapunov function involved. Further methods are applicable – for surveys, refer, e. g., to [29], [35].
A brief remark should be made on the case of smooth control Lyapunov functions. Here, one can exploit universal formulas for stabilizing controls [36], [37]. Their generalizations to the stochastic case exist. For instance, Florchinger [38] suggested constructions of stochastically stabilizing controls via Lie theory methods. Smooth control Lyapunov functions were also assumed in the stochastic stabilization work of Deng et al. [4] and Gao et al. [20], which addressed event-triggered digital implementation of a given feedback law that stabilizes the system in second moment. In the present work, in contrast, non-smooth control Lyapunov functions are considered.
There is no extension of the Clarke’s general framework for stabilization to the case of stochastic systems. Whereas Deng et al. [4] considered the continuous control case, the work [39] extended on these results in the case of sampled controls. However, the control Lyapunov function involved was smooth, whereas the non-smooth case was tackled only brieﬂy,

˘h Lower convex envelope of function h ˘h = sup{g | g is convex, g(x) ≤f(x)} “h Upper concave envelope of function h “h = inf{g | g is concave, g(x) ≥f(x)} co(A) Closed convex hull of set A Dvf(x) Lower directional Dini derivative [25] of f(·) at x in direction v ◦lh(·) l-fold iteration of function h(·), like so h(h(h(. . . ))) | {z } l times IA(·) Indicator function of set A a · b a multiplied by b, where a and b are scalars ⌈x⌉ x rounded to the closest greater or equal integer ⌊x⌋ x rounded to the closest less or equal integer a mod b remainder of a when divided by b Structure of the paper. All proofs and auxiliary lemmas are placed in the appendix. The main body contains the technical preliminaries; the main theorem on stochastic stabilization by means of non-smooth control Lyapunov functions under almost surely bounded driving noise; the discussion of the case of unbounded driving noise; the demonstrative experimental study.
## II. PRELIMINARIES
The aim of this work is to address stabilization of stochastic control systems of the class dXt = f(Xt, Ut) dt + σ(Xt, Ut)Zt dt, (1) speciﬁcally, under bounded noise. The current work elaborates on the matter of stochastic stabilization via sampled controls computed from non-smooth control Lyapunov functions to a full technical extent.
The engineering background of the proposed framework for stochastic stabilization is motivated by the two facts. First, as also mentioned above, most modern controllers are realized in digital devices that naturally lead to a sampled control scheme where control actions are computed at discrete, usually evenly distributed, moments in time upon receiving state measurements at discrete moments in time as well. In the presented work, the control law is treated explicitly in the sample-andhold mode, whereas the underlying system dynamics model is considered as time-continuous, to be precise, in the form of a stochastic differential equation. Second, the formalism of stochastic differential equations allows accounting for random uncertainty that may be related to model imperfection, system, measurement and/or actuator noise etc. Effects of noise magnitude and sampling time choice are demonstrated in an experimental case study with a mobile robot in Section V.
Contribution. Informally, the contribution of the current work is summarized as follows. In Theorem 1 it is shown that if a given non-linear stochastic control system with bounded noise has a, generally non-smooth, control Lyapunov function, a sample-and-hold policy can be produced that stabilizes the system’s equilibrium. The theorem explicitly provides the aforementioned policy and estimates the quality of resulting stabilization for a given conﬁguration of noise, sampling rate and computation error. Unlike previously mentioned results in stochastic stabilization, Theorem 1 concerns the case of a potentially non-smooth control-Lyapunov function and at the same time accounts for imperfections peculiar to a digital controller, namely control update latency and computation error.
Table of notation where {Xt}t, {Ut}t are the state and, respectively, control stochastic processes, X-, respectively, U-valued; f : X × U → Rn, σ : X × U →Rn×d; {Zt}t is a d-dimensional random process that is measurable with respect to t. The technical goal is to study stabilization of (1) by Markov control policies in sampled mode. “Sampled mode" here means that the controller computes control actions based on measurements of state at discrete equidistant moments in time and keeps these actions constant between the said moments in time. This is stated mathematically precise in Section III.
Now, proceed to the necessary deﬁnitions for stability.
Consider a general stochastic system dXt = f(Xt, t) dt + σ(Xt, t) dWt, (2) where dWt is a placeholder for either Zt dt or dBt with {Bt}t being a standard Brownian motion. The latter case will be used in the discussion on the unbounded noise case of Section IV.
Observe that if we were to apply a concrete policy Vt to the control system (1) by asserting Ut := Vt, we would get a system of the kind (2) provided the driving noise is of the form Zt dt. Now, we are ready to state the key deﬁnitions for stability.
Deﬁnition 1 (Semi-asymptotic stability in probability): The origin of a stochastic system (2) is said to be semiX State space Rn, where n ∈N U Control set, which is a subset of Rm, where m ∈N R+ [0, +∞) E [·] Expected value V [·] Variance P [·] Probability measure R+ [0, +∞) ∥·∥ Eucledian norm ∥·∥2 ∥·∥op Operator norm K∞ Class of kappa-inﬁnity functions [5] Closed ball of radius R centered at the origin Liph(R) Lipschitz constant of h(·) in BR a ∧b min(a, b) ⟨·, ·⟩ Scalar product tr(·) Matrix trace N(x, y) Normal distribution with mean x and variance y ¯ N(x, y, z) Truncated normal distribution with mean x, variance y and maximal deviation z ∇· Gradient as a row-vector

asymptotically stable in probability in R > 0 until r ≥0 if: ˜r(R, ¯Z, λ, δ, η) := α−1  η+ x0 ∈BR =⇒P  lim sup t→∞∥Xt∥≤r  = 1.
(3) p 2α2(R) +  2LipL   R+ λ + λ p 2α2(R)  λ2+ 2α2(R)  Lipf   R + λ p (8) + δ 2Lipf(y(R; δ))( ¯f(y(R; δ)) + ¯σ(y(R; δ)) ¯Z)+ + ¯σ(y(R; δ)) ¯Z  + δ( ¯f(y(R; δ)) + ¯σ(y(R; δ)) ¯Z)2  + 2λ2 + λ p 2α2(R), where for each r ≥0 we have ¯f(r) ≥∥f(x, u)∥, ∀x ∈Br, u ∈U, ¯σ(r) ≥∥σ(x, u)∥op , ∀x ∈Br, u ∈U, ∥f(x, u) −f(y, u)∥≤Lipf(r) ∥x −y∥, ∀x, y ∈Br, u ∈U, This notion is similar to (almost sure) local asymptotic stability. The only difference is that with asymptotic stability the attractor is a single point – the origin, whereas with semiasymptotic stability the attractor is a ball centered at the origin.
Thus r is the radius of the attractor and R is the radius of the basin of attraction. If a stochastic system is said to be semiasymptotically stable, this kind of attraction will occur almost surely. The need to introduce this notion arises from how adding noise to an asymptotically stable deterministic system impacts the said system’s stability. Unless the magnitude of added noise is too large, the system will generally preserve its attractive properties within some basin of attraction (BR), but the attraction will cease in some small neighborhood of the origin (Br).
∥L(x) −L(y)∥≤LipL(r) ∥x −y∥, ∀x, y ∈Br, LipL(·), Lipf(·), ¯f(·), ¯σ(·) – are non-decreasing and Deﬁnition 2 (Semi-asymptotic stability on average): The origin of a stochastic system (2) is said to be semiasymptotically stable on average in R > 0 until r ≥0: x0 ∈BR =⇒lim sup t→∞E [∥Xt∥] ≤r.
(4) upper-semicontinuous functions.
(9) For brevity, we denote ˆr¯µ, ¯ Z,δ,η(r) := ˆr(r, ¯Z, λ, δ, η).
We deﬁne Lλ (·) as the inﬁmal convolution with a parameter λ > 0 of L(·) as follows: !
, L(y) + ∥y −x∥2 Lλ (x) := inf y∈X 2λ2 (10) λα1(∥x∥) ≤Lλ (x) ≤λα2(∥x∥), λα1,λ α2 ∈K∞.
The latter deﬁnition is analogous to Deﬁnition 1, but describes stability in mean. Here the expected value of the state is guaranteed to get arbitrarily close to Br and stay there permanently, provided that the initial state was within BR.
The following deﬁnitions are required to state and prove Theorem 1, which is the central result of this work.
Deﬁnition 3: A non-negative locally Lipschitz-continuous function ρ : R+ →R+ is called a radial growth bound of system (14) iff Here, we used the upper left index λ for notation purposes to stress the relation to the inﬁmal convolution with a parameter λ. One way to obtain λα1(·) and λα2(·) is to compute the inﬁmal convolutions of α1(·) and α2(·).
ρ(∥x∥) ∥x∥≥xT f(x, u) + σT (x, u)x ¯Z, ∀u ∈U.
(5) Deﬁnition 7: A function ˆr : R6 + →R is called a mean attraction function of (1) if: ˆr(r, ¯µ, ˜σ, λ, δ, η) := ˘α−1  η+ + p 2α2(r)  2λLipL(r + λ p 2α2(r))Lipf(r+ Deﬁnition 4: A two-variable function y(R; t) is called a radial forecast of (1) iff there exists such a radial growth bound ρ that for each R ≥0, y(R; ·) equals to the (local) solution of: ( ˙y = ρ(y), + λ p 2α2(r)) + δ 2aLipf(r)( ¯f(r)+ y(0) = R.
(6) (11) + ¯σ(r)¯µ) + ¯σ(r)¯µ  + λ + 2δ Remark 1: Note that for a strictly positive radial growth bound ρ, y(R; t) = y(0; t + y−1(0; R)), λ2 (( ¯f(r) + ¯σ(r) ¯Z)2 + ˜σ2¯σ(r)2)  + + λ p 2α2(r), where the inversion y−1 is with respect to the second argument.
Deﬁnition 5: A function L is called a control Lyapunov function for (1) if it satisﬁes: ∀x ∈X inf ν∈co(f(x,U)) DνL(x) ≤−α3(∥x∥), α1(∥x∥) ≤L(x) ≤α2(∥x∥), α1, α2, α3 ∈K∞.
(7) where ˘α3(·) is the lower convex envelope of α3 on [0, r]. For brevity, let us denote ˆr¯µ,˜σ,λ,δ,η(r) := ˆr(r, ¯µ, ˜σ, λ, δ, η).
Naturally, an attraction function may only exist if L(x) and f(x, u) are locally Lipschitz continuous w.r.t. x. Also note that if LipL(·), Lipf(·), ¯f(·), ¯σ(·) fail to be non-decreasing, it would be easy to construct alternative bounds that are not only non-decreasing, but are in fact sharper than the original ones (i.e. by evaluating ˆf(r) = inf r≤r′ ¯f(r′)).
Deﬁnition 6: Let there be a control Lyapunov function L for (1) and let yR be a radial forecast of (1), then a partial function ˜r : R5 + →R is called an attraction function of (1) if: In Lemma 3 it is proven that both the attraction and mean attraction functions exist whenever bounds in (9) exist.

improbable. Therefore, an adequate reduction of support may in fact make the noise model more accurate.
There are also a number of common noise models that imply this kind of boundedness [40], in particular: • The Doering-Cai-Lin (DCL) noise r Remark 2: The domain of deﬁnition of ˜r(·, ¯Z, λ, δ, η) depends on δ, however for each R, ˜r(R, ¯Z, λ, δ, η) exists, provided that δ is sufﬁciently small. Unlike ˜r, the domain of deﬁnition of ˆr is not restricted.
Additionally we assume that some bounds for moments of ∥Zt∥are known, in particular, there exist numbers ¯µ, ˜σ such that: ∀t ¯µ ≥E [∥Zt∥] , dZt = −1 θZt dt + 1−Z2 t θ(γ+1) dBt, (16) ∀t ˜σ2 ≥V [∥Zt∥] .
(12) with parameters γ > −1, θ > 0; • The Tsallis-Stariolo-Borland (TSB) noise
## III. MAIN THEOREM
1−q dZt = −1 θ dBt, (17) θ Zt 1−Z2 t dt + q with θ > 0, q < 1 parameters; • Kessler–Sørensen (KS) noise dZt = −ϑ πθ tan   π 2 Zt  dt + π√ θ(γ+1) dBt, (18) with θ > 0, γ ≥0, ϑ = 2γ+1 γ+1 parameters.
Sample-and-hold mode introduces a latency between a change in the systems state and the controller’s response to that change. Considering such a setting yields a practical advantage: unlike feedback of the kind Ut = µ(Xt), sampleand-hold mode accurately describes policies that digital controllers can implement. Furthermore, it provides other beneﬁts.
A system produced by asserting Ut := µ(Xt) may have no solutions, e. g., ( dXt = Ut dt, X0 = 1, Ut := 1 −2IR+(Xt) (13) The following theorem demonstrates how a control Lyapunov function can be used to stabilize (14) in sampleand-hold mode. The theorem explicitly provides a stabilizing policy µ(x) for a given control Lyapunov function L(x). The theorem also provides estimates for the quality of resulting attraction.
Theorem 1: Let the following assumptions hold for system (14): (A1) Bounds as per (9) exist.
(A2) There exists a control Lyapunov function L(·): ∀x ∈X inf v∈co(f(x,U)) DvL(x) ≤−α3(∥x∥), (19) ∀x ∈X α1(∥x∥) ≤L(x) ≤α2(∥x∥), α1, α2, α3 ∈K∞, L X →R+.
fails to admit a solution. Such issues cannot occur in sampleand hold mode, unless f(·, Ut) or σ(·, Ut) is dicontinuous. It is fairly intuitive that a control Lyapunov function constructed for a deterministic system will partially preserve its properties if some noise were to be added, unless the magnitude of that noise is too large. However, naturally, the existence of a control Lyapunov function generally speaking does not imply much about stabilizability of systems described by (1), since the noise term σ(Xt, Ut)Zt dt can just entirely overhwelm the deterministic dynamics of the system. A way to remedy this problems is to consider bounded noise models.
Now, consider a special case of (1):         (14) (A3) The policy µ(x) is chosen so as to satisfy x −λx λ2 , f(λx, µ(x)) ≤ dXt = f(Xt, Ut) dt + σ(Xt, Ut)Zt dt, X0 = x0, f : X × U →Rn, σ : X × U →Rn×d, Zt is a measurable random process w.r.t. t, ∀t ∈R ∥Zt∥≤¯Z, (bounded noise) Ut := µ(Xt−(t mod δ)), (sample and hold policy)        x −λx inf u∈U λ2 , f(λx, u) + η, where λx := arg min x∗∈X (2λ2L(x∗) + ∥x∗−x∥), λ > 0.
(20) (A4) ∃R > 0 ∃i ∈N y   ◦i˜r ¯ Z,λ,δ,η(R∗); δ  ≤R.
(21) where R∗:= α−1 1 (α2(R)).
where dt implies Lebesgue integration.
We obtained the above system from (1) by assuming bounded noise and asserting that a sample-and-hold policy is in place.
On the ﬁrst glance it may seem like ∥Zt∥≤¯Z imposes a signiﬁcant restriction on physical objects that this model can represent, since even Gaussian white noise fails to be described by it. However, upon a closer inspection it becomes clear that this theoretical loss of generality does not have much of a negative impact in practice. Note that noise represented by the following model can very closely mimic Brownian noise: Then a unique global Caratheodory solution almost surely exists and the following can be claimed: Zt dt = ξ⌈λt⌉dt, where ξi ∼¯ N(0, σ2, ¯Z), {ξi} are independent (15) (C1) lim l→∞rl = r∗exists, where rl := ˜r(rl−1, ¯Z, λ, δ, η), r0 = R.
(22) Indeed, for real-world objects some values of noise are large enough to be considered impossible as opposed to merely

to determine a substantially smaller radius in which the mean state will stay.
(C2) The origin of the system is semi-asymptotically stable in probability in R until r, where r := λα−1 1 (λα2(y(r∗; δ))).
(23) (C3) The origin of the system is semi-asymptotically stable on average in R until ¯r, where ¯r := λ˘α−1 1 (λ“α2(ˆr(r, ¯µ, ˜σ, λ, δ, η)+ • Tuning. The attraction function can be used to discover values of parameters that ensure desired quality of stabilization. If we were to consider r and ¯r as functions of ( ¯Z, δ, η) and (¯µ, ˜σ, δ, η) respectively, then both of those functions would be strictly increasing with respect to each one of their arguments. Thus suitable values of parameters can be identiﬁed through a simple grid search.
+ ( ¯f(r) + ¯σ(r)¯µ)δ)), (24) and λ˘α, λ“α2 are envelopes over [0, r].
Corollary 1: (C2) and (C3) would hold even if r∗were to be replaced with any rl. Therefore there is no need to compute r∗ precisely, since the theorem holds for any of its approximations rl.
• Analysis of robustness. Given a Lyapunov function with a corresponding policy for a deterministic control system, one could investigate its robustness by inspecting how introducing noise, approximation error and response latency affects the quality of stabilization. This way, evaluating r and ¯r for various sets of parameters will show in which settings this controller performs sufﬁciently well. The latter will reveal suitable implementations and environments, for which the system is guaranteed to function as intended.
Remark 3: In the deterministic case, the analogous theorem would imply that by selecting a sufﬁciently small δ > 0 we could make the attractor arbitrarily small and the basin of attraction arbitrarily large. All of the claims in (C1), (C2) and (C3) would hold with ¯Z substituted for 0. Furthermore, deterministic counterparts of this theorem can be found in [25] and its generalization that accounted for computational uncertainty [41]. The related result under system and measurement uncertainty in deterministic form was further addressed in [42]. A particular difference to the latter work is that also convergence in mean in the sense of Deﬁnition 2 is shown in Theorem 1.
Remark 4: The assumption (A3) means that µ(x) is chosen by minimizing D x−λx 2λ2 , f(λx, µ(x)) E and the minimization error is at most η. This kind of an approximate minimizer will always exist. Furthermore the above theorem accounts for the fact that in practice we almost never have the luxury of using an exact minimizer.
• Safe reinforcement learning. If semi-asymptotic stability has been inferred over R, then any controller that implements µ(x) when near R is guaranteed to stay within λα−1 1 (λα2(R)) regardless of the policy used in other areas of the state space. This allows to utilize numerical optimization of reinforcement learning, while maintaining formal guarantees of Lyapunov theory (see, e. g., [43]).
Remark 6: Note that there are no extra restrictions on f(x, ·), σ(x, ·) and U, other than the ones imposed by (A1).
For the above theorem to hold f(x, ·), σ(x, ·) and U do not even have to be measurable. By using approximate minimizers, we circumvent having to rely on the extreme value theorem.
In the next section, we brieﬂy discuss the case when the system trajectory is an Itô process driven by a Brownian motion hence unbounded noise.
## IV. ITÔ PROCESSES
Remark 5: It may seem that (A4) imposes restrictions on the systems, to which the theorem is applicable, however it can be derived that for sufﬁciently small ¯Z, δ and η this assumption will hold. In other words, if (A4) does not hold, then that essentially means that noise magnitude, sampling time and optimization errors are too large to infer stability in BR.
Corollary 2: For arbitrary 0 < r < R, system (14) is semiasymptotically stable in probability in R until r, provided that ¯Z, δ and η are sufﬁciently small.
The case of unbounded noise can too be considered if assumptions of a different kind were to be made. Consider the following Itô drift-diffusion process, driven by standard Brownian motion Bt: ( dXt = f(Xt, Ut) dt + σ(Xt, Ut) dBt, Ut := µ(Xt−(t mod δ)), (sample and hold policy) (25) The generator of the stochastic differential equation of (25), for a smooth function L, is deﬁned as follows: AµL(x) =∇Lf(x, µ(x))+ + 1 2tr   (σ(x, µ(x)))⊤∇2L(x)σ(x, µ(x))  , (26) Corollary 3: For arbitrary 0 < r < R, system (14) is semiasymptotically stable on average in R until r, provided that E h ∥Zt∥2i , δ and η are sufﬁciently small.
Once an attraction function is obtained for a system of the kind (14), it can be used to inspect the inﬂuence of noise, latency and optimization error on stability. This implies a number of possible applications where ∇L is the gradient vector and ∇2L is the Hessian, i. e., the matrix of second-order derivatives. We deﬁne the operator Γµ R as follows: Γµ RL := ¯f µ R   Lip∇L (R) ¯f µ R+ + bRLipf(R) + ¯σRb′ RLipσ(R) + 1 2(¯σµ R)2LipR   ∇2L   .
(27) • Veriﬁcation. Known values of noise, latency and optimization error can be used to infer (average) semiasymptotic stability for given radii, producing a formal guarantee. Computing r = λα−1 1 (λα2(y(rl; δ))) for some l will yield a radius in which the state will remain permanently once it gets there. Likewise, one could compute ¯r = λ˘α−1 1 (λ“α2(ˆr(r, ¯µ, ˜σ, λ, δ, η) + ( ¯f(r) + ¯σ(r)¯µ)δ))

Proof: See [39, Theorem 1].
Corollary 4: Suppose that (30) has the form where ¯f µ R := sup x∈BR ∥f(x, µ(x))∥, ¯σµ R := sup x∈BR ∥σ(x, µ(x))∥, ∀x ∇L(x)f(x, µ(x)) ≤−α3(∥x∥).
(32) ∇2L(x) .
bR := sup x∈BR ∥∇L(x)∥, b′ R := sup x∈BR In other words, (L, µ) is a Lyapunov pair for the noiseless system ˙x = f(x, u). If it holds that (28) Now that we can no longer rely on the boundedness of noise, to assert stability we have to demand the existence of a stronger version of the classical Lyapunov function.
∃˜r > 0 ∀x /∈B˜r α3(∥x∥) ≥1 σ⊤(x, µ(x))∇2L(x)σ(x, µ(x)) , (33) Deﬁnition 8 (Stochastic Lyapunov pair): A stochastic Lyapunov pair (L, µ) is for the system (25) a pair of functions if: L ∈C2; there exist ¯α1, ¯α2 > 0, α3 ∈K∞with α3( p ∥x∥) convex; there exists α4 ∈K∞∀R Γµ RL ≤α4(R) s. t. α4( √ R) is concave; (monotone condition cf. [44], [19], [18]) there exists K > 0, Kµ s. t. ∀x, µ(x) ∈BKµ and ∀x, u ∈BKµ x⊤f(x, u) + 1 then assuming Ut := µ(Xt−(t mod δ)), for each R there exists a sufﬁciently small δ > 0, that (25) is semi-asymptotically stable on average in ρ over R In particular, (33) holds if ∥σ∥is uniformly bounded and ∇2L(x) has a growth rate lower than that of α3 everywhere except for a vicinity of the origin.
2 ∥σ(x, u)∥2 ≤K(1 + ∥x∥2); the following properties hold: ∀x ¯α1 ∥x∥2 ≤L(x) ≤¯α2 ∥x∥2 , (29) ∀x AµL(x) ≤−α3(∥x∥) + ¯Σ, ¯Σ > 0.
(30) Remark 7: The number ¯Σ > 0 in Deﬁnition 8 is related to the noise and differentiates the stochastic case from a deterministic one, which typically possesses a decay condition of the kind ⟨∇L(x), f(x, µ(x))⟩≤−α3(∥x∥).
Remark 9: The growth condition (33) in Corollary 4 may be justiﬁed as follows. Roughly speaking, taking derivatives decreases the growth rate. That is, one would normally expect that, outside some vicinity of the origin, ∇2L(x) grows slower than ∥∇L(x)∥. Such is the case when L is, e. g., polynomial. The diffusion function σ describes the noise magniﬁcation depending on the state and control action. It may be justiﬁed in some applications to assume this term to be bounded uniformly in x, u. All in all, Corollary 4 gives a particular hint on transferring a Lyapunov pair from a nominal, noiseless, to a noisy system.
## V. EXPERIMENTAL STUDY.
Remark 8: In general, for a function ϕ, the Jensen’s gap, i. e., E [ϕ(X)] −ϕ(E [X]) can be arbitrarily large. To relate various expected values in the analysis of Theorem 2, the Jensen’s inequality has to be utilized, which motivates the stated conditions. Notice, e. g., [45, Lemma 2.1] also used quadratic bounding functions of L. A condition AµL(x) = −cL+¯Σ, c > 0 (cf. [4, Theorem 4.1]) also ﬁts the assumptions since −cL ≤−c¯α1 ∥x∥2 and α3 is thus effectively c¯α1 ∥x∥2 and so α3( p ∥x∥) is convex. The function α4( p An experimental study of mobile robot parking was performed to demonstrate the effects of the developed theory (see Fig. 1). Experiments were performed under practical truncated white Gaussian noise of varying power introduced into the system.
∥x∥) being concave is satisﬁed if, e. g., L is quadratic, f(·, µ(·)) is Lipschitz and of linear growth, σ(·, µ(·)) is Lipschitz and bounded. This condition may be seen as restrictive, although, e. g., linear growth is often assumed in stochastic stabilization in mean (see, for instance, [46], [47], [48], [18], [19]). The monotone condition is in the style of [44] and is weaker than in related works on sampled stochastic stabilization (see, e. g., [19], [18]), whereas it should be noted that universal formulas with bounded controls are known [37]. Furthermore, this condition will secure global existence of strong solutions [44], which is unavoidable in case of S&H mode, and this is in contrast to the “standard” Lyapunov techniques in stochastic systems [1]. The reason is that, in the latter, decay of the subject Lyapunov function is ensured for all times, whereas in the herein considered case, there are necessarily time intervals in which the said decay cannot be guaranteed.
Fig. 1. Effects of sampling time and noise power on practical stabilization of a mobile robot. Top left: fragment of the test bed. Top right: test robot TurtleBot 3.
Theorem 2 (Itô process semi-asymp. stab. on average): Consider a stochastic system (25). Suppose there exists a stochastic Lyapunov pair (L, µ) and Ut = µ(Xt−(t mod δ)).
Then for each R > 0, ¯α3 > 0 there exists a sufﬁciently small δ > 0, that (25) is semi-asymptotically stable on average in R until ρ, where We used the above described method of inf-convolutions and the model ( ˙x1, ˙x2, ˙x3)⊤= (u1, u2, x1u2 −x2u1)⊤with a corresponding non-smooth control Lyapunov function L(x) = x2 1 + x2 2 + 2x2 3 −2|x3| p ρ = inf ρ′ { inf r′≥ r x2 1 + x2 2 [49], which is global and the control actions are conﬁned to [−1, 1]2. Notice that for a ﬁxed ¯α1 2¯α2 ρ′ (α3(r′) −¯Σ) ≥¯α3}.
(31)

noise power parameter, the decrease of the sampling time has limited effect due to the noise.
Proof: This follows from Lemma 1 and Lemma 2, since the attraction function is explicitly constructed from a radial forecast in (8).
3) Bounding properties of radial forecast: Lemma 4: Let t1 > 0, then the inequality ∥Xt1∥≤R implies that ∀t2 ≥t1 t2 ∈dom (y(R; ·)) =⇒ ∥Xt2∥≤y(R; t2), (37) where dom denotes the domain of a function.
Proof: Observe that ∥Xt∥d ∥Xt∥= Xt · dXt = (38) (XT t f(Xt, Ut) + XT t σ(Xt, Ut)Zt) dt ≤ ρ(∥Xt∥) ∥Xt∥dt.
Remark 10: Theorem 1 bears a fairly general character as physical systems are most adequately described by stochastic differential equations and controllers are commonly implemented in a sampled mode. Further examples of such settings include, e. g., mechanical and robotic systems driven by digital micro-controllers, stock market bots with time-discrete decisions to buy or sell, medical devices like insulin pumps with scheduled administration, greenhouse with digital climate control etc. The nature of noise in such examples can be interpreted in various ways, e. g., as unmodelled mechanical disturbance, say, due to friction or wear; noisy sensors; random ﬂuctuation of stock prices; ﬂuctuations in homeostasis; ﬂuctuations in plant respiration etc.
Thus, d ∥Xt∥≤ρ(∥Xt∥) dt, dy(t) = ρ(y(t)) dt,
## VI. CONCLUSION
Xt1 ≤y(t1).
(39) Let h(t) := ∥Xt∥−y(t). Now assume that h(t2) > 0, then ∃c ∈[t1, t2) h(c) = 0.
(40) This work was concerned with stabilization of nonlinear dynamical systems in the sample-and-hold framework. A novel theoretical result was derived that enables synthesis, veriﬁcation, tuning and robustness testing of digital stabilizers for stochastic systems with bounded noise.
## APPENDIX
Now, let d := sup{a ∈[t1, t2] | h(a) ≤0}. Obviously, d ≥c and h(d) = 0. By subtracting dy(t) = ρ(y(t)) dt from d ∥Xt∥≤ρ(∥Xt∥) dt we get
## A. Preliminaries
∀t ∈[d, t2] h(t) ≤h(d) + Z t d ρ(∥Xτ∥) −ρ(y(τ)) dτ = Z t d ρ(∥Xτ∥) −ρ(y(τ)) dτ.
1) Existence of a radial growth bound: Lemma 1: Under assumption (A1) there exists a radial growth bound ρ(·).
Proof: Observe that xT f(x, u) + σT (x, u)x ¯Z ≤ (41) Now, let ¯X := sup t∈[t1,t2] ∥Xt∥. Note that since y(R; ·) is non∥x∥∥f(x, u)∥+ ∥σ(x, u)∥∥x∥¯Z ≤ (34) decreasing and X(t2) > y(t2), we have ∥x∥( ¯f(∥x∥) + ¯σ(∥x∥) ¯Z).
∀t ∈[t1, t2] y(τ) ≤¯X.
(42) Therefore, ∀t ∈[d, t2] Z t d ρ(∥Xτ∥) −ρ(y(τ)) dτ ≤ Z t d Lipρ( ¯X)|h(τ)| dτ = Z t d Lipρ( ¯X)h(τ) dτ.
(43) Let ρ−(∥x∥) := ¯f(∥x∥) + ¯σ(∥x∥) ¯Z. Since the latter function is upper semi-continuous, by the extreme value theorem it has a maximum over any compact set. Now, we construct a locally Lipschitz continuous function ρ(·) that bounds ρ−(·) from above as follows: ρ(y) =(1 −y mod 1) max ˜y∈[⌊y⌋,⌊y⌋+1] ρ−(˜y) + Combining this with (41) gives (y mod 1) max ˜y∈[⌊y⌋+1,⌊y⌋+2] ρ−(˜y).
(35) ∀t ∈[d, t2] h(t) ≤ Z t d Lipρ( ¯X)h(τ) dτ.
(44) Thus, by the Grönwall inequality we have It is evident that ρ(·) is non-negative, locally Lipscitz continuous and ρ(y) ≥ρ−(y). Thus, we have h(t2) ≤0, (45) xT f(x, u) + σT (x, u)x ¯Z ≤∥x∥ρ(∥x∥).
(36) which contradicts our assumption that h(t2) > 0 4) Domain of deﬁnition remarks for attraction function: Lemma 5: Domain of deﬁnition of an attraction function occupies the entirety of R+ as δ approaches 0.
Proof: Due to existence of local solutions ∀R ≥0 ∃δ > 0 ∃y(R; δ) (46) Thus 2) Local existence of radial forecast: Lemma 2: For every radial growth bound, there exists a corresponding radial forecast.
Proof: According to Deﬁnition 3, any radial growth bound is locally Lipschitz continuous. Therefore by the PicardLindelöf theorem, (6) has a local solution for any non-negative y(0) := y0. By Deﬁnition 4, the latter local solution qualiﬁes as a radial forecast y(y0; ·).
∀R ≥0 ∃δ > 0 R ∈dom ˜r(·, ¯Z, λ, δ, η).
(47) Lemma 3: (A1) implies the existence of an attraction function.

## B. Decay
By Lemma 6, we have 2α2(∥x∥)) + η.
(60) −α3( λx ) + η ≤−α3(∥x∥−λ p 1) Inﬁmal convolution bounds: Lemma 6: The following inequality holds: λx −x 2 ≤2λ2L(x).
(48) Let there be some number t′ ∈(0, δ]. Now, let Fk := Xkδ+t′ −Xkδ.
Notice that Proof: Assume that λx −x 2 > 2λ2L(x), then Lλ (x) > Lλ  λx  + L(x) > L(x), (49) Fk = Z kδ+t′ kδ f(Xt, Ut) + σ(Xt, Ut)Zt dt =⇒ which is a contradiction.
∥Fk∥≤ Z kδ+t′ (61) kδ ∥f(Xt, Ut) + σ(Xt, Ut)Zt∥dt ≤ 2) Lλ Lyapunov properties: Lemma 7: The function Lλ(·) is positive-deﬁnite.
Proof: Obviously, Lλ(0) = 0. Now assume that if  ¯Z) ≤ δ( ¯f  max τ∈[kδ,kδ+t′] Xτ  + ¯σ  max τ∈[kδ,kδ+t′] Xτ ∃x ̸= 0 Lλ (x) ≤0, (50) δ( ¯f (y(∥Xkδ∥; t′)) + ¯σ (y(∥Xkδ∥; t′)) ¯Z).
then, λx −x L(λx) + From this point onward, we denote ¯f (y(∥Xkδ∥; t′)) and ¯σ (y(∥Xkδ∥; t′)) as simply ¯f and ¯σ accordingly. Denote 2λ2 ≤0.
(51) !
L(y) + ∥y −Xt∥2 .
(62) Since both terms in the left-hand side of the last displayed formula are non-negative, we have 2λ2 λXt := arg min y∈X Let us determine an upper bound for ⟨ζλ, Fk⟩. Notice that Fk can be expressed in the following way: L(λx) = 0, λx −x 2λ2 = 0, (52) which implies + Fk =t′f(Xkδ, Ukδ) + Z kδ+t′ kδ f(Xt, Ukδ) −f(Xkδ, Ukδ) dt | {z } =:A1 λx = 0 =⇒∥x∥2 2λ2 = 0 =⇒x = 0, (53) + Z kδ+t′ .
which in turn contradicts x ̸= 0.
kδ σ(Xt, Ukδ)Zt dt | {z } =:A2 Lemma 8: The function Lλ (·) is radially unbounded.
Proof: Suppose there is an unbounded sublevel set (63) A = {x | Lλ (x) ≤c}.
(54) Using this expression, deduce: ⟨ζλ, Fk⟩= t′⟨ζλ, f(Xkδ, Ukδ)⟩+ ⟨ζλ, A1 + A2⟩.
(64) Let xl ∈A be an unbounded sequence. Then, note that λxl l is unbounded =⇒  L(λxl) l is unbounded, ) For the latter term in the right-hand side of the last displayed relation, we have (λxl −xl λxl l is bounded =⇒ 2λ2 ⟨ζλ, A1 + A2⟩≤∥ζλ∥(∥A1∥+ ∥A2∥), l is unbounded, (65) ∥A1∥≤Lipf(y(∥Xkδ∥; t′))( ¯f + ¯σ ¯Z)t′2 (55) whence Lλ (xl) = L(λxl) + ∥λxl−xl∥ 2 , 2λ2 is an unbounded sequence, which contradicts Lλ (xl) ≤c.
∥A2∥≤¯σ ¯Zt′.
whereas for the former term, we have 3) Upper bound for Decay ⟨ζλ, f(λx, µ(x))⟩: We deﬁne a proximal subgradient of Lλ at λx as ζλ = x−λx ⟨ζλ, f(Xkδ, Ukδ)⟩= ⟨ζλ, f(Xkδ, Ukδ) −f(λXkδ, Ukδ)⟩+ 2λ2 .
Lemma 9: From (A3) it follows that + ⟨ζλ, f(λXkδ, Ukδ)⟩, ⟨ζλ, f(λx, µ(x))⟩≤−α3(max(0, ∥x∥−λ p ⟨ζλ, f(Xkδ, Ukδ) −f(λXkδ, Ukδ)⟩≤ 2α2(∥x∥))) + η.
(56) Proof: According to (A3): Lipf  ∥Xkδ∥+ λ p ⟨ζλ, f(λx, µ(x))⟩≤inf u∈U ⟨ζλ, f(λx, u)⟩+ η.
(57) It is known from [41] that 2α2(∥Xkδ∥)  ∥ζλ∥ Xkδ −λXkδ .
(66) Using (62), the factor ∥ζλ∥ Xkδ −λXkδ can be expressed and bounded as follows: ⟨ζλ, f(λx, u)⟩≤Df(λx,u)L(λx).
(58) ∥ζλ∥ Xkδ −λXkδ = 2(Lλ (Xkδ) −L(λXkδ)) ≤ 2(L(Xkδ) −L(λXkδ)) ≤ Thus, (67) 2LipL  ∥Xkδ∥+ λ p 2α2(∥Xkδ∥)  Xkδ −λXkδ ≤ inf u∈U ⟨ζλ, f(λx, u)⟩+ η ≤inf u∈U Df(λx,u)L(λx) + η ≤ 2α2(∥Xkδ∥)  λ p 2α2(∥Xkδ∥).
2LipL  ∥Xkδ∥+ λ p −α3( λx ) + η.
(59)

Substituting the obtained bounds, we get since α3(·) is strictly increasing. We conclude the proof by simply asserting ∆(ε) := − inf z∈[0,R](α3(z + ε)−α3(z)), which ⟨ζλ, Fk⟩≤t′ ⟨ζλ, f(λXkδ, Ukδ)⟩+ gives us 2α2(∥Xkδ∥)  2LipL   w(∥Xkδ∥)  Lipf   w(∥Xkδ∥)  λ p Lλ (∥Xkδ+t′∥) −Lλ (∥Xkδ∥) ≤t′∆(ε).
(78) (68) p 2α2(∥Xkδ∥) t′2 + λ 2 Lipf(y(∥Xkδ∥; t′))( ¯f + ¯σ ¯Z) + t′¯σ ¯Z  , Let us denote ˜r ¯ Z,λ,δ,η(R) as simply ˜r(R).
5) Iterated decay: Lemma 11: If we assume that ˜r(R) < R, then where w(∥Xkδ∥) = ∥Xkδ∥+ λ p ∀l ∈N ∃¯ε > 0 ∀ε ∈(0, ¯ε) ˜r(◦l˜r(R)+ε) < ◦l˜r(R)+ε. (79) 2α2(∥Xkδ∥).
It is known from [41] that Lλ (Xkδ+t′) −Lλ (Xkδ) ≤⟨ζλ, Fk⟩+ ∥Fk∥2 Proof: Since α−1 3 (ν(·, δ)) is composed of non-decreasing functions and λ p 2λ2 .
(69) Using (61) and (68) we get 2α2(·) is strictly increasing, due to (8) attraction function ˜r(·) is strictly increasing. Therefore, ˜r(R) < R implies ∀l ∈N ◦l ˜r(R) < ◦l−1˜r(R). Now, obviously Lλ (Xkδ+t′) −Lλ (Xkδ) ≤ ∀0 < ε < ◦l−1˜r(R) −◦l˜r(R) −t′α3   max(0, ∥Xkδ∥−λ p ˜r(◦l˜r(R) + ε) < ˜r(◦l−1˜r(R)) < ◦l˜r(R) + ε.
(80) 2α2(∥Xkδ∥))  + t′ν(∥Xkδ∥, t′), (70) where ν(∥Xkδ∥, t′) = η+ p 2α2(∥Xkδ∥) +  2LipL   w(∥Xkδ∥)  Lipf   w(∥Xkδ∥)  λ2+ λ Attraction function ˜r(·) is composed of upper semicontinuous and non-decreasing continuous functions, therefore it is upper semi-continuous. Thus ˜r(·) is right continuous, since it is both strictly increasing and upper semi-continuous.
+ t′ 2 Lipf(y(∥Xkδ∥; t′))( ¯f + ¯σ ¯Z) + ¯σ ¯Z  + t′( ¯f + ¯σ ¯Z)2 Lemma 12: ∃¯ε3 > 0 ∀ε3 ∈(0, ¯ε3) ∃ε1 ∈(0, ¯ε1) ∃ε2 ∈(0, ¯ε2) 2λ2 .
(71) Note that the attraction function is by deﬁnition ◦l+1 ˜r(R) + ε3 = ˜r(◦l˜r(R) + ε1) + ε2.
(81) 2α2(R).
(72) ˜r(R, ¯Z, λ, δ, η) = α−1 3 (ν(R, δ)) + λ p Proof: This follows from the right-continuity of ˜r(·).
Lemma 13: The condition ˜r(R) < R implies 4) Radial decay: Let xl denote Xlδ.
Lemma 10: If ∀l ∈N ∀0 < ε < R −◦l˜r(R) ∃∆l(ε) < 0 ˜r := ˜r(R, ¯Z, λ, δ, η) < R, (73) (82) ∥xk∥∈[◦l˜r(R) + ε, R] =⇒ then, the following condition holds: Lλ (xk+1) −Lλ (xk) ≤δ∆l(ε).
∀ε > 0 ∃∆(ε) < 0 ∀k ∈Z ∀t′ ∈(0, δ] Proof: The above statement has already been proven for n = 1, so let us assume that it holds for some n: Sl ⇐⇒∀0 < ε1 < R −◦l˜r(R) ∃∆l(ε1) < 0 ∥Xkδ∥∈[˜r + ε, R] =⇒Lλ (Xkδ+t′) −Lλ (Xkδ) ≤t′∆(ε).
(74) Proof: Observe that (83) ∥xk∥∈[◦l˜r(R) + ε1, R] =⇒ ∥Xkδ∥≥˜r(R, ¯Z, λ, δ, η) + ε ≥˜r(R, ¯Z, λ, t′, η) + ε =⇒ Lλ (xk+1) −Lλ (xk) ≤δ∆l(ε1).
2α2(R)) ≥ α3(∥Xkδ∥−ε −λ p α3(˜r(R, ¯Z, λ, t′, η) −λ p 2α2(R)) ≥ν(R, t′) ≥ By Lemma 11, we have ˜r(◦l˜r(R) + ε1) < ◦l˜r(R) + ε1, thus by Lemma 10, ∀0 < ε2 < ◦l˜r(R) + ε1 −˜r(◦l˜r(R) + ε1) =: ¯ε2 ∃∆(ε2) < 0 ∥xk∥∈[˜r(◦l˜r(R) + ε1) + ε2, ◦l˜r(R) + ε1] =⇒ ≥ν(∥Xkδ∥, t′).
(75) Therefore, using (70) we get α3(∥Xkδ∥−ε −λ p 2α2(R)) −α3(∥Xkδ∥−λ p 2α2(R)) ≥ ν(∥Xkδ∥, t′) −α3(∥Xkδ∥−λ p Lλ (xk+1) −Lλ (xk) ≤δ∆(ε2).
(84) By Lemma 12, this implies 2α2(∥Xkδ∥)) ≥ Lλ (∥Xkδ+t′∥) −Lλ (∥Xkδ∥) ∀ε3 ∈(0, ¯ε3) ∃∆(ε3) < 0 ∥xk∥∈[◦l+1˜r(R) + ε3, ◦l˜r(R) + ε1], (85) t′ .
(76) If we denote z := ∥Xkδ∥−ε −λ p 2α2(R), we obtain which in conjunction with Sl yields Lλ (∥Xkδ+t′∥) −Lλ (∥Xkδ∥) ∀ε3 ∈(0, ¯ε3) ∃˜∆l+1(ε3) < 0 t′ ≤ (86) ∥xk∥∈[◦l+1˜r(R) + ε3, R] =⇒ sup (77) z∈[˜r−λ√ 2α2(R),R−ε−λ√ 2α2(R)] (α3(z) −α3(z + ε)) ≤ Lλ (xk+1) −Lλ (xk) ≤δ ˜∆l+1(ε3), where ˜∆l+1(ε3) := min(∆(ε3), ∆l(ε1(ε3))).
− inf z∈[0,R](α3(z + ε) −α3(z)) < 0,

Consider ∆l+1(ε3) := ˜∆l+1(min(ε3, ¯ε3 2 )). Then, Lemma 17: If we assume that Sl+1 ⇐⇒∀0 < ε3 < R −◦l+1˜r(R) ∃∆l+1(ε1) < 0 ∃i ∈N ◦i ˜r(R∗) < R, (98) (87) ∥xk∥∈[◦l+1˜r(R) + ε3, R] =⇒ then, the following holds Lλ (xk+1) −Lλ (xk) ≤δ∆l+1(ε3).
Thus, the induction step is concluded.
∥xk∥≤R →∀ε > 0 ∃l ≥k ∥xl∥< r∗+ ε.
(99) 6) Limit decay: Since ◦l˜r(R) is a decreasing, it has a limit.
Let us denote this limit as r∗.
Lemma 14: If ˜r(R) < R then ∀ε ∈(0, R −r∗) ∃∆∗(ε) < 0 ∥xk∥∈[r∗+ ε, R] =⇒ Proof: First note that ˜r(R∗) < R∗, because the negation of this statement implies ◦i+1˜r(R∗) ≥◦i˜r(R∗), which contradicts Lemma 15.
Now let us assume the opposite of the statement is to be proven: Lλ (xk+1) −Lλ (xk) ≤δ∆∗(ε).
(88) (∥xk∥≤R) and ∃ε > 0 ∀l ≥k ∥xl∥≥r∗+ ε.
(100) Proof: The existence of a limit implies Since ˜r(R∗) < R∗, Lemma 14 and Lemma 16 yield ∀ε ∈(0, R −r∗) ∃l ∈N ◦l ˜r(R) < r∗+ ε.
(89) ∀ε ∈(0, R −r∗) ∃∆∗(ε) < 0 Thus, ∥xk∥∈[r∗+ ε, R∗] =⇒ Lλ (xk+1) −Lλ (xk) ≤δ∆∗(ε).
(101) ◦l ˜r(R) + r∗+ ε −◦l(ε)˜r(R) < r∗+ ε =⇒ Thus, if we assume that Lλ (xl) ≤λα2(R), then ∥xk∥∈[r∗+ ε, R] =⇒ Lλ (xl+1) ≤Lλ (xl) + ∆∗(ε) ≤λα2(R) =⇒ r∗+ ε −◦l(ε)˜r(R)  .
Lλ (xk+1) −Lλ (xk) ≤δ∆l(ε) ∥xl+1∥≤R∗, (102) (90) which in turn proves ∀l ≥k ∥xl∥≤R∗by induction, which then implies Lλ (xl) ≤Lλ (xk) + (n −k)δ∆∗(ε).
(103) Lemma 15: An attraction function ˜r(·) has the following property: ∀r ∈(r∗, R] ˜r(r) < r.
(91) Naturally, for n > k −Lλ(xk) δ∆∗(ε) this yields Lλ (xl) < 0, which is a contradiction.
Proof: The statement is already proven for r = R.
Assume that 2) Ultimate boundedness: Lemma 18: Under the assumption that ∃r+ ∈(r∗, R) ˜r(r+) ≥r+, (92) ∃i ∈N ◦i ˜r(R∗) < R, but due to convergence r∗< y(r∗; δ) ≤R, (104) ∃l ∈N (◦l˜r(R) > r+) and (◦l+1˜r(R) < r+), (93) ∥xk∥≤R.
which implies the following holds ˜r(◦l˜r(R)) > ˜r(r+) ≥r+ > ◦l+1˜r(R), (94) ∃N ≥k ∀l ≥N ∥xl∥≤λα−1 1 (λα2(y(r∗; δ))) = ¯r.
(105) an obvious contradiction.
Proof: Note, that Corollary 5: The number r∗is the largest root of ˜r(r) −r over [0, R].
y(r∗; δ) = r∗+ (y(r∗; δ) −r∗) = r∗+ ε.
(106)
## C. Semi-asymptotic stability in probability
By Lemma 17 ∃l ∈N∪{0} ∥xl∥< r∗+ε. Now let us assume that for some m ≥n Lλ (xi) ≤λα2(y(r∗; δ)).
(107) 1) Attraction: Let R∗denote λα−1 1 (λα2(R)). Obviously R ≤R∗.
Lemma 16: Under the assumption that Then, ∃i ∈N ◦i ˜r(R∗) < R, (95) ∥xi∥≤r∗=⇒∥xi+1∥≤y(r∗; δ) =⇒ =⇒Lλ (xi+1) ≤λα2(y(r∗; δ)), (108) whereas we have lim l→∞◦l˜r(R∗) = lim l→∞◦l˜r(R).
(96) ∥xi∥> r∗=⇒Lλ (xi+1) ≤Lλ (xi) ≤λα2(y(r∗; δ)).
(109) Since the statement holds for m = n, we have Proof: Notice ◦l˜r(R∗) is a bounded decreasing sequence, and, therefore, it has a limit. Furthermore, it has a subsequence ◦l˜r(◦i˜r(R∗)) that is bounded above by ◦l˜r(R), while the sequence ◦l˜r(R∗) itself is bounded below by ◦l˜r(R). Therefore, ∀m ≥l(ε) Lλ (xi) ≤λα2(y(r∗; δ)) =⇒ r∗≤lim l→∞◦l˜r(R∗) ≤r∗.
(97) =⇒∀m ≥l(ε) ∥xi∥≤λα−1 1 (λα2(y(r∗; δ))).
(110)

Now, let ξmax := sup τ∈[kδ,t] ξτ. Since [kδ, t] is compact and ξτ is Corollary 6: If y(r∗; δ) = r∗, then lim sup l→∞ ∥xl∥≤r∗.
Lemma 19: Assume that continuous, we have ξmax = ξtmax, where tmax ∈[kδ, t]. This yields ∃i ∈N ◦i ˜r(R∗) < R, ξ2 max ≤2 Z tmax kδ ξτχτ dτ =⇒ r∗< y(r∗; δ) ≤R, (111) ∥xk∥≤R.
ξ2 max ≤2 Z tmax kδ ξmaxχτ dτ =⇒ Then the following holds ξmax ≤2 Z tmax kδ χτ dτ =⇒ ∃t2 ≥kδ ∀t ≥t2 ∥Xt∥≤λα−1 1 (λα2(y(r∗; δ))).
(112) ξmax ≤2 Z t kδ χτ dτ =⇒ Proof: By Lemma 18 ξt ≤2 Z t kδ χτ dτ =⇒ ∃N ≥k ∀l ≥N ∥xl∥≤λα−1 1 (λα2(y(r∗; δ))), (113) q ¯f(r) + 2 ¯f(r)¯σ¯µ + ¯σ(r)2(¯µ2 + ˜σ2) dτ =⇒ ξt ≤2 Z t kδ Now consider an arbitrary t ≥Nδ, and let i := t−(t mod δ).
Then, using Lemma 14 we get ξ2 kδ+t′ ≤4(( ¯f(r) + ¯σ(r)¯µ)2 + ¯σ(r)2˜σ2)t′2.
(120) ∥xi∥> r∗=⇒Lλ (Xt) ≤Lλ (xi) , ∥xi∥≤r∗=⇒∥Xt∥≤y(r∗; t mod δ).
(114) Now let us determine a bound for E [⟨ζλ, Fk, ⟩] under the assumption (116). Recall from (64) that ⟨ζλ, Fk⟩≤δ⟨ζλ, f(xk, uk)⟩+ ∥ζλ∥(∥A1∥+ ∥A2∥) ≤ Corollary 7: If y(r∗; δ) = r∗, then lim sup t→∞∥Xt∥≤r∗.
p 2α2(∥xk∥) δ⟨ζλ, f(xk, uk)⟩+ Lemma 20: The norm state ∥Xt∥is of bounded variation on an arbitrary segment [a, b].
Proof: Note, that λ (∥A1∥+ ∥A2∥).
(121) Here, we consider the following bounds for ∥A1∥, ∥A2∥: Z t ∥Xb −Xa∥≤( ¯f + ¯σ ¯Z)|b −a|.
(115) ∥A1∥≤ Z kδ+t′ kδ Lipf kδ ( ¯f(r) + ¯σ(r) ∥Zτ∥) dτ dt, (122) ∥A2∥≤ Z kδ+t′ therefore Xt is locally Lipschitz continuous, which ensures that it has a ﬁnite total variation on any segment.
kδ ¯σ(r) ∥Zt∥dt.
This gives us 3) Mean decay: Let V [Zt] ≤˜σ and E [∥Zt∥] ≤¯µ.
Lemma 21: If we assume that for some r ∀t′ ∈(0, δ] ∥Xkδ+t′∥2 ≤r, (116) E [∥A1∥] ≤Lipf(r)( ¯f(r) + ¯σ(r)¯µ)t′2 2 , E [∥A2∥] ≤¯σ(r)¯µδ.
(123) then, the following holds: Recall the bounds from (66) and (67): ⟨ζλ, f(xk, uk)⟩≤⟨ζλ, f(λxk, uk)⟩+ ∀t′ ∈(0, δ] E h ∥Fk∥2i ≤4(( ¯f(r) + ¯σ(r)¯µ)2 + ¯σ(r)2˜σ2)t′2.
(117) Proof: Let F(t) := Xt −kδ.
+ ∥ζλ∥ f(xk, uk) −f(λxk, uk) , (124) ∥ζλ∥ f(xk, uk) −f(λxk, uk) ≤ d ∥F(t)∥≤¯f + ¯σ ∥Zt∥dt =⇒ 2α2(∥xk∥).
∥ζλ∥Lipf λxk −xk ≤2LipfLipLλ p d ∥F(t)∥2 ≤2 ∥F(t)∥( ¯f + ¯σ ∥Zt∥) dt =⇒ We now apply E [·] and obtain E h ∥F(t)∥2i ≤2 Z t kδ E  ∥F(τ)∥( ¯f + ¯σ ∥Zτ∥)  dτ =⇒ E [⟨ζλ, Fk⟩] ≤t′E  ⟨ζλ, f(λxk, uk)⟩  + r 2α2(r))LipL(r+ 2t′λ2Lipf(r + λ p E h ∥F(t)∥2i ≤2 Z t E h ∥F(τ)∥2iq E  ( ¯f + ¯σ ∥Zτ∥)2 dτ.
kδ (125) λ p 2α2(r)) p (118) 2α2(∥xk∥)+ p 2α2(∥xk∥) E  ( ¯f + ¯σ ∥Zτ∥)2 then Let ξt := r E h ∥F(t)∥2i , χt := q λ (t′2 2 Lipf(r)( ¯f(r) + ¯σ(r)¯µ) + t′¯σ(r)¯µ).
ξ2 t ≤2 Z t Recall that ˘α3(·) is deﬁned as the lower convex envelope of α3(·) over [0, r].
kδ ξτχτ dτ.
(119)

## D. Semi-asymptotic stability on average
Lemma 22: If (E [∥xk∥] ≥λ p 2α2(∥xk∥)) and (∥xk∥≤ r), then E  ⟨ζλ, f(λxk, uk)⟩  ≤ 1) Mean attraction: Lemma 24: If we assume that ∀l ≥k ∥xl∥≤r, then the following holds: 2α2(r)) + η.
(126) −˘α3(E [∥xk∥] −λ p ∀ε > 0 ∃l ≥k E [∥xl∥] < ˆr(r) + ε.
(136) Proof: This follows from Lemma 9 in conjunction with the Jensen’s inequality.
From (69), we have Proof: Assume that ˆr(r) ≥r. Then, obviously E [∥xl∥] < ˆr(¯r) + ε. Thus let us assume that ˆr(r) ≥r. Then, by Lemma 23, we have E [Lλ (Xkδ+t′)] −E [Lλ (Xkδ)] ≤ # " ∥Fk∥2 .
(127) E [⟨ζλ, Fk⟩] + E 2λ2 Which, under the assumption that (E [∥xk∥] ≥ λ p 2α2(∥xk∥)) and (∥xk∥≤r), expands to E [∥xl∥] ≥ˆr + ε =⇒E [Lλ (xl+1)] −E [Lλ (xl)] ≤δ∆(ε).
(137) But, if we assume the opposite of the statement to be proven, we have ∀l ≥k E [∥xl∥] ≥ˆr + ε =⇒ E [Lλ (xk+1)] −E [Lλ (xk)] ≤ ∀l ≥k E [Lλ (xl+1)] −E [Lλ (xl)] ≤∆(ε) =⇒ −t′˘α3(E [∥xk∥] −λ p 2α2(r)) + ˆν(r, t′)t′, (128) ∀l > k −E [Lλ (xk)] ∆(ε) E [Lλ (xl)] < 0, (138) which is an obvious contradiction.
where ˆν(r, t′) = η+ p 2α2(r)  2aLipL(w(r))Lipf(w(r))+ t′ 2) Mean ultimate boundedness: Let λ˘α1(·) be the upper concave envelope of λα1(·) over [0, r] and let λ“α2(·) be the lower convex envelope of λα2(·) over [0, r].
(129) 2aLipf(r)( ¯f(r) + ¯σ(r)¯µ)+ ¯σ(r)¯µ Lemma 25: If we assume that ∀l ≥k ∥xl∥≤r, then the following holds:  + 2t′ λ λ2 (( ¯f(r) + ¯σ(r) ¯Z)2+ ∃N ≥k ∀l ≥N ˜σ2¯σ(r)2).
E [∥xl∥] ≤λ˘α−1 1 (λ“α2(ˆr + ( ¯f(r) + ¯σ(r)¯µ)δ)).
(139) 4) Mean radial decay: The mean attraction function is deﬁned as 2α2(r).
(130) ˆr(r, ¯µ, ˜σ, a, δ, η) = ˘α−1 3 (ˆν(r, t′)) + λ p Lemma 23: If ˆr(r) < r, then Proof: The condition λ˘α−1 1 (λ“α2(ˆr + δ( ¯f(r) + ¯σ(r)¯µ))) = ˆr would imply ¯r ≤ ˆr, which immediately proves the lemma, so let us instead assume that λ˘α−1 1 (λ“α2(ˆr + ( ¯f(r) + ¯σ(r)¯µ)δ)) > ˆr. This yields ˆr + ( ¯f(r) + ¯σ(r)¯µ)δ = ˆr + ε ∀ε > 0 ∃∆(ε) < 0 ∀t′ ∈(0, δ] =⇒∃N ≥k E [∥xl∥] ≤ˆr + ( ¯f(r) + ¯σ(r)¯µ)δ.
(140) (E [∥xk∥] ≥ˆr + ε) and (∥xk∥≤r) =⇒ By the Jensen’s inequality, we have E [Lλ (Xkδ+t′)] −E [Lλ (Xkδ)] ≤t′∆(ε).
(131) Proof: Note that E [∥xk∥] ≥ˆr + ε implies E [Lλ (x)] ≤λ“α2(E [∥x∥]).
(141) E [∥xk∥] ≥λ p 2α2(r) + ε.
(132) Now, assume that for some n ≥N E [Lλ (xl)] ≤λ“α2(ˆr + δ( ¯f(r) + ¯σ(r) · ¯µ)).
(142) Similarly to the proof of Lemma 10, we have E [∥xk∥] ≥ˆr + ε =⇒ This means E [∥xl∥] > ˆr =⇒E [Lλ (xl+1)] < E [Lλ (xl)] ≤ =⇒˘α3(E [∥xk∥] −ε −λ p 2α2(r)) ≥ˆν(r, t′).
(133) λ“α2(ˆr + ( ¯f(r) + ¯σ(r)¯µ)δ), (143) Using (128), we get ˘α3(∥xk∥−ε −λ p 2α2(r)) −˘α3(∥xk∥−λ p 2α2(r)) ≥ but at the same time E [∥xl∥] ≤ˆr =⇒E [∥xl+1∥] −E [∥xl∥] ≤ # "Z (k+1)δ ≥E [Lλ (Xkδ+t′)] −E [Lλ (Xkδ)] E =⇒ (144) kδ ¯f(r) + ¯σ(r) ∥Zt∥dt t′ .
(134) Finally, by analogy with (77), we obtain E [Lλ (xl+1)] ≤λ“α2(E [∥xl+1∥]) ≤ λ“α2(ˆr + ( ¯f(r) + ¯σ(r)¯µ)δ).
˘α3(∥xk∥−ε −λ p 2α2(r)) −˘α3(∥xk∥−λ p 2α2(r)) ≤ − inf z∈[0,r](˘α3(z + ε) −˘α3(z)) < 0, Since the statement holds for n = N, the above constitutes a proof by induction of ∀l ≥N E [Lλ (xl)] ≤λ“α2(ˆr + δ( ¯f(r) + ¯σ(r) · ¯µ)).
(145) (135) which similarly allows us to assert ∆(ε) := −inf z∈[0,¯r](˘α3(z + ε) −˘α3(z)).

The statement of the lemma is evident if we consider the fact that λ˘α1(E [∥xl∥]) ≤E [Lλ (xl)] .
(146) Lemma 26: If we assume that ∃i ∈N ◦i ˜r(R∗) < R, r∗< y(r∗; δ) ≤R, (147) ∥xk∥≤R.
Then, it follows that ∃N ≥k ∀t ≥Nδ E [∥Xt∥] ≤λ˘α−1 1 (λ“α2(ˆr + δ( ¯f(r) + ¯σ(r) · ¯µ))).
(148) Proof: This follows from Lemma 19, Lemma 25 and Lemma 23.
## E. Proof of Theorem 1
(C1) From (A4) it follows that ◦i+1˜r(R) ≤◦i˜r(R). Since the sequence {◦i˜r(R)}i is bounded from below, the sequence converges.
(C2) Follows from (A4) by Lemma 19.
(C3) Follows from (A4) by Lemma 26.
