# Configuration¶

**Source:** https://nflreadpy.nflverse.com/api/configuration/

---


# Configuration¶


## nflreadpy.config.NflreadpyConfig
¶

Bases: BaseSettings


```
BaseSettings
```

Configuration settings for nflreadpy.

This class manages all configuration options for the nflreadpy package.
Settings can be configured via environment variables or programmatically.

- NFLREADPY_CACHE: Cache mode ("memory", "filesystem", or "off")
- NFLREADPY_CACHE_DIR: Directory path for filesystem cache
- NFLREADPY_CACHE_DURATION: Cache duration in seconds
- NFLREADPY_VERBOSE: Enable verbose output (true/false)
- NFLREADPY_TIMEOUT: HTTP request timeout in seconds
- NFLREADPY_USER_AGENT: Custom user agent string

```
from nflreadpy.config import update_config, get_config

# Update settings programmatically
update_config(cache_mode="filesystem", verbose=False)

# Get current settings
config = get_config()
print(f"Cache mode: {config.cache_mode}")
```


```
from nflreadpy.config import update_config, get_config

# Update settings programmatically
update_config(cache_mode="filesystem", verbose=False)

# Get current settings
config = get_config()
print(f"Cache mode: {config.cache_mode}")
```


## nflreadpy.config.update_config
¶


```
update_config(**kwargs: Any) -> None
```


```
update_config(**kwargs: Any) -> None
```

Update configuration settings programmatically.

Parameters:


```
**kwargs
```


```
Any
```

Configuration options to update. Valid options include:

- cache_mode: "memory", "filesystem", or "off"
- cache_dir: Path to cache directory (str or Path)
- cache_duration: Cache duration in seconds (int)
- verbose: Enable verbose output (bool)
- timeout: HTTP timeout in seconds (int)
- user_agent: Custom user agent string (str)

```
{}
```

Raises:


```
ValueError
```

If an unknown configuration option is provided.


```
# Enable filesystem caching with custom directory
update_config(
    cache_mode="filesystem",
    cache_dir="/path/to/my/cache",
    verbose=True
)

# Disable caching and increase timeout
update_config(
    cache_mode="off"
    timeout=60
)
```


```
# Enable filesystem caching with custom directory
update_config(
    cache_mode="filesystem",
    cache_dir="/path/to/my/cache",
    verbose=True
)

# Disable caching and increase timeout
update_config(
    cache_mode="off"
    timeout=60
)
```


```
src/nflreadpy/config.py
```


```
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
153
154
155
156
157
158
159
160
161
162
163
164
165
166
167
168
169
```


```
def update_config(**kwargs: Any) -> None:
    """Update configuration settings programmatically.

    Args:
        **kwargs: Configuration options to update. Valid options include:

            - cache_mode: "memory", "filesystem", or "off"
            - cache_dir: Path to cache directory (str or Path)
            - cache_duration: Cache duration in seconds (int)
            - verbose: Enable verbose output (bool)
            - timeout: HTTP timeout in seconds (int)
            - user_agent: Custom user agent string (str)

    Raises:
        ValueError: If an unknown configuration option is provided.

    Example:
        ```python
        # Enable filesystem caching with custom directory
        update_config(
            cache_mode="filesystem",
            cache_dir="/path/to/my/cache",
            verbose=True
        )

        # Disable caching and increase timeout
        update_config(
            cache_mode="off"
            timeout=60
        )
        ```
    """
    global config
    for key, value in kwargs.items():
        if hasattr(config, key):
            setattr(config, key, value)
        else:
            raise ValueError(f"Unknown configuration option: {key}")
```


```
def update_config(**kwargs: Any) -> None:
    """Update configuration settings programmatically.

    Args:
        **kwargs: Configuration options to update. Valid options include:

            - cache_mode: "memory", "filesystem", or "off"
            - cache_dir: Path to cache directory (str or Path)
            - cache_duration: Cache duration in seconds (int)
            - verbose: Enable verbose output (bool)
            - timeout: HTTP timeout in seconds (int)
            - user_agent: Custom user agent string (str)

    Raises:
        ValueError: If an unknown configuration option is provided.

    Example:
        ```python
        # Enable filesystem caching with custom directory
        update_config(
            cache_mode="filesystem",
            cache_dir="/path/to/my/cache",
            verbose=True
        )

        # Disable caching and increase timeout
        update_config(
            cache_mode="off"
            timeout=60
        )
        ```
    """
    global config
    for key, value in kwargs.items():
        if hasattr(config, key):
            setattr(config, key, value)
        else:
            raise ValueError(f"Unknown configuration option: {key}")
```


## nflreadpy.config.get_config
¶


```
get_config() -> NflreadpyConfig
```


```
get_config() -> NflreadpyConfig
```

Get the current configuration instance.

Returns:


```
NflreadpyConfig
```

The global configuration object containing all current settings.


```
config = get_config()
print(f"Cache directory: {config.cache_dir}")
print(f"Verbose mode: {config.verbose}")
```


```
config = get_config()
print(f"Cache directory: {config.cache_dir}")
print(f"Verbose mode: {config.verbose}")
```


```
src/nflreadpy/config.py
```


```
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
```


```
def get_config() -> NflreadpyConfig:
    """Get the current configuration instance.

    Returns:
        The global configuration object containing all current settings.

    Example:
        ```python
        config = get_config()
        print(f"Cache directory: {config.cache_dir}")
        print(f"Verbose mode: {config.verbose}")
        ```
    """
    return config
```


```
def get_config() -> NflreadpyConfig:
    """Get the current configuration instance.

    Returns:
        The global configuration object containing all current settings.

    Example:
        ```python
        config = get_config()
        print(f"Cache directory: {config.cache_dir}")
        print(f"Verbose mode: {config.verbose}")
        ```
    """
    return config
```


## nflreadpy.config.reset_config
¶


```
reset_config() -> None
```


```
reset_config() -> None
```

Reset all configuration settings to their default values.

This will restore all settings to their initial state, clearing any
programmatic or environment variable overrides.


```
# Make some changes
update_config(cache_mode="off", verbose=False)

# Reset everything back to defaults
reset_config()

# Now cache_mode is "memory" and verbose is True again
```


```
# Make some changes
update_config(cache_mode="off", verbose=False)

# Reset everything back to defaults
reset_config()

# Now cache_mode is "memory" and verbose is True again
```


```
src/nflreadpy/config.py
```


```
172
173
174
175
176
177
178
179
180
181
182
183
184
185
186
187
188
189
190
```


```
def reset_config() -> None:
    """Reset all configuration settings to their default values.

    This will restore all settings to their initial state, clearing any
    programmatic or environment variable overrides.

    Example:
        ```python
        # Make some changes
        update_config(cache_mode="off", verbose=False)

        # Reset everything back to defaults
        reset_config()

        # Now cache_mode is "memory" and verbose is True again
        ```
    """
    global config
    config = NflreadpyConfig()
```


```
def reset_config() -> None:
    """Reset all configuration settings to their default values.

    This will restore all settings to their initial state, clearing any
    programmatic or environment variable overrides.

    Example:
        ```python
        # Make some changes
        update_config(cache_mode="off", verbose=False)

        # Reset everything back to defaults
        reset_config()

        # Now cache_mode is "memory" and verbose is True again
        ```
    """
    global config
    config = NflreadpyConfig()
```

