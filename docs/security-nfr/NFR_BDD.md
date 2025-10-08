# Gherkin formated acceptance conditions

---

- **Feature**: Correctness of vote boards statuses
  - **Scenario**: Closed board voting attempt
    * **Given** Server is running and at least one voteboard has been closed
    * **When**  User is trying to vote on some closed voteboard
    * **Then**  Raise an exception

  - **Scenario**: Closed board unvoting attempt
    * **Given** Server is running and at least one voteboard has been closed
    * **When**  User is trying to remove vote on some closed voteboard
    * **Then**  Raise an exception

  - **Scenario**: Adding ideas to the vote board
    * **Given** Vote board with opened state(ON_VOTING) or with closed state
    * **When**  User is trying to add new idea's to this board
    * **Then**  Raise an exception

- **Feature**: Correctness of logging attempts threshold
  - **Scenario**: User logging into service account
    * **Given** 6th attempt of logging after five unsuccessful tries
    * **When**  User is trying to vote on some closed voteboard
    * **Then**  Return 429 code and start cooldown of 5 minutes

- **Feature**: Single voting strategy on each board
  - **Scenario**: User is trying to vote again, after he is
  already voted for some idea on this board
    * **Given** Voteboard opened and registered user's prime voice
    * **When**  Second attempt of voting happened without removing old vote
    * **Then**  Raise error

- **Feature**: Correctness of exception format
  - **Scenario**: Raise of exception on server
    * **Given** Stable work of server, users performs a queries
    * **When**  User query or internal state raises an exception
    * **Then**  Exception format checkers aren't failed
