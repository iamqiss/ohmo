//! ohmo-telemetry — CAN bus → SoC pipeline
//! MQTT ingestion, OBD-II PID decoding, Redis live state

pub mod can;
pub mod health;
pub mod ingestion;
pub mod models;
pub mod pipeline;
