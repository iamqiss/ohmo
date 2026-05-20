#!/usr/bin/env python3
"""
Ohmo Project Scaffolder
=======================
Run this script to generate the complete Ohmo monorepo structure.
Usage: python3 scaffold.py
"""

import os
import sys

# ── ANSI colours ────────────────────────────────────────────────────────────
GREEN  = "\033[92m"
ORANGE = "\033[93m"
CYAN   = "\033[96m"
RED    = "\033[91m"
RESET  = "\033[0m"
BOLD   = "\033[1m"

def log(msg):   print(f"{GREEN}  ✓ {msg}{RESET}")
def info(msg):  print(f"{CYAN}  → {msg}{RESET}")
def warn(msg):  print(f"{ORANGE}  ! {msg}{RESET}")
def error(msg): print(f"{RED}  ✗ {msg}{RESET}")

# ── Helpers ──────────────────────────────────────────────────────────────────
def mkfile(path: str, content: str = ""):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not os.path.exists(path):
        with open(path, "w") as f:
            f.write(content)
        log(path)
    else:
        warn(f"EXISTS (skipped): {path}")

def mkdir(path: str):
    os.makedirs(path, exist_ok=True)

# ── Content helpers ──────────────────────────────────────────────────────────
def crate_toml(name: str, deps: list[str] = None) -> str:
    dep_lines = ""
    if deps:
        dep_lines = "\n" + "\n".join(
            f'{d} = {{ path = "../../crates/{d}" }}' for d in deps
        )
    return f'''[package]
name = "{name}"
version = "0.1.0"
edition = "2021"

[dependencies]
tokio = {{ version = "1", features = ["full"] }}
serde = {{ version = "1", features = ["derive"] }}
serde_json = "1"
thiserror = "1"
anyhow = "1"
tracing = "1"
uuid = {{ version = "1", features = ["v4", "serde"] }}
chrono = {{ version = "0.4", features = ["serde"] }}{dep_lines}
'''

def service_toml(name: str, deps: list[str] = None) -> str:
    dep_lines = ""
    if deps:
        dep_lines = "\n" + "\n".join(
            f'{d} = {{ path = "../../crates/{d}" }}' for d in deps
        )
    return f'''[package]
name = "{name}"
version = "0.1.0"
edition = "2021"

[[bin]]
name = "{name}"
path = "src/main.rs"

[dependencies]
tokio = {{ version = "1", features = ["full"] }}
serde = {{ version = "1", features = ["derive"] }}
serde_json = "1"
thiserror = "1"
anyhow = "1"
tracing = "1"
tracing-subscriber = "1"
tonic = "0.11"
prost = "0.12"
axum = {{ version = "0.7", features = ["ws"] }}
tower = "0.4"
tower-http = {{ version = "0.5", features = ["cors", "trace"] }}
uuid = {{ version = "1", features = ["v4", "serde"] }}
chrono = {{ version = "0.4", features = ["serde"] }}
sqlx = {{ version = "0.7", features = ["postgres", "runtime-tokio-native-tls", "uuid", "chrono"] }}
redis = {{ version = "0.24", features = ["tokio-comp"] }}{dep_lines}
'''

def app_toml(name: str) -> str:
    return f'''[package]
name = "{name}"
version = "0.1.0"
edition = "2021"

[[bin]]
name = "{name}"
path = "src/main.rs"

[dependencies]
tokio = {{ version = "1", features = ["full"] }}
serde = {{ version = "1", features = ["derive"] }}
anyhow = "1"
tracing = "1"
# blinc = {{ path = "../../blinc" }}   # Uncomment when Blinc is linked
'''

def lib_rs(name: str, comment: str) -> str:
    return f'''//! {comment}

pub mod models;
'''

def mod_rs(comment: str) -> str:
    return f'''//! {comment}
'''

def stub_rs(comment: str) -> str:
    return f'''//! {comment}

// TODO: implement
'''

def main_rs(name: str) -> str:
    return f'''use anyhow::Result;
use tracing::info;

#[tokio::main]
async fn main() -> Result<()> {{
    tracing_subscriber::fmt::init();
    info!("Starting {name}...");
    Ok(())
}}
'''

def proto_file(service: str, package: str, methods: list[tuple]) -> str:
    method_strs = "\n".join(
        f"  rpc {m[0]} ({m[1]}) returns ({m[2]});"
        for m in methods
    )
    return f'''syntax = "proto3";

package {package};

// {service} service definition
service {service} {{
{method_strs}
}}
'''

def workspace_toml(crates: list[str], services: list[str], apps: list[str]) -> str:
    members = (
        [f'"crates/{c}"' for c in crates] +
        [f'"services/{s}"' for s in services] +
        [f'"apps/{a}"' for a in apps]
    )
    members_str = ",\n    ".join(members)
    return f'''[workspace]
resolver = "2"
members = [
    {members_str}
]

[workspace.dependencies]
tokio = {{ version = "1", features = ["full"] }}
serde = {{ version = "1", features = ["derive"] }}
serde_json = "1"
thiserror = "1"
anyhow = "1"
tracing = "1"
uuid = {{ version = "1", features = ["v4", "serde"] }}
chrono = {{ version = "0.4", features = ["serde"] }}
sqlx = {{ version = "0.7", features = ["postgres", "runtime-tokio-native-tls", "uuid", "chrono"] }}
redis = {{ version = "0.24", features = ["tokio-comp"] }}
tonic = "0.11"
prost = "0.12"
axum = {{ version = "0.7", features = ["ws"] }}

[profile.release]
opt-level = 3
lto = true
codegen-units = 1
'''

# ── Root files ───────────────────────────────────────────────────────────────
def scaffold_root(base: str):
    info("Scaffolding root files...")

    crates   = ["ohmo-core","ohmo-auth","ohmo-identity","ohmo-gatekeeper",
                 "ohmo-dispatch","ohmo-telemetry","ohmo-fleet","ohmo-charging",
                 "ohmo-trips","ohmo-payments","ohmo-places","ohmo-social",
                 "ohmo-messaging","ohmo-notifications","ohmo-support","ohmo-analytics"]
    services = ["ohmo-gateway","ohmo-dispatch-svc","ohmo-telemetry-svc"]
    apps     = ["ohmo-rider","ohmo-driver","ohmo-ops"]

    mkfile(f"{base}/Cargo.toml", workspace_toml(crates, services, apps))
    mkfile(f"{base}/.env.example", "DATABASE_URL=postgres://ohmo:ohmo@localhost:5432/ohmo\nREDIS_URL=redis://localhost:6379\nMQTT_URL=mqtt://localhost:1883\nJWT_SECRET=change_me_in_production\nAPP_ENV=development\n")
    mkfile(f"{base}/.env.development", "DATABASE_URL=postgres://ohmo:ohmo@localhost:5432/ohmo\nREDIS_URL=redis://localhost:6379\nMQTT_URL=mqtt://localhost:1883\nJWT_SECRET=dev_secret_key\nAPP_ENV=development\n")
    mkfile(f"{base}/.gitignore", "target/\n.env\n.env.development\n*.pem\n*.key\n.DS_Store\n")
    mkfile(f"{base}/.rustfmt.toml", 'edition = "2021"\nmax_width = 100\n')
    mkfile(f"{base}/.clippy.toml", 'msrv = "1.75"\n')
    mkfile(f"{base}/rust-toolchain.toml", '[toolchain]\nchannel = "stable"\ncomponents = ["rustfmt", "clippy"]\n')
    mkfile(f"{base}/LICENSE", "Copyright 2026 Neo Qiss. All rights reserved. Proprietary.\n")

# ── Proto files ──────────────────────────────────────────────────────────────
def scaffold_proto(base: str):
    info("Scaffolding proto files...")
    p = f"{base}/proto"

    mkfile(f"{p}/auth/auth.proto", proto_file("AuthService", "ohmo.auth", [
        ("Login",          "LoginRequest",          "LoginResponse"),
        ("Refresh",        "RefreshRequest",        "RefreshResponse"),
        ("Logout",         "LogoutRequest",         "LogoutResponse"),
        ("ValidateToken",  "ValidateTokenRequest",  "ValidateTokenResponse"),
    ]))

    mkfile(f"{p}/dispatch/dispatch.proto", proto_file("DispatchService", "ohmo.dispatch", [
        ("RequestTrip",    "TripRequest",           "TripAssignment"),
        ("CancelTrip",     "CancelTripRequest",     "CancelTripResponse"),
        ("AcceptTrip",     "AcceptTripRequest",     "AcceptTripResponse"),
        ("DeclineTrip",    "DeclineTripRequest",    "DeclineTripResponse"),
        ("GetDriverScore", "DriverScoreRequest",    "DriverScoreResponse"),
    ]))

    mkfile(f"{p}/telemetry/telemetry.proto", proto_file("TelemetryService", "ohmo.telemetry", [
        ("PushTelemetry",  "VehicleTelemetry",      "TelemetryAck"),
        ("GetVehicleSoC",  "VehicleSoCRequest",     "VehicleSoCResponse"),
        ("GetDongleHealth","DongleHealthRequest",   "DongleHealthResponse"),
    ]))

    mkfile(f"{p}/fleet/fleet.proto", proto_file("FleetService", "ohmo.fleet", [
        ("RegisterVehicle","RegisterVehicleRequest","RegisterVehicleResponse"),
        ("GetVehicle",     "GetVehicleRequest",     "Vehicle"),
        ("ListVehicles",   "ListVehiclesRequest",   "ListVehiclesResponse"),
        ("UpdateStatus",   "UpdateStatusRequest",   "UpdateStatusResponse"),
    ]))

    mkfile(f"{p}/trips/trips.proto", proto_file("TripService", "ohmo.trips", [
        ("CreateTrip",     "CreateTripRequest",     "Trip"),
        ("GetTrip",        "GetTripRequest",        "Trip"),
        ("UpdateTrip",     "UpdateTripRequest",     "Trip"),
        ("CompleteTrip",   "CompleteTripRequest",   "CompleteTripResponse"),
        ("RateTrip",       "RateTripRequest",       "RateTripResponse"),
    ]))

    mkfile(f"{p}/places/places.proto", proto_file("PlacesService", "ohmo.places", [
        ("SearchPlaces",   "SearchPlacesRequest",   "SearchPlacesResponse"),
        ("GetPlace",       "GetPlaceRequest",       "Place"),
        ("GetVibes",       "GetVibesRequest",       "GetVibesResponse"),
        ("GetTonight",     "GetTonightRequest",     "GetTonightResponse"),
    ]))

    mkfile(f"{p}/payments/payments.proto", proto_file("PaymentsService", "ohmo.payments", [
        ("ProcessPayment", "ProcessPaymentRequest", "ProcessPaymentResponse"),
        ("RequestPayout",  "PayoutRequest",         "PayoutResponse"),
        ("GetBalance",     "GetBalanceRequest",     "GetBalanceResponse"),
    ]))

    mkfile(f"{p}/charging/charging.proto", proto_file("ChargingService", "ohmo.charging", [
        ("GetNearestHub",  "NearestHubRequest",     "NearestHubResponse"),
        ("GetHubStatus",   "HubStatusRequest",      "HubStatusResponse"),
        ("StartSession",   "StartSessionRequest",   "ChargingSession"),
        ("EndSession",     "EndSessionRequest",     "EndSessionResponse"),
    ]))

    mkfile(f"{p}/social/social.proto", proto_file("SocialService", "ohmo.social", [
        ("Follow",         "FollowRequest",         "FollowResponse"),
        ("Unfollow",       "UnfollowRequest",       "UnfollowResponse"),
        ("GetPresence",    "PresenceRequest",        "PresenceResponse"),
        ("GetFriends",     "GetFriendsRequest",     "GetFriendsResponse"),
    ]))

    mkfile(f"{p}/messaging/messaging.proto", proto_file("MessagingService", "ohmo.messaging", [
        ("SendMessage",    "SendMessageRequest",    "Message"),
        ("GetMessages",    "GetMessagesRequest",    "GetMessagesResponse"),
        ("MarkRead",       "MarkReadRequest",       "MarkReadResponse"),
    ]))

    mkfile(f"{p}/support/support.proto", proto_file("SupportService", "ohmo.support", [
        ("CreateTicket",   "CreateTicketRequest",   "Ticket"),
        ("GetTicket",      "GetTicketRequest",      "Ticket"),
        ("ReportIncident", "IncidentRequest",       "IncidentResponse"),
    ]))

    mkfile(f"{p}/notifications/notifications.proto", proto_file("NotificationsService", "ohmo.notifications", [
        ("SendPush",       "PushRequest",           "PushResponse"),
        ("Subscribe",      "SubscribeRequest",      "stream NotificationEvent"),
    ]))

# ── ohmo-core ────────────────────────────────────────────────────────────────
def scaffold_ohmo_core(base: str):
    info("Scaffolding ohmo-core...")
    c = f"{base}/crates/ohmo-core"
    mkfile(f"{c}/Cargo.toml", crate_toml("ohmo-core"))
    mkfile(f"{c}/src/lib.rs", '''//! ohmo-core — shared foundation for all Ohmo crates

pub mod config;
pub mod errors;
pub mod traits;
pub mod types;
pub mod utils;
''')
    for module in ["types","errors","config","traits","utils"]:
        mkfile(f"{c}/src/{module}/mod.rs", mod_rs(f"ohmo-core::{module}"))

    for f in ["ids","money","geo","time","status"]:
        mkfile(f"{c}/src/types/{f}.rs", stub_rs(f"ohmo-core::types::{f}"))
    for f in ["domain","api","telemetry"]:
        mkfile(f"{c}/src/errors/{f}.rs", stub_rs(f"ohmo-core::errors::{f}"))
    for f in ["app","database","redis","mqtt","secrets"]:
        mkfile(f"{c}/src/config/{f}.rs", stub_rs(f"ohmo-core::config::{f}"))
    for f in ["repository","service","event"]:
        mkfile(f"{c}/src/traits/{f}.rs", stub_rs(f"ohmo-core::traits::{f}"))
    for f in ["pagination","validation","crypto"]:
        mkfile(f"{c}/src/utils/{f}.rs", stub_rs(f"ohmo-core::utils::{f}"))

# ── ohmo-auth ────────────────────────────────────────────────────────────────
def scaffold_ohmo_auth(base: str):
    info("Scaffolding ohmo-auth...")
    c = f"{base}/crates/ohmo-auth"
    mkfile(f"{c}/Cargo.toml", crate_toml("ohmo-auth", ["ohmo-core"]))
    mkfile(f"{c}/src/lib.rs", '''//! ohmo-auth — JWT, Argon2, OAuth2/OIDC, session management

pub mod jwt;
pub mod middleware;
pub mod oauth;
pub mod password;
pub mod session;
''')
    for module in ["jwt","password","oauth","session","middleware"]:
        mkfile(f"{c}/src/{module}/mod.rs", mod_rs(f"ohmo-auth::{module}"))

    for f in ["claims","encode","decode","refresh"]:
        mkfile(f"{c}/src/jwt/{f}.rs", stub_rs(f"JWT: {f}"))
    for f in ["hash","verify"]:
        mkfile(f"{c}/src/password/{f}.rs", stub_rs(f"Argon2 password: {f}"))
    for f in ["provider","google","apple"]:
        mkfile(f"{c}/src/oauth/{f}.rs", stub_rs(f"OAuth2/OIDC: {f}"))
    for f in ["store","create","revoke"]:
        mkfile(f"{c}/src/session/{f}.rs", stub_rs(f"Session: {f}"))
    for f in ["require_auth","require_role","rate_limit"]:
        mkfile(f"{c}/src/middleware/{f}.rs", stub_rs(f"Middleware: {f}"))

# ── ohmo-identity ────────────────────────────────────────────────────────────
def scaffold_ohmo_identity(base: str):
    info("Scaffolding ohmo-identity...")
    c = f"{base}/crates/ohmo-identity"
    mkfile(f"{c}/Cargo.toml", crate_toml("ohmo-identity", ["ohmo-core"]))
    mkfile(f"{c}/src/lib.rs", '''//! ohmo-identity — dual verification, eNaTIS, face match, background checks

pub mod enatis;
pub mod models;
pub mod pre_trip;
pub mod verification;
''')
    for module in ["verification","pre_trip","enatis","models"]:
        mkfile(f"{c}/src/{module}/mod.rs", mod_rs(f"ohmo-identity::{module}"))

    for f in ["face","document","licence","background"]:
        mkfile(f"{c}/src/verification/{f}.rs", stub_rs(f"Verification: {f}"))
    for f in ["rider","driver"]:
        mkfile(f"{c}/src/pre_trip/{f}.rs", stub_rs(f"Pre-trip verify: {f}"))
    for f in ["client","verify"]:
        mkfile(f"{c}/src/enatis/{f}.rs", stub_rs(f"eNaTIS: {f}"))
    for f in ["identity","verification"]:
        mkfile(f"{c}/src/models/{f}.rs", stub_rs(f"Model: {f}"))

# ── ohmo-gatekeeper ──────────────────────────────────────────────────────────
def scaffold_ohmo_gatekeeper(base: str):
    info("Scaffolding ohmo-gatekeeper...")
    c = f"{base}/crates/ohmo-gatekeeper"
    mkfile(f"{c}/Cargo.toml", crate_toml("ohmo-gatekeeper", ["ohmo-core","ohmo-identity"]))
    mkfile(f"{c}/src/lib.rs", '''//! ohmo-gatekeeper — Ohmo\'s immune system
//! Rate limiting, fraud detection, driver test, hot mic recording, RICA/POPIA compliance

pub mod compliance;
pub mod driver_test;
pub mod fraud;
pub mod geo_fence;
pub mod rate_limit;
pub mod recording;
''')
    for module in ["rate_limit","fraud","driver_test","recording","compliance","geo_fence"]:
        mkfile(f"{c}/src/{module}/mod.rs", mod_rs(f"ohmo-gatekeeper::{module}"))

    for f in ["sliding_window","token_bucket","store"]:
        mkfile(f"{c}/src/rate_limit/{f}.rs", stub_rs(f"Rate limit: {f}"))
    for f in ["detector","signals","velocity","device"]:
        mkfile(f"{c}/src/fraud/{f}.rs", stub_rs(f"Fraud: {f}"))
    for f in ["questions","randomiser","evaluator","categories"]:
        mkfile(f"{c}/src/driver_test/{f}.rs", stub_rs(f"Driver test: {f}"))
    for f in ["hot_mic","encrypt","purge","decrypt","consent"]:
        mkfile(f"{c}/src/recording/{f}.rs", stub_rs(f"Recording: {f}"))
    for f in ["rica","popia","audit"]:
        mkfile(f"{c}/src/compliance/{f}.rs", stub_rs(f"Compliance: {f}"))
    for f in ["zones","enforce","airport"]:
        mkfile(f"{c}/src/geo_fence/{f}.rs", stub_rs(f"Geo fence: {f}"))

# ── ohmo-dispatch ────────────────────────────────────────────────────────────
def scaffold_ohmo_dispatch(base: str):
    info("Scaffolding ohmo-dispatch...")
    c = f"{base}/crates/ohmo-dispatch"
    mkfile(f"{c}/Cargo.toml", crate_toml("ohmo-dispatch", ["ohmo-core","ohmo-telemetry"]))
    mkfile(f"{c}/src/lib.rs", '''//! ohmo-dispatch — EV-native matching engine
//! Scoring, OCC, dynamic weights, energy-aware routing

pub mod concurrency;
pub mod matching;
pub mod models;
pub mod routing;
pub mod scoring;
pub mod surge;
''')
    for module in ["scoring","matching","concurrency","routing","surge","models"]:
        mkfile(f"{c}/src/{module}/mod.rs", mod_rs(f"ohmo-dispatch::{module}"))

    # Scoring — the core algorithm
    mkfile(f"{c}/src/scoring/driver_score.rs", '''//! DriverScore — composite scoring function

use crate::scoring::weights::Weights;

/// Normalised scores for a single driver candidate (0.0 – 1.0)
#[derive(Debug, Clone)]
pub struct DriverScore {{
    pub proximity_score:  f64,
    pub battery_score:    f64,
    pub wear_score:       f64,
    pub charge_score:     f64,
    pub deadhead_score:   f64,
}}

impl DriverScore {{
    /// Weighted composite score
    pub fn total(&self, weights: &Weights) -> f64 {{
        self.proximity_score  * weights.proximity
            + self.battery_score  * weights.battery
            + self.wear_score     * weights.wear
            + self.charge_score   * weights.charge
            + self.deadhead_score * weights.deadhead
    }}

    pub fn calculate(
        distance_to_pickup_km:      f64,
        max_pickup_radius_km:       f64,
        predicted_soc_after_trip:   f64,
        min_safe_soc:               f64,
        vehicle_mileage:            f64,
        fleet_avg_mileage:          f64,
        current_soc:                f64,
        distance_to_nearest_hub_km: f64,
    ) -> Self {{
        // 1. Proximity — linear decay to 0 at max radius
        let proximity_score =
            (1.0 - (distance_to_pickup_km / max_pickup_radius_km)).max(0.0);

        // 2. Battery — hard veto if trip would leave car below safe threshold
        let battery_score = if predicted_soc_after_trip < min_safe_soc {{
            0.0
        }} else {{
            ((predicted_soc_after_trip - min_safe_soc) / (100.0 - min_safe_soc))
                .clamp(0.0, 1.0)
        }};

        // 3. Wear — prioritise under-utilised vehicles
        let wear_score = if vehicle_mileage == 0.0 && fleet_avg_mileage == 0.0 {{
            1.0
        }} else {{
            let ratio = vehicle_mileage / (fleet_avg_mileage + 0.1);
            (1.0 / (1.0 + ratio)).clamp(0.0, 1.0)
        }};

        // 4. Charge — prioritise cars sitting at 100% to discharge to healthy zone
        let charge_score = if current_soc > 85.0 {{
            ((current_soc - 85.0) / 15.0).clamp(0.0, 1.0)
        }} else {{
            0.1
        }};

        // 5. Deadhead — if low SoC, prioritise trips toward a charging hub
        let deadhead_score = if current_soc < 25.0 {{
            (1.0 - (distance_to_nearest_hub_km / 15.0)).max(0.0)
        }} else {{
            0.5
        }};

        DriverScore {{
            proximity_score,
            battery_score,
            wear_score,
            charge_score,
            deadhead_score,
        }}
    }}
}}
''')

    mkfile(f"{c}/src/scoring/weights.rs", '''//! Dynamic weight profiles — shift based on time of day

#[derive(Debug, Clone)]
pub struct Weights {{
    pub proximity: f64,
    pub battery:   f64,
    pub wear:      f64,
    pub charge:    f64,
    pub deadhead:  f64,
}}

impl Weights {{
    /// Select weight profile based on hour of day (0–23)
    pub fn for_hour(hour: u8) -> Self {{
        match hour {{
            // Peak morning + evening rush
            6..=9 | 16..=19 => Self {{
                proximity: 0.45,
                battery:   0.30,
                wear:      0.05,
                charge:    0.05,
                deadhead:  0.15,
            }},
            // Midday lull — prioritise fleet health
            10..=15 => Self {{
                proximity: 0.20,
                battery:   0.25,
                wear:      0.20,
                charge:    0.25,
                deadhead:  0.10,
            }},
            // Evening
            20..=23 => Self {{
                proximity: 0.35,
                battery:   0.30,
                wear:      0.10,
                charge:    0.10,
                deadhead:  0.15,
            }},
            // Overnight — maximise fleet recovery
            _ => Self {{
                proximity: 0.15,
                battery:   0.20,
                wear:      0.25,
                charge:    0.30,
                deadhead:  0.10,
            }},
        }}
    }}
}}
''')

    for f in ["proximity","battery","wear","charge","deadhead"]:
        mkfile(f"{c}/src/scoring/{f}.rs", stub_rs(f"Scoring component: {f}"))
    for f in ["engine","spatial","fanout","acceptance"]:
        mkfile(f"{c}/src/matching/{f}.rs", stub_rs(f"Matching: {f}"))
    for f in ["occ","cas","conflict"]:
        mkfile(f"{c}/src/concurrency/{f}.rs", stub_rs(f"OCC: {f}"))
    for f in ["client","energy","eta","eco"]:
        mkfile(f"{c}/src/routing/{f}.rs", stub_rs(f"Routing: {f}"))
    for f in ["detector","multiplier","zones"]:
        mkfile(f"{c}/src/surge/{f}.rs", stub_rs(f"Surge: {f}"))
    for f in ["trip_request","assignment","candidate"]:
        mkfile(f"{c}/src/models/{f}.rs", stub_rs(f"Model: {f}"))

# ── ohmo-telemetry ───────────────────────────────────────────────────────────
def scaffold_ohmo_telemetry(base: str):
    info("Scaffolding ohmo-telemetry...")
    c = f"{base}/crates/ohmo-telemetry"
    mkfile(f"{c}/Cargo.toml", crate_toml("ohmo-telemetry", ["ohmo-core"]))
    mkfile(f"{c}/src/lib.rs", '''//! ohmo-telemetry — CAN bus → SoC pipeline
//! MQTT ingestion, OBD-II PID decoding, Redis live state

pub mod can;
pub mod health;
pub mod ingestion;
pub mod models;
pub mod pipeline;
''')
    for module in ["ingestion","can","health","pipeline","models"]:
        mkfile(f"{c}/src/{module}/mod.rs", mod_rs(f"ohmo-telemetry::{module}"))

    for f in ["mqtt","udp","decoder"]:
        mkfile(f"{c}/src/ingestion/{f}.rs", stub_rs(f"Ingestion: {f}"))
    for f in ["parser","pids","soc","soh","odometer","tyres","dtc"]:
        mkfile(f"{c}/src/can/{f}.rs", stub_rs(f"CAN: {f}"))
    for f in ["watchdog","degraded","alerts"]:
        mkfile(f"{c}/src/health/{f}.rs", stub_rs(f"Health: {f}"))
    for f in ["normalise","validate","publish"]:
        mkfile(f"{c}/src/pipeline/{f}.rs", stub_rs(f"Pipeline: {f}"))
    for f in ["telemetry","dongle","signal"]:
        mkfile(f"{c}/src/models/{f}.rs", stub_rs(f"Model: {f}"))

# ── remaining crates (fleet, charging, trips, payments, places, social, messaging, notifications, support, analytics) ──
def scaffold_remaining_crates(base: str):
    crates = [
        ("ohmo-fleet",         ["ohmo-core","ohmo-telemetry"],
         ["vehicles","maintenance","battery","models"],
         {"vehicles":["registry","status","assignment"],
          "maintenance":["schedule","triggers","history","parts"],
          "battery":["health","cycles","degradation"],
          "models":["vehicle","maintenance"]}),

        ("ohmo-charging",      ["ohmo-core"],
         ["hubs","routing","public","models"],
         {"hubs":["registry","bays","queue","availability"],
          "routing":["nearest","deadhead"],
          "public":["sessions","pricing","billing"],
          "models":["hub","bay","session"]}),

        ("ohmo-trips",         ["ohmo-core","ohmo-dispatch","ohmo-payments"],
         ["lifecycle","pricing","rating","models"],
         {"lifecycle":["request","matching","pickup","active","complete"],
          "pricing":["base","surge","estimate"],
          "rating":["rider","driver","aggregate"],
          "models":["trip","waypoint"]}),

        ("ohmo-payments",      ["ohmo-core"],
         ["processing","payouts","providers","models"],
         {"processing":["charge","split","refund"],
          "payouts":["driver","batch","reconcile"],
          "providers":["peach","ozow"],
          "models":["payment","payout"]}),

        ("ohmo-places",        ["ohmo-core"],
         ["discovery","ads","tonight","models"],
         {"discovery":["vibe","proximity","trending","collections"],
          "ads":["auction","targeting","impression","billing"],
          "tonight":["pulse","hotspots","atmosphere"],
          "models":["place","vibe","ad"]}),

        ("ohmo-social",        ["ohmo-core"],
         ["friends","groups","privacy","models"],
         {"friends":["follow","presence","activity"],
          "groups":["create","members","outings"],
          "privacy":["ghost","precision","circles"],
          "models":["friendship","group"]}),

        ("ohmo-messaging",     ["ohmo-core"],
         ["direct","group","trip_chat","models"],
         {"direct":["send","read","delete"],
          "group":["create","send","members"],
          "trip_chat":["channel"],
          "models":["message","conversation"]}),

        ("ohmo-notifications", ["ohmo-core"],
         ["push","websocket","templates"],
         {"push":["fcm","apns","dispatch"],
          "websocket":["hub","fanout","events"],
          "templates":["trip","promo","system"]}),

        ("ohmo-support",       ["ohmo-core"],
         ["tickets","disputes","models"],
         {"tickets":["create","assign","resolve","escalate"],
          "disputes":["fare","incident","safety"],
          "models":["ticket","dispute"]}),

        ("ohmo-analytics",     ["ohmo-core"],
         ["fleet","drivers","riders","reports"],
         {"fleet":["utilisation","efficiency","revenue"],
          "drivers":["performance","earnings"],
          "riders":["behaviour","retention"],
          "reports":["daily","executive"]}),
    ]

    for name, deps, modules, files in crates:
        info(f"Scaffolding {name}...")
        c = f"{base}/crates/{name}"
        mkfile(f"{c}/Cargo.toml", crate_toml(name, deps))
        lib_content = f"//! {name}\n\n" + "\n".join(f"pub mod {m};" for m in modules) + "\n"
        mkfile(f"{c}/src/lib.rs", lib_content)
        for module in modules:
            mkfile(f"{c}/src/{module}/mod.rs", mod_rs(f"{name}::{module}"))
            for f in files.get(module, []):
                mkfile(f"{c}/src/{module}/{f}.rs", stub_rs(f"{name}::{module}::{f}"))

# ── Services ─────────────────────────────────────────────────────────────────
def scaffold_services(base: str):
    info("Scaffolding services...")

    # ohmo-gateway
    g = f"{base}/services/ohmo-gateway"
    mkfile(f"{g}/Cargo.toml", service_toml("ohmo-gateway", [
        "ohmo-core","ohmo-auth","ohmo-gatekeeper","ohmo-dispatch",
        "ohmo-trips","ohmo-places","ohmo-payments","ohmo-charging",
        "ohmo-social","ohmo-messaging","ohmo-notifications","ohmo-support"
    ]))
    mkfile(f"{g}/src/main.rs", main_rs("ohmo-gateway"))
    mkfile(f"{g}/src/server.rs",  stub_rs("Axum server setup + gRPC reflection"))
    mkfile(f"{g}/src/router.rs",  stub_rs("Route + gRPC service registration"))
    for mw in ["auth","cors","logging","tracing","gatekeeper"]:
        mkfile(f"{g}/src/middleware/{mw}.rs", stub_rs(f"Middleware: {mw}"))
    mkfile(f"{g}/src/middleware/mod.rs", mod_rs("ohmo-gateway::middleware"))
    for route in ["auth","riders","drivers","trips","fleet","places","charging","payments","support","notifications"]:
        mkfile(f"{g}/src/routes/v1/{route}.rs", stub_rs(f"gRPC route: {route}"))
    mkfile(f"{g}/src/routes/v1/mod.rs", mod_rs("ohmo-gateway::routes::v1"))
    mkfile(f"{g}/src/routes/mod.rs",    mod_rs("ohmo-gateway::routes"))
    for ws in ["rider","driver","ops"]:
        mkfile(f"{g}/src/routes/ws/{ws}.rs", stub_rs(f"WebSocket: {ws}"))
    mkfile(f"{g}/src/routes/ws/mod.rs", mod_rs("ohmo-gateway::routes::ws"))

    # ohmo-dispatch-svc
    d = f"{base}/services/ohmo-dispatch-svc"
    mkfile(f"{d}/Cargo.toml", service_toml("ohmo-dispatch-svc", ["ohmo-core","ohmo-dispatch","ohmo-telemetry"]))
    mkfile(f"{d}/src/main.rs",      main_rs("ohmo-dispatch-svc"))
    mkfile(f"{d}/src/worker.rs",    stub_rs("Tokio dispatch worker loop"))
    mkfile(f"{d}/src/health.rs",    stub_rs("Health check endpoint"))

    # ohmo-telemetry-svc
    t = f"{base}/services/ohmo-telemetry-svc"
    mkfile(f"{t}/Cargo.toml", service_toml("ohmo-telemetry-svc", ["ohmo-core","ohmo-telemetry"]))
    mkfile(f"{t}/src/main.rs",       main_rs("ohmo-telemetry-svc"))
    mkfile(f"{t}/src/subscriber.rs", stub_rs("MQTT subscriber main loop — CAN bus ingestion"))
    mkfile(f"{t}/src/health.rs",     stub_rs("Health check endpoint"))

# ── Apps ─────────────────────────────────────────────────────────────────────
def scaffold_apps(base: str):
    info("Scaffolding Blinc apps...")

    apps = {
        "ohmo-rider": {
            "state":   ["auth","trip","map"],
            "screens": ["home","explore","tonight","verification","settings"],
            "booking": ["search","tier","estimate","confirm"],
            "active_trip": ["map","eta","controls"],
            "friends": ["map","list","groups"],
            "place":   ["detail","collection"],
            "profile": ["overview","co2","achievements","history"],
            "components": ["map","place_card","friend_pin","vibe_tag"],
        },
        "ohmo-driver": {
            "state":   ["shift","vehicle","trip"],
            "screens": ["home","trip_request","verification"],
            "active_trip": ["navigation","rider_info","controls"],
            "trips":   ["queue","history"],
            "vehicle": ["overview","charging","maintenance"],
            "earnings":["today","weekly","campaigns"],
            "account": ["profile","documents","payout"],
            "components": ["battery_bar","earnings_ring","trip_card"],
        },
        "ohmo-ops": {
            "state":   ["fleet","alerts"],
            "executive":   ["pulse","status_ring","revenue"],
            "controller":  ["live_grid","soc_watchlist","hub_status","cas_sparkline","ping_health"],
            "maintenance": ["soh_leaderboard","cycle_counter","service_triggers"],
            "audit":       ["log","filters","export"],
            "components":  ["vehicle_pin","alert_badge","sparkline"],
        },
    }

    for app_name, structure in apps.items():
        info(f"  Scaffolding {app_name}...")
        a = f"{base}/apps/{app_name}"
        mkfile(f"{a}/Cargo.toml", app_toml(app_name))
        mkfile(f"{a}/src/main.rs", main_rs(app_name))
        mkfile(f"{a}/src/app.rs",  stub_rs(f"{app_name} root + navigation"))

        for key, files in structure.items():
            if key in ["state","screens","components","executive","controller",
                       "maintenance","audit","booking","active_trip","friends",
                       "place","profile","trips","vehicle","earnings","account"]:
                mkfile(f"{a}/src/{key}/mod.rs", mod_rs(f"{app_name}::{key}"))
                for f in files:
                    mkfile(f"{a}/src/{key}/{f}.rs", stub_rs(f"{app_name}::{key}::{f}"))

# ── Migrations ───────────────────────────────────────────────────────────────
def scaffold_migrations(base: str):
    info("Scaffolding migrations...")
    migrations = [
        ("001_init",          "Extensions, enums, base config"),
        ("002_users",         "Users, roles, permissions"),
        ("003_drivers",       "Drivers, verification status, eNaTIS"),
        ("004_riders",        "Riders, preferences, display names"),
        ("005_vehicles",      "Vehicles, telemetry config, dongle assignment"),
        ("006_fleet",         "Fleet assignments, wear tracking, rotation"),
        ("007_trips",         "Trips, waypoints, pricing, surge"),
        ("008_payments",      "Payments, payouts, ledger, reconciliation"),
        ("009_places",        "Places, vibes, collections, saved spots"),
        ("010_ads",           "Advertisements, impressions, billing"),
        ("011_charging",      "Hubs, bays, sessions, public charging"),
        ("012_maintenance",   "Maintenance records, schedules, parts"),
        ("013_support",       "Tickets, disputes, incident reports"),
        ("014_messaging",     "Messages, conversations, group chats"),
        ("015_notifications", "Notification log, push tokens"),
        ("016_social",        "Friends, groups, presence, privacy settings"),
        ("017_audit_log",     "Operator audit trail — immutable"),
        ("018_driver_test",   "Test questions, attempts, results"),
        ("019_recordings",    "Trip recording metadata (not audio blobs)"),
    ]
    for name, comment in migrations:
        mkfile(f"{base}/migrations/{name}.sql", f"-- {comment}\n-- TODO: implement\n")

# ── Infra ────────────────────────────────────────────────────────────────────
def scaffold_infra(base: str):
    info("Scaffolding infra...")
    mkfile(f"{base}/infra/docker-compose.yml", """version: '3.9'
services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_USER: ohmo
      POSTGRES_PASSWORD: ohmo
      POSTGRES_DB: ohmo
    ports: ["5432:5432"]
    volumes: [pgdata:/var/lib/postgresql/data]

  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]

  mosquitto:
    image: eclipse-mosquitto:2
    ports: ["1883:1883", "9001:9001"]
    volumes: [./infra/mosquitto:/mosquitto/config]

volumes:
  pgdata:
""")
    mkfile(f"{base}/infra/mosquitto/mosquitto.conf",
           "listener 1883\nallow_anonymous true\n")
    mkfile(f"{base}/infra/postgres/init.sql",
           "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";\nCREATE EXTENSION IF NOT EXISTS postgis;\n")
    for svc in ["gateway","dispatch","telemetry"]:
        mkfile(f"{base}/infra/Dockerfile.{svc}",
               f"FROM rust:1.78-slim\nWORKDIR /app\nCOPY . .\nRUN cargo build --release -p ohmo-{svc}-svc\nCMD [\"./target/release/ohmo-{svc}-svc\"]\n")

# ── Docs ─────────────────────────────────────────────────────────────────────
def scaffold_docs(base: str):
    info("Scaffolding docs...")
    docs = [
        ("architecture",          "System architecture overview"),
        ("dispatch-algorithm",    "Scoring function, weights, OCC deep dive"),
        ("telematics-pipeline",   "CAN bus → OBD-II → MQTT → Redis"),
        ("concurrency-model",     "OCC + CAS race condition handling"),
        ("fleet-ops-dashboard",   "Internal dashboard spec"),
        ("gatekeeper",            "Security architecture + compliance"),
        ("recording-compliance",  "Hot mic + RICA/POPIA + AES-256 per-session"),
        ("driver-verification",   "eNaTIS + K53 test spec + 9/10 threshold"),
    ]
    for name, comment in docs:
        mkfile(f"{base}/docs/{name}.md", f"# {comment}\n\n> TODO: write documentation\n")
    for api in ["rider-api","driver-api","ops-api"]:
        mkfile(f"{base}/docs/api/{api}.md", f"# {api.replace('-',' ').title()}\n\n> TODO: gRPC service definitions\n")

# ── Scripts ───────────────────────────────────────────────────────────────────
def scaffold_scripts(base: str):
    info("Scaffolding scripts...")
    mkfile(f"{base}/scripts/setup.sh",   "#!/bin/bash\n# Local dev setup\ndocker-compose -f infra/docker-compose.yml up -d\necho 'Ohmo dev stack running'\n")
    mkfile(f"{base}/scripts/migrate.sh", "#!/bin/bash\n# Run sqlx migrations\nsqlx migrate run\n")
    mkfile(f"{base}/scripts/seed.sh",    "#!/bin/bash\n# Seed development data\necho 'Seeding...'\n")
    mkfile(f"{base}/scripts/lint.sh",    "#!/bin/bash\ncargo fmt --all -- --check\ncargo clippy --all-targets --all-features -- -D warnings\n")
    for script in ["setup.sh","migrate.sh","seed.sh","lint.sh"]:
        os.chmod(f"{base}/scripts/{script}", 0o755)

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    base = "ohmo"

    print(f"\n{BOLD}{ORANGE}")
    print("  ╔═══════════════════════════════════════╗")
    print("  ║        OHMO PROJECT SCAFFOLDER        ║")
    print("  ║   Electric rides. Elevated codebase.  ║")
    print("  ╚═══════════════════════════════════════╝")
    print(f"{RESET}\n")

    if os.path.exists(base):
        warn(f"Directory '{base}' already exists. Files will be skipped if they exist.")
    else:
        mkdir(base)

    scaffold_root(base)
    scaffold_proto(base)
    scaffold_ohmo_core(base)
    scaffold_ohmo_auth(base)
    scaffold_ohmo_identity(base)
    scaffold_ohmo_gatekeeper(base)
    scaffold_ohmo_dispatch(base)
    scaffold_ohmo_telemetry(base)
    scaffold_remaining_crates(base)
    scaffold_services(base)
    scaffold_apps(base)
    scaffold_migrations(base)
    scaffold_infra(base)
    scaffold_docs(base)
    scaffold_scripts(base)

    # Count files
    total = sum(len(files) for _, _, files in os.walk(base))

    print(f"\n{BOLD}{GREEN}")
    print("  ╔═══════════════════════════════════════╗")
    print(f"  ║   ✓ Ohmo scaffolded — {total} files created  ║")
    print("  ║                                       ║")
    print("  ║   Next steps:                         ║")
    print("  ║   1. cd ohmo                          ║")
    print("  ║   2. cargo check                      ║")
    print("  ║   3. ./scripts/setup.sh               ║")
    print("  ║   4. ./scripts/migrate.sh             ║")
    print("  ║   5. cargo run -p ohmo-gateway        ║")
    print("  ║                                       ║")
    print("  ║   Built in Rust. 0% dilution. 😈      ║")
    print("  ╚═══════════════════════════════════════╝")
    print(f"{RESET}\n")

if __name__ == "__main__":
    main()
