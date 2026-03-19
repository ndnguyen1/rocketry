# Rocketry Project — Session Updates

## 2026-03-20 — Controller Investigation & Repo Exploration

### What was done

**Investigated CAS.slx (UTS Bluetongue 2023 Simulink model)**
- Extracted and read the XML contents of `CAS.slx` (from `utsrocketryteam-cas-controller`)
- Found it contains **only the aerodynamic plant** — no controller at all
- Plant built from: ISA Atmosphere Model → Dynamic Pressure → Aerospace Toolbox `Aerodynamic Forces and Moments` block
- Only one nonzero aero coefficient (`CD = 0.25`), CG = CP = origin, no moments
- Airbrake deflection is not an input — variable drag was never modelled
- `Model_Parameters.m` was empty; the full closed-loop model was never committed
- **Deleted** the `utsrocketryteam-cas-controller` folder as it was not useful

**Reviewed `airbrakecontroller.hpp` (root folder)**
- Skeleton for an LQR-style airbrake controller — every method is `TODO: IMPLEMENT ME`
- Designed to take full 6DOF state (position, velocity, attitude, attitude rate)
- Methods: `updateLinearModel`, `solveOptimalTrajectory`, `generateControllerGains`, `computeControllerEffort`
- More ambitious than current P controller — designed to handle non-vertical flight
- Never implemented; represents the intended next step from Mason's capstone

**Explored `UTS_rocketry_control` repo**
- Repo was already cloned locally
- **LQR is implemented for roll control only** (`Models/roll_dynamics.ipynb`):
  - 2-state system `[ω, φ]`, `scipy.linalg.solve_continuous_are()`, gain scheduled vs airspeed
- **Airbrake controller remains proportional** (`AirbrakeController.cpp`):
  - `δ_area = K × (v_target - v_actual)` with 4 rocket profiles (GECKO, BETA, BT, GOANNA)
  - Target velocity from NASA drag-coast apogee equation
  - Linear Cd model (not the 9-term CFD polynomial)
- `Rocket_Simulation.slx` (~691 KB) exists — full nonlinear flight simulation, not yet explored

### Current understanding of controller hierarchy
| Level | What | Status |
|-------|------|--------|
| Deployed firmware | P controller on velocity error | Working |
| `airbrakecontroller.hpp` | LQR skeleton for airbrake | Not implemented |
| `roll_dynamics.ipynb` | LQR for roll control | Implemented (Python) |
| Mason's capstone | LQR for airbrake/apogee | Described but not built |

### Next steps
- Implement `airbrakecontroller.hpp` methods using the LQR approach from `roll_dynamics.ipynb` as a reference
- Explore `Rocket_Simulation.slx` to understand the full plant model available for controller design
- Decide whether to port the LQR airbrake controller to Python simulation first or go straight to C++

---

## 2026-03-19 — Airbrake Cd Model Comparison Notebook

### File: `Models/airbrake_cd_comparison.ipynb`

#### What was done
Added **Section 6 — Formal Model Comparison** and updated **Section 7 — Verdict** to the existing notebook, which already had 5 models defined and visualised.

**New cells added (§6):**
- `§6 intro` — markdown explaining why in-sample metrics for refitted models are optimistic
- `CV cell` — 5-fold cross-validation (using `sklearn.Pipeline`) for the two refitted polynomials; prints CV RMSE ± 1σ vs in-sample RMSE to detect overfitting
- `Full metrics table` — pandas DataFrame ranking all 5 models by R², RMSE, MAE, Max |error| on the full 700-point CFD dataset, with CV RMSE column for refitted models
- `Controller-window table` — same metrics restricted to the operating envelope (v=60–200 m/s, ρ=0.7–1.1 kg/m³)
- `Bar charts` — side-by-side RMSE comparison (full dataset + controller window) with CV error bars overlaid on refitted models
- `Overlay residual scatter` — all 4 reasonable models' residuals on one axes for direct visual comparison

#### Models in the notebook (summary)
| Model | Source | In-sample R² | Notes |
|-------|--------|-------------|-------|
| Linear fit (`fcn.m`) | Mason's early MATLAB | −131 | Do not use |
| Firmware poly (9-term) | `ClosedLoopController.cpp` | 0.858 | Currently deployed |
| Refitted degree-2 | CFD refit (this notebook) | 0.899 | Near-identical coefficients to firmware |
| Mason `poly_predict` (deg-3) | `force_pred.mat` | poor | Fitted on narrower envelope |
| Refitted degree-8 | CFD refit (this notebook) | highest in-sample | Check CV RMSE — may be overfit (165 features, 700 pts) |

#### Next steps / to continue
- **Run §6** to get the actual CV RMSE numbers for deg-2 and deg-8
  - If deg-8 CV RMSE ≈ in-sample → consider porting to firmware (store 165 coefficients or use a lookup table)
  - If deg-8 CV RMSE >> in-sample → it is overfit; the refitted deg-2 is the best honest model
- **Check for `model_params.mat`** locally (Mason's degree-8 fit from `poly_predict.m`) — if it exists, load and compare against the refit in §2f
- **Decide firmware update path**: refitted deg-2 coefficients are essentially the same as current firmware, so any real improvement requires deg-8 or a different model structure
- The Mason `poly_predict` deg-3 cells (`cell id: earfkyrvjuj`) had an ipykernel error in a previous run — verify they execute cleanly in the current environment before trusting those outputs
