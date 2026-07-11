---
title: Adaptive Neural Network Control of a Marine Vessel With Constraints Using the Asymmetric Barrier Lyapunov Function
publication: IEEE Transactions on Cybernetics
date: 2017-07-00 7/2017
key: EMAWGACQ
---

Abstract—In this paper, we consider the trajectory tracking of a marine surface vessel in the presence of output constraints and uncertainties. An asymmetric barrier Lyapunov function is employed to cope with the output constraints. To handle the system uncertainties, we apply adaptive neural networks to approximate the unknown model parameters of a vessel. Both full state feedback control and output feedback control are proposed in this paper. The state feedback control law is designed by using the Moore–Penrose pseudoinverse in case that all states are known, and the output feedback control is designed using a highgain observer. Under the proposed method the controller is able to achieve the constrained output. Meanwhile, the signals of the closed loop system are semiglobally uniformly bounded. Finally, numerical simulations are carried out to verify the feasibility of the proposed controller.
Index Terms—Adaptive control, barrier Lyapunov function, constraints, marine vessel, neural networks (NNs), trajectory tracking.
## I. INTRODUCTION
N OWADAYS advanced control methods are broadly applied in modern offshore engineering applications, including the vessel system, mooring system, riser system, and installation system [1]–[4]. The marine vessel is of great importance in the offshore oil industry, marine transportation, and ocean engineering, etc. [5]–[7]. With the growth in the demand for the marine transportation and the deep research for the marine vessel, the traditional way to position the marine vessel has been unable to meet the needs for (973 Program) under Grant 2014CB744206, and in part by the Fundamental Research Funds for the China Central Universities of USTB under Grant FRFTP-15-005C1. This paper was recommended by Associate Editor J. Q. Gan.
Chengdu 611731, China.
C.
Sun is with the of Automation, Southeast Nanjing 210096, China.
Color versions of one or more of the ﬁgures in this paper are available online at http://ieeexplore.ieee.org.
modern navigation safety. In recent years, in order to track the desired trajectory precisely, a lot of researchers have tried to solve the control problem of the marine vessel [8]–[10].
Analyzing the cause of the marine vessel collision accidents, we know that the marine vessel is commonly inﬂuenced by position constraint. To tackle this problem, it is necessary to guarantee that the positions are not violated in the control design for the marine vessels. Therefore, in order to design the control system for the marine vessel to achieve feasible performance, it is necessary to handle the problem of the system with uncertain parameters and constraints.
Due to the unknown parameters of the marine vessel system, the model-based control method is not feasible. Numerous approaches have been proposed to approximate the control problem of the system with uncertainties [11]–[19]. For example, a tracking controller is designed using a model-based sliding mode approach in [20] and [21]. Pan et al. [22] presented an adaptive neural network (NN) with PD control strategy to achieve fast and low-frequency adaptation for a class of uncertain nonlinear systems. Based on backstepping, Do et al. [23] proposed a robust adaptive control of underactuated ships. A tracking controller using a class of feedforward approximators is developed for fully actuated ocean surface vessels in [24]. The problems of accurate identiﬁcation and learning control are presented for ocean surface ships in uncertain dynamical environments in [25].
Yang et al. [26] focused on trajectory tracking control for marine vessels under unknown time-varying environmental disturbance. In [27], robust adaptive control is proposed for the marine vessels with a thruster assisted mooring system. In this paper, we will employ adaptive NNs to solve the problem of the system with uncertainties, and this strategy has also been expanded to other research ﬁelds such as machine learning and adaptive diagnosis system [28]–[32].
Constraints are normally found in many dynamic systems [33]–[38]. They exist in many forms such as performance, safety speciﬁcations, and physical stoppages. Violation of constraints can degrade the performance of the system.
For example, a marine vessel’s position is constrained by a maximum value of travel and this has impact on the vessel’s control system; a marine vessel needs to avoid running against the rocks when it sail in the ocean. Designing a controller without taking into account constraints can lead to failure of control. Therefore, to deal with the constraint is also a challenge in achieving the control objective. There are 2168-2267 c⃝2016 IEEE. Personal use is permitted, but republication/redistribution requires IEEE permission.
See http://www.ieee.org/publications_standards/publications/rights/index.html for more information.

Fig. 1.
ABLF.
At the same time, the constraints are never violated. Section IV shows simulation of this paper and illustrates the feasibility of the proposed control. Section V concludes this paper.
## II. PRELIMINARIES AND PROBLEM FORMULATION
## A. Useful Technical Lemmas and Deﬁnitions
Lemma 1 [41]: For any positive constants ka, kb, let Z := {z1 ∈R : −ka < z1 < kb} ⊂R and N := Rl × Z ⊂Rl+1 (l is a positive integer) be open sets. Consider the system ˙ϕ = h(t, ϕ) where ϕ := [ω, z1]T ∈N(ω ∈Rl) and h : R+ ×N →Rl+1 is piecewise continuous, and locally Lipschitz in ϕ, uniformly in t, on R+ × N. Suppose that there exist two functions U : Rl × R+ →R+ and V1 : Z →R+, continuously differentiable and positive deﬁnite in their respective domains, such that V1(z1) →∞as z1 →−ka or z1 →kb γ1(∥ω∥) ≤U(ω, t) ≤γ2(∥ω∥) where γ1 and γ2 are class K∞functions. Let V(ϕ) := V1(z1, t) + U(ω), and z1(0) ∈Z ∈(−ka, kb). If the following inequality holds: ˙V = ∂V ∂ϕ h ≤−μV + λ where μ and λ are positive constants. Then z1(t) remains in the open set z1 ∈(−ka, kb), ∀t ∈[0, +∞).
Remark 1: In Lemma 1, we split the state space into z1 and ω, where z1 is the state to be constrained and ω is the free state. The constrained state z1 requires the barrier function V1 to prevent it from reaching the limits −ka and kb, while the states may involve quadratic functions.
An ABLF is shown in Fig. 1, where x = −ka1 and x = kb1 (ka1 ̸= kb1, ka1 > 0, and kb1 > 0) are the left and right boundary lines, respectively.
Lemma 2 [63]: For any positive constant ka ∈R, the following inequality holds for x ∈R in the interval |x| < |ka|: many methods to handle the constraints problem for the marine vessels. Bemporad [39] proposed reference governors for constrained nonlinear systems. Ngo et al. [40] developed barrier Lyapunov functions to handle the constraints for systems in the Brunovsky form. Tee et al. [41] presented control designs for single-input–single-output (SISO) nonlinear systems with an output constraint. Barrier Lyapunov functions are used for an SISO nonlinear system with output constraints [42], as well as a nonlinear system with the time-varying constraints [43]. A novel integral barrier Lyapunov function is proposed to settle the SISO nonlinear systems with state constraints in [44]. Therefore, it has been proven that the barrier Lyapunov function method is an effective method to deal with tracking problems with constraints. However, none of these works consider output feedback for a multiple-input–multipleoutput (MIMO) nonlinear system, nor the use of asymmetric barrier Lyapunov function (ABLF).
NN control is an effective method for handling the system with uncertainties and constraints [45]. In [46], an efﬁcient adaptive-critic-based NN controller is investigated for nonlinear pure-feedback systems. An adaptive neural plus proportional-derivative control is proposed to lead to semiglobal asymptotic stabilization for a class of uncertain afﬁne nonlinear systems in [47]. In [48], output feedback adaptive NN is investigated for two classes of nonlinear discrete-time systems with unknown control directions, and Yang et al. [49], [50] proposed optimized adaptive control and trajectory generation for a class of wheeled inverted pendulum models of vehicle systems with uncertainties. Approximationbased control technique which uses NN is employed to handle the model parametric uncertainties and unknown disturbances in [51]–[55]. In [56], adaptive NN control is investigated for single-master–multiple-slaves teleoperation in consideration of time delays and input dead-zone uncertainties for multiple mobile manipulators carrying a common object in a cooperative manner. Li et al. [57] provided optimal feet force distribution and control of quadruped robots under external disturbance forces. In [58], a composite adaptive tracking control is studied for a class of uncertain nonlinear systems in strict-feedback form. In [59], an adaptive neural control scheme, which takes the unknown output hysteresis and computational efﬁciency into account, is presented. The adaptive neural output feedback control is provided for a class of uncertain nonlinear SISO systems in [60]–[62]. Zhao et al. [63] proposed an adaptive NN control of a marine vessel with outputs constraints, but the authors do not solve the problem with unknown states. NNs are also applied for solving optimization problems [64]–[67]. Besides NNs, fuzzy logic control is also widely used for dealing with the nonlinear systems with uncertainties and constraints [68]–[72]. In [73]–[77], the authors constructively propose several powerful fuzzy logic control techniques for various nonlinear systems.
The rest of this paper is organized as follows. Section II covers the dynamics of a marine surface vessel with MIMO and preliminaries using the necessary lemmas, properties, and assumptions. In Section III, an adaptive NN control is designed by employing an ABLF, the uniform boundedness of the closed-loop system and the asymptotic tracing are achieved.
ln k2 a k2a −x2 ≤ x2 k2a −x2 .

HE et al.: ADAPTIVE NN CONTROL OF A MARINE VESSEL WITH CONSTRAINTS USING THE ABLF The dynamics of a marine surface vessel [24] with MIMO are described by ˙η = J(η)υ M ˙υ + C(υ)υ + D(υ)υ + g(η) = τ (1) Fig. 2.
Geometric ﬁgure of the marine surface vessel system.
where the output η = [ηx, ηy, ηψ]T ∈R3 represents the Earth-frame positions and heading, respectively, τ ∈R3 is the control input, υ = [υx, υy, υψ]T ∈R3 denotes the velocities of vessel in the vessel-frame system. M ∈R3×3 is a symmetric positive deﬁnite inertia matrix, C(υ) ∈R3×3 is the Centripetal and Coriolis torques, and D(υ) is the damping matrix, g(η) represents the restoring forces caused by force of gravity, ocean currents, and ﬂoatage, J(η) is the transformation matrix which is assumed to be nonsingular, and it is deﬁned as ⎤ ⎡ ⎦.
J(η) = Lemma 3 [78]: Suppose a system output y(t) and its ﬁrst n derivatives are bounded such that |y(k)| < YK with the positive constants YK, we can consider the following linear system: ⎣ cos ηψ −sin ηψ sin ηψ cos ηψ ε ˙πi = πi+1, i = 1, . . . , n −1 Let x1 = η, x2 = υ, then the vessel system can be described as ε ˙πn = −¯λ1πn −¯λ2πn−1 −· · · −¯λn−1π2 −π1 + x1(t) ˙x1 = J(x1)x2 ˙x2 = M−1 τ −C(x2)x2 −D(x2)x2 −g(x1) .
(2) where ε is any small positive constant and the parameters ¯λ1 to ¯λn−1 are chosen such that the polynomial sn + ¯λ1sn−1 + · · ·+ ¯λn−1s+1 is Hurwitz. Then, the following property holds: ξk = πk εk−1 −x(k−1) = −εψ(k), k = 1, . . . , n −1 where ψ = πn+ ¯λ1πn−1+· · ·+ ¯λn−1π1 with ψ(k) denoting the kth derivative of ψ. Also, there exist positive constants t∗and hk such that ∀t > t∗, we have ||ξk|| ≤εhk, k = 1, 2, 3, . . . , n.
Lemma 4 [79], [80]: Consider the basis function of Gaussian RBF NN with Z being the input vector, if ˆZ = Z −ς ¯ψ where ¯ψ is a bounded vector and constant ς > 0, then we have The control objective is to design an adaptive NN controller for the marine vessel so that it follows a desired trajectory xd(t) = [xd1(t), xd2(t), xd3(t)]T, while ensuring that all signals are bounded and their own constraints are not violated.
The following assumption will be used to achieve our control objective.
Assumption 1: There exist positive constants 3-D vectors Y0 = [Y01, Y02, Y03]T, Y0 = [Y01, Y02, Y03]T, A0 = [A01, A02, A03]T, satisfying max{Y0, Y0} ≤A0 ≤kc, such that, ∀t ≥0, the desired trajectory xd(t) satisﬁes −Y0 ≤ xd(t) ≤Y0.
  −  Z −μj T Z −μj 
## III. CONTROL DESIGN
, j = 1, 2, . . . , l sj(Z) = exp η2 j
## A. Model-Based Control
S  ˆZ  = S(Z) + ςSt In case that the parameters M, C(υ), D(υ), and g(η) are known, we denote z1 = [z11, z12, z13]T = x1 −xd, and z2 = [z21, z22, z23]T = x2 −α, where α = [α1, α2, α3]T is a stabilizing function to be designed.
Choosing the ABLF as    where the input vector Z ∈ Z ⊂ Rq, μj = [μj1, μj2, . . . , μjq]T is the center of the receptive ﬁeld and η2 i is the width of the Gaussian function. S(Z) = [S1(Z), S2(Z), S3(Z)]T, Si(Z) = [s1(Z), . . . , sl(Z)]T, the number of the node l > 1, and St is a bounded vector function.
V1 = 1 p(i) log k2 bi k2 bi −z2 1i + (1 −p(i)) log k2 ai k2 ai −z2 1i i=1
## B. Problem Formulation
(3) where log(•) denotes the natural logarithm of •, ka = [ka1, ka2, ka3]T = kc −Y0, kb = [kb1, kb2, kb3]T = kc −Y0.
p(i) is deﬁned as p(i) =  1, z1i > 0 0, z1i ≤0 i = 1, 2, 3.
(4) Differentiating of V1 with respect to time, we have    p(i) z1i˙z1i .
(5) ˙V1 = k2 ai −z2 1i k2 bi −z2 1i + (1 −p(i)) z1i˙z1i The motion and state variables of the single point mooring systems are deﬁned and measured with respect to two important reference frames: 1) earth-ﬁxed frame and 2) body-ﬁxed frame. Fig. 2 shows that the earth-ﬁxed frame is denoted as (xe, ye) with its origin located at the connection of the mooring line and the mooring terminal. The ﬁxed body frame, denoted as (xb, yb), is ﬁxed to the vessel body, and the origin coincides with the center of gravity of the moored vessel. The xb axis is directed from poop to fore along the longitudinal axis of the vessel, and the yb axis is directed to starboard.
i=1

Differentiating of z1 with respect to time, we have
## B. Adaptive Neural Network Control With
Full-State Feedback ˙z1i = ˙x1i −˙xdi = Ji(x1)(z2 + α) −˙xdi (6) where Ji(x1) is the ith line of J(x1). We propose α as α = JT(˙xd −A1) (7) where ⎡ ⎤ The parameters of the marine vessel system M, C(x2), D(x2), and g(x1) may be unknown in practice, and in this case the control law above is unfeasible.
To handle this problem we use approximator-based NNs to approximate the unknown parameters. In this section, we will design an adaptive NN control for solving this problem. The control law is proposed as follows: ⎣ ⎦   A1 =   p(1)  k2 b1 −z2  + (1 −p(1))  k2 a1 −z2  k1z11  p(2)  k2 b2 −z2  + (1 −p(2))  k2 a2 −z2  k2z12  p(3)  k2 b3 −z2  + (1 −p(3))  k2 a3 −z2  k3z13 τ = − p(i)z1iJT i (x1) (8) k2 ai −z2 1i k2 bi −z2 1i + (1 −p(i))z1iJT i (x1) i=1    − p(i) ki, i = 1, 2, 3, are positive constants. Substituting (6)–(8) to (5), we have  zT +kiz2 1i  k2 ai −z2 1i   zT +kiz2 1i  k2 bi −z2 1i  + (1 −p(i)) i=1    −K2z2 −ˆWTS(Z) (16) p(i)z1iJi(x1)z2 ˙V1 = − k2 bi −z2 1i i=1 kiz2 1i + i=1  + (1 −p(i))z1iJi(x1)z2 .
(9) k2 ai −z2 1i where (zT 2 )+ is the Moore–Penrose pseudoinverse of zT 2 , ˆW = [ ˆW1, ˆW2, ˆW3]T are the weights of the NN, S(Z) = [S1(Z), S2(Z), S3(Z)] are the basis functions, and Z = [xT 1 , xT 2 , αT, ˙αT] are the inputs of the NNs. The NN ˆWTS(Z) is used to approximate W∗TS(Z) Choosing the Lyapunov function V2 as V2 = V1 + 1 2zT 2 Mz2.
(10) W∗TS(Z) = ˆWTS(Z) −ϵ(Z) = −(C(x2)x2 + D(x2)x2 + g(x1) + M ˙α) −ϵ(Z) (17) The derivative of V2 with respect to time is ˙V2 = ˙V1 + zT 2 M˙z2.
(11) where ϵ(Z) ∈Rn is the approximation error. The adaptive law is given as follows: Differentiating z2 with respect to time yields ˙ˆWi = i  Si(Zi)z2,i −σi|z2i| ˆWi  , i = 1, 2, 3 (18) ˙z2 = ˙x2 −˙α = M−1 τ −C(x2)x2 −D(x2)x2 −g(x1) −˙α.
(12) Substituting (9) and (12) into (11), we have  where i = T i > 0 (i = 1, 2, 3) is the constant gain matrix, and σi > 0, i = 1, 2, 3 are small constants [81].
Lemma 5 [82]: For the adaptive law (18), there exists a compact set   p(i)z1iJi(x1)z2  ˙V2 = − k2 bi −z2 1i i=1 kiz2 1i + i=1 ω1 =  ˆWi|  ˆWi  ≤si  σi + (1 −p(i))z1iJi(x1)z2 k2 ai −z2 1i + zT τ −C(x2)x2 −D(x2)x2 −g(x1) −M ˙α .
(13) We design the control law as τ = C(x2)x2 + D(x2)x2 + g(x1) + M ˙α1 −K2z2    − p(i)z1iJT i (x1) (14) k2 ai −z2 1i k2 bi −z2 1i + (1 −p(i))z1iJT i (x1) i=1 where K2 is a positive deﬁnite matrix of 3 × 3. Substituting (14) into (13), we have  where ∥Si(Z)∥≤si with si > 0, such that ˆWi(t) ∈ω1, ∀t ≥0 provided that ˆWi(0) ∈ω1.
Theorem 1: Consider the marine surface vessel dynamics (1), under Assumption 1, with full-state feedback control law (16) together with adaption law (18), for initial conditions satisfy z1(0) ∈0 := {z1 ∈R3 : −ka < z1 < kb}, i.e., the initial conditions are bounded.
The signals of the closed loop system are semiglobally uniformly bounded (SGUB). And the asymptotic tracking is achieved, i.e., x1(t) →xd(t) as t →∞. The multiple output constraints are never violated, i.e., |x1| < kc, ∀t > 0, and the closed-loop error signals z1, z2 and ˜W will remain within the compact sets z1, z2,  ˜W, respectively, deﬁned by ˙V2 = − i=1 kiz2 1i −zT 2 K2z2.
(15) z1 :=  z1 ∈R3 −Dz1i ≤z1i ≤Dz1ii = 1, 2, 3  (19)    (20) z2 ∈R3∥z2∥≤ z2 := D λmin(M) According to Lemma 1, we know that the signal z1 remains in the interval −ka ≤z1 ≤kb, ∀t > 0, provided that −ka ≤ z1(0) ≤kb.

HE et al.: ADAPTIVE NN CONTROL OF A MARINE VESSEL WITH CONSTRAINTS USING THE ABLF where where Dz1i = k2 bi(1 −e−2(V2(0)+(C/ρ))), Dz1i = ⎛ ⎞ ⎞ ⎛ ⎝σ 2 i W∗ i 2 ⎠ ⎠ ρ = min ⎝min(2ki), 2λmin(K2 −I) λmax(M) , min 2λmax  −1 i  k2 ai(1 −e−2(V2(0)+(C/ρ))), D = 2(V2(0) + C/ρ), and ρ and C are two positive constants.
Proof: Considering the Lyapunov function V2 as (27)  n  V2 = V1 + 1 2zT 2 Mz2 + 1 C = 1 (28) i=1 ˜WT i −1 i ˜Wi (21) 2∥¯ϵ∥2 +  σ 2 i W∗ i 4 + σ 2 i 8 ϑ4  i=1 where ˜Wi = ˆWi −W∗ i , (i = 1, 2, 3), ˜Wi, ˆWi, and W∗ i are the NN weight error, estimated value, and actual value, respectively. Differentiating V2 with respect to time and substituting (16)–(18) to (22), we have where λmin(•) and λmax(•) denote the minimum and maximum eigenvalues of matrix •, where λ(A) are real, respectively. To ensure ρ > 0, the control gain K2 is chosen to satisfy the following condition:  ˙V2 = ˙V1 + zT 2 M˙z2 + λmin(K2 −I) > 0.
(29) i=1 ˜WT i −1 i ˙˜Wi    = − p(i)zT  zT +kiz2 1i  k2 bi −z2 1i  + (1 −p(i))zT  zT +kiz2 1i  k2 ai −z2 1i  i=1 + zT  −ˆWTS(Z) + W∗TS(Z) + ϵ(Z)  −zT 2 K2z2   − i=1 kiz2 1i + i=1 ˜WT i  Si(Z)z2,i −σi|z2i| ˆWi  .
(22) According to deﬁnition of the Moore–Penrose pseudoinverse, we can obtain zT  zT + =  0, z2 = [0, 0, 0]T 1, Otherwise.
(23) When z2 = [0, 0, 0]T, ˙V2 = − i=1 kiz2 1i ≤0.
According to Lemma 1, z1(t) remains in the open set z1 ∈ (−ka, kb), ∀t ∈[0, +∞), provided that z1(0) ∈(−ka, kb). As we know x1(t) = z1(t) + xd(t), −Y0 ≤xd(t) ≤Y0, and ka = kc −Y0, kb = kc −Y0. Hence, the output constraints are not violated, i.e., |x1| ≤kc, ∀t ≥0.
■ Remark 2: If C is equal to zero, we can say that the system could achieve exponential stability. However, for our controller, C = (1/2)∥¯ϵ(Z)∥2 +n i=1(σ 2 i /8)(∥W∗ i ∥4 +ϑ4), where σi is a control parameter in the adaptive law, which improves the robustness of the system. We can also design another adaptive law without the parameter of σi, but it will inﬂuence the robustness of the proposal control. If σi in C is set to zero, the term left is (1/2)∥¯ϵ(Z)∥2, which is the approximation error of NN, and is a positive constant. Therefore, we can achieve stability for our system, but not achieve exponential stability.
Then asymptotic stability of the system can still be drawn by Barbalat’s Lemma. Otherwise, in case of z2 ̸= [0, 0, . . . , 0]T, we have
## C. Adaptive Neural Network Control With Output Feedback
˙V2 ≤−zT 2 (K2 −I)z2 + 1 2∥¯ϵ(Z)∥2  + W∗ i 4 +  ˜Wi 4 −2 W∗ i 2 ˜Wi 2 σ 2 i i=1    − .
The state-feedback control is based on the condition that the states x1, x2 can be measured by sensors. In practice, some states cannot be measured because of technical or economical problems. To solve the problem, we apply a high-gain observer to estimate the unknown state x2. In this section, we will design the output feedback control using a high-gain observer. Considering the following linear system: p(i) log k2 bi k2 bi −z2 1i + (1 −p(i)) log k2 ai k2 ai −z2 1i i=1 ki ε ˙π1 = π2 (30) ε ˙π2 = −¯λ1π2 −π1 + x1.
(31) From Lemma 5, we can obtain  ˜Wi  =  ˆWi −W∗ i  ≤  ˆWi  + W∗ i  ≤si σi + W∗ i .
(24) According to Lemma 3, we have π2 For clariﬁcation, we deﬁne  ˜Wi  ≤si ε −˙x1 = −εψ(2) (32) σi + W∗ i  = ϑ (25) where ϑ > 0 is a constant. Thus, we can obtain ˙V2 ≤−zT 2 (K2 −I)z2 + 1 2∥¯ϵ(Z)∥2  where ε is any small constant, and there exist positive constants t∗and h2 such that ∀t > t∗, we have ∥ξ2∥≤εh2. From the deﬁnition of J(η), we also can know JT = J−1. So we can use (π2/ε) to estimate ˙x1, then x2 and z2 can be estimated as follows: + W∗ i 4 + ϑ4 −2 W∗ i 2 ˜Wi 2 σ 2 i i=1 ˆx2 = JT π2   ε (33)  − ˆz2 = JT π2 ε −α (34) p(i) kiz2 1i k2 bi −z2 1i + (1 −p(i)) kiz2 1i k2 ai −z2 1i i=1 ˜z2 = ˆz2 −z2 = JT π2 ≤−ρV2 + C (26) ε −α −JT ˙x1 + α = JTξ2.
(35)

From the full state feedback, we can rewrite the virtual control α and we choose Substituting (40) and (41), we have the time derivative of the Lyapunov function candidate V2 as    α = JT(˙xd −A2) (36) ˙V2 ≤− p(i) kiz2 1i k2 bi −z2 1i + (1 −p(i)) kiz2 1i k2 ai −z2 1i where i=1 ⎡ ⎤ " K2 −1 −zT 2I # z2 −zT 2 K2˜z2 + 1 2∥¯ϵ∥2 ⎦.
(37) A2 = ⎣ k1z11 k2z12 k3z13  − From above analysis, we have i=1 z2,i  ˆWT i Si  ˆZ  −W∗T i Si(Z)   ˙z1i = Ji(x1)  z2 + JT(˙xd −A2)  −˙xdi.
(38) +  ˜WT i Si  ˆZ  ˆz2,i − ˆz2i σi ˜WT i ˆWi  .
(45) i=1 Differentiating V1 with respect to time, we have   From Lemma 4 and using the properties, we have  ˙V1 = − −σi ˜WT i ˆWi ≤σi p(i) kiz2 1i k2 bi −z2 1i + (1 −p(i)) kiz2 i1 k2 ai −z2 1i i=1    W∗ i 2 −  ˜Wi 2 (46) Si  ˆZ  ≤li (47) + p(i)z1iJi(x1)z2 .
(39) k2 ai −z2 1i k2 bi −z2 1i + (1 −p(i))z1iJi(x1)z2 i=1 where li is a positive constant. Deﬁne ˜z2 = ˆz2 −z2 = JT(η)ξ2.
Now using the above two inequalities and Lemma 2, and applying (1/2)ξT 2 ξ2 ≤(1/2)ε2h2 2, we have From the full state feedback control design, we rewrite the control law and adaptation law to obtain the control and adaptation law for output feedback control as       ˙V2 ≤− τ = − p(i)z1iJT i (x1) kip(i) log k2 bi k2 bi −z2 1i + ki(1 −p(i)) log k2 ai k2 ai −z2 1i i=1 k2 ai −z2 1i k2 bi −z2 1i + (1 −p(i))z1iJT i (x1) i=1   σi − W∗ i 2 ˜Wi 2 + 1 σ 2 i 2∥¯ϵ∥2 + 4 ϑ2 i=1 i=1 −K2ˆz2 −ˆWTS(ˆZ) (40) ˙ˆWi = i  Si  ˆZ  ˆz2,i − ˆz2i σi ˆWi  (41) + λmax  KT 2 K2 + diag 2li/σi + 2I 1 2ε2h2   + 1  σ 2 i W∗ i 4 + σ 2 i 8 ϑ4  i=1 ς2∥Sti∥2W∗ i 2 + i=1 " K2 −5 −zT 2I # z2 ≤−ρV2 + C (48) where ρ and C are two constants deﬁned as ⎛ 2I  ρ = min ⎝2λmin(ki), 2λmin  K2 −5 λmax(M) , ⎛ ⎞ ⎞ where K2 is the control gain, i is the constant gain matrix, and σi > 0, (i = 1, 2, 3), are small positive constants.
Theorem 2: Consider the marine surface vessel dynamics (1), under Assumption 1, with output feedback control law (40) together with adaption law (41). The initial conditions satisfy z1(0) ∈0 := {z1 ∈R3 : −ka < z1 < kb}, i.e., the initial conditions are bounded. The signals of the closed loop system are SGUB. And the asymptotic tracing is achieved, i.e., x1(t) →xd(t) as t →∞. The multiple output constraints are never violated, i.e., |x1| < kc, ∀t > 0, and the closed-loop error signals z1 and z2 will remain within the compact sets z1, z2, respectively, deﬁned by ⎝σ 2 i W∗ i 2 ⎠ ⎠ (49) min i=1,2,3 z1 :=  z1 ∈R3 −Dz1i ≤z1i ≤Dz1ii = 1, 2, 3  (42) 2λmax  −1 i       (43) z2 ∈R3∥z2∥≤ z2 := C = 1 D λmin(M)  σ 2 i W∗ i 4 + σ 2 i 8 ϑ4  i=1 ς2∥Sti∥2W∗ i 2 + i=1 where Dz1i = + λmax  KT 2 K2 + diag 2li/σi + 2I 1 k2 bi(1 −e−2(V2(0)+(C/ρ))), Dz1i = 2ε2h2  σi + 1 2∥¯ϵ∥2 + 4 ϑ2.
(50) i=1 k2 ai(1 −e−2(V2(0)+(C/ρ))), D = 2(V2(0) + C/ρ), and ρ and C are two positive constants.
Proof: Considering the ABLF as  To ensure that ρ > 0, the control gain K2 is chosen to satisfy the following condition: V2 = V1 + 1 2zT 2 Mz2 + 1 i=1 ˜WT i −1 i ˜Wi (44) λmin " K2 −5 2I # > 0.
(51) where ˜Wi = ˆWi −W∗ i , (i = 1, 2, 3), ˜Wi, ˆWi, W∗ i are the NN error, estimated value, and actual value, respectively.

HE et al.: ADAPTIVE NN CONTROL OF A MARINE VESSEL WITH CONSTRAINTS USING THE ABLF Fig. 4.
Tracking error z1 for case I.
Fig. 3.
Comparison between x1 and xd (dashed line-xd, solid line-x1) for case I.
## IV. SIMULATION
The model used for simulation is the Cybership II, which is a 1:70 scale supply vessel replica built in a marine control laboratory in the Norwegian University of Science and Technology [24]. The desired trajectories of x1 are given as ⎧ ⎪⎨ x1xd(t) = 0.004 + 0.4 sin(0.5t) x1yd(t) = 0.005 + 0.014 cos(2t) ⎪⎩  .
(52) x1ψd(t) = tan−1 ˙ x1xd ˙ x1yd Fig. 5.
Control input τ for case I.
Fig. 6.
Comparison between x1 and xd (dashed line-xd, solid line-x1) for case II.
Matrix g(x1) is speciﬁed as g(x1) = [0.2 cos(x1ψ) −0.36 sin(x1ψ), 0.2 sin(x1ψ) + 0.36 cos(x1ψ), 0.18].
Three different cases are evaluated for the simulation studies. First, we examine the model-based control design in (14).
Second, the proposed adaptive NN control with the full state feedback (16) is considered. Third, the adaptive NN control with the output feedback (40) is evaluated.
Case I (Model Based Control): For the model based control, we choose the control parameters as follows 1 = 50I, 2 = 100I, 3 = 200I, σ1 = 0.001, σ2 = 0.001, and σ3 = 0.001.
The initial conditions are given as x1(0) = [0.004, 0.019, 0]T, x2(0) = [0.33, 0.005, 0]T. The control gains are given as K1 = diag[k1, k2, k3] = diag[0.01, 0.01, 0.01]T and K2 = diag[20, 20, 20]T.
From Fig. 3, it is observed that the trajectory can tack the desired trajectory under the model based control. The tracking error z1 is shown in Fig. 4, from which, we can obtain that z1 < kb and z1 > −ka, ∀t > 0. The corresponding inputs of the proposed control τ are shown in Fig. 5.
Case II (Adaptive Neural Network Control With the Full State Feedback): Choosing the control gains K1, K2 as K1 = diag[k1, k2, k3] = diag[10, 10, 0.01], K2 = diag[100, 100, 300], 1 = I50×50, 2 = I100×100, 3 = I200×200, the initial conditions are given as x1(0) = [0.004, 0.019, 0.02]T, x2(0) = [0.13, 0, 0]T.
The simulation results are as follows.
Fig. 6 illustrates the tracking trajectory and the desired trajectory with full state back. We can see that x1(t) stays within the set constraints when the proposed control (16) is used. The tracking error z1 is shown in Fig. 7. It can be seen that asymptotic tracking performance is achieved. z1 does not violate its constraints when its initial value satisﬁes [−0.008, −0.005, −0.006]T < z1(0) < [0.016, 0.015, 0.011]T

Fig. 7.
Tracking error z1 for case II.
Fig. 10.
Tracking error z1 for case III.
Fig. 8.
Control input τ for case II.
Fig. 11.
Control input τ for case III.
Fig. 9.
Comparison between x1 and xd (dashed line-xd, solid line-x1) for case III.
when the proposed control (16) is used. Fig. 8 gives the control input τ.
Case III (Adaptive Neural Network Control With the Output Feedback): Under same conditions in case II, simulations of this proposed control law are carried out.
Additionally, the initial conditions of the observer are set as π1 = π2 = ˙π1 = ˙π2 = 0.
From Fig. 9, it is observed that the trajectory can tack the desired trajectory under the output feedback neural network control. The tracking error z1 is shown in Fig. 10, and we can obtain that z1 < kb, and z1 > −ka, ∀t > 0. The corresponding inputs of the proposed control τ are shown in Fig. 11.
The tracking performance of the model-based control, state feedback control, and output feedback control are shown in Figs. 3, 6, and 9, respectively. From these ﬁgures, it can be seen that all three controllers can successfully track the desired trajectory. From Figs. 4, 7, and 10, we can also obtain the controllers never violate the set constraint and the tracking errors all converge to a small value close to zero.
The model based control has the best tracking performance and the least error. This is because it uses more information about dynamics of the marine vessel and hence it is a reasonable simulation result. The state feedback controller also has lesser error than the output feedback controller, because it assumes that all output information is measurable. Moreover, we can also conclude that the high gain observer is effective

HE et al.: ADAPTIVE NN CONTROL OF A MARINE VESSEL WITH CONSTRAINTS USING THE ABLF By solving the equation, we have and it can ensure the performance for the output feedback control.
V2 ≤V2(0) + C ρ .
(61)
## V. CONCLUSION
According (44), we have 2∥z2∥2 ≤ V2(0) + C ρ λmin(M) .
(62) For z1, we have ⎧ ⎪⎪⎪⎨ In this paper, we consider the control design for a fully actuated vessel with output constraints and uncertainties using the ABLF and adaptive NNs. We have proven that under the proposed control law, the signals of the closed loop system are SGUB, the asymptotic tracing is achieved, and the multiple output constraints are never violated. Simulation results have illustrated the effective performance of the designed control law.
2 log k2 bi k2 bi −z2 1i , 0 < z1i < kbi V2(0) + C ρ ≥ ⎪⎪⎪⎩
## APPENDIX
2 log k2 ai k2 ai −z2 1i , −kai < z1i ≤0.
(63)
## A. Proof of Theorem 1
Taking exponentials on both side of the inequality yields  ⎛ ⎞ V2(0)+C ρ ⎜⎝1 −e −2 ⎟⎠, 0 < z1i < kbi The signals z1, z2, ˜Wi(i = 1, 2, 3) are SGUB. The proof is given as follows.
Multiplying (26) by eρt, we have k2 bi ⎧ ⎪⎪⎪⎪⎪⎪⎪⎪⎨  ⎛ ⎞ z2 1i ≤  V2eρt ≤Ceρt.
(53) d dt V2(0)+C ρ ⎜⎝1 −e −2 ⎟⎠, −kai < z1i ≤0 k2 ai By solving the equation, we have ⎪⎪⎪⎪⎪⎪⎪⎪⎩ V2 ≤V2(0) + C (64) ρ .
(54) −Dz1i ≤z1i ≤Dz1i (65) According (21), we have where  2∥z2∥2 ≤ V2(0) + C ρ λmin(M) .
(55) ρ # " 1 −e −2  V2(0)+ C Dz1i = k2 bi For z1, we have  " 1 −e −2  V2(0)+ C ρ # , i = 1, 2, 3.
(66) ⎧ ⎪⎪⎪⎨ k2 ai Dz1i = 2 log k2 bi k2 bi −z2 1i , 0 < z1i < kbi V2(0) + C ρ ≥ ⎪⎪⎪⎩
## ACKNOWLEDGMENT
2 log k2 ai k2 ai −z2 1i , −kai < z1i ≤0.
(56) Taking exponentials on both side of the inequality yields " 1 −e −2  V2(0)+ C ⎧ ⎪⎪⎨ ρ # , 0 < z1i < kbi k2 bi The authors would like to thank the Editor-in-Chief, the Associate Editor, and the anonymous reviewers for their constructive comments which helped to improve the quality and presentation of this paper.
z2 1i ≤ ⎪⎪⎩ " 1 −e −2  V2(0)+ C ρ # , −kai < z1i ≤0 (57) k2 ai
