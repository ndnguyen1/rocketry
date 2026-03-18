# UTS Rocketry — CAS Board: System Documentation

This document covers the full Control Actuation System (CAS) codebase: what exists, how it works, what is broken, and what needs to be built for the 2026 board. It is intended as a reference for design discussions.

---

## 1. What the CAS Board Does

The CAS board sits inside the rocket and does two jobs during the coasting phase (after motor burnout, before apogee):

1. **Airbrake control** — deploys drag fins to bleed off kinetic energy so the rocket hits a target apogee altitude. This is a closed-loop controller that estimates where the rocket will end up and adjusts the brakes to steer it toward the target.
2. **Roll control** — stabilises the rocket's roll rate using a separate servo. This is new for 2026 and does not exist in the old firmware.

It also handles:
- Sensor acquisition (IMU, barometer)
- State estimation (Kalman filter)
- Data logging (SD card)
- Flight state management (on pad → ascent → coasting → apogee)

---

## 2. Hardware: Old vs New

| | Goanna 2024 (old, working) | CASBoard 2026 (new, no firmware) |
|---|---|---|
| **MCU** | Teensy 4.1 (NXP iMXRT1062, 600 MHz, Arduino framework) | STM32F405RGT6 (ARM Cortex-M4F, 168 MHz, STM32 HAL) |
| **Build system** | PlatformIO + Arduino | STM32CubeMX / STM32CubeIDE |
| **IMU** | Adafruit BNO08x (I2C) — fusion chip, outputs quaternions directly | LSM6DS3TR-C (SPI) — raw 6-axis (accel + gyro), no onboard fusion |
| **Barometer** | SparkFun BMP581 (I2C, address 0x46) | MPL3115A2R1 (I2C) |
| **Storage** | SD card on SPI (CS pin 10) | SD card on SPI2 + external flash on SPI2 |
| **Servo outputs** | 1x airbrake servo (PWM pin 5) | 2x servos (airbrake + roll control, timer PWM) |
| **Position feedback** | Quadrature encoder (pins 3 & 4, interrupt-driven) | Potentiometer (ADC input) |
| **Limit switches** | Not present | Digital inputs (GPIO) |
| **CAN bus** | Not present | CAN2 with SN65HVD230 transceiver (333 kHz) |
| **Current sensing** | Not present | INA180A2 on servo rail |
| **Cameras** | 3x RunCam (UART: Serial2/3/4) | Not planned |
| **Debug** | USB via Teensy | SWD (SWDIO, SWCLK, NRST) |
| **Power** | Via Teensy | LDL1117 3.3V LDO + dedicated 5V servo rail |

### Key change: IMU

The BNO08x in the old board is a "sensor fusion" chip — it runs its own AHRS algorithm internally and hands you a quaternion. You just read it.

The LSM6DS3TR-C in the new board gives you raw accelerometer (m/s²) and gyroscope (rad/s) data. **We have to implement attitude estimation ourselves** (e.g. Mahony filter or Madgwick filter) to get roll rate and orientation from those raw values. This is the biggest new firmware challenge.

### Key change: Two servos

The old board had one servo for airbrakes. The new board has two: one for airbrakes, one for roll control. These are independent control loops that need to run simultaneously.

---

## 3. Old Firmware Architecture

The old code is PlatformIO/Arduino structured as a set of libraries under `lib/`. The entry point is `src/main.cpp`.

```
main.cpp
└── Rocket          (top-level orchestrator)
    ├── Devices     (hardware abstraction: all sensors + actuators)
    │   ├── Barometer   (BMP581 via I2C)
    │   ├── Imu         (BNO08x via I2C)
    │   ├── CasServo    (PWM servo with calibration)
    │   ├── Encoder     (quadrature encoder)
    │   ├── Sd          (SD card logging)
    │   └── Runcam x3  (camera control via UART)
    ├── StateEstimator  (wraps EKF, converts pressure to altitude)
    │   └── EKF         (3-state Kalman filter)
    └── Controller*     (polymorphic: open-loop or closed-loop)
        ├── OpenLoopController
        └── ClosedLoopController
```

The `Atmosphere` library provides ISA air density calculations. `AreaToAngle` converts a cross-sectional area (m²) to a servo angle (degrees).

---

## 4. Flight State Machine

Defined in `lib/StateMachine/RocketState.hpp`. The enum has 8 states but only the first 4 are handled:

```
ON_PAD  →  ASCENT  →  COASTING  →  APOGEE
```

**DESCENT, DROGUE_DEPLOY, MAIN_DEPLOY, LANDED** are declared but never used — the `default` case in the switch falls through to `handleApogeeState()`.

### Transition logic

| Transition | Condition |
|---|---|
| ON_PAD → ASCENT | `velocity > 30 m/s` AND `filteredAltitude > 10 m` |
| ASCENT → COASTING | velocity has not increased for 5 consecutive loop iterations (motor burnout detection) |
| COASTING → APOGEE | velocity has been negative for 5 consecutive loop iterations |

### What happens in each state

- **ON_PAD:** Just logs data. Waits. After 20 minutes on pad, beeps and starts RunCam 2 (launch pad camera).
- **ASCENT:** Detects burnout by counting frames where velocity didn't increase. Tracks max velocity.
- **COASTING:** Calls `manageAirbrakes()` every loop. Watches for apogee.
- **APOGEE:** Commands servo to angle 0 (airbrakes closed). No further control.

---

## 5. Sensor Layer

### 5.1 Barometer (BMP581)

`lib/devices/Barometer.hpp/.cpp`

- Initialises on I2C address `0x46`
- Configures IIR filter coefficient 127 for both temperature and pressure (heavy smoothing)
- `getPressure()` → raw pressure in Pascals
- `getTemperature()` → temperature in °C
- `getRawAltitude(pressure)` → standard atmosphere formula: `44307.69 * (1 - (P/1013.25)^0.190284)` — altitude above sea level in metres
- `getAltitudeAGL(pressure)` → same formula but using `groundPressure` as reference instead of 1013.25 hPa. **BUG: this returns values ~10x too large.** The comment in the code says `//FIX 10 times greater than it should be`. This function is not used by the state estimator (it uses `getRawAltitude` via `baroToAlt` internally), so it hasn't caused a crash in flight but it's wrong.

### 5.2 IMU (BNO08x)

`lib/devices/Imu.hpp/.cpp`

- Initialises on I2C, up to 10 attempts
- Requests `SH2_GAME_ROTATION_VECTOR` — a fused quaternion that doesn't use the magnetometer (good for indoor/metal environments)
- Returns a `Quaternion` struct: `{qr, qi, qj, qk}` (real + imaginary parts)
- **BUG:** `readSensor()` has `return;` on the early-exit path (when no sensor event is available). This is a `return` with no value in a function that returns `Quaternion` — undefined behaviour. The comment says `//FIX`. In practice this means if the IMU hasn't produced data yet in a given loop cycle, the function returns garbage.
- The quaternion data is **only logged to SD**. It is not fed into the EKF or used for control. The IMU is effectively a passenger.

### 5.3 Encoder

`lib/devices/Encoder.hpp/.cpp`

- Quadrature encoder on pins 3 and 4 (interrupt-driven, `FOUR0` latch mode via `mathertel/RotaryEncoder`)
- `getEncoderAngle()` returns current angle in degrees
- `setEncoder(0)` zeros the encoder
- Used only for logging — the encoder reads physical airbrake position for data but is not part of the control loop

---

## 6. State Estimation

`lib/StateEstimator/` wraps `lib/EKF/`.

### 6.1 Startup calibration

`StateEstimator::begin()` runs a 5-second calibration loop at startup:
1. Reads pressure as fast as possible (with 10ms delays)
2. Calculates average pressure → this becomes `referencePressure`
3. Calculates standard deviation of pressure readings → converts to altitude standard deviation
4. Uses that altitude std as the initial uncertainty for the EKF covariance matrices (P, Q, R)

The reference pressure is what the barometric formula uses as "sea level" — so all altitudes from this point forward are relative to the launch site, not actual sea level.

### 6.2 The EKF

`lib/EKF/EKF.h/.cpp` — a standard linear Kalman filter (called EKF in name, but the dynamics model is linear so it's technically a KF).

**State vector:** `X = [altitude (m), vertical velocity (m/s), vertical acceleration (m/s²)]`

**Process model (state transition matrix A):**
```
[1   dt   0.5*dt²]   [alt]         [alt + vel*dt + 0.5*acc*dt²]
[0    1    dt    ] * [vel]    =     [vel + acc*dt              ]
[0    0    1    ]    [acc]          [acc                        ]
```
This is a constant-acceleration kinematic model.

**Measurement:** Only barometer altitude is fused. The measurement matrix `H = [1, 0, 0]` (we observe altitude directly).

**How it's called:**
- Every loop: `stateEstimator.update()` → calls `EKF::Update(baroAltitude)` which runs the full KF correction step using the latest pressure reading
- Every loop: `stateEstimator.getRocketState()` → calls `EKF::Predict()` then reads `X(0)` (altitude) and `X(1)` (velocity)

**Note on IMU:** The IMU acceleration is never fused. The EKF is running blind on barometer only. The `//Fuse IMU and Barometer` comment at the top of `EKF.h` was aspirational.

**Altitude conversion formula** used inside StateEstimator:
```cpp
altitude = 44330 * (1 - (pressure / referencePressure)^0.1902949)
```
This is the standard international barometric formula. Note: pressure is divided by 100 inside StateEstimator before passing to this formula (converting Pa to hPa), but the BMP581 returns Pa — the `/ 100` is applied in the right place.

---

## 7. Control System

### 7.1 Interface

`lib/Controller/Controller.hpp` defines an abstract base class:
```cpp
class Controller {
public:
  virtual float getSurfaceArea(float timestamp, float altitude, float velocity) = 0;
};
```

`getSurfaceArea()` returns the desired total rocket cross-sectional area in m². The caller then converts this to a servo angle.

### 7.2 Bug: wrong controller instantiated

In `Rocket::setup()`:
```cpp
// This config is prepared but never used:
ClosedLoopController::Config cfg = {2500, 13.0, 0.018801, 0.005352 + 0.018801};
// This overwrites it with open-loop:
this->controller = new OpenLoopController();
```
The closed-loop controller is never instantiated. The rocket always flies on open-loop.

### 7.3 Open-Loop Controller

`lib/Controller/OpenLoopController.cpp`

Simple time/velocity gating:
- If `timestamp < 2s` since coasting start → return 0 (closed)
- If `timestamp < 8s` OR `velocity >= 100 m/s` → return 1 (fully open)
- Otherwise → return 0 (closed)

The return values `0` and `1` are not in m² — they're passed to `AreaToAngle::convertFromArea()` which scales them by `*10000` to get cm² equivalent, so `0` maps to closed and `1` to... 10000 cm² which is way above `kMaxArea = 241.017 cm²` and thus clamps to 90° (fully open). This is a hack that works but is not clean.

### 7.4 Closed-Loop Controller (intended, not currently used)

`lib/Controller/ClosedLoopController.hpp/.cpp`

This is the real control logic. Each call to `getSurfaceArea()` does:

**Step 1 — Air density**
```
ρ = ρ₀ * (T/T₀)^((-g*M)/(R*λ) - 1)
```
Using International Standard Atmosphere constants (ISA troposphere model).

**Step 2 — Coefficient of drag (Cd)**
A 9-term polynomial regression model fitted from CFD data:
```
Cd = c₀ + c₁*A + c₂*ρ + c₃*v + c₄*A² + c₅*A*ρ + c₆*A*v + c₇*ρ² + c₈*v²
```
Where A is cross-sectional area (m²), ρ is air density (kg/m³), v is velocity (m/s).
Coefficients: `[1.2713593, -89.295723, -0.13991502, -0.0006423065, 2402.8217, 5.0624507, 0.011055673, 0.0020892442, 6.7298901e-07]`

**Step 3 — Terminal velocity**
```
Vt = sqrt(2 * m * g / (Cd * ρ * A))
```

**Step 4 — Estimated apogee** (from NASA flight equations with drag)
```
yMax = (Vt² / 2g) * ln((v² + Vt²) / Vt²)
estimatedApogee = currentAltitude + yMax
```

**Step 5 — Target velocity trajectory**
Given a target apogee `h_target` and current altitude `h`, what velocity should the rocket have right now to coast to exactly `h_target`?
```
altitudeError = h_target - h
w = altitudeError / (Vt² / 2g)
v_target = sqrt(Vt² * exp(w) - Vt²)
```
(Guard: if currentAltitude > targetApogee, return v_target = 0)

**Step 6 — Velocity error**
```
velocityError = v_target - v_current
```

**Step 7 — Gain scheduling**
4 gain bands based on current velocity:

| Velocity range (m/s) | Gain |
|---|---|
| 0 – 40 | -0.5576 |
| 40 – 80 | -0.1491 |
| 80 – 140 | -0.0500 |
| 140 – 180 | -0.0219 |
| > 180 | -0.035 (default, not really reached) |

Gains are negative because: if `v_current > v_target` (rocket going too fast → will overshoot), `velocityError` is negative, and multiplying by a negative gain gives a positive area increase (deploy more brakes).

**Step 8 — Optimal cross-section area**
```
optimalArea = gain * velocityError
optimalArea = clamp(optimalArea, minArea, maxArea)
```
Config values: `minArea = 0.018801 m²`, `maxArea = 0.024153 m²` (= 0.018801 + 0.005352).

### 7.5 Area to Servo Angle

`lib/AreaToAngle/AreaToAngle.h`

The area returned by the controller is in m². This function converts to servo angle (0–90°).

```
area_cm² = area_m² * 10000
range: kMinArea = 188.52 cm², kMaxArea = 241.017 cm²
```

Inverse quadratic mapping (fitted to the physical airbrake geometry):
```
angle = (-b + sqrt(b² - 4*a*(kMinArea - area_cm²))) / (2*a)
where a = -0.006, b = 1.1233
```

If area < kMinArea → angle = 0 (fully closed).
If area > kMaxArea → angle = 90 (fully open).

### 7.6 Servo (CasServo)

`lib/devices/CasServo.hpp/.cpp`

Takes a logical angle 0–90° and maps it to the physical servo PWM range.

```
physicalAngle = ((k90Pos - kClosedPos) / 90.0) * logicalAngle + kClosedPos
```

Configured values: `kClosedPos = 165`, `k90Pos = 20`, `kOpenPos = 20`.
So 0° → PWM 165, 90° → PWM 20. The servo runs in reverse (higher angle = lower PWM).

Backlash compensation is implemented (`kBackLashCompensation = 0` currently, so it's a no-op) — it adds/subtracts a fixed offset when direction changes.

`sendDirect(pos)` bypasses calibration and writes raw PWM value directly — used during init.

---

## 8. SD Logging

`lib/devices/Sd.hpp/.cpp` — SD card on SPI, chip select pin 10.

Every loop iteration, one CSV line is built up in a String:
```
timestamp, stateID, encoderAngle, pressure, temperature, rawAltitude, filteredAltitude, velocity, qr, qi, qj, qk, servoAngle
```

Written to SD every loop. Flushed (closed and reopened) every 1 second to reduce data loss risk.

---

## 9. Known Bugs in Old Code

| Location | Bug | Impact |
|---|---|---|
| `Rocket::setup()` | `ClosedLoopController::Config` is constructed but `this->controller = new OpenLoopController()` is assigned — closed loop never runs | **Critical: rocket never uses the designed controller** |
| `Imu::readSensor()` | `return;` on line 42 in a non-void function — UB if no sensor event available | High: can return garbage quaternion data |
| `Barometer::getAltitudeAGL()` | Returns altitude ~10x too large (comment: `//FIX`) | Low: this function is not used in the control path |
| `StateEstimator::begin()` | Initial covariance uses `rawAltitudeStd` for all three states (position, velocity, acceleration) — velocity and acceleration uncertainty should be different | Medium: EKF may converge slowly at startup |
| `ClosedLoopController::calculateRocketCrossArea()` | Returns `minArea + optimalArea` — but `optimalArea` is already clamped to `[minArea, maxArea]`, so total cross section can be up to `minArea + maxArea` which is not physically meaningful | Medium: needs to return just `optimalArea` |
| `OpenLoopController::getSurfaceArea()` | Returns `1` for "open" — relies on `AreaToAngle` clamping to work correctly, not a proper area | Low: works in practice |
| IMU not fused | EKF only uses barometer. IMU acceleration not used. | Medium: velocity estimates noisier than needed |

---

## 10. New Board: What Needs to Be Built

### 10.1 CubeMX / Hardware Config (incomplete)

The STM32CubeMX `.ioc` file currently has:
- ADC1, ADC2, CAN2, TIM14, SWD configured
- Clock stuck at 16 MHz (HSI only — PLL not configured)

**Needs to be added:**
- PLL: configure to 168 MHz (HSE 25 MHz → PLL → 168 MHz SYSCLK)
- SPI1: IMU (LSM6DS3TR-C) — SCK, MOSI, MISO, CS + EXTI for DRDY
- SPI2: SD card + external flash — SCK, MOSI, MISO, CS_SD, CS_FLASH
- I2C1: Barometer (MPL3115A2R1)
- TIM for second servo PWM output
- GPIO: limit switches, LED/NeoPixel, current sense enable

### 10.2 Device Drivers (all new)

| Driver | Notes |
|---|---|
| **LSM6DS3TR-C** (IMU) | SPI, raw accel + gyro. Need to configure ODR, full-scale range. Read via DRDY interrupt or polling. |
| **MPL3115A2R1** (barometer) | I2C. Different register map from BMP581. Need to port altitude reading. |
| **SD card** (FatFS) | Use STM32 HAL + FatFS middleware. Same logging structure as old code. |
| **PWM servos** | HAL timer PWM for both airbrake and roll control servos. Standard 50 Hz, 1000–2000 µs pulse width. |
| **ADC** (potentiometer) | HAL ADC for airbrake position feedback. |
| **CAN** (optional first pass) | CAN2 with SN65HVD230. HAL bxCAN driver. |

### 10.3 AHRS (new, required)

Because the LSM6DS3 is raw 6-axis (no onboard fusion), we need an Attitude and Heading Reference System algorithm.

For **roll control**, we specifically need:
- Roll angle (rotation around the rocket's long axis)
- Roll rate (directly from gyroscope Z-axis in body frame)

**Recommended approach: Mahony filter** or Madgwick filter. Both are lightweight, run well on Cortex-M4, and handle the 6-DOF (no magnetometer) case. The Madgwick filter is slightly simpler to implement.

For **airbrake control**, we need:
- Vertical acceleration (to fuse with baro in EKF)

This requires knowing the rocket orientation to project IMU accelerometer readings onto the vertical axis. So AHRS is a prerequisite for proper IMU-baro fusion.

### 10.4 State Estimator (port + improve)

Port the EKF from `lib/EKF/`. Replace Arduino-specific headers (`Arduino.h`, `ArduinoEigenDense.h`) with:
- `arm_math.h` (CMSIS DSP) or a lightweight matrix library
- `HAL_GetTick()` / DWT cycle counter instead of `micros()`

**Improvement:** Fuse IMU vertical acceleration as a second measurement into the EKF. This gives much better velocity estimates during high-g phases.

Updated measurement model with IMU:
```
H = [1  0  0]   (baro measures altitude)
    [0  0  1]   (IMU measures acceleration)
```

### 10.5 Airbrake Controller (port + fix)

Port `ClosedLoopController` with the following fixes:
1. **Fix the instantiation bug** — actually use `ClosedLoopController`, not `OpenLoopController`
2. **Fix `calculateRocketCrossArea()`** — should return just `optimalArea` (the airbrake-only contribution), not `minArea + optimalArea`
3. **Update physical parameters** for the 2026 rocket (mass, reference area, target apogee)
4. **Update Cd polynomial** if new CFD data is available for the 2026 airbrake geometry
5. **Update AreaToAngle** mapping for the new airbrake hardware geometry

### 10.6 Roll Controller (new)

The roll control loop does not exist anywhere in the old code. It needs to be designed from scratch.

**What it is:** A feedback controller that reads roll rate from the IMU gyroscope and commands the roll-control servo to reduce roll rate toward zero (or toward a target roll rate).

**Basic structure:**
```
rollRate = imu.getGyroZ()   // rad/s around body Z-axis (rocket long axis)
rollError = targetRollRate - rollRate
servoCommand = rollGain * rollError
rollServo.send(clamp(servoCommand, minAngle, maxAngle))
```

This is a rate controller (P-controller on roll rate). A PD controller (adding derivative of roll rate, i.e. roll acceleration) may be needed if a P-only controller is too oscillatory.

**Things to figure out:**
- What is the roll control mechanism? (canted fins? A separate movable surface?) The schematic shows a servo but the geometry isn't documented.
- What is the target roll rate? (Probably zero for stabilisation, or a specific spin rate for stability)
- What are the gains? These need to be tuned — either by simulation or test flights.
- Does roll control run at the same time as airbrake control, or only during certain phases?

### 10.7 Main Loop / State Machine (port)

The state machine logic can be ported directly with minimal changes. The key structural change is replacing Arduino `loop()` with an RTOS task or a `while(1)` with `HAL_Delay()`.

**Suggested structure for STM32:**
```
main()
├── SystemClock_Config()   (168 MHz PLL)
├── MX_GPIO_Init()
├── MX_SPI1_Init()         (IMU)
├── MX_SPI2_Init()         (SD + flash)
├── MX_I2C1_Init()         (baro)
├── MX_TIM14_Init()        (servo PWM)
├── MX_ADC1_Init()         (position feedback)
├── MX_CAN2_Init()         (telemetry bus)
└── FlightComputer::run()  (replaces Rocket::setup() + Rocket::loop())
```

---

## 11. Development Priorities

Suggested order of work:

1. **CubeMX** — finish clock tree (168 MHz), add all peripheral configs, generate HAL init code
2. **IMU driver** — SPI read of LSM6DS3, basic accel + gyro output
3. **Barometer driver** — I2C read of MPL3115A2
4. **Mahony/Madgwick AHRS** — get roll rate and orientation from raw IMU
5. **EKF port** — altitude + velocity estimation from baro (+ IMU accel fusion)
6. **Servo PWM** — both servos outputting correct 50 Hz PWM from timer
7. **Airbrake controller** — port ClosedLoopController, fix bugs, update parameters
8. **Roll controller** — design and implement
9. **State machine** — port flight state logic
10. **SD logging** — FatFS, same CSV format
11. **CAN bus** — inter-board comms (can be deferred to last)

---

## 12. Physical Parameters (2024 rocket, needs update for 2026)

These are the values currently in the closed-loop controller config:

| Parameter | Value | Unit |
|---|---|---|
| Target apogee | 2500 | m AGL |
| Rocket mass | 13.0 | kg |
| Min cross-sectional area (no brakes) | 0.018801 | m² |
| Max cross-sectional area (full brakes) | 0.024153 | m² (= 0.018801 + 0.005352) |
| Airbrake-only area | 0.005352 | m² |

Min area (body tube only): `0.018801 m²` → tube diameter ≈ 154 mm
Max additional area from brakes: `0.005352 m²` (per brake fin exposed area × number of fins)

The Cd polynomial coefficients were fitted from CFD data specific to this geometry. **If the 2026 airbrake geometry is different, new CFD runs and a new polynomial fit are needed.**

---

## 13. Coordinate System Convention

Not explicitly documented in the old code. Assumed:
- Z-axis = rocket long axis (positive = up / toward nose)
- Vertical velocity positive = upward
- Roll = rotation around Z-axis

The BNO08x game rotation vector uses the SH2 coordinate convention. When porting to raw LSM6DS3, the axis mapping needs to be confirmed against the board mounting orientation on the new PCB.

---

## 14. File Reference (Old Repo)

```
Goanna-cas-board-2024/
├── src/main.cpp                          — entry point (3 lines)
├── lib/
│   ├── Rocket/Rocket.hpp/.cpp            — top-level orchestrator, state machine
│   ├── devices/
│   │   ├── Devices.hpp/.cpp              — hardware aggregator
│   │   ├── Barometer.hpp/.cpp            — BMP581 driver
│   │   ├── Imu.hpp/.cpp                  — BNO08x driver (has bugs)
│   │   ├── CasServo.hpp/.cpp             — servo with calibration + backlash
│   │   ├── Encoder.hpp/.cpp              — quadrature encoder
│   │   ├── Sd.hpp/.cpp                   — SD card logging
│   │   └── Runcam.hpp/.cpp               — RunCam camera control
│   ├── StateEstimator/
│   │   ├── StateEstimator.h/.cpp         — baro calibration + EKF wrapper
│   ├── EKF/
│   │   ├── EKF.h/.cpp                    — 3-state Kalman filter
│   ├── Controller/
│   │   ├── Controller.hpp                — abstract base class
│   │   ├── ClosedLoopController.hpp/.cpp — apogee-targeting controller (NOT USED)
│   │   └── OpenLoopController.hpp/.cpp   — simple timed open/close
│   ├── AreaToAngle/AreaToAngle.h         — area m² → servo angle degrees
│   ├── Atmosphere/Atmosphere.hpp/.cpp    — ISA air density model
│   └── StateMachine/
│       ├── RocketState.hpp               — flight state enum
│       └── BrakeState.hpp                — airbrake state enum
└── platformio.ini                        — build config (Teensy 4.1 primary target)
```
