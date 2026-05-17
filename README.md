<div align="center">

<img src="https://img.shields.io/badge/ohmo-electric%20mobility-FF6B35?style=for-the-badge&logoColor=white" />

# ohmo

**Electric rides. Elevated experiences.**

*The world's first EV-native mobility and social discovery platform.*  
*Built entirely in Rust.*

<br />

[![Built with Rust](https://img.shields.io/badge/Built%20with-Rust-000000?style=flat-square&logo=rust&logoColor=FF6B35)](https://www.rust-lang.org/)
[![UI Framework](https://img.shields.io/badge/UI-Blinc%20%28wgpu%29-FF6B35?style=flat-square)](https://github.com/neoqiss/project-blinc)
[![Database](https://img.shields.io/badge/Database-PostgreSQL%20%2B%20Redis-336791?style=flat-square&logo=postgresql&logoColor=white)](https://postgresql.org)
[![License](https://img.shields.io/badge/License-Proprietary-black?style=flat-square)]()
[![Dilution](https://img.shields.io/badge/Equity%20Dilution-0%25-FF6B35?style=flat-square)]()

<br />

> *"In a little while you will see me no more,*  
> *and then after a little while you will see me."*

<br />

---

</div>

## What is Ohmo?

Ohmo is not another Uber clone.

Uber is a marketplace. Ohmo is a platform — one that owns its fleet, controls the full rider experience, and turns every trip into an act of urban discovery. While other ride-hailing companies push notifications, Ohmo surfaces **vibes**. While they track drivers, Ohmo manages **assets**. While they process payments, Ohmo builds **culture**.

Three businesses. One platform. Built in Rust.

| Stream | Description | Year 1 Target |
|--------|-------------|---------------|
| 🚗 **Rides** | EV-only ride hailing, Joburg → Cape Town → Durban | R18M GMV |
| 📍 **Places & Ads** | Location-aware discovery and priority placement | R4M revenue |
| ⚡ **Charging** | Public charging infrastructure, open to all EVs | R2M revenue |

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         OHMO PLATFORM                           │
├──────────────────┬──────────────────┬───────────────────────────┤
│   ohmo-rider     │   ohmo-driver    │      ohmo-ops             │
│   (Blinc UI)     │   (Blinc UI)     │   (Internal Dashboard)    │
│                  │                  │                           │
│  Discovery       │  Fleet Console   │  Executive View           │
│  Booking         │  Trip Queue      │  Controller View          │
│  Social Layer    │  Vehicle Health  │  Maintenance View         │
│  Friends Map     │  Earnings        │  Audit Logs               │
└────────┬─────────┴────────┬─────────┴───────────┬───────────────┘
         │                  │                     │
         └──────────────────┴─────────────────────┘
                            │
                    ┌───────▼────────┐
                    │  ohmo-gateway  │
                    │  (Axum + TLS)  │
                    │  WebSocket Hub │
                    └───────┬────────┘
                            │
         ┌──────────────────┼──────────────────┐
         │                  │                  │
┌────────▼───────┐ ┌────────▼───────┐ ┌────────▼───────┐
│ ohmo-dispatch  │ │ ohmo-telemetry │ │  ohmo-places   │
│                │ │                │ │                │
│ Scoring Engine │ │ MQTT Ingestion │ │ Discovery API  │
│ OCC + Redis    │ │ CAN Bus Decode │ │ Ad Placement   │
│ Dynamic Weights│ │ SoC Pipeline   │ │ Vibe Engine    │
└────────┬───────┘ └────────┬───────┘ └────────┬───────┘
         │                  │                  │
         └──────────────────┼──────────────────┘
                            │
              ┌─────────────┼─────────────┐
              │             │             │
        ┌─────▼────┐  ┌─────▼────┐  ┌────▼──────┐
        │PostgreSQL│  │  Redis   │  │  S3/Spaces│
        │          │  │          │  │           │
        │Audit Logs│  │Live SoC  │  │Media      │
        │Trip Hist │  │Versions  │  │Assets     │
        │Users     │  │Sessions  │  │           │
        └──────────┘  └──────────┘  └───────────┘
                            │
              ┌─────────────┼─────────────┐
              │             │             │
        ┌─────▼────┐  ┌─────▼────┐  ┌────▼──────┐
        │ Teltonika│  │ TomTom / │  │  Private  │
        │ OBD-II   │  │ HERE Maps│  │  APN      │
        │ Dongles  │  │ Energy   │  │ Vodacom / │
        │ CAN Bus  │  │ Routing  │  │ MTN       │
        └──────────┘  └──────────┘  └───────────┘
```

---

## Repository Structure

```
ohmo/
│
├── crates/
│   ├── ohmo-dispatch/          # The brain — EV-native matching engine
│   │   ├── src/
│   │   │   ├── scoring.rs      # DriverScore, Weights, dynamic weight shifting
│   │   │   ├── matching.rs     # Spatial pre-filter → score → CAS assign
│   │   │   ├── concurrency.rs  # OCC with Redis version counters
│   │   │   ├── weights.rs      # Time-of-day weight profiles
│   │   │   └── lib.rs
│   │   └── Cargo.toml
│   │
│   ├── ohmo-telemetry/         # CAN bus → SoC pipeline
│   │   ├── src/
│   │   │   ├── ingestion.rs    # MQTT binary packet decoder
│   │   │   ├── can_decoder.rs  # OBD-II PID → structured telemetry
│   │   │   ├── health.rs       # Dongle ping watchdog (30s timeout)
│   │   │   ├── soc.rs          # State of Charge normalisation
│   │   │   └── lib.rs
│   │   └── Cargo.toml
│   │
│   ├── ohmo-gateway/           # API layer — Axum + WebSocket hub
│   │   ├── src/
│   │   │   ├── routes/
│   │   │   │   ├── rider.rs
│   │   │   │   ├── driver.rs
│   │   │   │   ├── ops.rs
│   │   │   │   └── places.rs
│   │   │   ├── ws/             # WebSocket dispatch fanout
│   │   │   ├── middleware/     # Auth, rate limiting, logging
│   │   │   └── main.rs
│   │   └── Cargo.toml
│   │
│   ├── ohmo-places/            # Discovery, vibes, ad placement engine
│   │   ├── src/
│   │   │   ├── discovery.rs    # Vibe-based place ranking
│   │   │   ├── ads.rs          # Priority placement auction logic
│   │   │   ├── geo.rs          # Proximity + context scoring
│   │   │   └── lib.rs
│   │   └── Cargo.toml
│   │
│   └── ohmo-core/              # Shared types, errors, config
│       ├── src/
│       │   ├── types.rs        # VehicleId, DriverId, RiderId, TripId
│       │   ├── errors.rs       # OhmoError enum
│       │   ├── config.rs       # Environment-based config
│       │   └── lib.rs
│       └── Cargo.toml
│
├── apps/
│   ├── ohmo-rider/             # Rider app — Blinc UI
│   │   ├── src/
│   │   │   ├── screens/
│   │   │   │   ├── home.rs     # Where to tonight?
│   │   │   │   ├── explore.rs  # Vibe discovery + map
│   │   │   │   ├── friends.rs  # Social layer + friend map
│   │   │   │   ├── booking.rs  # Trip request flow
│   │   │   │   └── profile.rs  # CO₂ saved, achievements
│   │   │   └── main.rs
│   │   └── Cargo.toml
│   │
│   ├── ohmo-driver/            # Driver app — Blinc UI
│   │   ├── src/
│   │   │   ├── screens/
│   │   │   │   ├── home.rs     # Fleet console — calm, minimal
│   │   │   │   ├── trips.rs    # Trip queue + active ride
│   │   │   │   ├── vehicle.rs  # EV health, charging, quick actions
│   │   │   │   ├── earnings.rs # Visual earnings + campaigns
│   │   │   │   └── account.rs  # Verification + driver profile
│   │   │   └── main.rs
│   │   └── Cargo.toml
│   │
│   └── ohmo-ops/               # Internal dashboard — Blinc UI
│       ├── src/
│       │   ├── views/
│       │   │   ├── executive.rs    # Fleet pulse — utilisation, revenue, power cost
│       │   │   ├── controller.rs   # Live grid — SoC watchlist, hub metrics, CAS rate
│       │   │   ├── maintenance.rs  # SoH leaderboard, cycle counters, service triggers
│       │   │   └── audit.rs        # Operator override logs, immutable trail
│       │   └── main.rs
│       └── Cargo.toml
│
├── migrations/                 # PostgreSQL migrations (sqlx)
│   ├── 001_init.sql
│   ├── 002_vehicles.sql
│   ├── 003_drivers.sql
│   ├── 004_trips.sql
│   ├── 005_telemetry.sql
│   ├── 006_places.sql
│   └── 007_audit_log.sql
│
├── infra/                      # Deployment config
│   ├── docker-compose.yml
│   ├── Dockerfile.gateway
│   ├── Dockerfile.dispatch
│   ├── Dockerfile.telemetry
│   └── nginx.conf
│
├── docs/
│   ├── dispatch-algorithm.md   # Scoring function deep dive
│   ├── telematics-pipeline.md  # CAN bus → MQTT → Redis flow
│   ├── concurrency-model.md    # OCC + CAS race condition handling
│   └── fleet-ops-dashboard.md  # Internal dashboard spec
│
├── Cargo.toml                  # Workspace root
├── Cargo.lock
├── .env.example
└── README.md
```

---

## The Dispatch Engine

Ohmo's matching engine is EV-native from the ground up. It doesn't treat battery state as a constraint — it treats it as a **first-class variable** in every dispatch decision.

### Scoring Function

Every available driver is scored against every incoming trip request before assignment. The highest composite score wins.

```rust
pub struct Weights {
    pub proximity: f64,
    pub battery:   f64,
    pub wear:      f64,
    pub charge:    f64,
    pub deadhead:  f64,
}

pub struct DriverScore {
    pub proximity_score: f64,  // Distance decay to pickup
    pub battery_score:   f64,  // SoC safety buffer — hard veto at 0.0
    pub wear_score:      f64,  // Fleet degradation balancing
    pub charge_score:    f64,  // Optimal SoC zone management
    pub deadhead_score:  f64,  // Low-SoC routing toward charging hubs
}

impl DriverScore {
    pub fn total(&self, weights: &Weights) -> f64 {
        self.proximity_score * weights.proximity
            + self.battery_score * weights.battery
            + self.wear_score    * weights.wear
            + self.charge_score  * weights.charge
            + self.deadhead_score * weights.deadhead
    }
}
```

### Dynamic Weight Profiles

Weights shift automatically based on time of day, balancing rider experience against fleet health:

| Period | Proximity | Battery | Wear | Charge | Deadhead |
|--------|-----------|---------|------|--------|----------|
| Peak (06–09, 16–19) | 0.45 | 0.30 | 0.05 | 0.05 | 0.15 |
| Midday lull (10–15) | 0.20 | 0.25 | 0.20 | 0.25 | 0.10 |
| Evening (20–23) | 0.35 | 0.30 | 0.10 | 0.10 | 0.15 |
| Overnight | 0.15 | 0.20 | 0.25 | 0.30 | 0.10 |

### Concurrency — Optimistic Concurrency Control

Two riders requesting simultaneously never get assigned the same driver. No mutexes. No deadlocks. Pure OCC with Redis version counters:

```
Rider 1 Thread ──► Read Driver A (v12) ──► Score 0.95 ──► CAS(v12) ──► SUCCESS (v13) ──► Assigned ✅
                                                               │
Rider 2 Thread ──► Read Driver A (v12) ──► Score 0.94 ─────────┴──► CAS(v12) ──► FAIL (v13) ──► Next Best ♻️
```

---

## Telematics Pipeline

OEM APIs are too slow, too restricted, and too unreliable for a dispatch engine that needs SoC updates every 5–10 seconds across 200 vehicles.

Ohmo reads the **CAN bus directly.**

```
Vehicle CAN Bus
    │
    ▼
Teltonika / Geotab OBD-II Dongle
    │  (reads powertrain PIDs — SoC, SoH, odometer, tyre pressure)
    ▼
MQTT Binary Packets over Private Cellular APN
    │  (Vodacom / MTN dedicated APN — not public internet)
    ▼
ohmo-telemetry (Rust ingestion microservice)
    │  (decode → validate → normalise)
    ▼
Redis (live state — SoC, location, version counter)
    │
    ▼
ohmo-dispatch (scoring engine reads from Redis)
```

**Dongle watchdog:** If any vehicle stops broadcasting for >30 seconds, `ohmo-ops` controller view fires an alert immediately. Rishen's team knows before the driver does.

---

## Fleet Operations Dashboard

Three views. One source of truth.

### Executive View — Fleet Pulse
- **Active Utilisation Rate** — % of fleet currently generating revenue
- **Real-Time Revenue vs Power Cost** — live financial ledger, margin per km
- **Fleet Status Ring** — Online / On Trip / Charging / Offline breakdown
- **Total Energy Efficiency** — fleet-wide kWh/km

### Controller View — Live Operations
- **Low-SoC Watchlist** — vehicles below 20% not routed toward a charger
- **Charging Hub Status** — bay occupancy, queue depth, cars en route per hub
- **CAS Rejection Rate Sparkline** — engine contention indicator, surge signal
- **Telematics Ping Health** — dongle connectivity feed, 30s timeout alerts

### Maintenance View — Asset Management
- **SoH Leaderboard** — battery capacity retention ranked across fleet
- **Deep Cycle Counter** — vehicles accumulating unhealthy 0→100% charge cycles
- **Preventive Maintenance Triggers** — automated alerts for tyres, brakes, cabin filters
- **wear_score Override** — manual adjustment of individual vehicle dispatch priority

### Audit Log — Immutable Operator Trail

```sql
CREATE TABLE operator_audit_log (
    id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    operator_id    UUID NOT NULL REFERENCES operators(id),
    action_type    TEXT NOT NULL,
    vehicle_id     UUID REFERENCES vehicles(id),
    driver_id      UUID REFERENCES drivers(id),
    previous_state JSONB,
    new_state      JSONB,
    reason         TEXT,
    ip_address     INET
);
```

Every manual override. Every weight adjustment. Every forced assignment. Timestamped, attributed, immutable.

---

## Tech Stack

| Layer | Technology | Why |
|-------|------------|-----|
| **Language** | Rust | Memory safety, zero-cost abstractions, async performance |
| **UI Framework** | [Blinc](https://github.com/neoqiss/project-blinc) | GPU-accelerated, wgpu, spring physics — built in-house |
| **API Layer** | Axum | Ergonomic, tower-compatible, async-first |
| **Async Runtime** | Tokio | Industry standard, battle-tested concurrency |
| **Primary DB** | PostgreSQL + sqlx | Relational integrity, audit logs, trip history |
| **Live State** | Redis | Sub-millisecond SoC reads, OCC version counters |
| **Telematics** | Teltonika / Geotab OBD-II | Direct CAN bus access, private APN |
| **Routing** | TomTom / HERE (EV routing) | Energy-aware turn-by-turn, not just distance |
| **Spatial Index** | PostGIS + R-tree | Geospatial pre-filter before scoring |
| **Messaging** | MQTT (Eclipse Mosquitto) | Lightweight, reliable for IoT/telematics |
| **Deployment** | Docker + Nginx | Simple, portable, self-hosted |

---

## Roadmap

### Phase 1 — Foundation `[In Progress]`
- [ ] `ohmo-core` — shared types, error handling, config
- [ ] `ohmo-telemetry` — MQTT ingestion, CAN decoder, SoC pipeline
- [ ] `ohmo-dispatch` — scoring engine, OCC, dynamic weights
- [ ] `ohmo-gateway` — Axum API, WebSocket hub
- [ ] PostgreSQL migrations — schema v1
- [ ] Redis integration — live state layer

### Phase 2 — Driver Experience
- [ ] `ohmo-driver` app — Blinc UI, full driver console
- [ ] Trip request flow — 14s acceptance window, infotainment mirror
- [ ] Vehicle screen — live EV health, quick actions, charging finder
- [ ] Earnings screen — visual, gamified, campaign-aware

### Phase 3 — Rider Experience
- [ ] `ohmo-rider` app — Blinc UI, full discovery platform
- [ ] Home screen — "Where to tonight?" + vibe exploration
- [ ] Friends layer — social map, live presence, group outings
- [ ] Booking flow — tier selection, ETA, CO₂ impact per trip
- [ ] Profile — achievements, CO₂ saved, days with Ohmo

### Phase 4 — Operations
- [ ] `ohmo-ops` dashboard — all three views live
- [ ] Telematics health monitoring — dongle watchdog, alert feed
- [ ] Audit log UI — searchable, filterable, exportable
- [ ] Charging hub management — bay status, queue routing

### Phase 5 — Places & Ads
- [ ] `ohmo-places` — vibe engine, discovery ranking
- [ ] Priority placement auction — business-facing ad system
- [ ] Curated collections — "Hidden gems in Sandton", "Date nights"
- [ ] "Tonight" mode — ambient live city intelligence

### Phase 6 — Scale
- [ ] Cape Town fleet onboarding
- [ ] Durban fleet onboarding
- [ ] Charging network — public hubs, open to all EVs
- [ ] Multi-city ops dashboard
- [ ] Global expansion groundwork

---

## Fleet

Initial launch fleet: **200 EVs** at Durban harbour, ready for Johannesburg deployment.

| Model | Category | Range |
|-------|----------|-------|
| Dongfeng Box | Ohmo Go | ~330 km |
| BYD Dolphin Surf | Ohmo Go | ~340 km |
| Geely E2 | Ohmo Go | ~310 km |
| Mini Countryman Electric *(Phase 2)* | Ohmo Comfort | ~460 km |
| Volvo EX90 *(Phase 3)* | Ohmo XL | ~580 km |
| BMW i7 *(Phase 3)* | Ohmo Luxury | ~625 km |

All vehicles equipped with Teltonika OBD-II telematics dongles on private cellular APN.

---

## Team

| Person | Role |
|--------|------|
| **Neo Qiss** `@neoqiss` | Founder, Systems Architect, Rust Engineer |
| **Rishen Govender** | Head of Fleet & EV Mechanics |
| **Khumo** | Head of Cybersecurity |
| **Ivani** | UI/UX Design Lead |
| **Peter Liu** | Fleet Supply Partner |

---

## The Philosophy

> The car is the product.  
> The phone is the key.

Most ride-hailing companies built software marketplaces and bolted drivers on top. Ohmo owns the fleet, reads the CAN bus, controls the charging infrastructure, and surfaces the city as a living, breathing discovery layer.

The dispatch engine doesn't know about rides. It knows about **energy, wear, terrain, and time.** The rider app doesn't know about transportation. It knows about **vibes, friends, and places.**

The rides just happen in between.

---

## License

Proprietary. All rights reserved.  
© 2026 Ohmo. Built in Johannesburg. Owned entirely.

---

<div align="center">

<br />

**ohmo** · Johannesburg · Est. 2026

*Electric rides. Elevated experiences.*

[![](https://img.shields.io/badge/ohmo.app-FF6B35?style=for-the-badge&logoColor=white)](https://ohmo.app)

</div>
