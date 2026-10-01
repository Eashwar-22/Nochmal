import base64
from hashlib import sha256
from html import escape

import streamlit as st


def render_audio_player(
    audio_bytes: bytes,
    *,
    label: str,
    compact: bool = False,
) -> None:
    """Render a small custom player while preserving the supplied audio bytes."""
    encoded_audio = base64.b64encode(audio_bytes).decode("ascii")
    player_hash = sha256(audio_bytes + label.encode("utf-8")).hexdigest()[:12]
    player_id = f"nochmal-audio-{player_hash}"
    safe_label = escape(label)
    shell_height = 72 if compact else 84
    button_size = 50 if compact else 60
    time_size = 14 if compact else 17
    control_size = 38 if compact else 44
    component_height = 88 if compact else 100

    st.iframe(
        f"""
        <!doctype html>
        <html lang="en">
        <head>
          <meta charset="utf-8">
          <style>
            * {{ box-sizing: border-box; }}
            html, body {{
              margin: 0;
              padding: 0;
              background: transparent;
              font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            }}
            .audio-shell {{
              position: relative;
              display: flex;
              align-items: center;
              gap: 12px;
              width: 100%;
              height: {shell_height}px;
              padding: 10px 14px;
              border: 1px solid #dce3e8;
              border-radius: 14px;
              background: #ffffff;
              box-shadow: 0 8px 24px rgba(19, 39, 51, 0.08);
            }}
            .play-button {{
              display: grid;
              flex: 0 0 {button_size}px;
              width: {button_size}px;
              height: {button_size}px;
              place-items: center;
              padding: 0;
              border: 0;
              border-radius: 50%;
              background: #ed6a4d;
              cursor: pointer;
              transition: background 120ms ease, transform 120ms ease;
            }}
            .play-button:hover {{ background: #da593d; }}
            .play-button:active {{ transform: scale(0.97); }}
            .play-button:focus-visible {{
              outline: 3px solid rgba(49, 93, 148, 0.3);
              outline-offset: 2px;
            }}
            .play-button svg {{
              width: 62%;
              height: 62%;
            }}
            .pause-symbol {{ display: none; }}
            .play-button.is-playing .play-symbol {{ display: none; }}
            .play-button.is-playing .pause-symbol {{ display: block; }}
            .time-display {{
              flex: 0 0 auto;
              color: #14222d;
              font-size: {time_size}px;
              font-variant-numeric: tabular-nums;
              font-weight: 750;
              letter-spacing: -0.03em;
              white-space: nowrap;
            }}
            .timeline-wrap {{
              position: relative;
              display: flex;
              flex: 1 1 auto;
              align-items: center;
              height: 32px;
            }}
            .track {{
              position: absolute;
              left: 0;
              right: 0;
              height: 6px;
              overflow: hidden;
              border: 0;
              border-radius: 999px;
              background: rgba(20, 34, 45, 0.14);
              pointer-events: none;
            }}
            .progress {{
              height: 100%;
              width: 0;
              background: #ed6a4d;
            }}
            .timeline {{
              position: relative;
              z-index: 2;
              width: 100%;
              height: 32px;
              margin: 0;
              appearance: none;
              background: transparent;
              cursor: pointer;
            }}
            .timeline::-webkit-slider-runnable-track {{
              height: 6px;
              background: transparent;
            }}
            .timeline::-webkit-slider-thumb {{
              width: 14px;
              height: 14px;
              margin-top: -2px;
              appearance: none;
              border: 2px solid #fffdf8;
              border-radius: 50%;
              background: #ed6a4d;
              opacity: 0;
              transition: opacity 120ms ease;
            }}
            .audio-shell:hover .timeline::-webkit-slider-thumb,
            .timeline:focus-visible::-webkit-slider-thumb {{ opacity: 1; }}
            .timeline::-moz-range-track {{
              height: 6px;
              background: transparent;
            }}
            .timeline::-moz-range-thumb {{
              width: 12px;
              height: 12px;
              border: 2px solid #fffdf8;
              border-radius: 50%;
              background: #ed6a4d;
              opacity: 0;
            }}
            .audio-shell:hover .timeline::-moz-range-thumb,
            .timeline:focus-visible::-moz-range-thumb {{ opacity: 1; }}
            .utility-button {{
              display: grid;
              flex: 0 0 {control_size}px;
              width: {control_size}px;
              height: {control_size}px;
              place-items: center;
              padding: 0;
              border: 0;
              border-radius: 10px;
              background: transparent;
              color: #14222d;
              cursor: pointer;
            }}
            .utility-button:hover {{ background: #eceee8; }}
            .utility-button:focus-visible {{
              outline: 3px solid rgba(49, 93, 148, 0.3);
              outline-offset: 1px;
            }}
            .volume-button svg {{ width: 100%; height: 100%; }}
            .mute-slash {{ display: none; }}
            .volume-button.is-muted .volume-waves {{ display: none; }}
            .volume-button.is-muted .mute-slash {{ display: block; }}
            .options-wrap {{
              position: relative;
              display: flex;
              align-items: center;
            }}
            .menu-button svg {{ width: 70%; height: 70%; }}
            .speed-menu {{
              position: absolute;
              z-index: 5;
              top: 50%;
              right: calc(100% + 6px);
              display: none;
              gap: 4px;
              padding: 5px;
              border: 1px solid #dde0d8;
              border-radius: 10px;
              background: #ffffff;
              box-shadow: 0 10px 24px rgba(71, 61, 43, 0.14);
              transform: translateY(-50%);
              white-space: nowrap;
            }}
            .speed-menu.is-open {{ display: flex; }}
            .speed-option {{
              padding: 5px 7px;
              border: 0;
              border-radius: 6px;
              background: transparent;
              color: #252721;
              font-size: 12px;
              font-weight: 650;
              cursor: pointer;
            }}
            .speed-option:hover,
            .speed-option.is-active {{ background: #f0f1ed; }}
            .sr-only {{
              position: absolute;
              width: 1px;
              height: 1px;
              padding: 0;
              margin: -1px;
              overflow: hidden;
              clip: rect(0, 0, 0, 0);
              white-space: nowrap;
              border: 0;
            }}
          </style>
        </head>
        <body>
          <div class="audio-shell">
            <button class="play-button" type="button" aria-label="{safe_label}">
              <svg class="play-symbol" viewBox="0 0 32 32" aria-hidden="true">
                <path d="M9 5 L26 16 L9 27 Z" fill="#fffdf8"></path>
              </svg>
              <svg class="pause-symbol" viewBox="0 0 32 32" aria-hidden="true">
                <rect x="8" y="6" width="6" height="20" rx="1" fill="#fffdf8"></rect>
                <rect x="18" y="6" width="6" height="20" rx="1" fill="#fffdf8"></rect>
              </svg>
            </button>
            <div class="time-display" aria-label="Audio time">
              <span class="current-time">0:00</span>
              <span aria-hidden="true"> / </span>
              <span class="duration">0:00</span>
            </div>
            <div class="timeline-wrap">
              <div class="track"><div class="progress"></div></div>
              <input
                class="timeline"
                type="range"
                min="0"
                max="100"
                step="0.1"
                value="0"
                aria-label="Audio progress"
              >
            </div>
            <button class="utility-button volume-button" type="button" aria-label="Mute audio">
              <svg viewBox="0 0 48 48" aria-hidden="true">
                <path d="M7 19 H14 L24 10 V38 L14 29 H7 Z" fill="#fffdf8" stroke="#252721" stroke-width="2.3" stroke-linejoin="round"></path>
                <g class="volume-waves" fill="none" stroke="#252721" stroke-linecap="round" stroke-width="2.5">
                  <path d="M30 17 Q35 24 30 31"></path>
                  <path d="M35 12 Q43 24 35 36"></path>
                </g>
                <path class="mute-slash" d="M30 17 L40 31 M40 17 L30 31" fill="none" stroke="#252721" stroke-linecap="round" stroke-width="2.5"></path>
              </svg>
            </button>
            <div class="options-wrap">
              <button class="utility-button menu-button" type="button" aria-label="Playback options" aria-expanded="false">
                <svg viewBox="0 0 28 40" aria-hidden="true">
                  <circle cx="14" cy="8" r="3.2" fill="#252721"></circle>
                  <circle cx="14" cy="20" r="3.2" fill="#252721"></circle>
                  <circle cx="14" cy="32" r="3.2" fill="#252721"></circle>
                </svg>
              </button>
              <div class="speed-menu" role="menu" aria-label="Playback speed">
                <button class="speed-option" type="button" data-rate="0.75">0.75×</button>
                <button class="speed-option is-active" type="button" data-rate="1">1×</button>
                <button class="speed-option" type="button" data-rate="1.25">1.25×</button>
              </div>
            </div>
            <span class="sr-only" aria-live="polite"></span>
            <audio preload="metadata">
              <source src="data:audio/wav;base64,{encoded_audio}" type="audio/wav">
            </audio>
          </div>
          <script>
            const playerId = "{player_id}";
            const shell = document.querySelector(".audio-shell");
            const button = shell.querySelector(".play-button");
            const timeline = shell.querySelector(".timeline");
            const progress = shell.querySelector(".progress");
            const currentTime = shell.querySelector(".current-time");
            const duration = shell.querySelector(".duration");
            const volumeButton = shell.querySelector(".volume-button");
            const menuButton = shell.querySelector(".menu-button");
            const speedMenu = shell.querySelector(".speed-menu");
            const speedOptions = shell.querySelectorAll(".speed-option");
            const status = shell.querySelector(".sr-only");
            const audio = shell.querySelector("audio");
            const channel = "BroadcastChannel" in window
              ? new BroadcastChannel("nochmal-audio-player")
              : null;

            function showPlaying() {{
              button.classList.add("is-playing");
              button.setAttribute("aria-label", "Pause audio");
              status.textContent = "Audio playing";
            }}

            function showPaused() {{
              button.classList.remove("is-playing");
              button.setAttribute("aria-label", "{safe_label}");
              status.textContent = "Audio paused";
            }}

            function formatTime(seconds) {{
              if (!Number.isFinite(seconds)) return "0:00";
              const minutes = Math.floor(seconds / 60);
              const remainingSeconds = Math.floor(seconds % 60)
                .toString()
                .padStart(2, "0");
              return `${{minutes}}:${{remainingSeconds}}`;
            }}

            function updateDuration() {{
              duration.textContent = formatTime(audio.duration);
            }}

            button.addEventListener("click", async () => {{
              if (audio.paused) {{
                if (channel) channel.postMessage(playerId);
                try {{
                  await audio.play();
                  showPlaying();
                }} catch (error) {{
                  status.textContent = "Audio could not be played";
                }}
              }} else {{
                audio.pause();
                showPaused();
              }}
            }});

            audio.addEventListener("timeupdate", () => {{
              if (!Number.isFinite(audio.duration) || audio.duration === 0) return;
              const percentage = (audio.currentTime / audio.duration) * 100;
              timeline.value = percentage;
              progress.style.width = `${{percentage}}%`;
              currentTime.textContent = formatTime(audio.currentTime);
            }});

            audio.addEventListener("loadedmetadata", updateDuration);
            audio.addEventListener("durationchange", updateDuration);

            audio.addEventListener("ended", () => {{
              showPaused();
            }});

            timeline.addEventListener("input", () => {{
              if (!Number.isFinite(audio.duration)) return;
              audio.currentTime = (Number(timeline.value) / 100) * audio.duration;
              progress.style.width = `${{timeline.value}}%`;
              currentTime.textContent = formatTime(audio.currentTime);
            }});

            volumeButton.addEventListener("click", () => {{
              audio.muted = !audio.muted;
              volumeButton.classList.toggle("is-muted", audio.muted);
              volumeButton.setAttribute(
                "aria-label",
                audio.muted ? "Unmute audio" : "Mute audio"
              );
              status.textContent = audio.muted ? "Audio muted" : "Audio unmuted";
            }});

            menuButton.addEventListener("click", () => {{
              const isOpen = speedMenu.classList.toggle("is-open");
              menuButton.setAttribute("aria-expanded", String(isOpen));
            }});

            speedOptions.forEach((option) => {{
              option.addEventListener("click", () => {{
                audio.playbackRate = Number(option.dataset.rate);
                speedOptions.forEach((item) => item.classList.remove("is-active"));
                option.classList.add("is-active");
                speedMenu.classList.remove("is-open");
                menuButton.setAttribute("aria-expanded", "false");
                status.textContent = `Playback speed ${{option.textContent}}`;
              }});
            }});

            if (channel) {{
              channel.addEventListener("message", (event) => {{
                if (event.data === playerId || audio.paused) return;
                audio.pause();
                showPaused();
              }});
            }}
          </script>
        </body>
        </html>
        """,
        width="stretch",
        height=component_height,
    )


def render_replay_button(audio_bytes: bytes, *, label: str) -> None:
    """Render a compact text control for replaying an existing audio clip."""
    encoded_audio = base64.b64encode(audio_bytes).decode("ascii")
    player_hash = sha256(audio_bytes + label.encode("utf-8")).hexdigest()[:12]
    player_id = f"nochmal-replay-{player_hash}"
    safe_label = escape(label)

    st.iframe(
        f"""
        <!doctype html>
        <html lang="en">
        <head>
          <meta charset="utf-8">
          <style>
            * {{ box-sizing: border-box; }}
            html, body {{
              margin: 0;
              padding: 0;
              background: transparent;
              font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            }}
            button {{
              display: inline-flex;
              align-items: center;
              gap: 7px;
              min-height: 38px;
              padding: 4px 0;
              border: 0;
              background: transparent;
              color: #a9a9a9;
              font-size: 15px;
              font-weight: 700;
              cursor: pointer;
            }}
            button:hover {{ color: #777777; }}
            button:focus-visible {{
              border-radius: 5px;
              outline: 2px solid #1769d2;
              outline-offset: 2px;
            }}
            .play-icon {{
              width: 0;
              height: 0;
              border-top: 9px solid transparent;
              border-bottom: 9px solid transparent;
              border-left: 14px solid currentColor;
            }}
            .pause-icon {{
              width: 14px;
              height: 17px;
              border-right: 5px solid currentColor;
              border-left: 5px solid currentColor;
            }}
            .sr-only {{
              position: absolute;
              width: 1px;
              height: 1px;
              margin: -1px;
              overflow: hidden;
              clip: rect(0, 0, 0, 0);
              white-space: nowrap;
            }}
          </style>
        </head>
        <body>
          <button type="button" aria-label="{safe_label}">
            <span class="play-icon" aria-hidden="true"></span>
            <span class="button-label">{safe_label}</span>
          </button>
          <span class="sr-only" aria-live="polite"></span>
          <audio preload="metadata">
            <source src="data:audio/wav;base64,{encoded_audio}" type="audio/wav">
          </audio>
          <script>
            const playerId = "{player_id}";
            const button = document.querySelector("button");
            const icon = button.querySelector("span");
            const buttonLabel = button.querySelector(".button-label");
            const status = document.querySelector(".sr-only");
            const audio = document.querySelector("audio");
            const channel = "BroadcastChannel" in window
              ? new BroadcastChannel("nochmal-audio-player")
              : null;

            function showPlaying() {{
              icon.className = "pause-icon";
              buttonLabel.textContent = "Pause audio";
              button.setAttribute("aria-label", "Pause audio");
              status.textContent = "Audio playing";
            }}

            function showPaused() {{
              icon.className = "play-icon";
              buttonLabel.textContent = "{safe_label}";
              button.setAttribute("aria-label", "{safe_label}");
              status.textContent = "Audio paused";
            }}

            button.addEventListener("click", async () => {{
              if (audio.paused) {{
                if (channel) channel.postMessage(playerId);
                try {{
                  await audio.play();
                  showPlaying();
                }} catch (error) {{
                  status.textContent = "Audio could not be played";
                }}
              }} else {{
                audio.pause();
                showPaused();
              }}
            }});

            audio.addEventListener("ended", showPaused);

            if (channel) {{
              channel.addEventListener("message", (event) => {{
                if (event.data === playerId || audio.paused) return;
                audio.pause();
                showPaused();
              }});
            }}
          </script>
        </body>
        </html>
        """,
        width="stretch",
        height=42,
    )
