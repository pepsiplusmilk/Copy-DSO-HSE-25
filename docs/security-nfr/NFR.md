# Table of nonfunctional requirements of the project

| ID     | Name                              | Description                                                   | Metrics                                               | Check (where/how)           | Component       | Priority |
|--------|-----------------------------------|---------------------------------------------------------------|-------------------------------------------------------|-----------------------------|-----------------|----------|
| NFR-01 | Password storage                  | Secure users password hashing via Argon2id                    | t=3, m=256MB, p=1                                     | Configuration files + tests | auth            | High     |
| NFR-02 | Correctness of board statuses     | Ensure users can't vote on closed boards                      | 100% of voting routes reject invalid status           | Unit tests                  | api/repo        | High     |
| NFR-03 | Voting response time              | p95 <= 150 ms @ 150 RPS on stage                              | p95 <= 150 ms @ 150 RPS                               | High load tests             | voting          | Medium   |
| NFR-04 | Login attempt threshold (p95/p99) | On login: <= 5 retries, after that 429 with 5 min cooldown    | 6th attempt returns 429; cooldown lasts in [5;10] min | Rate-limit metrics + logs   | auth            | Medium   |
| NFR-05 | Login response time               | p95 <= 500 ms at 150 RPS on stage                             | p95 <= 500 ms @ 150 RPS                               | High load tests             | auth            | Low      |
| NFR-06 | Block additional voting           | Block user from voting multiple times for the same idea       | 100% of voting routes reject repeated vote            | Unit tests                  | voting          | High     |
| NFR-07 | RFC7807 exception format adopting | Save corr_id; uniform JSON standard for errors (RFC7807)      | 100% of endpoints                                     | Contract testing            | errors          | Low      |
| NFR-08 | Personal data privacy             | User credentials and vote distribution are secured and masked | 100% of endpoints do not return personal data         | Unit tests                  | auth/api/voting | High     |
