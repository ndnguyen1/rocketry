# Airbrake Model Notebook — Update Log

## Session: 2026-03-17

### Context
Working on `Models/airbrake_cd_comparison.ipynb` — comparing Cd models against `Mason's Sims/Rocket_Controller/matlab 1/matlab/CFD_final.csv` (700 points, 10 area values × 7 densities × 10 velocities).

---

### What was done

#### 1. Jupyter server
Started Jupyter on the Pi, accessible from laptop at `http://192.168.0.24:8888` (no password). Also available via Tailscale at `http://100.73.181.52:8888`. Server runs in background; restart with:
```bash
nohup jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser --NotebookApp.token='' --NotebookApp.password='' --notebook-dir=/home/raspberryred/Documents/raspberryred/rocketry > /tmp/jupyter.log 2>&1 &
```

#### 2. Bug fix — plot 3b (Cd vs Airbrake Area) bottom 2 graphs had no CFD data
**Root cause:** CFD velocity grid is multiples of 30 m/s only (30, 60, 90 … 300). Two slices used `v=100` and `v=200` which don't exist — mask returned empty.
**Fix:** Changed slices to `v=120` and `v=210`.
**Secondary fix:** Removed a duplicate `ax.scatter` call that was plotting area in m² on a cm² axis (invisible near left edge).

#### 3. Added Mason's poly_predict models to the notebook
New section **2e–2f** inserted after the firmware vs refitted comparison cell.

**2e — Mason poly_predict (degree-3, `force_pred.mat`)**
- File: `Mason's Sims/PTI/Rocket_Controller 3/Rocket_Controller/Cd_Estimator_Draft/matlab/force_pred.mat`
- This IS the `model_params.mat` file referenced by `poly_predict.m`, just named differently in the Cd_Estimator_Draft branch
- Predicts drag **force** (not Cd) via degree-3 polynomial on z-scored inputs, then divides out dynamic pressure: `Cd = F / (0.5 * rho * v² * A)`
- R² = −5.65 on full CFD dataset — was likely fitted on a narrower operating envelope, not the full 30–300 m/s range
- 20 coefficients (degree-3 with 3 inputs = 1+3+6+10)
- sklearn `PolynomialFeatures(degree=3)` feature ordering matches MATLAB's `get_poly_features(X, 3)` exactly

**2f — Refitted degree-8 polynomial (Mason's pipeline)**
- `model_params.mat` for the degree-8 version (`matlab 1/poly_predict.m`) was **not committed** to the repo
- Replicated the pipeline: `StandardScaler` → `PolynomialFeatures(degree=8)` → `LinearRegression` fitted on `CFD_final.csv`
- 165 features for 3 inputs at degree 8
- This gives the upper bound of what Mason's approach can achieve on this dataset

**All comparison plots updated** to include both new models (darkorange = Mason poly3, purple = refitted deg-8):
- 3a: Cd vs velocity (2×2, 5 lines each)
- 3b: Cd vs airbrake area (2×2, 5 lines each)
- 3c: Residuals (2×3 grid, 5 models + hidden 6th slot)
- 3d: Heatmap (2×2 grid — linear model excluded, its off-scale values crush the colormap)
- Section 4: Drag force comparison (2×3 grid)
- Section 5: Controller window errors (2×5 grid)

---

### Key findings so far

| Model | Features | R² (all CFD) |
|-------|----------|-------------|
| Linear (`fcn.m`) | 3 | −131 |
| Firmware 9-term | 9 (deg-2) | 0.858 |
| Refitted deg-2 | 9 (deg-2) | 0.899 |
| Mason poly_predict (deg-3) | 20 | −5.65 |
| Refitted deg-8 | 165 | TBD (run notebook) |

- Firmware coefficients and refitted deg-2 coefficients are nearly identical → firmware was likely fitted on this exact CFD dataset
- Mason's `fcn.m` (linear) was a prototype only — `poly_predict.m` is his intended final model
- Mason's `force_pred.mat` (deg-3) performs poorly on full range — probably fitted on a subset

---

### Open questions / next steps

1. **Run the notebook end-to-end** to get the actual R²/RMSE for the refitted deg-8 model and update the summary table
2. **Mason's `model_params.mat`** — may exist on Mason's local machine but was never committed. If retrieved, load it in 2e as an alternative to `force_pred.mat` and compare
3. **Decide on firmware model** — is the ~1.5% Cd RMSE of the degree-2 acceptable for the controller, or is it worth porting degree-8 to the Teensy?
4. **Controller window** (Section 5) is the practically relevant comparison — the full-range metrics are misleading for a model that only operates at 60–200 m/s
5. **CAS system integration** — haven't started building the actual airbrake control model yet; the Cd model comparison is the prerequisite

---

### File locations

| File | Purpose |
|------|---------|
| `Models/airbrake_cd_comparison.ipynb` | Main comparison notebook |
| `Mason's Sims/Rocket_Controller/matlab 1/matlab/CFD_final.csv` | CFD reference data (700 points) |
| `Mason's Sims/Rocket_Controller/matlab 1/matlab/fcn.m` | Linear Cd model (prototype) |
| `Mason's Sims/Rocket_Controller/matlab 1/matlab/poly_predict.m` | Degree-8 poly model (no params file) |
| `Mason's Sims/PTI/Rocket_Controller 3/Rocket_Controller/Cd_Estimator_Draft/matlab/force_pred.mat` | Degree-3 fitted params (the only available model_params) |
| `Mason's Sims/Rocket_Controller/matlab 1/matlab/get_poly_features.m` | MATLAB polynomial feature generator |
