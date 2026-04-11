use bevy::asset::AssetPath;
use bevy::prelude::*;
use serde::Deserialize;

#[derive(Debug, Deserialize)]
pub struct Manifest {
    pub version: u32,
    pub ghosts: Vec<GhostEntry>,
}

#[derive(Debug, Deserialize, Clone)]
pub struct GhostEntry {
    pub slug: String,
    pub title: String,
    pub coordinate: [f64; 2],
    pub era_year: u32,
    pub era_window: [u32; 2],
    pub niche_tags: Vec<String>,
    pub format: String,
    pub file: String,
    #[serde(default)]
    pub preview: Option<String>,
    #[serde(default)]
    pub animated: bool,
    #[serde(default)]
    pub source_attribution: Option<String>,
    #[serde(default)]
    pub notes: Option<String>,
}

#[derive(Component, Debug)]
pub struct Ghost {
    pub slug: String,
    pub title: String,
    pub coordinate: [f64; 2],
    pub era_year: u32,
    pub era_window: [u32; 2],
    pub niche_tags: Vec<String>,
    pub animated: bool,
}

#[derive(Resource, Debug)]
pub struct GhostManifest {
    pub entries: Vec<GhostEntry>,
}

const MANIFEST_PATH: &str = "assets/pointclouds/MANIFEST.json";

/// Read and parse the manifest. On native, reads from the filesystem.
/// On WASM, std::fs is unavailable so we start with zero ghosts.
fn read_manifest() -> Manifest {
    #[cfg(not(target_arch = "wasm32"))]
    {
        use std::fs;
        use std::path::Path;

        let manifest_path = Path::new(MANIFEST_PATH);
        match fs::read_to_string(manifest_path) {
            Ok(contents) => match serde_json::from_str(&contents) {
                Ok(m) => return m,
                Err(e) => {
                    warn!(
                        "Failed to parse {}: {}. Starting with zero ghosts.",
                        MANIFEST_PATH, e
                    );
                }
            },
            Err(e) => {
                warn!(
                    "Failed to read {}: {}. Starting with zero ghosts.",
                    MANIFEST_PATH, e
                );
            }
        }
    }

    #[cfg(target_arch = "wasm32")]
    {
        info!("WASM build: ghost manifest will be loaded via asset system (not yet implemented). Starting with zero ghosts.");
    }

    Manifest {
        version: 2,
        ghosts: vec![],
    }
}

pub fn load_ghost_manifest(mut commands: Commands, asset_server: Res<AssetServer>) {
    let manifest = read_manifest();

    info!(
        "Ghost manifest v{}: {} ghost(s) declared",
        manifest.version,
        manifest.ghosts.len()
    );
    let entries = manifest.ghosts.clone();
    commands.insert_resource(GhostManifest {
        entries: entries.clone(),
    });

    for entry in &entries {
        let glb_path = format!("pointclouds/{}", entry.file);

        // On native, check if the file exists on disk before trying to load
        #[cfg(not(target_arch = "wasm32"))]
        {
            use std::path::Path;
            let full_path = Path::new("assets").join("pointclouds").join(&entry.file);
            if !full_path.exists() {
                warn!(
                    "Ghost '{}': file '{}' not found on disk — skipping. Sync from shared storage.",
                    entry.slug, entry.file
                );
                continue;
            }
        }

        info!("Ghost '{}': loading '{}'", entry.slug, glb_path);

        let asset_path: AssetPath<'static> = AssetPath::from(glb_path);
        commands.spawn((
            SceneRoot(asset_server.load(GltfAssetLabel::Scene(0).from_asset(asset_path))),
            Transform::default(),
            Visibility::default(),
            Ghost {
                slug: entry.slug.clone(),
                title: entry.title.clone(),
                coordinate: entry.coordinate,
                era_year: entry.era_year,
                era_window: entry.era_window,
                niche_tags: entry.niche_tags.clone(),
                animated: entry.animated,
            },
            Name::new(entry.title.clone()),
        ));
    }
}
