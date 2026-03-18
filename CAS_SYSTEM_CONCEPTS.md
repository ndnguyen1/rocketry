# UTS Rocketry — CAS Board: Concepts & Theory Documentation

This document captures explanations of the key concepts underlying the CAS board codebase — the physics, maths, and engineering decisions. It is intended as a companion to `CAS_SYSTEM_DOCUMENTATION.md` for anyone who needs to understand *why* things work the way they do, not just *what* they do.

---

## 1. ISA Barometric Formula

### What it is

The International Standard Atmosphere (ISA) is a model that defines how pressure, temperature, and density vary with altitude, assuming a standardised, calm atmosphere. It is not perfectly accurate on any given day, but it is consistent and good enough for rocketry.

The key relationship is that pressure drops as you go up because there is less air above you pressing down. In the troposphere (below ~11km, which covers everything relevant here), temperature also drops linearly with altitude at the lapse rate λ = 0.0065 K/m. This gives:

```
P(h) = P₀ * (1 - λ*h/T₀)^(g*M/R*λ)
```

Where:
- P₀ = 101325 Pa (sea-level pressure)
- T₀ = 288.15 K (sea-level temperature)
- g = 9.80665 m/s²
- M = 0.0289644 kg/mol (molar mass of air)
- R = 8.314 J/mol·K (universal gas constant)
- λ = 0.0065 K/m (temperature lapse rate)

### Inverting for altitude

Rearranging to get altitude from a pressure reading:

```
h = (T₀/λ) * (1 - (P/P₀)^(R*λ/g*M))
```

Which simplifies to the form used in the code:

```
h = 44307.69 * (1 - (P/101325)^0.190284)
```

The exponent 0.190284 is R*λ/(g*M) pre-calculated.

### How it is used in the CAS board

At startup, the board samples pressure for 5 seconds and stores the average as `referencePressure` (the ground-level P₀ for that day). From that point, every barometer reading is converted to altitude-above-ground using that reference instead of the standard 101325 Pa. This automatically corrects for whatever the actual atmospheric pressure is on launch day — on a low-pressure day, using 101325 as reference would make the board think it is already at 300m altitude before leaving the pad.

### The getAltitudeAGL() bug

`getRawAltitude(pressure)` uses the standard sea-level reference (1013.25 hPa) as P₀, returning altitude above sea level. If the launch site is at 50m elevation, this returns 50m while sitting on the pad.

`getAltitudeAGL(pressure)` was meant to give altitude above ground level by using the calibrated ground pressure as P₀ instead of 1013.25. In theory this is correct — by using measured ground pressure as reference, the formula naturally outputs 0m on the pad and actual height above ground during flight. But somewhere in the function the units are wrong (the comment says `//FIX 10 times greater than it should be`), so it returns values approximately 10x too large.

The working path uses `getRawAltitude()` to get absolute sea-level altitude, and the StateEstimator handles the AGL correction separately through the calibrated `referencePressure`. The `getAltitudeAGL()` function is dead code in practice, which is why the bug has never caused a flight issue.

---

## 2. Quaternions

### Why not Euler angles?

The intuitive approach to representing rocket orientation would be three angles: roll, pitch, and yaw. There are three problems with this:

**Gimbal lock.** When one rotation axis aligns with another, you lose a degree of freedom and the representation becomes singular — you can no longer distinguish rotations around two axes. For a rocket pointing nearly straight up, this is a real problem.

**Interpolation.** Interpolating between two orientations with Euler angles does not give the shortest rotation path. Quaternions interpolate cleanly (SLERP — spherical linear interpolation).

**Numerical stability.** Composing many small rotations by multiplying Euler angles accumulates errors in ugly ways. Quaternion multiplication keeps things on the unit sphere and normalisation is trivial (divide by magnitude).

### What a quaternion is

A quaternion is a way of representing a 3D orientation using four numbers: one real part and three imaginary parts:

```
q = w + xi + yj + zk
```

In the code's notation: `{qr, qi, qj, qk}` (real + imaginary parts).

A unit quaternion encodes a rotation by angle θ around unit axis (x, y, z) as:

```
q = cos(θ/2) + sin(θ/2)*(xi + yj + zk)
```

### How it is used in the CAS board

The BNO08x uses `SH2_GAME_ROTATION_VECTOR` — a fused quaternion from its internal AHRS, no magnetometer, just accelerometer + gyroscope fusion done on the chip. You just read the result. The quaternion tells you exactly how the rocket is oriented relative to its starting orientation.

The quaternion data is currently only logged to SD. The original plan was to use it to project the IMU's acceleration vector onto the vertical axis (the IMU measures acceleration in body frame, not world frame — if the rocket is tilting, the axes mix). That projection requires the quaternion. But it was never implemented, hence the comment `//Fuse IMU and Barometer` sitting above dead code.

On the new board, this projection must be implemented using the output of the Mahony/Madgwick filter.

---

## 3. The Kalman Filter

### Relationship to the Luenberger observer

The Kalman filter is the optimal Luenberger observer for linear stochastic systems. Both have the same structure.

**Luenberger observer:** For a system `ẋ = Ax + Bu` with output `y = Cx`, build an observer:

```
x̂̇ = Ax̂ + Bu + L(y - Cx̂)
```

The observer runs a model of the system in parallel. The term `L(y - Cx̂)` is a correction — the difference between what the sensor actually says and what the model predicted the sensor should say, scaled by a gain matrix L. L is tuned by hand based on how much you trust the model vs the sensor.

**Kalman filter:** Exactly the same structure, but L (called the Kalman gain K) is computed optimally at every timestep based on two noise covariance matrices you specify: Q (process noise — how much uncertainty is in your model) and R (measurement noise — how much uncertainty is in your sensor). The filter automatically trades off between trusting the model and trusting the sensor based on their relative uncertainties. When sensor noise R is high, the filter trusts the model more. When process noise Q is high, it trusts the sensor more.

### The 3-state filter in the CAS board

State vector: `X = [altitude (m), vertical velocity (m/s), vertical acceleration (m/s²)]ᵀ`

#### Prediction step

```
X_pred = A * X
P_pred = A * P * Aᵀ + Q
```

A is the kinematic state transition matrix with timestep dt:

```
A = [1   dt   0.5*dt²]
    [0    1    dt    ]
    [0    0    1     ]
```

Multiplying out: this is just the kinematic equations of motion (s = ut + ½at²). The model says: given the current state estimate, where should the rocket be one timestep later if physics holds?

P is the covariance matrix — a 3×3 matrix tracking how uncertain you are about each state and how the uncertainties relate to each other.

`A * P * Aᵀ` propagates that uncertainty forward through the kinematic equations. Uncertainty in velocity bleeds into uncertainty in altitude over time — this captures exactly how much.

`+ Q` adds process noise — extra uncertainty injected each step because the model is not perfect (wind, unmodelled aerodynamics, etc.). This prevents the filter from becoming overconfident in its model over time.

#### Update step

```
K = P_pred * Hᵀ * (H * P_pred * Hᵀ + R)⁻¹
X = X_pred + K * (z - H * X_pred)
P = (I - K*H) * P_pred
```

H is the measurement matrix. Since the barometer only measures altitude: `H = [1, 0, 0]`.

**Computing K (Kalman gain):**

- `H * P_pred * Hᵀ` — scalar here (1×3 × 3×3 × 3×1 = 1×1). The predicted uncertainty in the altitude estimate specifically.
- `+ R` — measurement noise variance (how noisy is the barometer).
- The division gives the ratio of how much the model is uncertain vs how much the sensor is uncertain.
- `P_pred * Hᵀ` — 3×1 vector of how each state's uncertainty couples to the altitude measurement.
- K ends up as a 3×1 vector: if R is large (noisy sensor), K is small (distrust measurement). If P_pred is large (uncertain model), K is large (trust measurement).

**Computing the updated state:**

`(z - H * X_pred)` is the innovation — the difference between what the sensor measured and what the model predicted it would measure. If the model was perfect, this would be zero.

`K * innovation` — a 3×1 correction vector. Even though you only measured altitude, the correction propagates to velocity and acceleration through the off-diagonal covariances.

**Updating covariance:**

After incorporating a measurement you know more, so P shrinks. If K is large (measurement trusted), P shrinks a lot. If K is small, P barely changes.

### Why it is called EKF but is not one

The Extended Kalman Filter is for nonlinear systems — it linearises around the current estimate at each step. But the dynamics model here is linear (constant-acceleration kinematics) and the measurement is linear (direct altitude observation). This is technically a plain KF. The name is probably aspirational from when IMU fusion was planned — projecting IMU acceleration through a quaternion rotation is nonlinear and would require a true EKF.

### What it gives you

A smoothed, fused estimate of altitude and — crucially — velocity. The barometer alone cannot give velocity directly; differentiating altitude amplifies noise badly. The KF integrates the kinematic model to provide a clean velocity estimate, which is exactly what the closed-loop controller needs.

---

## 4. The 9-Term CFD Polynomial

### The problem

Aerodynamic drag on the rocket depends on the airbrake cross-sectional area A, the air density ρ (which changes with altitude), and velocity v. Analytical derivation of Cd for a complex airbrake geometry is not tractable, so the designer ran CFD (Computational Fluid Dynamics) simulations across a grid of (A, ρ, v) combinations and measured the resulting Cd.

### Polynomial regression

The CFD dataset gives points of (A, ρ, v) → Cd. A smooth, cheap-to-evaluate function is then fitted. The basis functions chosen are all combinations of the inputs up to second order:

```
[1, A, ρ, v, A², A·ρ, A·v, ρ², v²]
```

That is 9 terms (hence 9-term). Least-squares regression finds coefficients c₀...c₈:

```
Cd = c₀ + c₁·A + c₂·ρ + c₃·v + c₄·A² + c₅·A·ρ + c₆·A·v + c₇·ρ² + c₈·v²
```

In matrix form: `c = (XᵀX)⁻¹Xᵀy` where X is the matrix of basis function evaluations across all CFD samples and y is the vector of corresponding Cd values.

### Why this set of terms

It is a second-order polynomial in three variables with no cubic terms or three-way interactions. It is simple enough to fit well with a modest CFD dataset, cheap to evaluate on a microcontroller (just multiplications and additions), and captures the main nonlinear interactions (A², A·v, etc.) that matter for drag.

### The specific coefficients

```
[1.2713593, -89.295723, -0.13991502, -0.0006423065,
 2402.8217, 5.0624507, 0.011055673, 0.0020892442, 6.7298901e-07]
```

These were fitted to CFD runs for the 2024 rocket geometry specifically. If the 2026 airbrake fins are a different shape or size, new CFD runs and a new polynomial fit are required. The Cd polynomial feeds directly into the terminal velocity and apogee estimation calculations, so an inaccurate polynomial means an inaccurate controller.

### Where it sits in the control chain

Inside `ClosedLoopController::getSurfaceArea()`:

1. Cd is computed from current estimated (A, ρ, v) via the polynomial
2. Terminal velocity: `Vt = sqrt(2 * m * g / (Cd * ρ * A))`
3. Estimated apogee: `yMax = (Vt² / 2g) * ln((v² + Vt²) / Vt²)`
4. Target velocity from that apogee is computed
5. Velocity error drives gain-scheduled proportional control
6. Output is a desired cross-sectional area in m²

---

## 5. Raw 6-Axis IMU vs Fusion Chip, and the Mahony/Madgwick Filter

### BNO08x (old board) — fusion chip

The BNO08x contains a full microcontroller running Bosch's proprietary AHRS algorithm internally. You send it a command ("give me game rotation vectors") and it returns a quaternion. All sensor fusion — integrating gyroscope, correcting drift with accelerometer — happens inside the chip. From the firmware's perspective this is trivial: read quaternion over I2C.

### LSM6DS3TR-C (new board) — raw MEMS sensor

This chip gives raw accelerometer readings in m/s² and gyroscope readings in rad/s at a configurable sample rate. There is no onboard fusion. The firmware receives numbers like "1.2 m/s² on X, -0.3 on Y, 9.7 on Z" and must turn that into orientation itself.

### The drift problem

A gyroscope measures angular rate. To get orientation you integrate rate over time — but gyroscopes have bias (a small constant error) that, when integrated, produces orientation error that grows without bound. Leave a gyroscope sitting still for a minute and it will report you have rotated. The accelerometer helps: in a relatively steady state it points toward gravity and gives an absolute reference for pitch and roll. The fusion algorithm combines both to get drift-corrected orientation.

### Mahony filter

Maintains an estimate of orientation as a quaternion. Each step:
1. Integrates the gyroscope rate to propagate orientation forward
2. Computes the error between where gravity should be (given current quaternion) and where the accelerometer says it actually is
3. Feeds that error back as a correction to the gyroscope integration via a PI controller

It is lightweight, runs in microseconds on a Cortex-M4, and is well-suited to applications without a magnetometer.

### Madgwick filter

Similar philosophy but uses gradient descent optimisation to find the quaternion rotation that minimises error between the measured accelerometer direction and the expected gravity direction. Slightly simpler to implement than Mahony, similar computational cost, comparable accuracy for this application.

### The symmetric error assumption and its limits

Both filters treat the accelerometer correction symmetrically — a 10° error in any direction gets the same correction magnitude. There is no concept of being more confident about one axis than another. Contrast this with the Kalman filter, which maintains a full covariance matrix P tracking different uncertainty levels explicitly.

More critically: both filters assume the accelerometer is a reliable indicator of "down" at all times. **During high-g phases (motor burn), the accelerometer sees the vector sum of gravity, thrust, and aerodynamic forces — not just gravity.** The filter will interpret this spurious signal as orientation information and pull the quaternion estimate toward a wrong answer.

**Practical mitigation — adaptive gain scheduling:** Reduce the accelerometer correction gain Kp when the accelerometer magnitude deviates significantly from 1g:

```c
float accel_magnitude = sqrt(ax*ax + ay*ay + az*az);
float error_from_1g = fabs(accel_magnitude - 9.81);
float adaptive_Kp = Kp * max(0, 1 - error_from_1g / threshold);
```

During motor burn Kp drops to nearly zero and the filter runs gyroscope-only. During coasting (gravity + small aero forces) Kp recovers and drift correction resumes.

For the CAS board this is manageable: the board's control tasks (airbrake and roll control) only activate during coasting, by which point the high-g burn phase is over and the filter has time to reconverge.

### For the rocket specifically

Roll rate is available directly from the gyroscope Z-axis — no filter needed for that. The filter is needed to produce the orientation quaternion for projecting accelerometer data into the world frame for EKF fusion. The output quaternion is in the same format as the BNO08x was providing, so the rest of the pipeline can remain structurally similar.

---

## 6. Arduino/PlatformIO vs STM32 HAL, and CubeMX

### Arduino framework

A high-level abstraction layer that hides almost all hardware details. `pinMode()`, `digitalWrite()`, `Serial.begin()`, `micros()` — these map to the underlying hardware registers without requiring knowledge of them. Fast to develop in, but provides limited control over timing, interrupts, and peripheral configuration. The Teensy 4.1 runs Arduino on top of its NXP chip.

### PlatformIO

A build system and IDE extension that manages compiling and flashing for many embedded targets including Teensy. It downloads toolchains and libraries automatically. It is not a hardware abstraction — it just runs the Arduino framework (or others) for you. Think of it as the CMake/pip of the embedded world.

### STM32 HAL (Hardware Abstraction Layer)

The STM32's equivalent of Arduino but lower-level and more explicit. Instead of `Serial.begin(9600)`, you configure a UART peripheral by writing a struct with baud rate, word length, stop bits, parity, etc. and calling `HAL_UART_Init()`. Nothing happens by magic — every peripheral must be explicitly initialised, every clock configured, every interrupt enabled. It is more verbose but gives full control and deterministic timing, which is important for a flight computer with strict loop timing requirements.

### Why the switch was made

**Timing is not deterministic on Arduino.** Arduino's `loop()` runs as fast as it can with no guarantees. If an SD card write takes 3ms longer than expected, everything downstream is delayed. On STM32 with HAL, a control loop can be placed in a hardware timer interrupt that fires at exactly 1kHz regardless of what else is happening.

**Parallelism is difficult on Arduino.** Everything is sequential in one loop. On STM32 with FreeRTOS, genuinely concurrent tasks can run — IMU reading at 1kHz, EKF at 500Hz, SD logging at 100Hz — with proper priority scheduling ensuring important tasks always run on time.

**The Arduino abstraction hides things now needed.** DMA (Direct Memory Access — peripherals write directly to memory without CPU involvement, so the processor is not idle waiting for SPI transfers), precise interrupt configuration, and power modes exist on the Teensy hardware but the Arduino layer makes them awkward to use properly.

**The STM32F405 is an industry standard.** The original Pixhawk ran on an F405. It is well-understood, has a large ecosystem, is reliable at rocketry altitudes, has hardware floating point (Cortex-M4F), runs at 168MHz, and has all the required peripherals: multiple SPI buses, I2C, CAN, hardware timers for PWM, ADC.

**The raw IMU is the right choice for a serious flight computer.** The BNO08x is a black box — you cannot tune the internal AHRS, implement adaptive gain scheduling during high-g phases, or access raw data for your own filter. A raw IMU gives full control over the estimation pipeline, at the cost of having to implement AHRS yourself.

### CubeMX

A graphical tool from ST that generates HAL initialisation code. You open it, see a visual diagram of the STM32 chip, click on pins to assign peripherals (SPI1 on these pins, I2C1 on those pins, timer PWM on this pin), configure the clock tree (set PLL multipliers to hit 168MHz), and it generates a complete C project with all the `MX_SPI1_Init()`, `MX_I2C1_Init()` etc. functions filled in correctly. Application code is then written on top of that generated scaffold.

### Current CubeMX problem

The `.ioc` file (CubeMX project) is incomplete. The clock is at 16MHz (the HSI default — the chip runs off its internal RC oscillator) instead of 168MHz from the PLL. That means everything runs at roughly 1/10th the intended speed. SPI1, SPI2, I2C1 are not configured so there are no generated drivers for the IMU, flash, or barometer. A timer for the second servo PWM is not set up. Until CubeMX is finished and HAL code regenerated, none of the new peripherals can be used.

The required additions to the CubeMX config are:

- PLL: configure to 168MHz (HSE 25MHz → PLL → 168MHz SYSCLK)
- SPI1: IMU (LSM6DS3TR-C) with EXTI for DRDY interrupt
- SPI2: SD card + external flash with separate chip selects
- I2C1: Barometer (MPL3115A2R1)
- Additional timer: second servo PWM output
- GPIO: limit switches, LED/NeoPixel, current sense enable

---

## 7. Summary of Known Bugs in Old Firmware

| Location | Bug | Impact |
|---|---|---|
| `Rocket::setup()` | `ClosedLoopController::Config` is constructed but `OpenLoopController` is assigned — closed loop never runs | Critical: rocket never uses the designed controller |
| `Imu::readSensor()` | `return;` in non-void function — undefined behaviour if no sensor event available | High: can return garbage quaternion data |
| `Barometer::getAltitudeAGL()` | Returns altitude ~10x too large | Low: function not used in control path |
| `StateEstimator::begin()` | Initial covariance uses altitude std for all three states including velocity and acceleration | Medium: EKF may converge slowly at startup |
| `ClosedLoopController::calculateRocketCrossArea()` | Returns `minArea + optimalArea` instead of just `optimalArea` | Medium: cross section can exceed physical maximum |
| IMU not fused | EKF only uses barometer — IMU acceleration never integrated | Medium: velocity estimates noisier than needed |

---

## 8. Development Priorities for 2026 Board

In suggested order:

1. Finish CubeMX — clock tree to 168MHz, all peripheral configs, regenerate HAL init code
2. IMU driver — SPI read of LSM6DS3, basic accel + gyro output
3. Barometer driver — I2C read of MPL3115A2R1
4. Mahony or Madgwick AHRS — roll rate and orientation from raw IMU, with adaptive gain scheduling
5. EKF port — altitude + velocity from baro, add IMU accel as second measurement
6. Servo PWM — both servos at correct 50Hz from timer
7. Airbrake controller — port ClosedLoopController, fix all bugs, update physical parameters
8. Roll controller — design and implement from scratch
9. State machine — port flight state logic
10. SD logging — FatFS, same CSV format
11. CAN bus — inter-board comms (can be deferred)
