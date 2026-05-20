//! DriverScore — composite scoring function

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
