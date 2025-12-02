"""
Generate comprehensive HTML documentation for NFL Play-by-Play data columns
"""
import nflreadpy as nfl
from pathlib import Path
from datetime import datetime

# Column definitions organized by category
COLUMN_DEFINITIONS = {
    # Game & Play Identifiers
    'play_id': 'Numeric play ID that when used with game_id and drive provides the unique identifier for each play',
    'game_id': 'Ten digit identifier for NFL game in the format YYYY_WW_AWAY_HOME',
    'old_game_id': 'Legacy game identifier from previous data formats',
    'season': 'Four digit number indicating to which season the game belongs (e.g., 2023)',
    'season_type': 'Type of season: REG (Regular Season), POST (Postseason), PRE (Preseason)',
    'week': 'Week number within the season',
    'game_date': 'Date on which the game was played',
    'nfl_api_id': 'Identifier for the play in the NFL API',

    # Team Information
    'home_team': 'String abbreviation for the home team (e.g., KC, SF, BUF)',
    'away_team': 'String abbreviation for the away team',
    'posteam': 'String abbreviation for the team with possession of the ball',
    'posteam_type': 'Whether the possessing team is home or away',
    'defteam': 'String abbreviation for the team on defense',

    # Field Position & Situation
    'yardline_100': 'Numeric distance in yards from the opponent\'s endzone (100 = own goalline, 0 = opponent goalline)',
    'side_of_field': 'Which team\'s side of the field the play starts from',
    'yrdln': 'String representation of yard line (e.g., "KC 25", "SF 40")',
    'down': 'The down for the given play (1-4)',
    'ydstogo': 'Numeric yards in distance from first down marker or endzone',
    'goal_to_go': 'Binary indicator (0 or 1) for whether the play is a goal-to-go situation',

    # Time & Clock
    'qtr': 'Quarter of the game (1-4, 5 for overtime)',
    'time': 'Time remaining in the quarter in MM:SS format',
    'quarter_seconds_remaining': 'Numeric seconds remaining in the quarter',
    'half_seconds_remaining': 'Numeric seconds remaining in the half',
    'game_seconds_remaining': 'Numeric seconds remaining in the game',
    'game_half': 'Which half of the game (Half1, Half2, Overtime)',
    'quarter_end': 'Binary indicator for whether the play ended a quarter',
    'play_clock': 'Seconds on the play clock when the ball was snapped',
    'start_time': 'Wall clock time when the game started',
    'time_of_day': 'Wall clock time when the play occurred',
    'end_clock_time': 'Time on game clock when the play ended',

    # Play Description & Type
    'desc': 'Detailed string description of the play as provided by NFL',
    'play_type': 'String indicating type of play: pass, run, punt, field_goal, kickoff, extra_point, qb_kneel, qb_spike, no_play',
    'play_type_nfl': 'Play type as classified by the NFL',
    'yards_gained': 'Numeric yards gained (or lost) by the possessing team on the play',
    'sp': 'Binary indicator for whether the play is a scoring play (TD, FG, or safety)',
    'aborted_play': 'Binary indicator for whether the play was aborted/blown dead',
    'play_deleted': 'Binary indicator for whether the play was deleted/nullified',
    'special_teams_play': 'Binary indicator for whether the play is a special teams play',
    'st_play_type': 'Type of special teams play',

    # Offensive Formation
    'shotgun': 'Binary indicator for whether the offense was in shotgun formation',
    'no_huddle': 'Binary indicator for whether the offense used a no-huddle approach',
    'qb_dropback': 'Binary indicator for whether the QB dropped back to pass',
    'qb_kneel': 'Binary indicator for QB kneel play',
    'qb_spike': 'Binary indicator for QB spike play',
    'qb_scramble': 'Binary indicator for QB scramble on a pass play',

    # Passing Metrics
    'pass': 'Binary indicator for whether the play was a pass',
    'pass_attempt': 'Binary indicator for whether the play was a pass attempt',
    'complete_pass': 'Binary indicator for whether the pass was completed',
    'incomplete_pass': 'Binary indicator for whether the pass was incomplete',
    'pass_length': 'Length of the pass: short or deep',
    'pass_location': 'Lateral location of the pass: left, middle, or right',
    'air_yards': 'Numeric value for distance in yards perpendicular to the LOS at where the targeted receiver either caught or didn\'t catch the ball',
    'yards_after_catch': 'Numeric value for distance in yards perpendicular to the yard line where the receiver made the reception to where the play ended',
    'passing_yards': 'Total passing yards gained on the play',

    # Rushing Metrics
    'rush': 'Binary indicator for whether the play was a rush',
    'rush_attempt': 'Binary indicator for whether the play was a rush attempt',
    'run_location': 'Lateral location of the run: left, middle, or right',
    'run_gap': 'Gap through which the run went: end, guard, or tackle',
    'rushing_yards': 'Total rushing yards gained on the play',

    # Kicking & Special Teams
    'field_goal_attempt': 'Binary indicator for field goal attempt',
    'field_goal_result': 'Result of field goal: made, missed, or blocked',
    'kick_distance': 'Numeric distance in yards for kickoffs, field goals, and punts',
    'extra_point_attempt': 'Binary indicator for extra point attempt',
    'extra_point_result': 'Result of extra point: good, failed, blocked, safety, or aborted',
    'two_point_attempt': 'Binary indicator for two-point conversion attempt',
    'two_point_conv_result': 'Result of two-point conversion: success or failure',
    'kickoff_attempt': 'Binary indicator for kickoff',
    'punt_attempt': 'Binary indicator for punt',
    'punt_blocked': 'Binary indicator for whether the punt was blocked',
    'punt_inside_twenty': 'Binary indicator for punt downed inside the 20-yard line',
    'punt_in_endzone': 'Binary indicator for punt that entered the endzone',
    'punt_out_of_bounds': 'Binary indicator for punt that went out of bounds',
    'punt_downed': 'Binary indicator for punt that was downed',
    'punt_fair_catch': 'Binary indicator for fair catch on a punt',
    'kickoff_inside_twenty': 'Binary indicator for kickoff returned inside the 20-yard line',
    'kickoff_in_endzone': 'Binary indicator for kickoff into the endzone',
    'kickoff_out_of_bounds': 'Binary indicator for kickoff out of bounds',
    'kickoff_downed': 'Binary indicator for kickoff downed',
    'kickoff_fair_catch': 'Binary indicator for fair catch on kickoff',
    'touchback': 'Binary indicator for touchback',
    'own_kickoff_recovery': 'Binary indicator for kicking team recovering their own kickoff',
    'own_kickoff_recovery_td': 'Binary indicator for kicking team recovering own kickoff for touchdown',

    # Scoring
    'touchdown': 'Binary indicator for whether the play resulted in a touchdown',
    'pass_touchdown': 'Binary indicator for passing touchdown',
    'rush_touchdown': 'Binary indicator for rushing touchdown',
    'return_touchdown': 'Binary indicator for return touchdown',
    'td_team': 'String abbreviation for which team scored the touchdown',
    'td_player_name': 'Name of the player who scored the touchdown',
    'td_player_id': 'Unique identifier for the touchdown scorer',
    'safety': 'Binary indicator for safety',
    'safety_player_name': 'Name of player who recorded the safety',
    'safety_player_id': 'ID of player who recorded the safety',

    # Score Tracking
    'total_home_score': 'Total points scored by the home team so far in the game',
    'total_away_score': 'Total points scored by the away team so far in the game',
    'posteam_score': 'Current score of the team with possession',
    'defteam_score': 'Current score of the defensive team',
    'score_differential': 'Score differential from the perspective of the posteam (posteam_score - defteam_score)',
    'posteam_score_post': 'Score of the possession team after the play',
    'defteam_score_post': 'Score of the defensive team after the play',
    'score_differential_post': 'Score differential after the play',
    'away_score': 'Total away team score at end of game',
    'home_score': 'Total home team score at end of game',

    # Expected Points (EP) and Expected Points Added (EPA)
    'ep': 'Expected points with respect to the possession team before the play',
    'epa': 'Expected Points Added - the difference between EP at the start and end of a play. Measure of a play\'s impact on the score',
    'air_epa': 'EPA from the air yards alone. For completions this is actual value, for incompletions it\'s hypothetical value if completed',
    'yac_epa': 'EPA from yards after catch alone. For completions this is actual value, for incompletions it\'s the cost of the incompletion',
    'comp_air_epa': 'EPA from the air yards alone only for completions (0 otherwise)',
    'comp_yac_epa': 'EPA from yards after catch alone only for completions (0 otherwise)',
    'total_home_epa': 'Cumulative total EPA for the home team in the game so far',
    'total_away_epa': 'Cumulative total EPA for the away team in the game so far',
    'total_home_rush_epa': 'Cumulative rushing EPA for the home team',
    'total_away_rush_epa': 'Cumulative rushing EPA for the away team',
    'total_home_pass_epa': 'Cumulative passing EPA for the home team',
    'total_away_pass_epa': 'Cumulative passing EPA for the away team',
    'total_home_comp_air_epa': 'Cumulative completion air EPA for the home team',
    'total_away_comp_air_epa': 'Cumulative completion air EPA for the away team',
    'total_home_comp_yac_epa': 'Cumulative completion YAC EPA for the home team',
    'total_away_comp_yac_epa': 'Cumulative completion YAC EPA for the away team',
    'total_home_raw_air_epa': 'Cumulative raw air EPA for the home team',
    'total_away_raw_air_epa': 'Cumulative raw air EPA for the away team',
    'total_home_raw_yac_epa': 'Cumulative raw YAC EPA for the home team',
    'total_away_raw_yac_epa': 'Cumulative raw YAC EPA for the away team',
    'qb_epa': 'EPA credited to the QB on the play',

    # Win Probability (WP) and Win Probability Added (WPA)
    'wp': 'Estimated win probability for the posteam before the play',
    'wpa': 'Win Probability Added - change in win probability from the play',
    'def_wp': 'Win probability for the defensive team',
    'home_wp': 'Win probability for the home team before the play',
    'away_wp': 'Win probability for the away team before the play',
    'home_wp_post': 'Win probability for the home team after the play',
    'away_wp_post': 'Win probability for the away team after the play',
    'vegas_wp': 'Win probability for posteam incorporating pre-game Vegas line',
    'vegas_wpa': 'Win probability added incorporating Vegas line',
    'vegas_home_wp': 'Win probability for home team incorporating Vegas line',
    'vegas_home_wpa': 'Win probability added for home team incorporating Vegas line',
    'air_wpa': 'WPA through the air (same logic as air_epa)',
    'yac_wpa': 'WPA from yards after catch (same logic as yac_epa)',
    'comp_air_wpa': 'WPA from air yards on completions only',
    'comp_yac_wpa': 'WPA from YAC on completions only',
    'total_home_rush_wpa': 'Cumulative rushing WPA for home team',
    'total_away_rush_wpa': 'Cumulative rushing WPA for away team',
    'total_home_pass_wpa': 'Cumulative passing WPA for home team',
    'total_away_pass_wpa': 'Cumulative passing WPA for away team',
    'total_home_comp_air_wpa': 'Cumulative completion air WPA for home team',
    'total_away_comp_air_wpa': 'Cumulative completion air WPA for away team',
    'total_home_comp_yac_wpa': 'Cumulative completion YAC WPA for home team',
    'total_away_comp_yac_wpa': 'Cumulative completion YAC WPA for away team',
    'total_home_raw_air_wpa': 'Cumulative raw air WPA for home team',
    'total_away_raw_air_wpa': 'Cumulative raw air WPA for away team',
    'total_home_raw_yac_wpa': 'Cumulative raw YAC WPA for home team',
    'total_away_raw_yac_wpa': 'Cumulative raw YAC WPA for away team',

    # Next Score Probabilities
    'no_score_prob': 'Predicted probability of no score occurring next',
    'opp_fg_prob': 'Predicted probability of opponent scoring next with a field goal',
    'opp_safety_prob': 'Predicted probability of opponent scoring next with a safety',
    'opp_td_prob': 'Predicted probability of opponent scoring next with a touchdown',
    'fg_prob': 'Predicted probability of posteam scoring next with a field goal',
    'safety_prob': 'Predicted probability of posteam scoring next with a safety',
    'td_prob': 'Predicted probability of posteam scoring next with a touchdown',
    'extra_point_prob': 'Probability of extra point being successful',
    'two_point_conversion_prob': 'Probability of two-point conversion being successful',

    # Completion Probability & Advanced Passing Metrics
    'cp': 'Completion probability based on numerous factors including air yards, player separation, etc.',
    'cpoe': 'Completion Percentage Over Expected - difference between actual completion % and expected completion %',
    'xpass': 'Probability that the play is a pass based on the current down, distance, and field position',
    'pass_oe': 'Pass Over Expected - difference between actual pass play and expected pass probability',

    # Expected Yards After Catch (xYAC)
    'xyac_epa': 'Expected value of EPA gained after the catch, starting from where catch was made',
    'xyac_mean_yardage': 'Average expected yards after the catch',
    'xyac_median_yardage': 'Median expected yards after the catch',
    'xyac_success': 'Binary indicator for whether the actual YAC met or exceeded the expected YAC',
    'xyac_fd': 'Probability of earning a first down based on where the ball was caught',

    # Downs & Conversions
    'first_down': 'Binary indicator for whether the play resulted in a first down',
    'first_down_rush': 'Binary indicator for first down via rush',
    'first_down_pass': 'Binary indicator for first down via pass',
    'first_down_penalty': 'Binary indicator for first down via penalty',
    'third_down_converted': 'Binary indicator for successful third down conversion',
    'third_down_failed': 'Binary indicator for failed third down conversion',
    'fourth_down_converted': 'Binary indicator for successful fourth down conversion',
    'fourth_down_failed': 'Binary indicator for failed fourth down conversion',

    # Drive Information
    'drive': 'Numeric drive number in the game',
    'fixed_drive': 'Numeric drive number (with fixes applied for data consistency)',
    'fixed_drive_result': 'Result of the drive: Touchdown, Field Goal, Punt, Turnover, etc.',
    'drive_real_start_time': 'Wall clock time when drive started',
    'drive_play_count': 'Number of plays in the drive',
    'drive_time_of_possession': 'Time of possession for the drive in MM:SS',
    'drive_first_downs': 'Number of first downs achieved in the drive',
    'drive_inside20': 'Binary indicator for drive ending inside opponent\'s 20-yard line',
    'drive_ended_with_score': 'Binary indicator for whether drive ended with points scored',
    'drive_quarter_start': 'Quarter when the drive started',
    'drive_quarter_end': 'Quarter when the drive ended',
    'drive_yards_penalized': 'Total yards gained/lost via penalties during the drive',
    'drive_start_transition': 'How the offense got the ball to start the drive',
    'drive_end_transition': 'How the offense lost the ball to end the drive',
    'drive_game_clock_start': 'Game clock time when drive started',
    'drive_game_clock_end': 'Game clock time when drive ended',
    'drive_start_yard_line': 'Yard line where drive started',
    'drive_end_yard_line': 'Yard line where drive ended',
    'drive_play_id_started': 'Play ID of the first play in the drive',
    'drive_play_id_ended': 'Play ID of the last play in the drive',
    'end_yard_line': 'Yard line where the play ended',

    # Series Information
    'series': 'Numeric series number (starts at 1st & 10, ends with new 1st or change of possession)',
    'series_success': 'Binary indicator for whether the series resulted in a first down or touchdown',
    'series_result': 'Result of the series: First down, Touchdown, Turnover, Punt, etc.',
    'order_sequence': 'Order of the play within the series',
    'ydsnet': 'Net yards gained by the posteam on the series so far',
    'success': 'Binary indicator for whether the play was "successful" (contextually positive EPA)',

    # Turnovers & Ball Security
    'interception': 'Binary indicator for interception',
    'fumble': 'Binary indicator for fumble on the play',
    'fumble_forced': 'Binary indicator for forced fumble',
    'fumble_not_forced': 'Binary indicator for unforced fumble',
    'fumble_out_of_bounds': 'Binary indicator for fumble that went out of bounds',
    'fumble_lost': 'Binary indicator for fumble that was lost to the other team',
    'sack': 'Binary indicator for QB sack',
    'out_of_bounds': 'Binary indicator for play ending out of bounds',

    # Defensive Plays
    'qb_hit': 'Binary indicator for QB hit',
    'solo_tackle': 'Binary indicator for solo tackle',
    'assist_tackle': 'Binary indicator for assist tackle',
    'tackle_with_assist': 'Binary indicator for tackle with assist',
    'tackled_for_loss': 'Binary indicator for tackle for loss',
    'defensive_two_point_attempt': 'Binary indicator for defensive two-point attempt',
    'defensive_two_point_conv': 'Binary indicator for successful defensive two-point conversion',
    'defensive_extra_point_attempt': 'Binary indicator for defensive extra point attempt',
    'defensive_extra_point_conv': 'Binary indicator for successful defensive extra point conversion',

    # Penalties & Replay
    'penalty': 'Binary indicator for penalty on the play',
    'penalty_team': 'Team that committed the penalty',
    'penalty_type': 'Type of penalty called',
    'penalty_yards': 'Yards gained or lost due to penalty',
    'replay_or_challenge': 'Binary indicator for replay or coach\'s challenge',
    'replay_or_challenge_result': 'Result of the replay/challenge',

    # Timeouts
    'timeout': 'Binary indicator for timeout called',
    'timeout_team': 'Team that called the timeout',
    'home_timeouts_remaining': 'Number of timeouts remaining for home team',
    'away_timeouts_remaining': 'Number of timeouts remaining for away team',
    'posteam_timeouts_remaining': 'Number of timeouts remaining for possession team',
    'defteam_timeouts_remaining': 'Number of timeouts remaining for defensive team',

    # Returns
    'return_team': 'Team that returned the kick or punt',
    'return_yards': 'Yards gained on the return',

    # Lateral Plays
    'lateral_reception': 'Binary indicator for lateral on a reception',
    'lateral_rush': 'Binary indicator for lateral on a rush',
    'lateral_return': 'Binary indicator for lateral on a return',
    'lateral_recovery': 'Binary indicator for lateral on a fumble recovery',

    # Player IDs and Names (Primary)
    'passer_player_id': 'Unique identifier for the player who attempted the pass',
    'passer_player_name': 'Name of the passer',
    'passer': 'Short name of passer',
    'passer_id': 'Alternative passer ID',
    'passer_jersey_number': 'Jersey number of the passer',
    'receiver_player_id': 'Unique identifier for the targeted receiver',
    'receiver_player_name': 'Name of the receiver',
    'receiver': 'Short name of receiver',
    'receiver_id': 'Alternative receiver ID',
    'receiver_jersey_number': 'Jersey number of the receiver',
    'rusher_player_id': 'Unique identifier for the ball carrier on rush plays',
    'rusher_player_name': 'Name of the rusher',
    'rusher': 'Short name of rusher',
    'rusher_id': 'Alternative rusher ID',
    'rusher_jersey_number': 'Jersey number of the rusher',

    # Lateral Player Information
    'lateral_receiver_player_id': 'ID of player who received a lateral',
    'lateral_receiver_player_name': 'Name of lateral receiver',
    'lateral_receiving_yards': 'Yards gained by lateral receiver',
    'lateral_rusher_player_id': 'ID of player who lateraled on a rush',
    'lateral_rusher_player_name': 'Name of lateral rusher',
    'lateral_rushing_yards': 'Yards gained by lateral rusher',
    'lateral_sack_player_id': 'ID of player involved in lateral on sack',
    'lateral_sack_player_name': 'Name of player involved in lateral on sack',

    # Interception Players
    'interception_player_id': 'ID of player who intercepted the pass',
    'interception_player_name': 'Name of interceptor',
    'lateral_interception_player_id': 'ID of player who received lateral on interception return',
    'lateral_interception_player_name': 'Name of lateral interception receiver',

    # Return Players
    'punt_returner_player_id': 'ID of punt returner',
    'punt_returner_player_name': 'Name of punt returner',
    'lateral_punt_returner_player_id': 'ID of player receiving lateral on punt return',
    'lateral_punt_returner_player_name': 'Name of lateral punt returner',
    'kickoff_returner_player_id': 'ID of kickoff returner',
    'kickoff_returner_player_name': 'Name of kickoff returner',
    'lateral_kickoff_returner_player_id': 'ID of player receiving lateral on kickoff return',
    'lateral_kickoff_returner_player_name': 'Name of lateral kickoff returner',

    # Special Teams Players
    'punter_player_id': 'ID of the punter',
    'punter_player_name': 'Name of punter',
    'kicker_player_id': 'ID of the kicker',
    'kicker_player_name': 'Name of kicker',
    'own_kickoff_recovery_player_id': 'ID of player who recovered own team\'s kickoff',
    'own_kickoff_recovery_player_name': 'Name of own kickoff recovery player',
    'blocked_player_id': 'ID of player who blocked the kick',
    'blocked_player_name': 'Name of blocking player',

    # Defensive Players - Tackles for Loss
    'tackle_for_loss_1_player_id': 'ID of first player credited with tackle for loss',
    'tackle_for_loss_1_player_name': 'Name of first TFL player',
    'tackle_for_loss_2_player_id': 'ID of second player credited with tackle for loss',
    'tackle_for_loss_2_player_name': 'Name of second TFL player',

    # Defensive Players - QB Hits
    'qb_hit_1_player_id': 'ID of first player credited with QB hit',
    'qb_hit_1_player_name': 'Name of first QB hit player',
    'qb_hit_2_player_id': 'ID of second player credited with QB hit',
    'qb_hit_2_player_name': 'Name of second QB hit player',

    # Defensive Players - Forced Fumbles
    'forced_fumble_player_1_team': 'Team of first forced fumble player',
    'forced_fumble_player_1_player_id': 'ID of first forced fumble player',
    'forced_fumble_player_1_player_name': 'Name of first forced fumble player',
    'forced_fumble_player_2_team': 'Team of second forced fumble player',
    'forced_fumble_player_2_player_id': 'ID of second forced fumble player',
    'forced_fumble_player_2_player_name': 'Name of second forced fumble player',

    # Defensive Players - Solo Tackles
    'solo_tackle_1_team': 'Team of first solo tackler',
    'solo_tackle_1_player_id': 'ID of first solo tackler',
    'solo_tackle_1_player_name': 'Name of first solo tackler',
    'solo_tackle_2_team': 'Team of second solo tackler',
    'solo_tackle_2_player_id': 'ID of second solo tackler',
    'solo_tackle_2_player_name': 'Name of second solo tackler',

    # Defensive Players - Assist Tackles
    'assist_tackle_1_player_id': 'ID of first assist tackler',
    'assist_tackle_1_player_name': 'Name of first assist tackler',
    'assist_tackle_1_team': 'Team of first assist tackler',
    'assist_tackle_2_player_id': 'ID of second assist tackler',
    'assist_tackle_2_player_name': 'Name of second assist tackler',
    'assist_tackle_2_team': 'Team of second assist tackler',
    'assist_tackle_3_player_id': 'ID of third assist tackler',
    'assist_tackle_3_player_name': 'Name of third assist tackler',
    'assist_tackle_3_team': 'Team of third assist tackler',
    'assist_tackle_4_player_id': 'ID of fourth assist tackler',
    'assist_tackle_4_player_name': 'Name of fourth assist tackler',
    'assist_tackle_4_team': 'Team of fourth assist tackler',

    # Defensive Players - Tackles with Assist
    'tackle_with_assist_1_player_id': 'ID of first player in tackle with assist',
    'tackle_with_assist_1_player_name': 'Name of first tackle with assist player',
    'tackle_with_assist_1_team': 'Team of first tackle with assist player',
    'tackle_with_assist_2_player_id': 'ID of second player in tackle with assist',
    'tackle_with_assist_2_player_name': 'Name of second tackle with assist player',
    'tackle_with_assist_2_team': 'Team of second tackle with assist player',

    # Defensive Players - Pass Defense
    'pass_defense_1_player_id': 'ID of first player credited with pass defense',
    'pass_defense_1_player_name': 'Name of first pass defense player',
    'pass_defense_2_player_id': 'ID of second player credited with pass defense',
    'pass_defense_2_player_name': 'Name of second pass defense player',

    # Fumble Information
    'fumbled_1_team': 'Team of first player who fumbled',
    'fumbled_1_player_id': 'ID of first player who fumbled',
    'fumbled_1_player_name': 'Name of first fumbling player',
    'fumbled_2_player_id': 'ID of second player who fumbled (rare)',
    'fumbled_2_player_name': 'Name of second fumbling player',
    'fumbled_2_team': 'Team of second fumbling player',

    # Fumble Recovery
    'fumble_recovery_1_team': 'Team that recovered the fumble',
    'fumble_recovery_1_yards': 'Yards gained on fumble recovery return',
    'fumble_recovery_1_player_id': 'ID of first fumble recovery player',
    'fumble_recovery_1_player_name': 'Name of first fumble recovery player',
    'fumble_recovery_2_team': 'Team of second fumble recovery (if lateral)',
    'fumble_recovery_2_yards': 'Yards gained on second fumble recovery',
    'fumble_recovery_2_player_id': 'ID of second fumble recovery player',
    'fumble_recovery_2_player_name': 'Name of second fumble recovery player',

    # Sack Players
    'sack_player_id': 'ID of player credited with the sack',
    'sack_player_name': 'Name of sacking player',
    'half_sack_1_player_id': 'ID of first player in half-sack',
    'half_sack_1_player_name': 'Name of first half-sack player',
    'half_sack_2_player_id': 'ID of second player in half-sack',
    'half_sack_2_player_name': 'Name of second half-sack player',

    # Generic Player Fields
    'name': 'Generic player name field',
    'jersey_number': 'Generic jersey number field',
    'id': 'Generic player ID field',

    # Fantasy Fields
    'fantasy': 'Binary indicator for fantasy-relevant play',
    'fantasy_id': 'Fantasy player ID',
    'fantasy_player_name': 'Fantasy player name',
    'fantasy_player_id': 'Alternative fantasy player ID',

    # Game/Stadium Information
    'location': 'Location where game was played (Home/Neutral)',
    'result': 'Final result from home team perspective (positive = home win)',
    'total': 'Total points scored in the game',
    'spread_line': 'Pre-game point spread',
    'total_line': 'Pre-game over/under line',
    'div_game': 'Binary indicator for divisional game',
    'roof': 'Type of roof: outdoors, dome, open, closed',
    'surface': 'Playing surface type: grass, fieldturf, etc.',
    'temp': 'Temperature at kickoff (Fahrenheit)',
    'wind': 'Wind speed at kickoff (MPH)',
    'stadium': 'Name of stadium',
    'stadium_id': 'Unique identifier for stadium',
    'game_stadium': 'Stadium name (alternative field)',
    'weather': 'Weather conditions description',
    'home_coach': 'Name of home team head coach',
    'away_coach': 'Name of away team head coach',
    'home_opening_kickoff': 'Binary indicator for home team receiving opening kickoff',

    # Additional Play Indicators
    'special': 'Binary indicator for special teams play',
    'play': 'Binary indicator for countable play',
    'receiving_yards': 'Total receiving yards on the play',
}


def generate_column_category(col_name):
    """Categorize columns for better organization"""
    if any(x in col_name for x in ['play_id', 'game_id', 'season', 'week', 'old_game_id', 'nfl_api_id']):
        return 'Game & Play Identifiers'
    elif any(x in col_name for x in ['team', 'posteam', 'defteam']):
        return 'Team Information'
    elif any(x in col_name for x in ['yardline', 'down', 'ydstogo', 'goal_to_go', 'side_of_field', 'yrdln']):
        return 'Field Position & Down/Distance'
    elif any(x in col_name for x in ['qtr', 'time', 'clock', 'half', 'quarter']):
        return 'Time & Clock'
    elif any(x in col_name for x in ['desc', 'play_type', 'yards_gained', 'sp', 'aborted', 'deleted']):
        return 'Play Description & Type'
    elif any(x in col_name for x in ['shotgun', 'huddle', 'qb_dropback', 'qb_kneel', 'qb_spike', 'qb_scramble']):
        return 'Offensive Formation'
    elif any(x in col_name for x in ['pass', 'air_yards', 'yac', 'completion', 'cp', 'cpoe']) and 'epa' not in col_name and 'wpa' not in col_name:
        return 'Passing Metrics'
    elif any(x in col_name for x in ['rush', 'run_']) and 'epa' not in col_name and 'wpa' not in col_name:
        return 'Rushing Metrics'
    elif any(x in col_name for x in ['field_goal', 'extra_point', 'two_point', 'kick', 'punt']) and 'player' not in col_name:
        return 'Kicking & Special Teams'
    elif any(x in col_name for x in ['touchdown', 'td_', 'safety']) and 'prob' not in col_name and 'player' not in col_name:
        return 'Scoring'
    elif 'score' in col_name and 'prob' not in col_name:
        return 'Score Tracking'
    elif 'epa' in col_name or col_name == 'ep':
        return 'Expected Points (EPA)'
    elif 'wp' in col_name or 'wpa' in col_name:
        return 'Win Probability (WP/WPA)'
    elif 'prob' in col_name:
        return 'Probability Metrics'
    elif 'xyac' in col_name:
        return 'Expected YAC (xYAC)'
    elif 'xpass' in col_name or 'pass_oe' in col_name:
        return 'Expected Pass Metrics'
    elif any(x in col_name for x in ['first_down', 'third_down', 'fourth_down']):
        return 'Downs & Conversions'
    elif 'drive' in col_name:
        return 'Drive Information'
    elif 'series' in col_name or col_name in ['order_sequence', 'ydsnet', 'success']:
        return 'Series Information'
    elif any(x in col_name for x in ['interception', 'fumble', 'sack', 'out_of_bounds']) and 'player' not in col_name:
        return 'Turnovers & Ball Security'
    elif any(x in col_name for x in ['tackle', 'qb_hit', 'defensive']) and 'player' not in col_name:
        return 'Defensive Plays'
    elif any(x in col_name for x in ['penalty', 'replay', 'challenge']):
        return 'Penalties & Replay'
    elif 'timeout' in col_name:
        return 'Timeouts'
    elif 'return' in col_name and 'player' not in col_name:
        return 'Returns'
    elif 'lateral' in col_name and 'player' not in col_name:
        return 'Lateral Plays'
    elif any(x in col_name for x in ['passer', 'receiver', 'rusher']) and not any(y in col_name for y in ['lateral', 'punt', 'kick']):
        return 'Primary Player Information'
    elif 'lateral' in col_name and 'player' in col_name:
        return 'Lateral Player Information'
    elif 'interception' in col_name and 'player' in col_name:
        return 'Interception Players'
    elif 'returner' in col_name or ('return' in col_name and 'player' in col_name):
        return 'Return Players'
    elif ('punter' in col_name or 'kicker' in col_name or 'blocked' in col_name or 'own_kickoff' in col_name) and 'player' in col_name:
        return 'Special Teams Players'
    elif 'tackle_for_loss' in col_name:
        return 'Defensive Players - TFL'
    elif 'qb_hit' in col_name and 'player' in col_name:
        return 'Defensive Players - QB Hits'
    elif 'forced_fumble' in col_name:
        return 'Defensive Players - Forced Fumbles'
    elif 'solo_tackle' in col_name and 'player' in col_name:
        return 'Defensive Players - Solo Tackles'
    elif 'assist_tackle' in col_name and 'player' in col_name:
        return 'Defensive Players - Assist Tackles'
    elif 'tackle_with_assist' in col_name:
        return 'Defensive Players - Tackles with Assist'
    elif 'pass_defense' in col_name:
        return 'Defensive Players - Pass Defense'
    elif 'fumbled' in col_name or 'fumble_recovery' in col_name:
        return 'Fumble Players'
    elif 'sack' in col_name and 'player' in col_name:
        return 'Sack Players'
    elif 'fantasy' in col_name:
        return 'Fantasy Fields'
    elif any(x in col_name for x in ['stadium', 'roof', 'surface', 'temp', 'wind', 'weather', 'location', 'result', 'total', 'spread', 'div_game', 'coach']):
        return 'Game/Stadium Information'
    elif col_name in ['name', 'jersey_number', 'id']:
        return 'Generic Player Fields'
    else:
        return 'Other'


def create_pbp_documentation():
    """Create comprehensive HTML documentation for PBP columns"""

    # Load PBP data
    print("Loading 2023 play-by-play data...")
    pbp = nfl.load_pbp(2023)

    # Organize columns by category
    categorized_cols = {}
    for col in pbp.columns:
        category = generate_column_category(col)
        if category not in categorized_cols:
            categorized_cols[category] = []

        # Get column metadata
        dtype = str(pbp[col].dtype)
        null_count = pbp[col].null_count()
        null_pct = (null_count / pbp.height * 100) if pbp.height > 0 else 0

        try:
            n_unique = pbp[col].n_unique()
        except:
            n_unique = "N/A"

        # Get sample values
        try:
            samples = pbp[col].drop_nulls().unique().head(3).to_list()
            sample_str = ', '.join(str(s)[:30] for s in samples)
        except:
            sample_str = "N/A"

        # Get definition
        definition = COLUMN_DEFINITIONS.get(col, "No description available")

        categorized_cols[category].append({
            'name': col,
            'dtype': dtype,
            'null_pct': null_pct,
            'n_unique': n_unique,
            'samples': sample_str,
            'definition': definition
        })

    # Sort categories
    category_order = [
        'Game & Play Identifiers',
        'Team Information',
        'Field Position & Down/Distance',
        'Time & Clock',
        'Play Description & Type',
        'Offensive Formation',
        'Passing Metrics',
        'Rushing Metrics',
        'Kicking & Special Teams',
        'Scoring',
        'Score Tracking',
        'Expected Points (EPA)',
        'Win Probability (WP/WPA)',
        'Probability Metrics',
        'Expected Pass Metrics',
        'Expected YAC (xYAC)',
        'Downs & Conversions',
        'Drive Information',
        'Series Information',
        'Turnovers & Ball Security',
        'Defensive Plays',
        'Penalties & Replay',
        'Timeouts',
        'Returns',
        'Lateral Plays',
        'Primary Player Information',
        'Lateral Player Information',
        'Interception Players',
        'Return Players',
        'Special Teams Players',
        'Defensive Players - TFL',
        'Defensive Players - QB Hits',
        'Defensive Players - Forced Fumbles',
        'Defensive Players - Solo Tackles',
        'Defensive Players - Assist Tackles',
        'Defensive Players - Tackles with Assist',
        'Defensive Players - Pass Defense',
        'Fumble Players',
        'Sack Players',
        'Generic Player Fields',
        'Fantasy Fields',
        'Game/Stadium Information',
        'Other'
    ]

    # Generate HTML
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NFL Play-by-Play Data Dictionary</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}

        header {{
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}

        h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 700;
        }}

        .subtitle {{
            font-size: 1.1em;
            opacity: 0.9;
            margin-bottom: 20px;
        }}

        .stats {{
            display: flex;
            justify-content: center;
            gap: 40px;
            margin-top: 20px;
            flex-wrap: wrap;
        }}

        .stat {{
            text-align: center;
        }}

        .stat-number {{
            font-size: 2em;
            font-weight: bold;
            display: block;
        }}

        .stat-label {{
            font-size: 0.9em;
            opacity: 0.8;
        }}

        .info-section {{
            background: #f8f9fa;
            padding: 30px 40px;
            border-bottom: 1px solid #e0e0e0;
        }}

        .info-section h2 {{
            color: #1e3c72;
            margin-bottom: 15px;
        }}

        .info-section p {{
            color: #666;
            line-height: 1.8;
            margin-bottom: 10px;
        }}

        .info-section ul {{
            list-style-position: inside;
            color: #666;
            margin-left: 20px;
        }}

        .info-section li {{
            margin: 5px 0;
        }}

        .info-section a {{
            color: #2a5298;
            text-decoration: none;
            font-weight: 500;
        }}

        .info-section a:hover {{
            text-decoration: underline;
        }}

        .search-box {{
            padding: 30px 40px;
            background: #fff;
            border-bottom: 2px solid #e0e0e0;
            position: sticky;
            top: 0;
            z-index: 100;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}

        #searchInput {{
            width: 100%;
            padding: 15px 20px;
            font-size: 16px;
            border: 2px solid #ddd;
            border-radius: 8px;
            transition: all 0.3s;
        }}

        #searchInput:focus {{
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }}

        .content {{
            padding: 40px;
        }}

        .category {{
            margin-bottom: 50px;
            scroll-margin-top: 100px;
        }}

        .category-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            cursor: pointer;
            user-select: none;
        }}

        .category-header:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        }}

        .category-title {{
            font-size: 1.5em;
            font-weight: 600;
        }}

        .category-count {{
            background: rgba(255,255,255,0.2);
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
        }}

        .column-grid {{
            display: grid;
            gap: 20px;
        }}

        .column-card {{
            background: white;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 20px;
            transition: all 0.3s;
        }}

        .column-card:hover {{
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            transform: translateY(-2px);
        }}

        .column-name {{
            font-family: 'Courier New', monospace;
            font-size: 1.1em;
            font-weight: 600;
            color: #667eea;
            margin-bottom: 10px;
        }}

        .column-definition {{
            color: #444;
            line-height: 1.6;
            margin-bottom: 15px;
        }}

        .column-meta {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 10px;
            padding-top: 15px;
            border-top: 1px solid #f0f0f0;
        }}

        .meta-item {{
            font-size: 0.85em;
        }}

        .meta-label {{
            color: #888;
            font-weight: 500;
            display: block;
        }}

        .meta-value {{
            color: #333;
            font-family: 'Courier New', monospace;
            display: block;
            margin-top: 2px;
        }}

        .samples {{
            background: #f8f9fa;
            padding: 8px 12px;
            border-radius: 4px;
            font-size: 0.85em;
            margin-top: 10px;
            font-family: 'Courier New', monospace;
            color: #555;
        }}

        footer {{
            background: #f8f9fa;
            padding: 30px;
            text-align: center;
            color: #666;
            border-top: 1px solid #e0e0e0;
        }}

        .hidden {{
            display: none;
        }}

        .no-results {{
            text-align: center;
            padding: 60px 20px;
            color: #999;
        }}

        .no-results-icon {{
            font-size: 4em;
            margin-bottom: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>NFL Play-by-Play Data Dictionary</h1>
            <p class="subtitle">Comprehensive documentation for all {len(pbp.columns)} columns in the nflverse PBP dataset</p>
            <div class="stats">
                <div class="stat">
                    <span class="stat-number">{len(pbp.columns)}</span>
                    <span class="stat-label">Total Columns</span>
                </div>
                <div class="stat">
                    <span class="stat-number">{pbp.height:,}</span>
                    <span class="stat-label">Plays (2023)</span>
                </div>
                <div class="stat">
                    <span class="stat-number">{len([c for c in categorized_cols if categorized_cols[c]])}</span>
                    <span class="stat-label">Categories</span>
                </div>
            </div>
        </header>

        <div class="info-section">
            <h2>About This Data</h2>
            <p>This comprehensive data dictionary documents all columns available in the NFL play-by-play dataset from <strong>nflverse/nflreadpy</strong>. The data includes detailed play-level information from every NFL game, with advanced analytics including Expected Points Added (EPA), Win Probability Added (WPA), and Next Gen Stats metrics.</p>

            <h2 style="margin-top: 25px;">Key Metrics Explained</h2>
            <ul>
                <li><strong>EPA (Expected Points Added)</strong>: Measure of a play's impact on the score. Difference between expected points before and after the play.</li>
                <li><strong>WPA (Win Probability Added)</strong>: Change in win probability resulting from a play.</li>
                <li><strong>CPOE (Completion % Over Expected)</strong>: How much better/worse a QB's completion rate is compared to expectation based on throw difficulty.</li>
                <li><strong>xYAC (Expected Yards After Catch)</strong>: Predicted yards after catch based on where the ball was caught and defensive positioning.</li>
            </ul>

            <h2 style="margin-top: 25px;">Data Sources & References</h2>
            <ul>
                <li><a href="https://github.com/nflverse/nflreadpy" target="_blank">nflreadpy GitHub Repository</a></li>
                <li><a href="https://nflreadr.nflverse.com/articles/dictionary_pbp.html" target="_blank">nflverse Play-by-Play Data Dictionary</a></li>
                <li><a href="https://nflfastr.com/articles/field_descriptions.html" target="_blank">nflfastR Field Descriptions</a></li>
                <li><a href="https://www.nfl.com/news/next-gen-stats-intro-to-expected-yards-after-catch-0ap3000000983644" target="_blank">NFL Next Gen Stats</a></li>
            </ul>

            <p style="margin-top: 20px; font-size: 0.9em; color: #888;">
                <strong>Generated:</strong> {datetime.now().strftime('%B %d, %Y at %I:%M %p')} |
                <strong>Data Source:</strong> nflreadpy 2023 Season
            </p>
        </div>

        <div class="search-box">
            <input
                type="text"
                id="searchInput"
                placeholder="Search columns by name or description... (e.g., 'epa', 'passer', 'touchdown')"
                autocomplete="off"
            />
        </div>

        <div class="content" id="content">
"""

    # Add categories
    for category in category_order:
        if category not in categorized_cols or not categorized_cols[category]:
            continue

        cols = categorized_cols[category]
        html += f"""
            <div class="category" data-category="{category}">
                <div class="category-header">
                    <span class="category-title">{category}</span>
                    <span class="category-count">{len(cols)} columns</span>
                </div>
                <div class="column-grid">
"""

        for col in cols:
            html += f"""
                    <div class="column-card" data-column="{col['name']}" data-definition="{col['definition'].lower()}">
                        <div class="column-name">{col['name']}</div>
                        <div class="column-definition">{col['definition']}</div>
                        <div class="column-meta">
                            <div class="meta-item">
                                <span class="meta-label">Data Type</span>
                                <span class="meta-value">{col['dtype']}</span>
                            </div>
                            <div class="meta-item">
                                <span class="meta-label">Null %</span>
                                <span class="meta-value">{col['null_pct']:.1f}%</span>
                            </div>
                            <div class="meta-item">
                                <span class="meta-label">Unique Values</span>
                                <span class="meta-value">{col['n_unique']}</span>
                            </div>
                        </div>
                        <div class="samples">
                            <strong>Samples:</strong> {col['samples']}
                        </div>
                    </div>
"""

        html += """
                </div>
            </div>
"""

    # Close HTML
    html += """
            <div id="noResults" class="no-results hidden">
                <div class="no-results-icon">🔍</div>
                <h2>No columns found</h2>
                <p>Try a different search term</p>
            </div>
        </div>

        <footer>
            <p><strong>NFL Play-by-Play Data Dictionary</strong></p>
            <p>Created for CS513 Final Project - Understanding NFL Analytics Data</p>
            <p style="margin-top: 10px; font-size: 0.9em;">
                Data provided by nflverse | Documentation generated with nflreadpy
            </p>
        </footer>
    </div>

    <script>
        const searchInput = document.getElementById('searchInput');
        const categories = document.querySelectorAll('.category');
        const noResults = document.getElementById('noResults');

        searchInput.addEventListener('input', function(e) {
            const searchTerm = e.target.value.toLowerCase().trim();
            let hasResults = false;

            categories.forEach(category => {
                const cards = category.querySelectorAll('.column-card');
                let categoryHasVisible = false;

                cards.forEach(card => {
                    const columnName = card.dataset.column.toLowerCase();
                    const definition = card.dataset.definition.toLowerCase();

                    if (searchTerm === '' || columnName.includes(searchTerm) || definition.includes(searchTerm)) {
                        card.classList.remove('hidden');
                        categoryHasVisible = true;
                        hasResults = true;
                    } else {
                        card.classList.add('hidden');
                    }
                });

                if (categoryHasVisible) {
                    category.classList.remove('hidden');
                } else {
                    category.classList.add('hidden');
                }
            });

            if (hasResults) {
                noResults.classList.add('hidden');
            } else {
                noResults.classList.remove('hidden');
            }
        });

        // Optional: Add category collapse/expand functionality
        document.querySelectorAll('.category-header').forEach(header => {
            header.addEventListener('click', function() {
                const grid = this.nextElementSibling;
                if (grid.style.display === 'none') {
                    grid.style.display = 'grid';
                } else {
                    grid.style.display = 'none';
                }
            });
        });
    </script>
</body>
</html>
"""

    # Save the file
    output_path = Path('pbp_data_dictionary.html')
    output_path.write_text(html, encoding='utf-8')

    print(f"\n[OK] Created comprehensive PBP documentation: {output_path.absolute()}")
    print(f"    - {len(pbp.columns)} columns documented")
    print(f"    - {len([c for c in categorized_cols if categorized_cols[c]])} categories")
    print(f"    - Searchable HTML interface")
    print(f"\nOpen {output_path.absolute()} in your browser to view!")


if __name__ == '__main__':
    create_pbp_documentation()
