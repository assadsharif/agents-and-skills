# ADR-0001: Use PostgreSQL as Primary Database

**Status:** Accepted
**Date:** 2026-02-18
**Decision Makers:** Engineering Team, Technical Lead
**Affected Areas:** Data persistence, backend architecture, deployment

---

## Context

**This is a reference example showing proper ADR structure and decision documentation.**

### Background

We are building a SaaS application for user authentication and authorization management. The system needs to:

- Store user accounts, roles, and permissions
- Handle complex relational queries (user-role-permission mappings)
- Support ACID transactions for security-critical operations
- Scale to 100K+ users over next 12 months
- Provide audit logging for compliance (SOC 2, GDPR)

### Problem Statement

**We need to select a primary database that balances:**
1. Relational data modeling capabilities
2. ACID compliance for security operations
3. Performance at scale (100K+ users)
4. Developer familiarity and ecosystem maturity
5. Cost-effectiveness for early-stage startup
6. Deployment flexibility (self-hosted and cloud)

### Forces (Constraints & Requirements)

**Must Have:**
- ✅ ACID transactions (critical for auth operations)
- ✅ Complex JOIN support (user-role-permission relationships)
- ✅ JSON/JSONB support (flexible metadata storage)
- ✅ Open source with commercial backing
- ✅ Strong Python ORM support (SQLAlchemy/SQLModel)

**Should Have:**
- Full-text search capabilities
- Row-level security for multi-tenancy
- Built-in replication and high availability
- Mature cloud hosting options (AWS RDS, etc.)

**Nice to Have:**
- Time-series data support for analytics
- Geographic/spatial data types
- Advanced indexing (GIN, GiST)

**Constraints:**
- Budget: <$200/month for database hosting (early stage)
- Team expertise: Strong PostgreSQL experience, limited NoSQL
- Timeline: Must be production-ready in 6 weeks

---

## Decision

**We will use PostgreSQL 15+ as our primary database.**

### Rationale

1. **Relational Model Match:** Our data is inherently relational (users ↔ roles ↔ permissions). PostgreSQL's foreign keys, constraints, and JOIN performance are ideal.

2. **ACID Guarantees:** Authentication and authorization require strong consistency. PostgreSQL's MVCC and transaction isolation prevent race conditions in permission checks.

3. **JSON Flexibility:** JSONB columns allow schema evolution for user metadata without migrations, combining SQL structure with NoSQL flexibility.

4. **Ecosystem Maturity:**
   - SQLAlchemy/SQLModel provide excellent ORMs
   - pg_bouncer for connection pooling
   - pgvector extension if we add AI features
   - Comprehensive monitoring tools (pg_stat_statements, pgAdmin)

5. **Deployment Options:**
   - Self-hosted on AWS EC2 (early stage)
   - Migrate to AWS RDS PostgreSQL when scaling
   - Supabase or Neon for managed alternative

6. **Team Expertise:** Team has 5+ years PostgreSQL experience; minimal learning curve.

7. **Cost:** Free for self-hosted; AWS RDS starts at $15/month for db.t3.micro.

---

## Consequences

### Positive

- ✅ **Data Integrity:** ACID transactions prevent inconsistent auth states
- ✅ **Query Power:** Complex permission checks via single SQL query
- ✅ **Ecosystem:** Vast library of extensions (pgcrypto, pg_trgm, timescaledb)
- ✅ **Operational Maturity:** Battle-tested at scale (Instagram, Spotify, Reddit)
- ✅ **Developer Velocity:** Team already proficient; no training needed
- ✅ **Cost-Effective:** Open source; low hosting costs for current scale

### Negative

- ⚠️ **Write Scalability Ceiling:** Single-master architecture limits write throughput (mitigated by read replicas for queries)
- ⚠️ **Schema Migrations:** Require downtime or careful online migration planning
- ⚠️ **Connection Overhead:** Each connection has memory cost; requires connection pooling (pg_bouncer)
- ⚠️ **No Native Horizontal Sharding:** Future sharding requires Citus extension or application-level partitioning

### Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Single point of failure | HIGH | Configure streaming replication with failover |
| Write bottleneck at scale | MEDIUM | Implement read replicas; use caching (Redis) for hot paths |
| Schema lock during migrations | MEDIUM | Use pg-online-schema-change or blue-green deployment |
| Connection pool exhaustion | LOW | Deploy pg_bouncer in transaction mode; monitor connections |

---

## Alternatives Considered

### Option 1: MongoDB (NoSQL Document Store)

**Pros:**
- Flexible schema (no migrations)
- Horizontal sharding built-in
- JSON-native storage

**Cons:**
- ❌ No ACID across documents (auth requires strong consistency)
- ❌ Complex JOINs inefficient ($lookup aggregation pipelines)
- ❌ Team lacks deep MongoDB experience
- ❌ ORM support weaker (MongoEngine vs SQLAlchemy maturity)

**Rejected Because:** Authentication/authorization is fundamentally relational. MongoDB's eventual consistency and weak JOIN support are deal-breakers for security-critical operations.

---

### Option 2: MySQL/MariaDB

**Pros:**
- ACID compliance
- Mature ecosystem
- Strong replication

**Cons:**
- ❌ Weaker JSON support (JSON column vs JSONB indexing)
- ❌ Less powerful full-text search
- ❌ Limited extension ecosystem vs PostgreSQL
- ❌ No equivalent to PostgreSQL's advanced types (arrays, JSONB operators, ranges)

**Rejected Because:** PostgreSQL's JSONB, array types, and extension ecosystem provide technical advantages that justify its selection. Team preference also strongly favors PostgreSQL.

---

### Option 3: Amazon DynamoDB (NoSQL Key-Value)

**Pros:**
- Serverless, auto-scaling
- Single-digit millisecond latency
- Built-in replication

**Cons:**
- ❌ No complex queries (single-table design required)
- ❌ Limited transaction support (max 100 items)
- ❌ Vendor lock-in (AWS-only)
- ❌ High cost at scale ($1.25/million writes)
- ❌ Steep learning curve for team

**Rejected Because:** DynamoDB's single-table design pattern is incompatible with our relational auth model. Cost and vendor lock-in are secondary concerns.

---

### Option 4: SQLite (Embedded Database)

**Pros:**
- Zero-config, file-based
- Perfect for development/testing
- Lightweight

**Cons:**
- ❌ No network access (single-machine only)
- ❌ Limited concurrency (writes block)
- ❌ No built-in replication
- ❌ Not production-ready for multi-user SaaS

**Rejected Because:** SQLite cannot support a networked SaaS application. Will use for local development/testing only.

---

## Implementation Plan

### Phase 1: Development Setup (Week 1)

- [ ] Install PostgreSQL 15 locally via Docker Compose
- [ ] Configure SQLModel ORM with connection pooling
- [ ] Set up Alembic for schema migrations
- [ ] Create initial schema (users, roles, permissions tables)
- [ ] Write database seeder for development data

### Phase 2: Production Deployment (Week 2-3)

- [ ] Deploy PostgreSQL on AWS EC2 (t3.small)
- [ ] Configure automated backups (daily snapshots to S3)
- [ ] Set up pg_bouncer for connection pooling
- [ ] Enable SSL/TLS for database connections
- [ ] Configure monitoring (CloudWatch + pg_stat_statements)

### Phase 3: High Availability (Month 2-3)

- [ ] Set up streaming replication (primary + 1 replica)
- [ ] Configure automatic failover (patroni or repmgr)
- [ ] Implement read-write split in application layer
- [ ] Load test with 10K concurrent users

---

## Success Metrics

**After 3 months, we will evaluate this decision based on:**

- ✅ Query performance: p95 latency < 100ms for auth checks
- ✅ Availability: 99.9% uptime (43 minutes downtime/month)
- ✅ Data integrity: Zero auth state inconsistencies
- ✅ Developer velocity: Schema migrations < 5 minutes
- ✅ Cost: Database hosting < $200/month

**Decision will be revisited if:**
- Write throughput exceeds 1000 writes/second (requires sharding)
- Storage exceeds 500GB (consider data archival strategy)
- Team size grows to require specialized DBA (may consider managed service)

---

## References

- [PostgreSQL Official Documentation](https://www.postgresql.org/docs/15/)
- [SQLModel ORM Guide](https://sqlmodel.tiangolo.com/)
- [AWS RDS PostgreSQL Best Practices](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_PostgreSQL.html)
- [High Performance PostgreSQL (Book)](https://www.postgresql.org/docs/books/)

---

## Related Documents

- **Specification:** `specs/user-authentication/spec.md`
- **Implementation Plan:** `specs/user-authentication/plan.md`
- **Database Schema:** `docs/architecture/database-schema.md`
- **Related ADRs:**
  - ADR-0002: Use SQLModel ORM for Python Database Access
  - ADR-0003: Implement Row-Level Security for Multi-Tenancy

---

## Approval

**Proposed:** 2026-02-15
**Reviewed:** 2026-02-17 (Engineering team meeting)
**Accepted:** 2026-02-18
**Supersedes:** None (first database decision)

**Reviewers:**
- ✅ Technical Lead
- ✅ Backend Engineer
- ✅ DevOps Engineer

---

## Amendments

None yet. See amendment log below if decision is modified.

---

## Usage Note

**This ADR serves as a reference example for:**

1. **Comprehensive context** - Background, problem statement, forces clearly explained
2. **Explicit decision** - Clear statement of what was chosen and why
3. **Balanced consequences** - Both positive and negative impacts documented
4. **Thorough alternatives** - 4 alternatives considered with pros/cons
5. **Actionable implementation** - Phased plan with checkboxes
6. **Measurable success** - Specific metrics to evaluate decision
7. **Traceability** - Links to specs, plans, related ADRs

**When creating your own ADRs:**
- Use this structure as a starting point
- Adapt sections based on decision complexity
- Focus on "why" not just "what"
- Document alternatives honestly (including why rejected)
- Make consequences concrete (metrics, timelines, risks)

---

**ADR Template Location:** `.specify/templates/adr-template.md`
**Creation Script:** `.specify/scripts/bash/create-adr.sh`
