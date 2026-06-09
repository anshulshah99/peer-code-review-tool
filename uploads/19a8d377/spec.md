# Number Guessing Game — Project Specification

## Overview

A CLI-based number guessing game where the player tries to guess a randomly chosen secret number within a limited number of attempts. The game gives directional feedback after each guess and tracks the player's score across multiple rounds.

## Functional Requirements

### 1. Game Setup
- On launch, prompt the player for their name.
- Display a welcome message that includes the player's name.
- Ask the player to choose a difficulty level before each round:
  - **Easy**: secret number in range 1–50, 10 attempts allowed
  - **Medium**: secret number in range 1–100, 7 attempts allowed
  - **Hard**: secret number in range 1–200, 5 attempts allowed

### 2. Gameplay Loop
- Generate a random integer within the range for the chosen difficulty.
- On each turn, display the number of attempts remaining.
- Prompt the player to enter a guess.
- Validate that the input is an integer; if not, display an error message and do **not** count it as an attempt.
- After a valid guess, display one of:
  - `Too low!` — if the guess is below the secret number
  - `Too high!` — if the guess is above the secret number
  - `Correct! You guessed it in X attempt(s).` — if the guess matches

### 3. Round End
- If the player uses all attempts without guessing correctly, reveal the secret number.
- After each round (win or loss), ask if the player wants to play again (`y`/`n`).

### 4. Scoring
- Track the total number of rounds played and rounds won across the session.
- At the end of the session (when the player quits), display a summary:
  ```
  Thanks for playing, <name>!
  Rounds played: X
  Rounds won:    Y
  Win rate:      Z%
  ```

### 5. Input Handling
- Strip leading/trailing whitespace from all inputs.
- Accept `y`, `yes`, `n`, `no` (case-insensitive) for yes/no prompts.
- Any unrecognized yes/no input should re-prompt the player.

## Non-Functional Requirements
- The game must run entirely in the terminal with no external dependencies beyond the Python standard library.
- Code must be organized into at least these functions: `get_difficulty()`, `play_round()`, `show_summary()`.
