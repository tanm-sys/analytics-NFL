# 🧩 Component Diagram

Class relationships and module dependencies.

---

## 📦 Package Overview

```mermaid
classDiagram
    direction TB
    
    class NFLDataLoader {
        +data_dir: str
        +input_df: DataFrame
        +output_df: DataFrame
        +supplementary_df: DataFrame
        --
        +load_all_weeks(weeks, verbose)
        +load_supplementary()
        +create_play_dataset()
        +get_play_tracking(game_id, play_id)
        +get_player_frames(game_id, play_id, nfl_id)
        +standardize_coordinates(df)
        +get_players_to_predict(game_id, play_id)
        +get_play_metadata(game_id, play_id)
        +summary_stats()
    }
    
    class FeatureEngineer {
        +FRAME_RATE: int = 10
        +FRAME_INTERVAL: float = 0.1
        +smooth_sigma: float
        --
        +calculate_velocity(df)
        +calculate_acceleration(df)
        +calculate_jerk(df)
        +calculate_path_metrics(df)
        +calculate_distance_to_point(df, x, y)
        +calculate_player_separation(df1, df2)
        +calculate_closing_speed(df1, df2)
        +process_player_tracking(df)
        +detect_reaction_frame(df, threshold)
        +calculate_break_quality(df, break_frame)
    }
    
    class RAIComponents {
        <<dataclass>>
        +rtd: float
        +te: float
        +bpq: float
        +cms: float
        +sd: float
        +rai: float
        +player_role: str
        +nfl_id: int
        --
        +to_dict()
    }
    
    class RAICalculator {
        +feature_engineer: FeatureEngineer
        +rtd_thresholds: dict
        +weights: dict
        +normalization_params: dict
        --
        +calculate_rtd(player_df, player_role)
        +calculate_te(player_df)
        +calculate_bpq(player_df)
        +calculate_cms(defender_df, ball_trajectory)
        +calculate_sd(receiver_df, defender_df)
        +normalize_component(value, component)
        +calculate_composite_rai(components, role)
        +calculate_player_rai(input_df, output_df, ...)
        +calculate_play_rai(input_df, output_df, ...)
    }
    
    RAICalculator --> FeatureEngineer : uses
    RAICalculator --> RAIComponents : creates
```

---

## 📊 Visualization Classes

```mermaid
classDiagram
    direction TB
    
    class NFLFieldPlotter {
        +figsize: tuple
        +colors: dict
        --
        +create_field(ax, yard_range)
        +plot_players(ax, player_data, show_trails)
        +plot_trajectories(ax, predicted, actual, nfl_id)
        +plot_ball_trajectory(ax, start, end)
    }
    
    class RAIVisualizer {
        +output_dir: Path
        +field_plotter: NFLFieldPlotter
        +colors: dict
        --
        +plot_rai_distribution(rai_df, group_by, save)
        +plot_component_breakdown(rai_components, top_n)
        +plot_reaction_heatmap(player_data, rai_scores)
        +plot_coverage_comparison(rai_by_coverage)
        +create_play_animation_frames(input_df, output_df, ...)
    }
    
    class VideoGenerator {
        +output_dir: Path
        +field_plotter: NFLFieldPlotter
        +fps: int
        --
        +create_play_video(input_df, output_df, ...)
        +render_frame(ax, frame_data, ...)
    }
    
    RAIVisualizer --> NFLFieldPlotter : contains
    VideoGenerator --> NFLFieldPlotter : uses
```

---

## 🔄 Analysis Pipeline

```mermaid
classDiagram
    direction TB
    
    class RAIAnalysis {
        +data_dir: str
        +output_dir: Path
        +loader: NFLDataLoader
        +feature_engineer: FeatureEngineer
        +rai_calculator: RAICalculator
        +visualizer: RAIVisualizer
        +video_gen: VideoGenerator
        +results_df: DataFrame
        +insights: dict
        --
        +load_data(weeks, verbose)
        +calculate_all_rai(sample_size, verbose)
        +generate_insights()
        +create_visualizations(save)
        +create_sample_video(n_plays)
        +export_results()
        +run_full_analysis(weeks, sample_size, create_videos)
    }
    
    RAIAnalysis --> NFLDataLoader : uses
    RAIAnalysis --> FeatureEngineer : uses
    RAIAnalysis --> RAICalculator : uses
    RAIAnalysis --> RAIVisualizer : uses
    RAIAnalysis --> VideoGenerator : uses
```

---

## 🖥️ Dashboard Components

```mermaid
classDiagram
    direction LR
    
    class DashboardApp {
        <<Streamlit>>
        +main()
        +setup_page_config()
        +initialize_session_state()
    }
    
    class OverviewPage {
        +render_key_metrics()
        +render_rai_distribution()
        +render_summary_cards()
    }
    
    class PlayerExplorerPage {
        +render_player_selector()
        +render_player_stats()
        +render_player_history()
    }
    
    class PlayAnalysisPage {
        +render_play_selector()
        +render_field_view()
        +render_rai_breakdown()
    }
    
    class CoverageAnalysisPage {
        +render_coverage_comparison()
        +render_role_analysis()
    }
    
    class LeaderboardsPage {
        +render_top_players()
        +render_rankings()
        +render_filters()
    }
    
    class DashboardDataLoader {
        +load_rai_results()
        +load_player_aggregates()
        +get_unique_players()
        +get_unique_games()
    }
    
    class ChartComponents {
        +create_metric_card()
        +create_distribution_chart()
        +create_radar_chart()
    }
    
    class Field3D {
        +create_3d_field()
        +plot_player_positions()
    }
    
    class Themes {
        +get_theme_colors()
        +apply_theme()
    }
    
    DashboardApp --> OverviewPage
    DashboardApp --> PlayerExplorerPage
    DashboardApp --> PlayAnalysisPage
    DashboardApp --> CoverageAnalysisPage
    DashboardApp --> LeaderboardsPage
    
    OverviewPage --> DashboardDataLoader
    OverviewPage --> ChartComponents
    
    PlayerExplorerPage --> DashboardDataLoader
    PlayerExplorerPage --> ChartComponents
    
    PlayAnalysisPage --> Field3D
    PlayAnalysisPage --> DashboardDataLoader
```

---

## 🔗 Module Dependencies

```mermaid
graph TB
    subgraph external["External Dependencies"]
        PD["pandas"]
        NP["numpy"]
        SP["scipy"]
        MPL["matplotlib"]
        SNS["seaborn"]
        PLT["plotly"]
        ST["streamlit"]
        IO["imageio"]
        TQDM["tqdm"]
    end
    
    subgraph core["nfl_rai Package"]
        DL["data_loader"]
        FE["feature_engineering"]
        RC["rai_calculator"]
        VIZ["visualizations"]
        VID["video_generator"]
    end
    
    subgraph analysis["Analysis"]
        RA["rai_analysis"]
    end
    
    subgraph dashboard["Dashboard"]
        APP["app"]
        PAGES["pages/*"]
        COMP["components/*"]
    end
    
    PD --> DL & FE & RC
    NP --> FE & RC & VIZ
    SP --> FE
    MPL & SNS --> VIZ
    PLT --> COMP
    ST --> APP & PAGES
    IO --> VID
    TQDM --> DL & RA
    
    DL --> FE
    FE --> RC
    RC --> VIZ
    RC --> VID
    
    DL & FE & RC & VIZ & VID --> RA
    
    APP --> PAGES
    PAGES --> COMP
    
    style external fill:#1a365d,stroke:#3182ce,color:#fff
    style core fill:#22543d,stroke:#38a169,color:#fff
    style analysis fill:#553c9a,stroke:#805ad5,color:#fff
    style dashboard fill:#c53030,stroke:#fc8181,color:#fff
```

---

## 📐 Entity Relationships

```mermaid
erDiagram
    GAME ||--o{ PLAY : contains
    PLAY ||--o{ TRACKING_FRAME : has
    PLAY ||--|| SUPPLEMENTARY : metadata
    PLAYER ||--o{ TRACKING_FRAME : appears_in
    PLAY ||--o{ RAI_RESULT : generates
    PLAYER ||--o{ RAI_RESULT : has
    
    GAME {
        int gameId PK
        date gameDate
        string homeTeam
        string awayTeam
    }
    
    PLAY {
        int gameId FK
        int playId PK
        int quarter
        int down
        int yardsToGo
        string coverage
    }
    
    PLAYER {
        int nflId PK
        string displayName
        string position
        string team
    }
    
    TRACKING_FRAME {
        int gameId FK
        int playId FK
        int nflId FK
        int frameId
        float x
        float y
        float s
        float a
        string event
    }
    
    SUPPLEMENTARY {
        int gameId FK
        int playId FK
        float x_end
        float y_end
        string coverageType
    }
    
    RAI_RESULT {
        int gameId FK
        int playId FK
        int nflId FK
        float rtd
        float te
        float bpq
        float cms
        float sd
        float rai
        string player_role
    }
```

---

## 🔄 State Flow

```mermaid
stateDiagram-v2
    direction LR
    
    [*] --> Initialized: Create NFLDataLoader
    
    Initialized --> DataLoaded: load_all_weeks()
    DataLoaded --> MetadataLoaded: load_supplementary()
    
    MetadataLoaded --> Processing: For each play
    
    state Processing {
        [*] --> ExtractPlay
        ExtractPlay --> CalculateFeatures
        CalculateFeatures --> CalculateRAI
        CalculateRAI --> StoreResults
        StoreResults --> [*]
    }
    
    Processing --> Complete: All plays processed
    Complete --> Visualizing: create_visualizations()
    Visualizing --> Exporting: export_results()
    Exporting --> [*]
```

---

## ⏭️ Next Steps

- **[API Reference](../api-reference/data-loader.md)** - Detailed method documentation
- **[Data Schema](../technical/data-schema.md)** - Column specifications
- **[Dashboard Components](../technical/dashboard-components.md)** - UI architecture
