import polars as pl
from pathlib import Path

def get_five_teams(df, week):
    """
    Gets five random teams that played on or after a certain week in the season
    """
    on_or_after = df.filter(df['week'] >= week)
    if on_or_after.height == 0:
        print(f'No teams played after week {week}')
    # print 5 teams that played on or after this week
    five_rand_teams = five_home_teams = on_or_after.sample(n=5, with_replacement=True)
    home_col = five_rand_teams.select(pl.col('home_team'))
    print(f'{home_col.height} teams played after week {week}\n... Returned those teams')
    return five_rand_teams


def explore_columns(df, output='rich', save_path=None, sample_size=5):
    """
    Pretty print column information for any Polars DataFrame.

    Useful for understanding large datasets from nflverse (pbp, rosters, player_stats, etc.)

    Parameters:
    -----------
    df : pl.DataFrame
        The Polars DataFrame to explore
    output : str, default='rich'
        Output format: 'rich' (terminal), 'html', 'markdown', or 'simple'
    save_path : str or Path, optional
        If provided, saves the output to this file (for HTML/markdown)
    sample_size : int, default=5
        Number of sample values to show per column

    Returns:
    --------
    str or None
        Returns formatted string for markdown/html, prints for rich/simple

    Examples:
    ---------
    >>> import nflreadpy as nfl
    >>> pbp = nfl.load_pbp(2023)
    >>> explore_columns(pbp)  # Rich terminal output
    >>> explore_columns(pbp, output='html', save_path='pbp_columns.html')
    >>> explore_columns(pbp, output='markdown', save_path='columns.md')
    """

    # Gather column information
    col_info = []
    for col in df.columns:
        dtype = str(df[col].dtype)
        null_count = df[col].null_count()
        null_pct = (null_count / df.height * 100) if df.height > 0 else 0

        # Get unique count (limit to reasonable number for performance)
        try:
            n_unique = df[col].n_unique()
        except:
            n_unique = "N/A"

        # Get sample values (non-null)
        try:
            samples = df[col].drop_nulls().unique().head(sample_size).to_list()
            sample_str = ', '.join(str(s)[:50] for s in samples)  # Truncate long values
        except:
            sample_str = "N/A"

        col_info.append({
            'column': col,
            'dtype': dtype,
            'nulls': f"{null_count} ({null_pct:.1f}%)",
            'unique': str(n_unique),
            'samples': sample_str
        })

    # Format output based on selected type
    if output == 'rich':
        try:
            from rich.console import Console
            from rich.table import Table

            console = Console()
            table = Table(title=f"DataFrame Schema ({df.height} rows × {len(df.columns)} columns)")

            table.add_column("Column", style="cyan", no_wrap=True)
            table.add_column("Data Type", style="magenta")
            table.add_column("Nulls", style="yellow")
            table.add_column("Unique", style="green")
            table.add_column("Sample Values", style="blue", max_width=50)

            for info in col_info:
                table.add_row(
                    info['column'],
                    info['dtype'],
                    info['nulls'],
                    info['unique'],
                    info['samples']
                )

            console.print(table)
            return None

        except ImportError:
            print("⚠️  'rich' library not installed. Install with: pip install rich")
            print("Falling back to simple output...\n")
            output = 'simple'

    if output == 'simple':
        print(f"\n{'='*80}")
        print(f"DataFrame Schema: {df.height} rows × {len(df.columns)} columns")
        print(f"{'='*80}\n")

        for info in col_info:
            print(f"Column: {info['column']}")
            print(f"  Type: {info['dtype']}")
            print(f"  Nulls: {info['nulls']}")
            print(f"  Unique: {info['unique']}")
            print(f"  Samples: {info['samples']}")
            print()
        return None

    elif output == 'markdown':
        lines = [
            f"# DataFrame Schema\n",
            f"**Dimensions:** {df.height} rows × {len(df.columns)} columns\n",
            "| Column | Data Type | Nulls | Unique Values | Sample Values |",
            "|--------|-----------|-------|---------------|---------------|"
        ]

        for info in col_info:
            lines.append(
                f"| {info['column']} | {info['dtype']} | {info['nulls']} | "
                f"{info['unique']} | {info['samples'][:100]} |"
            )

        result = '\n'.join(lines)

        if save_path:
            Path(save_path).write_text(result, encoding='utf-8')
            print(f"[OK] Saved to {save_path}")

        return result

    elif output == 'html':
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>DataFrame Schema</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        h1 {{
            color: #333;
        }}
        .info {{
            margin-bottom: 20px;
            color: #666;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            background-color: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        th {{
            background-color: #4CAF50;
            color: white;
            padding: 12px;
            text-align: left;
            position: sticky;
            top: 0;
        }}
        td {{
            padding: 10px;
            border-bottom: 1px solid #ddd;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        .dtype {{
            color: #e91e63;
            font-family: monospace;
        }}
        .nulls {{
            color: #ff9800;
        }}
        .unique {{
            color: #4CAF50;
        }}
        .samples {{
            color: #2196F3;
            font-size: 0.9em;
            max-width: 400px;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
    </style>
</head>
<body>
    <h1>DataFrame Schema</h1>
    <div class="info">
        <strong>Dimensions:</strong> {df.height:,} rows × {len(df.columns)} columns
    </div>
    <table>
        <thead>
            <tr>
                <th>Column</th>
                <th>Data Type</th>
                <th>Nulls</th>
                <th>Unique Values</th>
                <th>Sample Values</th>
            </tr>
        </thead>
        <tbody>
"""

        for info in col_info:
            html += f"""
            <tr>
                <td><strong>{info['column']}</strong></td>
                <td class="dtype">{info['dtype']}</td>
                <td class="nulls">{info['nulls']}</td>
                <td class="unique">{info['unique']}</td>
                <td class="samples">{info['samples']}</td>
            </tr>
"""

        html += """
        </tbody>
    </table>
</body>
</html>
"""

        if save_path:
            Path(save_path).write_text(html, encoding='utf-8')
            print(f"[OK] Saved to {save_path}")

        return html

    else:
        raise ValueError(f"Unknown output format: {output}. Use 'rich', 'html', 'markdown', or 'simple'")



