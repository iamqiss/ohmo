//! Dynamic weight profiles — shift based on time of day

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
