# Load Functions¶

**Source:** https://nflreadpy.nflverse.com/api/load_functions/

---


# Load Functions¶


## nflreadpy.load_pbp
¶

Load NFL play-by-play data.


### load_pbp
¶


```
load_pbp(
    seasons: int | list[int] | bool | None = None,
) -> pl.DataFrame
```


```
load_pbp(
    seasons: int | list[int] | bool | None = None,
) -> pl.DataFrame
```

Load NFL play-by-play data.

Parameters:


```
seasons
```


```
int | list[int] | bool | None
```

Season(s) to load. If None, loads current season.
    If True, loads all available data since 1999.
    If int or list of ints, loads specified season(s).


```
None
```

Returns:


```
DataFrame
```

Polars DataFrame with play-by-play data.

https://nflreadr.nflverse.com/reference/load_pbp.html

https://nflreadr.nflverse.com/articles/dictionary_pbp.html


```
src/nflreadpy/load_pbp.py
```


```
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35
36
37
38
39
40
41
42
43
44
45
46
47
48
49
50
51
52
53
```


```
def load_pbp(seasons: int | list[int] | bool | None = None) -> pl.DataFrame:
    """
    Load NFL play-by-play data.

    Args:
        seasons: Season(s) to load. If None, loads current season.
                If True, loads all available data since 1999.
                If int or list of ints, loads specified season(s).

    Returns:
        Polars DataFrame with play-by-play data.

    See Also:
        <https://nflreadr.nflverse.com/reference/load_pbp.html>

    Data Dictionary:
        <https://nflreadr.nflverse.com/articles/dictionary_pbp.html>
    """
    if seasons is None:
        seasons = [get_current_season()]
    elif seasons is True:
        # Load all available seasons (1999 to current)
        current_season = get_current_season()
        seasons = list(range(1999, current_season + 1))
    elif isinstance(seasons, int):
        seasons = [seasons]

    # Validate seasons
    current_season = get_current_season()
    for season in seasons:
        if not isinstance(season, int) or season < 1999 or season > current_season:
            raise ValueError(f"Season must be between 1999 and {current_season}")

    downloader = get_downloader()
    dataframes = []

    for season in seasons:
        path = f"pbp/play_by_play_{season}"
        df = downloader.download("nflverse-data", path, season=season)
        dataframes.append(df)

    if len(dataframes) == 1:
        return dataframes[0]
    else:
        return pl.concat(dataframes, how="diagonal_relaxed")
```


```
def load_pbp(seasons: int | list[int] | bool | None = None) -> pl.DataFrame:
    """
    Load NFL play-by-play data.

    Args:
        seasons: Season(s) to load. If None, loads current season.
                If True, loads all available data since 1999.
                If int or list of ints, loads specified season(s).

    Returns:
        Polars DataFrame with play-by-play data.

    See Also:
        <https://nflreadr.nflverse.com/reference/load_pbp.html>

    Data Dictionary:
        <https://nflreadr.nflverse.com/articles/dictionary_pbp.html>
    """
    if seasons is None:
        seasons = [get_current_season()]
    elif seasons is True:
        # Load all available seasons (1999 to current)
        current_season = get_current_season()
        seasons = list(range(1999, current_season + 1))
    elif isinstance(seasons, int):
        seasons = [seasons]

    # Validate seasons
    current_season = get_current_season()
    for season in seasons:
        if not isinstance(season, int) or season < 1999 or season > current_season:
            raise ValueError(f"Season must be between 1999 and {current_season}")

    downloader = get_downloader()
    dataframes = []

    for season in seasons:
        path = f"pbp/play_by_play_{season}"
        df = downloader.download("nflverse-data", path, season=season)
        dataframes.append(df)

    if len(dataframes) == 1:
        return dataframes[0]
    else:
        return pl.concat(dataframes, how="diagonal_relaxed")
```


## nflreadpy.load_player_stats
¶


```
load_player_stats(
    seasons: int | list[int] | bool | None = None,
    summary_level: Literal[
        "week", "reg", "post", "reg+post"
    ] = "week",
) -> pl.DataFrame
```


```
load_player_stats(
    seasons: int | list[int] | bool | None = None,
    summary_level: Literal[
        "week", "reg", "post", "reg+post"
    ] = "week",
) -> pl.DataFrame
```

Load NFL player statistics.

Parameters:


```
seasons
```


```
int | list[int] | bool | None
```

Season(s) to load. If None, loads current season.
    If True, loads all available data.
    If int or list of ints, loads specified season(s).


```
None
```


```
summary_level
```


```
Literal['week', 'reg', 'post', 'reg+post']
```

Summary level ("week", "reg", "post", "reg+post").


```
'week'
```

Returns:


```
DataFrame
```

Polars DataFrame with player statistics.

https://nflreadr.nflverse.com/reference/load_player_stats.html

https://nflreadr.nflverse.com/articles/dictionary_player_stats.html


```
src/nflreadpy/load_stats.py
```


```
67
68
69
70
71
72
73
74
75
76
77
78
79
80
81
82
83
84
85
86
87
88
89
```


```
def load_player_stats(
    seasons: int | list[int] | bool | None = None,
    summary_level: Literal["week", "reg", "post", "reg+post"] = "week",
) -> pl.DataFrame:
    """
    Load NFL player statistics.

    Args:
        seasons: Season(s) to load. If None, loads current season.
                If True, loads all available data.
                If int or list of ints, loads specified season(s).
        summary_level: Summary level ("week", "reg", "post", "reg+post").

    Returns:
        Polars DataFrame with player statistics.

    See Also:
        <https://nflreadr.nflverse.com/reference/load_player_stats.html>

    Data Dictionary:
        <https://nflreadr.nflverse.com/articles/dictionary_player_stats.html>
    """
    return _load_stats("player", seasons, summary_level)
```


```
def load_player_stats(
    seasons: int | list[int] | bool | None = None,
    summary_level: Literal["week", "reg", "post", "reg+post"] = "week",
) -> pl.DataFrame:
    """
    Load NFL player statistics.

    Args:
        seasons: Season(s) to load. If None, loads current season.
                If True, loads all available data.
                If int or list of ints, loads specified season(s).
        summary_level: Summary level ("week", "reg", "post", "reg+post").

    Returns:
        Polars DataFrame with player statistics.

    See Also:
        <https://nflreadr.nflverse.com/reference/load_player_stats.html>

    Data Dictionary:
        <https://nflreadr.nflverse.com/articles/dictionary_player_stats.html>
    """
    return _load_stats("player", seasons, summary_level)
```


## nflreadpy.load_team_stats
¶


```
load_team_stats(
    seasons: int | list[int] | bool | None = None,
    summary_level: Literal[
        "week", "reg", "post", "reg+post"
    ] = "week",
) -> pl.DataFrame
```


```
load_team_stats(
    seasons: int | list[int] | bool | None = None,
    summary_level: Literal[
        "week", "reg", "post", "reg+post"
    ] = "week",
) -> pl.DataFrame
```

Load NFL team statistics.

Parameters:


```
seasons
```


```
int | list[int] | bool | None
```

Season(s) to load. If None, loads current season.
    If True, loads all available data.
    If int or list of ints, loads specified season(s).


```
None
```


```
summary_level
```


```
Literal['week', 'reg', 'post', 'reg+post']
```

Summary level ("week", "reg", "post", "reg+post").


```
'week'
```

Returns:


```
DataFrame
```

Polars DataFrame with team statistics.

https://nflreadr.nflverse.com/reference/load_team_stats.html

https://nflreadr.nflverse.com/articles/dictionary_team_stats.html


```
src/nflreadpy/load_stats.py
```


```
92
 93
 94
 95
 96
 97
 98
 99
100
101
102
103
104
105
106
107
108
109
110
111
112
113
114
```


```
def load_team_stats(
    seasons: int | list[int] | bool | None = None,
    summary_level: Literal["week", "reg", "post", "reg+post"] = "week",
) -> pl.DataFrame:
    """
    Load NFL team statistics.

    Args:
        seasons: Season(s) to load. If None, loads current season.
                If True, loads all available data.
                If int or list of ints, loads specified season(s).
        summary_level: Summary level ("week", "reg", "post", "reg+post").

    Returns:
        Polars DataFrame with team statistics.

    See Also:
        <https://nflreadr.nflverse.com/reference/load_team_stats.html>

    Data Dictionary:
        <https://nflreadr.nflverse.com/articles/dictionary_team_stats.html>
    """
    return _load_stats("team", seasons, summary_level)
```


```
def load_team_stats(
    seasons: int | list[int] | bool | None = None,
    summary_level: Literal["week", "reg", "post", "reg+post"] = "week",
) -> pl.DataFrame:
    """
    Load NFL team statistics.

    Args:
        seasons: Season(s) to load. If None, loads current season.
                If True, loads all available data.
                If int or list of ints, loads specified season(s).
        summary_level: Summary level ("week", "reg", "post", "reg+post").

    Returns:
        Polars DataFrame with team statistics.

    See Also:
        <https://nflreadr.nflverse.com/reference/load_team_stats.html>

    Data Dictionary:
        <https://nflreadr.nflverse.com/articles/dictionary_team_stats.html>
    """
    return _load_stats("team", seasons, summary_level)
```


## nflreadpy.load_schedules
¶

Load NFL schedule data.


### load_schedules
¶


```
load_schedules(
    seasons: int | list[int] | bool | None = True,
) -> pl.DataFrame
```


```
load_schedules(
    seasons: int | list[int] | bool | None = True,
) -> pl.DataFrame
```

Load NFL schedules.

Parameters:


```
seasons
```


```
int | list[int] | bool | None
```

Season(s) to load. If True (default), loads all available data.
    If int or list of ints, loads specified season(s).
    If None, loads current season.


```
True
```

Returns:


```
DataFrame
```

Polars DataFrame with schedule data.

https://nflreadr.nflverse.com/reference/load_schedules.html

https://nflreadr.nflverse.com/articles/dictionary_schedules.html


```
src/nflreadpy/load_schedules.py
```


```
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35
36
37
38
39
40
41
42
43
44
45
46
47
48
49
50
51
52
```


```
def load_schedules(seasons: int | list[int] | bool | None = True) -> pl.DataFrame:
    """
    Load NFL schedules.

    Args:
        seasons: Season(s) to load. If True (default), loads all available data.
                If int or list of ints, loads specified season(s).
                If None, loads current season.

    Returns:
        Polars DataFrame with schedule data.

    See Also:
        <https://nflreadr.nflverse.com/reference/load_schedules.html>

    Data Dictionary:
        <https://nflreadr.nflverse.com/articles/dictionary_schedules.html>
    """
    downloader = get_downloader()

    # Load the full games dataset
    df = downloader.download("nflverse-data", "schedules/games")

    # Filter by seasons if specified
    if seasons is not True:
        if seasons is None:
            seasons = [get_current_season()]
        elif isinstance(seasons, int):
            seasons = [seasons]

        # Filter the dataframe by season
        df = df.filter(pl.col("season").is_in(seasons))

    # Validate and clean roof values (matching nflreadr logic)
    if "roof" in df.columns:
        valid_roof_values = ["dome", "outdoors", "closed", "open"]
        df = df.with_columns(
            pl.when(pl.col("roof").is_in(valid_roof_values))
            .then(pl.col("roof"))
            .otherwise(None)
            .alias("roof")
        )

    return df
```


```
def load_schedules(seasons: int | list[int] | bool | None = True) -> pl.DataFrame:
    """
    Load NFL schedules.

    Args:
        seasons: Season(s) to load. If True (default), loads all available data.
                If int or list of ints, loads specified season(s).
                If None, loads current season.

    Returns:
        Polars DataFrame with schedule data.

    See Also:
        <https://nflreadr.nflverse.com/reference/load_schedules.html>

    Data Dictionary:
        <https://nflreadr.nflverse.com/articles/dictionary_schedules.html>
    """
    downloader = get_downloader()

    # Load the full games dataset
    df = downloader.download("nflverse-data", "schedules/games")

    # Filter by seasons if specified
    if seasons is not True:
        if seasons is None:
            seasons = [get_current_season()]
        elif isinstance(seasons, int):
            seasons = [seasons]

        # Filter the dataframe by season
        df = df.filter(pl.col("season").is_in(seasons))

    # Validate and clean roof values (matching nflreadr logic)
    if "roof" in df.columns:
        valid_roof_values = ["dome", "outdoors", "closed", "open"]
        df = df.with_columns(
            pl.when(pl.col("roof").is_in(valid_roof_values))
            .then(pl.col("roof"))
            .otherwise(None)
            .alias("roof")
        )

    return df
```


## nflreadpy.load_teams
¶

Load NFL team data.


### load_teams
¶


```
load_teams() -> pl.DataFrame
```


```
load_teams() -> pl.DataFrame
```

Load NFL team information.

Returns:


```
DataFrame
```

Polars DataFrame with team data including abbreviations, names,        colors, logos, and other team metadata.

https://nflreadr.nflverse.com/reference/load_teams.html


```
src/nflreadpy/load_teams.py
```


```
8
 9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
```


```
def load_teams() -> pl.DataFrame:
    """
    Load NFL team information.

    Returns:
        Polars DataFrame with team data including abbreviations, names,\
        colors, logos, and other team metadata.

    See Also:
        <https://nflreadr.nflverse.com/reference/load_teams.html>
    """
    downloader = get_downloader()

    # Load teams data from nflverse-data repository
    df = downloader.download("nflverse-data", "teams/teams_colors_logos")

    return df
```


```
def load_teams() -> pl.DataFrame:
    """
    Load NFL team information.

    Returns:
        Polars DataFrame with team data including abbreviations, names,\
        colors, logos, and other team metadata.

    See Also:
        <https://nflreadr.nflverse.com/reference/load_teams.html>
    """
    downloader = get_downloader()

    # Load teams data from nflverse-data repository
    df = downloader.download("nflverse-data", "teams/teams_colors_logos")

    return df
```


## nflreadpy.load_players
¶

Load NFL player data.


### load_players
¶


```
load_players() -> pl.DataFrame
```


```
load_players() -> pl.DataFrame
```

Load NFL player information.

This is a comprehensive source of player information including basic details,
draft information, positions, and ID mappings across multiple data sources
(GSIS, PFR, PFF, OTC, ESB, ESPN).

Returns:


```
DataFrame
```

Polars DataFrame with player data - one row per player with comprehensive         player information including names, physical stats, draft info, and         cross-platform ID mappings.

https://nflreadr.nflverse.com/reference/load_players.html

https://nflreadr.nflverse.com/articles/dictionary_players.html


```
src/nflreadpy/load_players.py
```


```
8
 9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
```


```
def load_players() -> pl.DataFrame:
    """
    Load NFL player information.

    This is a comprehensive source of player information including basic details,
    draft information, positions, and ID mappings across multiple data sources
    (GSIS, PFR, PFF, OTC, ESB, ESPN).

    Returns:
        Polars DataFrame with player data - one row per player with comprehensive \
        player information including names, physical stats, draft info, and \
        cross-platform ID mappings.

    See Also:
        <https://nflreadr.nflverse.com/reference/load_players.html>

    Data Dictionary:
        <https://nflreadr.nflverse.com/articles/dictionary_players.html>
    """
    downloader = get_downloader()

    # Load players data from nflverse-data repository
    df = downloader.download("nflverse-data", "players/players")

    return df
```


```
def load_players() -> pl.DataFrame:
    """
    Load NFL player information.

    This is a comprehensive source of player information including basic details,
    draft information, positions, and ID mappings across multiple data sources
    (GSIS, PFR, PFF, OTC, ESB, ESPN).

    Returns:
        Polars DataFrame with player data - one row per player with comprehensive \
        player information including names, physical stats, draft info, and \
        cross-platform ID mappings.

    See Also:
        <https://nflreadr.nflverse.com/reference/load_players.html>

    Data Dictionary:
        <https://nflreadr.nflverse.com/articles/dictionary_players.html>
    """
    downloader = get_downloader()

    # Load players data from nflverse-data repository
    df = downloader.download("nflverse-data", "players/players")

    return df
```


## nflreadpy.load_rosters
¶

Load NFL roster data.


### load_rosters
¶


```
load_rosters(
    seasons: int | list[int] | bool | None = None,
) -> pl.DataFrame
```


```
load_rosters(
    seasons: int | list[int] | bool | None = None,
) -> pl.DataFrame
```

Load NFL team rosters.

Parameters:


```
seasons
```


```
int | list[int] | bool | None
```

Season(s) to load. If None, loads current roster year.
    If True, loads all available data since 1920.
    If int or list of ints, loads specified season(s).


```
None
```

Returns:


```
DataFrame
```

Polars DataFrame with roster data.

https://nflreadr.nflverse.com/reference/load_rosters.html

https://nflreadr.nflverse.com/articles/dictionary_rosters.html


```
src/nflreadpy/load_rosters.py
```


```
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35
36
37
38
39
40
41
42
43
44
45
46
47
48
49
50
51
52
53
```


```
def load_rosters(seasons: int | list[int] | bool | None = None) -> pl.DataFrame:
    """
    Load NFL team rosters.

    Args:
        seasons: Season(s) to load. If None, loads current roster year.
                If True, loads all available data since 1920.
                If int or list of ints, loads specified season(s).

    Returns:
        Polars DataFrame with roster data.

    See Also:
        <https://nflreadr.nflverse.com/reference/load_rosters.html>

    Data Dictionary:
        <https://nflreadr.nflverse.com/articles/dictionary_rosters.html>
    """
    if seasons is None:
        seasons = [get_current_season(roster=True)]
    elif seasons is True:
        # Load all available seasons (1920 to current roster year)
        current_roster_year = get_current_season(roster=True)
        seasons = list(range(1920, current_roster_year + 1))
    elif isinstance(seasons, int):
        seasons = [seasons]

    # Validate seasons
    current_roster_year = get_current_season(roster=True)
    for season in seasons:
        if not isinstance(season, int) or season < 1920 or season > current_roster_year:
            raise ValueError(f"Season must be between 1920 and {current_roster_year}")

    downloader = get_downloader()
    dataframes = []

    for season in seasons:
        path = f"rosters/roster_{season}"
        df = downloader.download("nflverse-data", path, season=season)
        dataframes.append(df)

    if len(dataframes) == 1:
        return dataframes[0]
    else:
        return pl.concat(dataframes, how="diagonal_relaxed")
```


```
def load_rosters(seasons: int | list[int] | bool | None = None) -> pl.DataFrame:
    """
    Load NFL team rosters.

    Args:
        seasons: Season(s) to load. If None, loads current roster year.
                If True, loads all available data since 1920.
                If int or list of ints, loads specified season(s).

    Returns:
        Polars DataFrame with roster data.

    See Also:
        <https://nflreadr.nflverse.com/reference/load_rosters.html>

    Data Dictionary:
        <https://nflreadr.nflverse.com/articles/dictionary_rosters.html>
    """
    if seasons is None:
        seasons = [get_current_season(roster=True)]
    elif seasons is True:
        # Load all available seasons (1920 to current roster year)
        current_roster_year = get_current_season(roster=True)
        seasons = list(range(1920, current_roster_year + 1))
    elif isinstance(seasons, int):
        seasons = [seasons]

    # Validate seasons
    current_roster_year = get_current_season(roster=True)
    for season in seasons:
        if not isinstance(season, int) or season < 1920 or season > current_roster_year:
            raise ValueError(f"Season must be between 1920 and {current_roster_year}")

    downloader = get_downloader()
    dataframes = []

    for season in seasons:
        path = f"rosters/roster_{season}"
        df = downloader.download("nflverse-data", path, season=season)
        dataframes.append(df)

    if len(dataframes) == 1:
        return dataframes[0]
    else:
        return pl.concat(dataframes, how="diagonal_relaxed")
```


## nflreadpy.load_rosters_weekly
¶

Load NFL weekly rosters data.


### load_rosters_weekly
¶


```
load_rosters_weekly(
    seasons: int | list[int] | bool | None = None,
) -> pl.DataFrame
```


```
load_rosters_weekly(
    seasons: int | list[int] | bool | None = None,
) -> pl.DataFrame
```

Load NFL weekly rosters data.

Data available from 2002 onwards.

Parameters:


```
seasons
```


```
int | list[int] | bool | None
```

Season(s) to load. If None, loads current season.
    If True, loads all available data since 2002.
    If int or list of ints, loads specified season(s).


```
None
```

Returns:


```
DataFrame
```

Polars DataFrame with weekly roster data including player status        changes, injury designations, and week-by-week roster moves.

https://nflreadr.nflverse.com/reference/load_rosters_weekly.html

https://nflreadr.nflverse.com/articles/dictionary_roster_status.html


```
src/nflreadpy/load_rosters_weekly.py
```


```
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35
36
37
38
39
40
41
42
43
44
45
46
47
48
49
50
51
52
53
54
55
56
```


```
def load_rosters_weekly(seasons: int | list[int] | bool | None = None) -> pl.DataFrame:
    """
    Load NFL weekly rosters data.

    Data available from 2002 onwards.

    Args:
        seasons: Season(s) to load. If None, loads current season.
                If True, loads all available data since 2002.
                If int or list of ints, loads specified season(s).

    Returns:
        Polars DataFrame with weekly roster data including player status\
        changes, injury designations, and week-by-week roster moves.

    See Also:
        <https://nflreadr.nflverse.com/reference/load_rosters_weekly.html>

    Data Dictionary:
        <https://nflreadr.nflverse.com/articles/dictionary_roster_status.html>
    """
    if seasons is None:
        seasons = [get_current_season()]
    elif seasons is True:
        # Load all available seasons (2002 to current)
        current_season = get_current_season()
        seasons = list(range(2002, current_season + 1))
    elif isinstance(seasons, int):
        seasons = [seasons]

    # Validate seasons
    current_season = get_current_season()
    for season in seasons:
        if not isinstance(season, int) or season < 2002 or season > current_season:
            raise ValueError(f"Season must be between 2002 and {current_season}")

    downloader = get_downloader()
    dataframes = []

    for season in seasons:
        path = f"weekly_rosters/roster_weekly_{season}"
        df = downloader.download("nflverse-data", path, season=season)
        dataframes.append(df)

    if len(dataframes) == 1:
        return dataframes[0]
    else:
        return pl.concat(dataframes, how="diagonal_relaxed")
```


```
def load_rosters_weekly(seasons: int | list[int] | bool | None = None) -> pl.DataFrame:
    """
    Load NFL weekly rosters data.

    Data available from 2002 onwards.

    Args:
        seasons: Season(s) to load. If None, loads current season.
                If True, loads all available data since 2002.
                If int or list of ints, loads specified season(s).

    Returns:
        Polars DataFrame with weekly roster data including player status\
        changes, injury designations, and week-by-week roster moves.

    See Also:
        <https://nflreadr.nflverse.com/reference/load_rosters_weekly.html>

    Data Dictionary:
        <https://nflreadr.nflverse.com/articles/dictionary_roster_status.html>
    """
    if seasons is None:
        seasons = [get_current_season()]
    elif seasons is True:
        # Load all available seasons (2002 to current)
        current_season = get_current_season()
        seasons = list(range(2002, current_season + 1))
    elif isinstance(seasons, int):
        seasons = [seasons]

    # Validate seasons
    current_season = get_current_season()
    for season in seasons:
        if not isinstance(season, int) or season < 2002 or season > current_season:
            raise ValueError(f"Season must be between 2002 and {current_season}")

    downloader = get_downloader()
    dataframes = []

    for season in seasons:
        path = f"weekly_rosters/roster_weekly_{season}"
        df = downloader.download("nflverse-data", path, season=season)
        dataframes.append(df)

    if len(dataframes) == 1:
        return dataframes[0]
    else:
        return pl.concat(dataframes, how="diagonal_relaxed")
```


## nflreadpy.load_snap_counts
¶

Load NFL snap count data.


### load_snap_counts
¶


```
load_snap_counts(
    seasons: int | list[int] | bool | None = None,
) -> pl.DataFrame
```


```
load_snap_counts(
    seasons: int | list[int] | bool | None = None,
) -> pl.DataFrame
```

Load NFL snap count data.

Data sourced from Pro Football Reference, available since 2012.

Parameters:


```
seasons
```


```
int | list[int] | bool | None
```

Season(s) to load. If None, loads current season.
    If True, loads all available data since 2012.
    If int or list of ints, loads specified season(s).


```
None
```

Returns:


```
DataFrame
```

Polars DataFrame with snap count data including player information,        offensive/defensive snaps, and snap percentages.

https://nflreadr.nflverse.com/reference/load_snap_counts.html

https://nflreadr.nflverse.com/articles/dictionary_snap_counts.html


```
src/nflreadpy/load_snap_counts.py
```


```
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35
36
37
38
39
40
41
42
43
44
45
46
47
48
49
50
51
52
53
54
55
56
```


```
def load_snap_counts(seasons: int | list[int] | bool | None = None) -> pl.DataFrame:
    """
    Load NFL snap count data.

    Data sourced from Pro Football Reference, available since 2012.

    Args:
        seasons: Season(s) to load. If None, loads current season.
                If True, loads all available data since 2012.
                If int or list of ints, loads specified season(s).

    Returns:
        Polars DataFrame with snap count data including player information,\
        offensive/defensive snaps, and snap percentages.

    See Also:
        <https://nflreadr.nflverse.com/reference/load_snap_counts.html>

    Data Dictionary:
        <https://nflreadr.nflverse.com/articles/dictionary_snap_counts.html>
    """
    if seasons is None:
        seasons = [get_current_season()]
    elif seasons is True:
        # Load all available seasons (2012 to current)
        current_season = get_current_season()
        seasons = list(range(2012, current_season + 1))
    elif isinstance(seasons, int):
        seasons = [seasons]

    # Validate seasons
    current_season = get_current_season()
    for season in seasons:
        if not isinstance(season, int) or season < 2012 or season > current_season:
            raise ValueError(f"Season must be between 2012 and {current_season}")

    downloader = get_downloader()
    dataframes = []

    for season in seasons:
        path = f"snap_counts/snap_counts_{season}"
        df = downloader.download("nflverse-data", path, season=season)
        dataframes.append(df)

    if len(dataframes) == 1:
        return dataframes[0]
    else:
        return pl.concat(dataframes, how="diagonal_relaxed")
```


```
def load_snap_counts(seasons: int | list[int] | bool | None = None) -> pl.DataFrame:
    """
    Load NFL snap count data.

    Data sourced from Pro Football Reference, available since 2012.

    Args:
        seasons: Season(s) to load. If None, loads current season.
                If True, loads all available data since 2012.
                If int or list of ints, loads specified season(s).

    Returns:
        Polars DataFrame with snap count data including player information,\
        offensive/defensive snaps, and snap percentages.

    See Also:
        <https://nflreadr.nflverse.com/reference/load_snap_counts.html>

    Data Dictionary:
        <https://nflreadr.nflverse.com/articles/dictionary_snap_counts.html>
    """
    if seasons is None:
        seasons = [get_current_season()]
    elif seasons is True:
        # Load all available seasons (2012 to current)
        current_season = get_current_season()
        seasons = list(range(2012, current_season + 1))
    elif isinstance(seasons, int):
        seasons = [seasons]

    # Validate seasons
    current_season = get_current_season()
    for season in seasons:
        if not isinstance(season, int) or season < 2012 or season > current_season:
            raise ValueError(f"Season must be between 2012 and {current_season}")

    downloader = get_downloader()
    dataframes = []

    for season in seasons:
        path = f"snap_counts/snap_counts_{season}"
        df = downloader.download("nflverse-data", path, season=season)
        dataframes.append(df)

    if len(dataframes) == 1:
        return dataframes[0]
    else:
        return pl.concat(dataframes, how="diagonal_relaxed")
```


## nflreadpy.load_nextgen_stats
¶

Load NFL Next Gen Stats data.


### load_nextgen_stats
¶


```
load_nextgen_stats(
    seasons: int | list[int] | bool | None = None,
    stat_type: Literal[
        "passing", "receiving", "rushing"
    ] = "passing",
) -> pl.DataFrame
```


```
load_nextgen_stats(
    seasons: int | list[int] | bool | None = None,
    stat_type: Literal[
        "passing", "receiving", "rushing"
    ] = "passing",
) -> pl.DataFrame
```

Load NFL Next Gen Stats data.

Data available since 2016.

Parameters:


```
seasons
```


```
int | list[int] | bool | None
```

Season(s) to load. If None, loads current season.
    If True, loads all available data since 2016.
    If int or list of ints, loads specified season(s).


```
None
```


```
stat_type
```


```
Literal['passing', 'receiving', 'rushing']
```

Type of stats to load. Options: "passing", "receiving", "rushing".


```
'passing'
```

Returns:


```
DataFrame
```

Polars DataFrame with Next Gen Stats data including advanced metrics        for passing, receiving, or rushing performance.

https://nflreadr.nflverse.com/reference/load_nextgen_stats.html

https://nflreadr.nflverse.com/articles/dictionary_nextgen_stats.html


```
src/nflreadpy/load_nextgen_stats.py
```


```
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35
36
37
38
39
40
41
42
43
44
45
46
47
48
49
50
51
52
53
54
55
56
57
58
59
60
61
62
63
64
```


```
def load_nextgen_stats(
    seasons: int | list[int] | bool | None = None,
    stat_type: Literal["passing", "receiving", "rushing"] = "passing",
) -> pl.DataFrame:
    """
    Load NFL Next Gen Stats data.

    Data available since 2016.

    Args:
        seasons: Season(s) to load. If None, loads current season.
                If True, loads all available data since 2016.
                If int or list of ints, loads specified season(s).
        stat_type: Type of stats to load. Options: "passing", "receiving", "rushing".

    Returns:
        Polars DataFrame with Next Gen Stats data including advanced metrics\
        for passing, receiving, or rushing performance.

    See Also:
        <https://nflreadr.nflverse.com/reference/load_nextgen_stats.html>

    Data Dictionary:
        <https://nflreadr.nflverse.com/articles/dictionary_nextgen_stats.html>
    """
    if stat_type not in ["passing", "receiving", "rushing"]:
        raise ValueError("stat_type must be 'passing', 'receiving', or 'rushing'")

    if seasons is None:
        seasons = [get_current_season()]
    elif seasons is True:
        # Load all available seasons (2016 to current)
        current_season = get_current_season()
        seasons = list(range(2016, current_season + 1))
    elif isinstance(seasons, int):
        seasons = [seasons]

    # Validate seasons
    current_season = get_current_season()
    for season in seasons:
        if not isinstance(season, int) or season < 2016 or season > current_season:
            raise ValueError(f"Season must be between 2016 and {current_season}")

    downloader = get_downloader()

    # Load the full dataset for the stat type
    path = f"nextgen_stats/ngs_{stat_type}"
    df = downloader.download("nflverse-data", path, stat_type=stat_type)

    # Filter by seasons
    if "season" in df.columns:
        df = df.filter(pl.col("season").is_in(seasons))

    return df
```


```
def load_nextgen_stats(
    seasons: int | list[int] | bool | None = None,
    stat_type: Literal["passing", "receiving", "rushing"] = "passing",
) -> pl.DataFrame:
    """
    Load NFL Next Gen Stats data.

    Data available since 2016.

    Args:
        seasons: Season(s) to load. If None, loads current season.
                If True, loads all available data since 2016.
                If int or list of ints, loads specified season(s).
        stat_type: Type of stats to load. Options: "passing", "receiving", "rushing".

    Returns:
        Polars DataFrame with Next Gen Stats data including advanced metrics\
        for passing, receiving, or rushing performance.

    See Also:
        <https://nflreadr.nflverse.com/reference/load_nextgen_stats.html>

    Data Dictionary:
        <https://nflreadr.nflverse.com/articles/dictionary_nextgen_stats.html>
    """
    if stat_type not in ["passing", "receiving", "rushing"]:
        raise ValueError("stat_type must be 'passing', 'receiving', or 'rushing'")

    if seasons is None:
        seasons = [get_current_season()]
    elif seasons is True:
        # Load all available seasons (2016 to current)
        current_season = get_current_season()
        seasons = list(range(2016, current_season + 1))
    elif isinstance(seasons, int):
        seasons = [seasons]

    # Validate seasons
    current_season = get_current_season()
    for season in seasons:
        if not isinstance(season, int) or season < 2016 or season > current_season:
            raise ValueError(f"Season must be between 2016 and {current_season}")

    downloader = get_downloader()

    # Load the full dataset for the stat type
    path = f"nextgen_stats/ngs_{stat_type}"
    df = downloader.download("nflverse-data", path, stat_type=stat_type)

    # Filter by seasons
    if "season" in df.columns:
        df = df.filter(pl.col("season").is_in(seasons))

    return df
```


## nflreadpy.load_ftn_charting
¶

Load FTN charting data.


### load_ftn_charting
¶


```
load_ftn_charting(
    seasons: int | list[int] | bool | None = None,
) -> pl.DataFrame
```


```
load_ftn_charting(
    seasons: int | list[int] | bool | None = None,
) -> pl.DataFrame
```

Load FTN charting data.

Data available since 2022.

Parameters:


```
seasons
```


```
int | list[int] | bool | None
```

Season(s) to load. If None, loads current season.
    If True, loads all available data since 2022.
    If int or list of ints, loads specified season(s).


```
None
```

Returns:


```
DataFrame
```

Polars DataFrame with FTN charting data including detailed        play-by-play charting information and advanced metrics.

https://nflreadr.nflverse.com/reference/load_ftn_charting.html

https://nflreadr.nflverse.com/articles/dictionary_ftn_charting.html


```
src/nflreadpy/load_ftn_charting.py
```


```
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35
36
37
38
39
40
41
42
43
44
45
46
47
48
49
50
51
52
53
54
55
56
```


```
def load_ftn_charting(seasons: int | list[int] | bool | None = None) -> pl.DataFrame:
    """
    Load FTN charting data.

    Data available since 2022.

    Args:
        seasons: Season(s) to load. If None, loads current season.
                If True, loads all available data since 2022.
                If int or list of ints, loads specified season(s).

    Returns:
        Polars DataFrame with FTN charting data including detailed\
        play-by-play charting information and advanced metrics.

    See Also:
        <https://nflreadr.nflverse.com/reference/load_ftn_charting.html>

    Data Dictionary:
        <https://nflreadr.nflverse.com/articles/dictionary_ftn_charting.html>
    """
    if seasons is None:
        seasons = [get_current_season()]
    elif seasons is True:
        # Load all available seasons (2022 to current)
        current_season = get_current_season()
        seasons = list(range(2022, current_season + 1))
    elif isinstance(seasons, int):
        seasons = [seasons]

    # Validate seasons
    current_season = get_current_season()
    for season in seasons:
        if not isinstance(season, int) or season < 2022 or season > current_season:
            raise ValueError(f"Season must be between 2022 and {current_season}")

    downloader = get_downloader()
    dataframes = []

    for season in seasons:
        path = f"ftn_charting/ftn_charting_{season}"
        df = downloader.download("nflverse-data", path, season=season)
        dataframes.append(df)

    if len(dataframes) == 1:
        return dataframes[0]
    else:
        return pl.concat(dataframes, how="diagonal_relaxed")
```


```
def load_ftn_charting(seasons: int | list[int] | bool | None = None) -> pl.DataFrame:
    """
    Load FTN charting data.

    Data available since 2022.

    Args:
        seasons: Season(s) to load. If None, loads current season.
                If True, loads all available data since 2022.
                If int or list of ints, loads specified season(s).

    Returns:
        Polars DataFrame with FTN charting data including detailed\
        play-by-play charting information and advanced metrics.

    See Also:
        <https://nflreadr.nflverse.com/reference/load_ftn_charting.html>

    Data Dictionary:
        <https://nflreadr.nflverse.com/articles/dictionary_ftn_charting.html>
    """
    if seasons is None:
        seasons = [get_current_season()]
    elif seasons is True:
        # Load all available seasons (2022 to current)
        current_season = get_current_season()
        seasons = list(range(2022, current_season + 1))
    elif isinstance(seasons, int):
        seasons = [seasons]

    # Validate seasons
    current_season = get_current_season()
    for season in seasons:
        if not isinstance(season, int) or season < 2022 or season > current_season:
            raise ValueError(f"Season must be between 2022 and {current_season}")

    downloader = get_downloader()
    dataframes = []

    for season in seasons:
        path = f"ftn_charting/ftn_charting_{season}"
        df = downloader.download("nflverse-data", path, season=season)
        dataframes.append(df)

    if len(dataframes) == 1:
        return dataframes[0]
    else:
        return pl.concat(dataframes, how="diagonal_relaxed")
```


## nflreadpy.load_participation
¶

Load NFL participation data.


### load_participation
¶


```
load_participation(
    seasons: int | list[int] | bool | None = None,
) -> pl.DataFrame
```


```
load_participation(
    seasons: int | list[int] | bool | None = None,
) -> pl.DataFrame
```

Load NFL participation data.

Data available since 2016.

Parameters:


```
seasons
```


```
int | list[int] | bool | None
```

Season(s) to load. If None, loads current season.
    If True, loads all available data since 2016.
    If int or list of ints, loads specified season(s).


```
None
```

Returns:


```
DataFrame
```

Polars DataFrame with participation data including player involvement        on specific plays and snap participation details.

https://nflreadr.nflverse.com/reference/load_participation.html

https://nflreadr.nflverse.com/articles/dictionary_participation.html


```
src/nflreadpy/load_participation.py
```


```
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35
36
37
38
39
40
41
42
43
44
45
46
47
48
49
50
51
52
53
54
55
56
57
58
59
60
61
62
```


```
def load_participation(seasons: int | list[int] | bool | None = None) -> pl.DataFrame:
    """
    Load NFL participation data.

    Data available since 2016.

    Args:
        seasons: Season(s) to load. If None, loads current season.
                If True, loads all available data since 2016.
                If int or list of ints, loads specified season(s).

    Returns:
        Polars DataFrame with participation data including player involvement\
        on specific plays and snap participation details.

    See Also:
        <https://nflreadr.nflverse.com/reference/load_participation.html>

    Data Dictionary:
        <https://nflreadr.nflverse.com/articles/dictionary_participation.html>
    """
    # we expect to have participation data available after the final week of the
    # season from FTN
    current_week = get_current_week(use_date=False)
    if current_week == 22:
        max_season = get_current_season()
    else:
        max_season = get_current_season() - 1

    if seasons is None:
        seasons = [max_season]
    elif seasons is True:
        # Load all available seasons (2016 to max_season)
        seasons = list(range(2016, max_season + 1))
    elif isinstance(seasons, int):
        seasons = [seasons]

    # Validate seasons
    for season in seasons:
        if not isinstance(season, int) or season < 2016 or season > max_season:
            raise ValueError(f"Season must be between 2016 and {max_season}")

    downloader = get_downloader()
    dataframes = []

    for season in seasons:
        path = f"pbp_participation/pbp_participation_{season}"
        df = downloader.download("nflverse-data", path, season=season)
        dataframes.append(df)

    if len(dataframes) == 1:
        return dataframes[0]
    else:
        return pl.concat(dataframes, how="diagonal_relaxed")
```


```
def load_participation(seasons: int | list[int] | bool | None = None) -> pl.DataFrame:
    """
    Load NFL participation data.

    Data available since 2016.

    Args:
        seasons: Season(s) to load. If None, loads current season.
                If True, loads all available data since 2016.
                If int or list of ints, loads specified season(s).

    Returns:
        Polars DataFrame with participation data including player involvement\
        on specific plays and snap participation details.

    See Also:
        <https://nflreadr.nflverse.com/reference/load_participation.html>

    Data Dictionary:
        <https://nflreadr.nflverse.com/articles/dictionary_participation.html>
    """
    # we expect to have participation data available after the final week of the
    # season from FTN
    current_week = get_current_week(use_date=False)
    if current_week == 22:
        max_season = get_current_season()
    else:
        max_season = get_current_season() - 1

    if seasons is None:
        seasons = [max_season]
    elif seasons is True:
        # Load all available seasons (2016 to max_season)
        seasons = list(range(2016, max_season + 1))
    elif isinstance(seasons, int):
        seasons = [seasons]

    # Validate seasons
    for season in seasons:
        if not isinstance(season, int) or season < 2016 or season > max_season:
            raise ValueError(f"Season must be between 2016 and {max_season}")

    downloader = get_downloader()
    dataframes = []

    for season in seasons:
        path = f"pbp_participation/pbp_participation_{season}"
        df = downloader.download("nflverse-data", path, season=season)
        dataframes.append(df)

    if len(dataframes) == 1:
        return dataframes[0]
    else:
        return pl.concat(dataframes, how="diagonal_relaxed")
```


## nflreadpy.load_draft_picks
¶

Load NFL draft pick data.


### load_draft_picks
¶


```
load_draft_picks(
    seasons: int | list[int] | bool | None = True,
) -> pl.DataFrame
```


```
load_draft_picks(
    seasons: int | list[int] | bool | None = True,
) -> pl.DataFrame
```

Load NFL draft pick data.

Data covers draft picks since 1980, sourced from Pro Football Reference.

Parameters:


```
seasons
```


```
int | list[int] | bool | None
```

Season(s) to load. If True (default), loads all available data.
    If int or list of ints, loads specified season(s).
    If None, loads current season.


```
True
```

Returns:


```
DataFrame
```

Polars DataFrame with draft pick data including draft year, round,        pick number, player information, and team data.

https://nflreadr.nflverse.com/reference/load_draft_picks.html

https://nflreadr.nflverse.com/articles/dictionary_draft_picks.html


```
src/nflreadpy/load_draft_picks.py
```


```
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35
36
37
38
39
40
41
42
43
44
45
```


```
def load_draft_picks(seasons: int | list[int] | bool | None = True) -> pl.DataFrame:
    """
    Load NFL draft pick data.

    Data covers draft picks since 1980, sourced from Pro Football Reference.

    Args:
        seasons: Season(s) to load. If True (default), loads all available data.
                If int or list of ints, loads specified season(s).
                If None, loads current season.

    Returns:
        Polars DataFrame with draft pick data including draft year, round,\
        pick number, player information, and team data.

    See Also:
        <https://nflreadr.nflverse.com/reference/load_draft_picks.html>

    Data Dictionary:
        <https://nflreadr.nflverse.com/articles/dictionary_draft_picks.html>
    """
    downloader = get_downloader()

    # Load the full draft picks dataset
    df = downloader.download("nflverse-data", "draft_picks/draft_picks")

    # Filter by seasons if specified
    if seasons is not True:
        if seasons is None:
            seasons = [get_current_season()]
        elif isinstance(seasons, int):
            seasons = [seasons]

        # Filter the dataframe by season
        df = df.filter(pl.col("season").is_in(seasons))

    return df
```


```
def load_draft_picks(seasons: int | list[int] | bool | None = True) -> pl.DataFrame:
    """
    Load NFL draft pick data.

    Data covers draft picks since 1980, sourced from Pro Football Reference.

    Args:
        seasons: Season(s) to load. If True (default), loads all available data.
                If int or list of ints, loads specified season(s).
                If None, loads current season.

    Returns:
        Polars DataFrame with draft pick data including draft year, round,\
        pick number, player information, and team data.

    See Also:
        <https://nflreadr.nflverse.com/reference/load_draft_picks.html>

    Data Dictionary:
        <https://nflreadr.nflverse.com/articles/dictionary_draft_picks.html>
    """
    downloader = get_downloader()

    # Load the full draft picks dataset
    df = downloader.download("nflverse-data", "draft_picks/draft_picks")

    # Filter by seasons if specified
    if seasons is not True:
        if seasons is None:
            seasons = [get_current_season()]
        elif isinstance(seasons, int):
            seasons = [seasons]

        # Filter the dataframe by season
        df = df.filter(pl.col("season").is_in(seasons))

    return df
```


## nflreadpy.load_injuries
¶

Load NFL injury data.


### load_injuries
¶


```
load_injuries(
    seasons: int | list[int] | bool | None = None,
) -> pl.DataFrame
```


```
load_injuries(
    seasons: int | list[int] | bool | None = None,
) -> pl.DataFrame
```

Load NFL injury data.

Data available since 2009.

Parameters:


```
seasons
```


```
int | list[int] | bool | None
```

Season(s) to load. If None, loads current season.
    If True, loads all available data since 2009.
    If int or list of ints, loads specified season(s).


```
None
```

Returns:


```
DataFrame
```

Polars DataFrame with injury data including player information,        injury details, and status reports.

https://nflreadr.nflverse.com/reference/load_injuries.html

https://nflreadr.nflverse.com/articles/dictionary_injuries.html


```
src/nflreadpy/load_injuries.py
```


```
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35
36
37
38
39
40
41
42
43
44
45
46
47
48
49
50
51
52
53
54
55
56
```


```
def load_injuries(seasons: int | list[int] | bool | None = None) -> pl.DataFrame:
    """
    Load NFL injury data.

    Data available since 2009.

    Args:
        seasons: Season(s) to load. If None, loads current season.
                If True, loads all available data since 2009.
                If int or list of ints, loads specified season(s).

    Returns:
        Polars DataFrame with injury data including player information,\
        injury details, and status reports.

    See Also:
        <https://nflreadr.nflverse.com/reference/load_injuries.html>

    Data Dictionary:
        <https://nflreadr.nflverse.com/articles/dictionary_injuries.html>
    """
    if seasons is None:
        seasons = [get_current_season()]
    elif seasons is True:
        # Load all available seasons (2009 to current)
        current_season = get_current_season()
        seasons = list(range(2009, current_season + 1))
    elif isinstance(seasons, int):
        seasons = [seasons]

    # Validate seasons
    current_season = get_current_season()
    for season in seasons:
        if not isinstance(season, int) or season < 2009 or season > current_season:
            raise ValueError(f"Season must be between 2009 and {current_season}")

    downloader = get_downloader()
    dataframes = []

    for season in seasons:
        path = f"injuries/injuries_{season}"
        df = downloader.download("nflverse-data", path, season=season)
        dataframes.append(df)

    if len(dataframes) == 1:
        return dataframes[0]
    else:
        return pl.concat(dataframes, how="diagonal_relaxed")
```


```
def load_injuries(seasons: int | list[int] | bool | None = None) -> pl.DataFrame:
    """
    Load NFL injury data.

    Data available since 2009.

    Args:
        seasons: Season(s) to load. If None, loads current season.
                If True, loads all available data since 2009.
                If int or list of ints, loads specified season(s).

    Returns:
        Polars DataFrame with injury data including player information,\
        injury details, and status reports.

    See Also:
        <https://nflreadr.nflverse.com/reference/load_injuries.html>

    Data Dictionary:
        <https://nflreadr.nflverse.com/articles/dictionary_injuries.html>
    """
    if seasons is None:
        seasons = [get_current_season()]
    elif seasons is True:
        # Load all available seasons (2009 to current)
        current_season = get_current_season()
        seasons = list(range(2009, current_season + 1))
    elif isinstance(seasons, int):
        seasons = [seasons]

    # Validate seasons
    current_season = get_current_season()
    for season in seasons:
        if not isinstance(season, int) or season < 2009 or season > current_season:
            raise ValueError(f"Season must be between 2009 and {current_season}")

    downloader = get_downloader()
    dataframes = []

    for season in seasons:
        path = f"injuries/injuries_{season}"
        df = downloader.download("nflverse-data", path, season=season)
        dataframes.append(df)

    if len(dataframes) == 1:
        return dataframes[0]
    else:
        return pl.concat(dataframes, how="diagonal_relaxed")
```


## nflreadpy.load_contracts
¶

Load NFL contract data.


### load_contracts
¶


```
load_contracts() -> pl.DataFrame
```


```
load_contracts() -> pl.DataFrame
```

Load NFL historical contract data.

Returns:


```
DataFrame
```

Polars DataFrame with historical contract information including        player details, contract terms, values, and team information.

https://nflreadr.nflverse.com/reference/load_contracts.html

https://nflreadr.nflverse.com/articles/dictionary_contracts.html


```
src/nflreadpy/load_contracts.py
```


```
8
 9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
```


```
def load_contracts() -> pl.DataFrame:
    """
    Load NFL historical contract data.

    Returns:
        Polars DataFrame with historical contract information including\
        player details, contract terms, values, and team information.

    See Also:
        <https://nflreadr.nflverse.com/reference/load_contracts.html>

    Data Dictionary:
        <https://nflreadr.nflverse.com/articles/dictionary_contracts.html>
    """
    downloader = get_downloader()

    # Load historical contracts data from nflverse-data repository
    df = downloader.download("nflverse-data", "contracts/historical_contracts")

    return df
```


```
def load_contracts() -> pl.DataFrame:
    """
    Load NFL historical contract data.

    Returns:
        Polars DataFrame with historical contract information including\
        player details, contract terms, values, and team information.

    See Also:
        <https://nflreadr.nflverse.com/reference/load_contracts.html>

    Data Dictionary:
        <https://nflreadr.nflverse.com/articles/dictionary_contracts.html>
    """
    downloader = get_downloader()

    # Load historical contracts data from nflverse-data repository
    df = downloader.download("nflverse-data", "contracts/historical_contracts")

    return df
```


## nflreadpy.load_officials
¶

Load NFL officials data.


### load_officials
¶


```
load_officials(
    seasons: int | list[int] | bool | None = True,
) -> pl.DataFrame
```


```
load_officials(
    seasons: int | list[int] | bool | None = True,
) -> pl.DataFrame
```

Load NFL officials data.

Data covers NFL officials assigned to games from 2015 onwards.

Parameters:


```
seasons
```


```
int | list[int] | bool | None
```

Season(s) to load. If True (default), loads all available data.
    If int or list of ints, loads specified season(s).
    If None, loads current season.


```
True
```

Returns:


```
DataFrame
```

Polars DataFrame with officials data including referee assignments,        crew information, and game details.

https://nflreadr.nflverse.com/reference/load_officials.html


```
src/nflreadpy/load_officials.py
```


```
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35
36
37
38
39
40
41
42
43
44
45
46
47
48
49
```


```
def load_officials(seasons: int | list[int] | bool | None = True) -> pl.DataFrame:
    """
    Load NFL officials data.

    Data covers NFL officials assigned to games from 2015 onwards.

    Args:
        seasons: Season(s) to load. If True (default), loads all available data.
                If int or list of ints, loads specified season(s).
                If None, loads current season.

    Returns:
        Polars DataFrame with officials data including referee assignments,\
        crew information, and game details.

    See Also:
        <https://nflreadr.nflverse.com/reference/load_officials.html>
    """
    downloader = get_downloader()

    # Load the full officials dataset
    df = downloader.download("nflverse-data", "officials/officials")

    # Filter by seasons if specified
    if seasons is not True:
        if seasons is None:
            seasons = [get_current_season()]
        elif isinstance(seasons, int):
            seasons = [seasons]

        # Validate seasons (2015 minimum)
        current_season = get_current_season()
        for season in seasons:
            if not isinstance(season, int) or season < 2015 or season > current_season:
                raise ValueError(f"Season must be between 2015 and {current_season}")

        # Filter the dataframe by season
        if "season" in df.columns:
            df = df.filter(pl.col("season").is_in(seasons))

    return df
```


```
def load_officials(seasons: int | list[int] | bool | None = True) -> pl.DataFrame:
    """
    Load NFL officials data.

    Data covers NFL officials assigned to games from 2015 onwards.

    Args:
        seasons: Season(s) to load. If True (default), loads all available data.
                If int or list of ints, loads specified season(s).
                If None, loads current season.

    Returns:
        Polars DataFrame with officials data including referee assignments,\
        crew information, and game details.

    See Also:
        <https://nflreadr.nflverse.com/reference/load_officials.html>
    """
    downloader = get_downloader()

    # Load the full officials dataset
    df = downloader.download("nflverse-data", "officials/officials")

    # Filter by seasons if specified
    if seasons is not True:
        if seasons is None:
            seasons = [get_current_season()]
        elif isinstance(seasons, int):
            seasons = [seasons]

        # Validate seasons (2015 minimum)
        current_season = get_current_season()
        for season in seasons:
            if not isinstance(season, int) or season < 2015 or season > current_season:
                raise ValueError(f"Season must be between 2015 and {current_season}")

        # Filter the dataframe by season
        if "season" in df.columns:
            df = df.filter(pl.col("season").is_in(seasons))

    return df
```


## nflreadpy.load_combine
¶

Load NFL Combine data.


### load_combine
¶


```
load_combine(
    seasons: int | list[int] | bool | None = True,
) -> pl.DataFrame
```


```
load_combine(
    seasons: int | list[int] | bool | None = True,
) -> pl.DataFrame
```

Load NFL Combine data.

Parameters:


```
seasons
```


```
int | list[int] | bool | None
```

Season(s) to load. If True (default), loads all available data.
    If int or list of ints, loads specified season(s).
    If None, loads current season.


```
True
```

Returns:


```
DataFrame
```

Polars DataFrame with NFL Combine data including player measurements,        test results (40-yard dash, bench press, etc.), and draft information.

https://nflreadr.nflverse.com/reference/load_combine.html

https://nflreadr.nflverse.com/articles/dictionary_combine.html


```
src/nflreadpy/load_combine.py
```


```
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35
36
37
38
39
40
41
42
43
44
```


```
def load_combine(seasons: int | list[int] | bool | None = True) -> pl.DataFrame:
    """
    Load NFL Combine data.

    Args:
        seasons: Season(s) to load. If True (default), loads all available data.
                If int or list of ints, loads specified season(s).
                If None, loads current season.

    Returns:
        Polars DataFrame with NFL Combine data including player measurements,\
        test results (40-yard dash, bench press, etc.), and draft information.

    See Also:
        <https://nflreadr.nflverse.com/reference/load_combine.html>

    Data Dictionary:
        <https://nflreadr.nflverse.com/articles/dictionary_combine.html>
    """
    downloader = get_downloader()

    # Load the full combine dataset
    df = downloader.download("nflverse-data", "combine/combine")

    # Filter by seasons if specified
    if seasons is not True:
        if seasons is None:
            seasons = [get_current_season()]
        elif isinstance(seasons, int):
            seasons = [seasons]

        # Filter the dataframe by season
        if "season" in df.columns:
            df = df.filter(pl.col("season").is_in(seasons))

    return df
```


```
def load_combine(seasons: int | list[int] | bool | None = True) -> pl.DataFrame:
    """
    Load NFL Combine data.

    Args:
        seasons: Season(s) to load. If True (default), loads all available data.
                If int or list of ints, loads specified season(s).
                If None, loads current season.

    Returns:
        Polars DataFrame with NFL Combine data including player measurements,\
        test results (40-yard dash, bench press, etc.), and draft information.

    See Also:
        <https://nflreadr.nflverse.com/reference/load_combine.html>

    Data Dictionary:
        <https://nflreadr.nflverse.com/articles/dictionary_combine.html>
    """
    downloader = get_downloader()

    # Load the full combine dataset
    df = downloader.download("nflverse-data", "combine/combine")

    # Filter by seasons if specified
    if seasons is not True:
        if seasons is None:
            seasons = [get_current_season()]
        elif isinstance(seasons, int):
            seasons = [seasons]

        # Filter the dataframe by season
        if "season" in df.columns:
            df = df.filter(pl.col("season").is_in(seasons))

    return df
```


## nflreadpy.load_depth_charts
¶

Load NFL depth charts data.


### load_depth_charts
¶


```
load_depth_charts(
    seasons: int | list[int] | bool | None = None,
) -> pl.DataFrame
```


```
load_depth_charts(
    seasons: int | list[int] | bool | None = None,
) -> pl.DataFrame
```

Load NFL depth charts data.

Data available from 2001 onwards.

Parameters:


```
seasons
```


```
int | list[int] | bool | None
```

Season(s) to load. If None, loads current season.
    If True, loads all available data since 2001.
    If int or list of ints, loads specified season(s).


```
None
```

Returns:


```
DataFrame
```

Polars DataFrame with depth charts data including player positions,        depth chart rankings, and team information.

https://nflreadr.nflverse.com/reference/load_depth_charts.html

https://nflreadr.nflverse.com/articles/dictionary_depth_charts.html


```
src/nflreadpy/load_depth_charts.py
```


```
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35
36
37
38
39
40
41
42
43
44
45
46
47
48
49
50
51
52
53
54
55
56
```


```
def load_depth_charts(seasons: int | list[int] | bool | None = None) -> pl.DataFrame:
    """
    Load NFL depth charts data.

    Data available from 2001 onwards.

    Args:
        seasons: Season(s) to load. If None, loads current season.
                If True, loads all available data since 2001.
                If int or list of ints, loads specified season(s).

    Returns:
        Polars DataFrame with depth charts data including player positions,\
        depth chart rankings, and team information.

    See Also:
        <https://nflreadr.nflverse.com/reference/load_depth_charts.html>

    Data Dictionary:
        <https://nflreadr.nflverse.com/articles/dictionary_depth_charts.html>
    """
    if seasons is None:
        seasons = [get_current_season(roster=True)]
    elif seasons is True:
        # Load all available seasons (2001 to current)
        current_season = get_current_season(roster=True)
        seasons = list(range(2001, current_season + 1))
    elif isinstance(seasons, int):
        seasons = [seasons]

    # Validate seasons
    current_season = get_current_season(roster=True)
    for season in seasons:
        if not isinstance(season, int) or season < 2001 or season > current_season:
            raise ValueError(f"Season must be between 2001 and {current_season}")

    downloader = get_downloader()
    dataframes = []

    for season in seasons:
        path = f"depth_charts/depth_charts_{season}"
        df = downloader.download("nflverse-data", path, season=season)
        dataframes.append(df)

    if len(dataframes) == 1:
        return dataframes[0]
    else:
        return pl.concat(dataframes, how="diagonal_relaxed")
```


```
def load_depth_charts(seasons: int | list[int] | bool | None = None) -> pl.DataFrame:
    """
    Load NFL depth charts data.

    Data available from 2001 onwards.

    Args:
        seasons: Season(s) to load. If None, loads current season.
                If True, loads all available data since 2001.
                If int or list of ints, loads specified season(s).

    Returns:
        Polars DataFrame with depth charts data including player positions,\
        depth chart rankings, and team information.

    See Also:
        <https://nflreadr.nflverse.com/reference/load_depth_charts.html>

    Data Dictionary:
        <https://nflreadr.nflverse.com/articles/dictionary_depth_charts.html>
    """
    if seasons is None:
        seasons = [get_current_season(roster=True)]
    elif seasons is True:
        # Load all available seasons (2001 to current)
        current_season = get_current_season(roster=True)
        seasons = list(range(2001, current_season + 1))
    elif isinstance(seasons, int):
        seasons = [seasons]

    # Validate seasons
    current_season = get_current_season(roster=True)
    for season in seasons:
        if not isinstance(season, int) or season < 2001 or season > current_season:
            raise ValueError(f"Season must be between 2001 and {current_season}")

    downloader = get_downloader()
    dataframes = []

    for season in seasons:
        path = f"depth_charts/depth_charts_{season}"
        df = downloader.download("nflverse-data", path, season=season)
        dataframes.append(df)

    if len(dataframes) == 1:
        return dataframes[0]
    else:
        return pl.concat(dataframes, how="diagonal_relaxed")
```


## nflreadpy.load_trades
¶

Load NFL trades data.


### load_trades
¶


```
load_trades() -> pl.DataFrame
```


```
load_trades() -> pl.DataFrame
```

Load NFL trades data.

Returns:


```
DataFrame
```

Polars DataFrame with NFL trade information including players,        teams, draft picks, and trade details.

https://nflreadr.nflverse.com/reference/load_trades.html

https://nflreadr.nflverse.com/articles/dictionary_trades.html


```
src/nflreadpy/load_trades.py
```


```
8
 9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
```


```
def load_trades() -> pl.DataFrame:
    """
    Load NFL trades data.

    Returns:
        Polars DataFrame with NFL trade information including players,\
        teams, draft picks, and trade details.

    See Also:
        <https://nflreadr.nflverse.com/reference/load_trades.html>

    Data Dictionary:
        <https://nflreadr.nflverse.com/articles/dictionary_trades.html>
    """
    downloader = get_downloader()

    df = downloader.download("nflverse-data", "trades/trades")

    return df
```


```
def load_trades() -> pl.DataFrame:
    """
    Load NFL trades data.

    Returns:
        Polars DataFrame with NFL trade information including players,\
        teams, draft picks, and trade details.

    See Also:
        <https://nflreadr.nflverse.com/reference/load_trades.html>

    Data Dictionary:
        <https://nflreadr.nflverse.com/articles/dictionary_trades.html>
    """
    downloader = get_downloader()

    df = downloader.download("nflverse-data", "trades/trades")

    return df
```


## nflreadpy.load_pfr_advstats
¶

Load Pro Football Reference advanced statistics.


### load_pfr_advstats
¶


```
load_pfr_advstats(
    seasons: int | list[int] | bool | None = None,
    stat_type: Literal[
        "pass", "rush", "rec", "def"
    ] = "pass",
    summary_level: Literal["week", "season"] = "week",
) -> pl.DataFrame
```


```
load_pfr_advstats(
    seasons: int | list[int] | bool | None = None,
    stat_type: Literal[
        "pass", "rush", "rec", "def"
    ] = "pass",
    summary_level: Literal["week", "season"] = "week",
) -> pl.DataFrame
```

Load Pro Football Reference advanced statistics.

Parameters:


```
seasons
```


```
int | list[int] | bool | None
```

Season(s) to load. If None, loads current season.
    If True, loads all available data (2018-current).
    If int or list of ints, loads specified season(s).
    Only used when summary_level="week".


```
None
```


```
stat_type
```


```
Literal['pass', 'rush', 'rec', 'def']
```

Type of statistics to load:
      - "pass": Passing statistics
      - "rush": Rushing statistics
      - "rec": Receiving statistics
      - "def": Defensive statistics


```
'pass'
```


```
summary_level
```


```
Literal['week', 'season']
```

Summary level:
          - "week": Weekly statistics by season
          - "season": Season-level statistics (all seasons combined)


```
'week'
```

Returns:


```
DataFrame
```

Polars DataFrame with Pro Football Reference advanced statistics.

Data is available from 2018 onwards.

- nflreadr docs
- example of advanced passing season-level stats
- example of advanced passing week-level stats

```
src/nflreadpy/load_pfr_advstats.py
```


```
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35
36
37
38
39
40
41
42
43
44
45
46
47
48
49
50
51
52
53
54
55
56
57
58
59
60
61
62
63
64
65
66
67
68
69
70
71
72
```


```
def load_pfr_advstats(
    seasons: int | list[int] | bool | None = None,
    stat_type: Literal["pass", "rush", "rec", "def"] = "pass",
    summary_level: Literal["week", "season"] = "week",
) -> pl.DataFrame:
    """
    Load Pro Football Reference advanced statistics.

    Args:
        seasons: Season(s) to load. If None, loads current season.
                If True, loads all available data (2018-current).
                If int or list of ints, loads specified season(s).
                Only used when summary_level="week".
        stat_type: Type of statistics to load:
                  - "pass": Passing statistics
                  - "rush": Rushing statistics
                  - "rec": Receiving statistics
                  - "def": Defensive statistics
        summary_level: Summary level:
                      - "week": Weekly statistics by season
                      - "season": Season-level statistics (all seasons combined)

    Returns:
        Polars DataFrame with Pro Football Reference advanced statistics.

    Note:
        Data is available from 2018 onwards.

    See Also:
       - [nflreadr docs](https://nflreadr.nflverse.com/reference/load_pfr_advstats.html)
       - [example of advanced passing season-level stats](https://www.pro-football-reference.com/years/2025/passing_advanced.htm)
       - [example of advanced passing week-level stats](https://www.pro-football-reference.com/boxscores/202509040phi.htm#all_passing_advanced)

    """
    # Validate stat_type
    if stat_type not in ["pass", "rush", "rec", "def"]:
        raise ValueError("stat_type must be 'pass', 'rush', 'rec', or 'def'")

    # Validate summary_level
    if summary_level not in ["week", "season"]:
        raise ValueError("summary_level must be 'week' or 'season'")

    # Handle seasons parameter
    if seasons is None:
        seasons = [get_current_season()]
    elif seasons is True:
        # Load all available seasons (2018-current)
        current_season = get_current_season()
        seasons = list(range(2018, current_season + 1))
    elif isinstance(seasons, int):
        seasons = [seasons]

    # Validate seasons
    current_season = get_current_season()
    for season in seasons:
        if not isinstance(season, int) or season < 2018 or season > current_season:
            raise ValueError(f"Season must be between 2018 and {current_season}")

    if summary_level == "season":
        return _load_pfr_advstats_season(seasons, stat_type)
    else:
        return _load_pfr_advstats_week(seasons, stat_type)
```


```
def load_pfr_advstats(
    seasons: int | list[int] | bool | None = None,
    stat_type: Literal["pass", "rush", "rec", "def"] = "pass",
    summary_level: Literal["week", "season"] = "week",
) -> pl.DataFrame:
    """
    Load Pro Football Reference advanced statistics.

    Args:
        seasons: Season(s) to load. If None, loads current season.
                If True, loads all available data (2018-current).
                If int or list of ints, loads specified season(s).
                Only used when summary_level="week".
        stat_type: Type of statistics to load:
                  - "pass": Passing statistics
                  - "rush": Rushing statistics
                  - "rec": Receiving statistics
                  - "def": Defensive statistics
        summary_level: Summary level:
                      - "week": Weekly statistics by season
                      - "season": Season-level statistics (all seasons combined)

    Returns:
        Polars DataFrame with Pro Football Reference advanced statistics.

    Note:
        Data is available from 2018 onwards.

    See Also:
       - [nflreadr docs](https://nflreadr.nflverse.com/reference/load_pfr_advstats.html)
       - [example of advanced passing season-level stats](https://www.pro-football-reference.com/years/2025/passing_advanced.htm)
       - [example of advanced passing week-level stats](https://www.pro-football-reference.com/boxscores/202509040phi.htm#all_passing_advanced)

    """
    # Validate stat_type
    if stat_type not in ["pass", "rush", "rec", "def"]:
        raise ValueError("stat_type must be 'pass', 'rush', 'rec', or 'def'")

    # Validate summary_level
    if summary_level not in ["week", "season"]:
        raise ValueError("summary_level must be 'week' or 'season'")

    # Handle seasons parameter
    if seasons is None:
        seasons = [get_current_season()]
    elif seasons is True:
        # Load all available seasons (2018-current)
        current_season = get_current_season()
        seasons = list(range(2018, current_season + 1))
    elif isinstance(seasons, int):
        seasons = [seasons]

    # Validate seasons
    current_season = get_current_season()
    for season in seasons:
        if not isinstance(season, int) or season < 2018 or season > current_season:
            raise ValueError(f"Season must be between 2018 and {current_season}")

    if summary_level == "season":
        return _load_pfr_advstats_season(seasons, stat_type)
    else:
        return _load_pfr_advstats_week(seasons, stat_type)
```


## nflreadpy.load_ff_playerids
¶


```
load_ff_playerids() -> pl.DataFrame
```


```
load_ff_playerids() -> pl.DataFrame
```

Load fantasy football player IDs from DynastyProcess.com database.

Returns:


```
DataFrame
```

Polars DataFrame with comprehensive player ID mappings across platforms.

This function loads data from an R data file (.rds). While Python cannot
directly read RDS files, we attempt to use CSV format if available.

https://nflreadr.nflverse.com/reference/load_ff_playerids.html


```
src/nflreadpy/load_ffverse.py
```


```
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
```


```
def load_ff_playerids() -> pl.DataFrame:
    """
    Load fantasy football player IDs from DynastyProcess.com database.

    Returns:
        Polars DataFrame with comprehensive player ID mappings across platforms.

    Note:
        This function loads data from an R data file (.rds). While Python cannot
        directly read RDS files, we attempt to use CSV format if available.

    See Also:
        <https://nflreadr.nflverse.com/reference/load_ff_playerids.html>
    """
    downloader = get_downloader()

    df = downloader.download("dynastyprocess", "db_playerids", format=DataFormat.CSV)

    return df
```


```
def load_ff_playerids() -> pl.DataFrame:
    """
    Load fantasy football player IDs from DynastyProcess.com database.

    Returns:
        Polars DataFrame with comprehensive player ID mappings across platforms.

    Note:
        This function loads data from an R data file (.rds). While Python cannot
        directly read RDS files, we attempt to use CSV format if available.

    See Also:
        <https://nflreadr.nflverse.com/reference/load_ff_playerids.html>
    """
    downloader = get_downloader()

    df = downloader.download("dynastyprocess", "db_playerids", format=DataFormat.CSV)

    return df
```


## nflreadpy.load_ff_rankings
¶


```
load_ff_rankings(
    type: Literal["draft", "week", "all"] = "draft",
) -> pl.DataFrame
```


```
load_ff_rankings(
    type: Literal["draft", "week", "all"] = "draft",
) -> pl.DataFrame
```

Load fantasy football rankings and projections.

Parameters:


```
type
```


```
Literal['draft', 'week', 'all']
```

Type of rankings to load:
- "draft": Draft rankings/projections
- "week": Weekly rankings/projections
- "all": All historical rankings/projections


```
'draft'
```

Returns:


```
DataFrame
```

Polars DataFrame with fantasy football rankings data.

https://nflreadr.nflverse.com/reference/load_ff_rankings.html


```
src/nflreadpy/load_ffverse.py
```


```
33
34
35
36
37
38
39
40
41
42
43
44
45
46
47
48
49
50
51
52
53
54
55
56
57
58
59
60
61
62
63
64
65
66
67
68
```


```
def load_ff_rankings(type: Literal["draft", "week", "all"] = "draft") -> pl.DataFrame:
    """
    Load fantasy football rankings and projections.

    Args:
        type: Type of rankings to load:
            - "draft": Draft rankings/projections
            - "week": Weekly rankings/projections
            - "all": All historical rankings/projections

    Returns:
        Polars DataFrame with fantasy football rankings data.

    See Also:
        <https://nflreadr.nflverse.com/reference/load_ff_rankings.html>
    """
    downloader = get_downloader()

    # Map ranking types to file names
    file_mapping = {
        "draft": "db_fpecr_latest",
        "week": "fp_latest_weekly",
        "all": "db_fpecr",
    }

    if type not in file_mapping:
        raise ValueError(f"Invalid type '{type}'. Must be one of: draft, week, all")

    filename = file_mapping[type]

    if type == "all":
        df = downloader.download("dynastyprocess", filename)
    else:
        df = downloader.download("dynastyprocess", filename, format=DataFormat.CSV)

    return df
```


```
def load_ff_rankings(type: Literal["draft", "week", "all"] = "draft") -> pl.DataFrame:
    """
    Load fantasy football rankings and projections.

    Args:
        type: Type of rankings to load:
            - "draft": Draft rankings/projections
            - "week": Weekly rankings/projections
            - "all": All historical rankings/projections

    Returns:
        Polars DataFrame with fantasy football rankings data.

    See Also:
        <https://nflreadr.nflverse.com/reference/load_ff_rankings.html>
    """
    downloader = get_downloader()

    # Map ranking types to file names
    file_mapping = {
        "draft": "db_fpecr_latest",
        "week": "fp_latest_weekly",
        "all": "db_fpecr",
    }

    if type not in file_mapping:
        raise ValueError(f"Invalid type '{type}'. Must be one of: draft, week, all")

    filename = file_mapping[type]

    if type == "all":
        df = downloader.download("dynastyprocess", filename)
    else:
        df = downloader.download("dynastyprocess", filename, format=DataFormat.CSV)

    return df
```


## nflreadpy.load_ff_opportunity
¶


```
load_ff_opportunity(
    seasons: int | list[int] | None = None,
    stat_type: Literal[
        "weekly", "pbp_pass", "pbp_rush"
    ] = "weekly",
    model_version: Literal["latest", "v1.0.0"] = "latest",
) -> pl.DataFrame
```


```
load_ff_opportunity(
    seasons: int | list[int] | None = None,
    stat_type: Literal[
        "weekly", "pbp_pass", "pbp_rush"
    ] = "weekly",
    model_version: Literal["latest", "v1.0.0"] = "latest",
) -> pl.DataFrame
```

Load fantasy football opportunity data.

This function loads opportunity and target share data for fantasy football
analysis from the ffverse/ffopportunity repository.

Parameters:


```
seasons
```


```
int | list[int] | None
```

Season(s) to load. If None (default), loads current season.
    If int or list of ints, loads specified season(s). True loads all seasons.


```
None
```


```
stat_type
```


```
Literal['weekly', 'pbp_pass', 'pbp_rush']
```

Type of stats to load:
- "weekly": Weekly opportunity data
- "pbp_pass": Play-by-play passing data
- "pbp_rush": Play-by-play rushing data


```
'weekly'
```


```
model_version
```


```
Literal['latest', 'v1.0.0']
```

Model version to load:
- "latest": Most recent model version
- "v1.0.0": Specific model version


```
'latest'
```

Returns:


```
DataFrame
```

Polars DataFrame with fantasy football opportunity data.

Raises:


```
ValueError
```

If season is outside valid range or invalid parameters provided.

https://nflreadr.nflverse.com/reference/load_ff_opportunity.html


```
src/nflreadpy/load_ffverse.py
```


```
71
 72
 73
 74
 75
 76
 77
 78
 79
 80
 81
 82
 83
 84
 85
 86
 87
 88
 89
 90
 91
 92
 93
 94
 95
 96
 97
 98
 99
100
101
102
103
104
105
106
107
108
109
110
111
112
113
114
115
116
117
118
119
120
121
122
123
124
125
126
127
128
129
130
131
132
133
134
135
136
137
138
139
140
141
142
143
144
145
146
147
148
149
150
151
152
```


```
def load_ff_opportunity(
    seasons: int | list[int] | None = None,
    stat_type: Literal["weekly", "pbp_pass", "pbp_rush"] = "weekly",
    model_version: Literal["latest", "v1.0.0"] = "latest",
) -> pl.DataFrame:
    """
    Load fantasy football opportunity data.

    This function loads opportunity and target share data for fantasy football
    analysis from the ffverse/ffopportunity repository.

    Args:
        seasons: Season(s) to load. If None (default), loads current season.
                If int or list of ints, loads specified season(s). True loads all seasons.
        stat_type: Type of stats to load:
            - "weekly": Weekly opportunity data
            - "pbp_pass": Play-by-play passing data
            - "pbp_rush": Play-by-play rushing data
        model_version: Model version to load:
            - "latest": Most recent model version
            - "v1.0.0": Specific model version

    Returns:
        Polars DataFrame with fantasy football opportunity data.

    Raises:
        ValueError: If season is outside valid range or invalid parameters provided.

    See Also:
        <https://nflreadr.nflverse.com/reference/load_ff_opportunity.html>
    """
    downloader = get_downloader()

    # Validate parameters
    valid_stat_types = ["weekly", "pbp_pass", "pbp_rush"]
    if stat_type not in valid_stat_types:
        raise ValueError(
            f"Invalid stat_type '{stat_type}'. Must be one of: {valid_stat_types}"
        )

    valid_versions = ["latest", "v1.0.0"]
    if model_version not in valid_versions:
        raise ValueError(
            f"Invalid model_version '{model_version}'. Must be one of: {valid_versions}"
        )

    min_year = 2006
    current_season = get_current_season()
    # Handle seasons parameter
    if seasons is None:
        seasons = [current_season]
    elif seasons is True:
        # Load all available seasons (min_year to current)
        current_season = get_current_season()
        seasons = list(range(min_year, current_season + 1))
    elif isinstance(seasons, int):
        seasons = [seasons]

    # Validate season range
    for season in seasons:
        if not isinstance(season, int) or season < min_year or season > current_season:
            raise ValueError(f"Season must be between {min_year} and {current_season}")

    # Load data for each season
    dataframes = []
    for season in seasons:
        # Build the release tag and filename based on the R implementation
        release_tag = f"{model_version}-data"
        filename = f"ep_{stat_type}_{season}"

        # Build the path for the ffopportunity repository
        path = f"{release_tag}/{filename}"

        df = downloader.download("ffopportunity", path)

        dataframes.append(df)

    # Combine all seasons
    if len(dataframes) == 1:
        return dataframes[0]
    else:
        return pl.concat(dataframes, how="diagonal_relaxed")
```


```
def load_ff_opportunity(
    seasons: int | list[int] | None = None,
    stat_type: Literal["weekly", "pbp_pass", "pbp_rush"] = "weekly",
    model_version: Literal["latest", "v1.0.0"] = "latest",
) -> pl.DataFrame:
    """
    Load fantasy football opportunity data.

    This function loads opportunity and target share data for fantasy football
    analysis from the ffverse/ffopportunity repository.

    Args:
        seasons: Season(s) to load. If None (default), loads current season.
                If int or list of ints, loads specified season(s). True loads all seasons.
        stat_type: Type of stats to load:
            - "weekly": Weekly opportunity data
            - "pbp_pass": Play-by-play passing data
            - "pbp_rush": Play-by-play rushing data
        model_version: Model version to load:
            - "latest": Most recent model version
            - "v1.0.0": Specific model version

    Returns:
        Polars DataFrame with fantasy football opportunity data.

    Raises:
        ValueError: If season is outside valid range or invalid parameters provided.

    See Also:
        <https://nflreadr.nflverse.com/reference/load_ff_opportunity.html>
    """
    downloader = get_downloader()

    # Validate parameters
    valid_stat_types = ["weekly", "pbp_pass", "pbp_rush"]
    if stat_type not in valid_stat_types:
        raise ValueError(
            f"Invalid stat_type '{stat_type}'. Must be one of: {valid_stat_types}"
        )

    valid_versions = ["latest", "v1.0.0"]
    if model_version not in valid_versions:
        raise ValueError(
            f"Invalid model_version '{model_version}'. Must be one of: {valid_versions}"
        )

    min_year = 2006
    current_season = get_current_season()
    # Handle seasons parameter
    if seasons is None:
        seasons = [current_season]
    elif seasons is True:
        # Load all available seasons (min_year to current)
        current_season = get_current_season()
        seasons = list(range(min_year, current_season + 1))
    elif isinstance(seasons, int):
        seasons = [seasons]

    # Validate season range
    for season in seasons:
        if not isinstance(season, int) or season < min_year or season > current_season:
            raise ValueError(f"Season must be between {min_year} and {current_season}")

    # Load data for each season
    dataframes = []
    for season in seasons:
        # Build the release tag and filename based on the R implementation
        release_tag = f"{model_version}-data"
        filename = f"ep_{stat_type}_{season}"

        # Build the path for the ffopportunity repository
        path = f"{release_tag}/{filename}"

        df = downloader.download("ffopportunity", path)

        dataframes.append(df)

    # Combine all seasons
    if len(dataframes) == 1:
        return dataframes[0]
    else:
        return pl.concat(dataframes, how="diagonal_relaxed")
```

