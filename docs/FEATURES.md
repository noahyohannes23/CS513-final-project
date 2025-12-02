# DC-Perspective Play Prediction Model
## Advanced Feature Engineering Plan

Generated: 2025-11-28
Goal: Predict opponent play calling from a defensive coordinator's perspective

---

## Data Sources Available

### 1. Play-by-Play (372 columns!)
- **Basic**: down, distance, yardline, score_differential, time remaining
- **Advanced**: EPA, WPA, success rate, shotgun, no_huddle
- **Play outcomes**: yards_gained, first_down conversions
- **Personnel hints**: qb_dropback, qb_scramble

### 2. Participation Data (46,168 plays)
- **Offensive personnel**: "11 personnel", "12 personnel", etc.
- **Defensive alignment**: defenders_in_box, defense_personnel
- **Pressure metrics**: was_pressure, number_of_pass_rushers
- **QB metrics**: time_to_throw (for pass plays)
- **Formation**: offense_formation

### 3. Injuries Data (5,599 records)
- Practice status by player/week
- Game status (Out, Questionable, Doubtful)
- Key starters missing

### 4. Schedules Data (285 games)
- **Weather**: roof type, temp, wind, surface
- **Context**: rest days (away_rest, home_rest)
- **Rivalry**: div_game indicator
- **Coaches**: away_coach, home_coach

### 5. Snap Counts (26,540 player-game records)
- **Fatigue tracking**: offense_snaps, offense_pct
- **Usage patterns**: Who's playing more/less than usual

### 6. NextGen Stats
- Advanced passing metrics
- Separation data
- Route running analytics

---

## Feature Categories

### CATEGORY 1: Team Tendency Features (DC Intelligence Core)

#### 1A. Historical Play Calling Patterns
**Compute rolling averages for last N games:**
```
For each team + situation:
- Pass rate by down (1st, 2nd, 3rd, 4th)
- Pass rate by distance (short: <3, medium: 3-7, long: >7)
- Pass rate by field position (own territory, midfield, red zone, goal line)
- Pass rate by score differential (trailing >7, trailing 1-7, tied, leading 1-7, leading >7)
- Pass rate by quarter (Q1, Q2, Q3, Q4)
- Pass rate by time remaining (<2 min in half)
```

**Example Features:**
- `team_pass_rate_3rd_long_last_4_games`: Team's pass rate on 3rd & 7+ in last 4 games
- `team_pass_rate_redzone_season`: Team's pass rate inside 20
- `team_pass_rate_trailing_q4`: Team's pass rate when losing in Q4

#### 1B. Offensive Coordinator Tendencies
```
- OC's career pass rate in key situations
- First play of drive tendencies
- Play-action usage rate
- Screen pass frequency
- RPO (Run-Pass Option) frequency (derived from formation + personnel)
```

#### 1C. Personnel Package Tendencies
```
From participation data:
- Pass rate from 11 personnel (1 RB, 1 TE, 3 WR)
- Pass rate from 12 personnel (1 RB, 2 TE, 2 WR)
- Pass rate from 21 personnel (2 RB, 1 TE, 2 WR)
- Pass rate from empty backfield
- Pass rate from shotgun vs under center
```

#### 1D. Opponent-Specific History
```
- How has this team performed against THIS defense historically?
- Past meetings this season
- Division rival adjustments
```

### CATEGORY 2: Momentum Features

#### 2A. Recent Play Success
```
Looking back last 3-5 plays in current drive:
- Success rate (EPA > 0 or gained yards > expected)
- Explosive play rate (10+ yards)
- Average EPA per play
- First down conversion rate
- Consecutive successful plays (streak)
```

**Example Features:**
- `momentum_success_last_3_plays`: % of successful plays in last 3
- `momentum_epa_last_5_plays`: Average EPA over last 5 plays
- `momentum_explosive_last_drive`: Has explosive play (10+ yards) on this drive
- `momentum_consecutive_successful`: Count of consecutive successful plays

#### 2B. Drive Efficiency
```
Current drive metrics:
- Yards per play on drive
- Number of first downs on drive
- Number of plays on drive (fatigue indicator)
- Drive EPA accumulated
- Time of possession on drive
```

#### 2C. Game Flow Momentum
```
- Score changes in last 2 drives
- EPA swing in last drive
- Recent turnover (within last 2 drives)
- Momentum shift indicator (recent score by opponent)
```

### CATEGORY 3: Fatigue Features

#### 3A. Offensive Fatigue
```
- Number of plays on current drive
- Total offensive snaps in game so far
- Plays run in last 5 minutes
- Time since last timeout
- No-huddle frequency (indicates urgency/fatigue)
```

**Example Features:**
- `fatigue_drive_length`: Number of plays on current drive
- `fatigue_total_snaps`: Total offensive plays run so far
- `fatigue_plays_last_5min`: Plays run in last 5 game minutes
- `fatigue_seconds_since_timeout`: Seconds since team's last timeout
- `fatigue_tempo`: Average seconds between plays in last drive

#### 3B. Defensive Fatigue
```
- Total defensive snaps faced
- Recent defensive drive length (were they just on field for 10+ plays?)
- Back-to-back possessions (3-and-out by opponent)
```

#### 3C. Personnel Fatigue
```
From snap count data:
- Is starting RB at high snap % (tired = more passing)?
- Are offensive linemen at high snap count?
- Backup QB or RB getting snaps?
```

### CATEGORY 4: Personnel & Matchup Features

#### 4A. Who's On The Field (from participation)
```
- Number of WRs on field
- Number of TEs on field
- Number of RBs on field
- Empty backfield indicator
- Personnel grouping (11, 12, 21, 22, etc.)
```

#### 4B. Key Player Availability (from injuries + snap counts)
```
- Starting RB healthy/available?
- Top WR playing (or injured)?
- Starting QB or backup?
- Offensive line injuries
```

**Example Features:**
- `personnel_top_rb_available`: Is RB1 active and not injured?
- `personnel_top_wr_snap_pct_recent`: Top WR's snap % in recent games
- `personnel_backup_qb_playing`: Backup QB indicator

#### 4C. Matchup Quality
```
- WR quality vs CB quality (could use NextGen separation stats)
- Pass rush quality vs O-line quality
- Run defense ranking vs run offense ranking
```

### CATEGORY 5: Situational Context

#### 5A. Game Script
```
- Winning/losing (and by how much)
- Expected game script (underdog teams pass more)
- Vegas spread vs actual score differential
```

#### 5B. Environmental
```
From schedules data:
- Outdoor vs dome vs closed roof
- Temperature (cold = less passing)
- Wind speed (high wind = more running)
- Surface type (turf vs grass)
```

**Example Features:**
- `context_outdoor`: Outdoor game indicator
- `context_temperature`: Temperature in Fahrenheit
- `context_wind_high`: Wind > 15 mph
- `context_cold_weather`: Temp < 40°F

#### 5C. Game Type
```
- Division game (more conservative?)
- Prime time game (Thursday/Sunday/Monday night)
- Rest days differential (team playing on short rest)
- Playoff implications
```

### CATEGORY 6: Formation & Pre-Snap (from participation)

#### 6A. Offensive Formation Indicators
```
- Shotgun vs under center
- Formation type (from participation.offense_formation)
- Motion usage (could infer from play timing)
```

#### 6B. Defensive Alignment Response
```
- Defenders in box (from participation)
- Number of pass rushers (from participation)
- Coverage type (man vs zone from participation)
```

**Example Features:**
- `formation_shotgun`: Shotgun formation
- `formation_defenders_in_box`: Number of defenders in box
- `formation_light_box`: < 6 defenders in box (run opportunity)
- `formation_heavy_box`: 8+ defenders in box (passing situation)

---

## Advanced Feature Ideas

### 1. Sequential Features (LSTM/Time-Series)
```
- Last 10 plays as a sequence (run, pass, run, run, pass...)
- Pattern detection: Does team alternate run/pass?
- Script tendencies: Do they script first 15 plays?
```

### 2. Interaction Features
```
- down * distance (3rd and 10 very different from 3rd and 1)
- score_diff * time_remaining (losing + late = passing)
- personnel * down (11 personnel on 3rd down = likely pass)
- field_position * score_diff (red zone + losing = pass)
```

### 3. Opponent-Adjusted Features
```
- Team's pass rate vs league average
- Tendency deviation (how much they deviate from expected)
- Explosive play rate vs THIS defense historically
```

### 4. Network/Graph Features
```
- QB-WR connection strength (target share)
- Formation clustering (similar formations grouped)
- Play calling network (what plays follow other plays)
```

---

## Implementation Priority

### Phase 1: Foundation (Start Here)
1. ✅ Load and cache all data sources
2. Basic team tendencies (historical pass rates)
3. Momentum features (recent play success)
4. Fatigue features (drive length, snaps)

### Phase 2: Personnel & Context
5. Personnel features (from participation)
6. Injury integration (key player availability)
7. Environmental features (weather, rest)
8. Formation features (shotgun, defenders in box)

### Phase 3: Advanced
9. Opponent-specific tendencies
10. Interaction features
11. Sequential/time-series features
12. Advanced matchup analytics

---

## Model Architecture Options

### Option 1: Team-Specific Models
Train separate model for each opponent (32 models)
- Pros: Captures team-specific quirks perfectly
- Cons: Less training data per model, maintenance burden

### Option 2: Global Model with Team Embeddings
Single model with team encoded as categorical feature
- Pros: More training data, shared learning
- Cons: May not capture unique team tendencies

### Option 3: Hierarchical Model
Base situation model + team adjustment layer
- Pros: Best of both worlds
- Cons: More complex architecture

### Option 4: Ensemble
Combine multiple approaches
- Base logistic regression (interpretable)
- Random Forest (captures interactions)
- XGBoost (best performance)
- LSTM (sequential patterns)

**Recommendation: Start with Option 2 (global model), then try Option 4 (ensemble)**

---

## Success Metrics

1. **Accuracy**: Overall prediction accuracy
2. **AUC-ROC**: Discriminative ability
3. **Brier Score**: Calibration quality
4. **Situational Accuracy**: Accuracy on 3rd down specifically
5. **Team-Specific Performance**: Accuracy vs each opponent
6. **Feature Importance**: Which features matter most?

---

## Next Steps

1. ✅ Data exploration complete
2. Implement Phase 1 feature engineering
3. Create train/test split (chronological: games 1-14 train, 15+ test)
4. Baseline model (simple features)
5. Add advanced features iteratively
6. Model comparison and ensembling
7. Evaluation and interpretation
