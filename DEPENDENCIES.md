# Framework Dependencies - Status & Migration Roadmap

**Last Updated:** 2025-11-25  
**Review Schedule:** Quarterly (March, June, September, December)

---

## Purpose

This document tracks all external framework dependencies in Amsha, assesses their risks, and documents isolation strategies. As a common library, we must minimize framework coupling to ensure long-term stability.

---

## Critical Framework Dependencies

### 1. CrewAI (0.201.1)
**Category:** Core Orchestration Framework  
**Risk Level:** 🔴 **HIGH** - Core business logic dependency

**Usage:**
- Agent and Task orchestration
- Crew execution
- LLM integration

**Isolation Status:** ⚠️ **Partial**
- ✅ Domain models are framework-agnostic (`AgentData`, `TaskData`)
- ❌ Services directly use `crewai.Agent`, `crewai.Task`, `crewai.Crew`
- ❌ Orchestrators import CrewAI types directly

**Migration Path:**
1. Create `adapters/crewai/crewai_agent_adapter.py`
2. Create `adapters/crewai/crewai_task_adapter.py`
3. Define `IAgentFramework` protocol for alternative frameworks
4. Refactor services to use adapters instead of direct imports

**Alternative Frameworks:**
- LangGraph (LangChain)
- AutoGen (Microsoft)
- Custom orchestration layer

**Action Items:**
- [ ] Create adapter layer for CrewAI (Q2 2025)
- [ ] Monitor CrewAI changelog for breaking changes
- [ ] Evaluate LangGraph as alternative (Q3 2025)

---



---

- ✅ Well isolated, no action needed

---

### 4. PyMongo (4.11.3)
**Category:** Database Driver  
**Risk Level:** 🟡 **MEDIUM** - Data persistence dependency

**Usage:**
- Repository implementations in `repo/adapters/mongo/`
- Agent/Task/Crew config storage

**Isolation Status:** ✅ **Excellent**
- Repository pattern already isolates MongoDB
- `IAgentRepository`, `ITaskRepository` interfaces defined
- Easy to add PostgreSQL or other database adapters

**Migration Path:**
- Already follows best practice
- Can add SQL adapter without changing services

**Alternative Databases:**
- PostgreSQL (with SQLAlchemy)
- DynamoDB
- Firebase/Firestore
- In-memory (for testing)

**Action Items:**
- ✅ Well isolated via repository pattern
- [ ] Consider adding SQL adapter for broader adoption (Q4 2025)

---

- ✅ Well isolated via repository pattern
- [ ] Consider adding SQL adapter for broader adoption (Q4 2025)

---

### 6. Pandas (2.3.2)
**Category:** Data Processing  
**Risk Level:** 🟢 **LOW** - Utility dependency

**Usage:**
- Data processing in MLOps
- CSV/Excel handling
- Topic modeling data manipulation

**Isolation Status:** ⚠️ **Partial**
- Used in utilities and preprocessing
- Some leakage into domain layer

**Migration Path:**
- Consider Polars (faster, more memory efficient)
- Abstract DataFrame operations behind interface

**Alternative Frameworks:**
- Polars (Rust-based, faster)
- Dask (distributed)
- Native Python (for simple cases)

**Action Items:**
- [ ] Evaluate Polars for performance gains (Q3 2025)
- [ ] Create DataFrame abstraction if needed

---

## Utility Libraries (Low Risk)

These are stable, well-maintained libraries with minimal breaking change risk:

| Library | Version | Purpose | Risk | Isolation |
|---------|---------|---------|------|-----------|
| Pydantic | 2.11.9 | Data validation | 🟢 LOW | ✅ Core pattern |
| PyYAML | 6.0.3 | Config parsing | 🟢 LOW | ✅ Utils only |
| BeautifulSoup | 4.13.4 | HTML parsing | 🟢 LOW | ✅ Preprocessing |
| NetworkX | 3.4.2 | Graph analysis | 🟢 LOW | ✅ Guardrails only |
| NLTK | 3.9.1 | NLP utilities | 🟢 LOW | ✅ Preprocessing |
| scikit-learn | 1.6.1 | ML utilities | 🟢 LOW | ✅ Analysis only |
| docling | 2.53.0 | Document parsing | 🟢 LOW | ✅ Knowledge Source |
| psutil | 7.1.3 | System monitoring | 🟢 LOW | ✅ Utilities |
| nvidia-ml-py | 13.580.82 | GPU monitoring | 🟢 LOW | ✅ Utilities |

---

## Dependency Review Schedule

### Quarterly Review (Every 3 Months)

1. **Check for Updates:**
   ```bash
   pip list --outdated
   ```

2. **Review Changelogs:**
   - CrewAI: Check for breaking changes
   - DVC: Monitor CLI interface changes
   - BERTopic: Review API updates

3. **Update This Document:**
   - Change risk levels if frameworks become unmaintained
   - Update isolation status after refactoring
   - Document new dependencies

4. **Measure Coupling:**
   ```bash
   # Count direct framework imports in service layer
   grep -r "from crewai" src/nikhil/amsha/toolkit/*/service/ | wc -l
   grep -r "import dvc" src/nikhil/amsha/toolkit/*/service/ | wc -l
   ```

### Annual Review (Every 12 Months)

1. **Framework Health Assessment:**
   - Is the framework actively maintained?
   - Are there better alternatives?
   - What's the community size?

2. **Migration Feasibility:**
   - Cost/benefit of switching frameworks
   - Effort required for isolation
   - Impact on dependent projects

3. **Refactoring Priority:**
   - High-risk, poorly isolated → Immediate action
   - Medium-risk, partial isolation → Plan refactoring
   - Low-risk, well isolated → Monitor only

---

## Coupling Reduction Roadmap

### Q1 2025
- [ ] Create `IDataVersioner` interface for DVC isolation
- [ ] Implement `DVCVersioner` adapter
- [ ] Document framework upgrade process

### Q2 2025
- [ ] Create CrewAI adapter layer
- [ ] Refactor services to use CrewAI adapters
- [ ] Add LangGraph research spike

### Q3 2025
- [ ] Evaluate Polars vs Pandas
- [ ] Research Git LFS as DVC alternative
- [ ] Measure coupling metrics (baseline)

### Q4 2025
- [ ] Add SQL repository adapter
- [ ] Complete CrewAI isolation
- [ ] Reduce service layer coupling to <5%

---

## Framework Selection Criteria

When evaluating new framework dependencies, use these criteria:

### ✅ Prefer Frameworks That:
- Have active maintenance (commits in last 3 months)
- Have large community (>1000 GitHub stars)
- Follow semantic versioning
- Have clear upgrade paths
- Are abstraction-friendly (not tightly coupled)

### ❌ Avoid Frameworks That:
- Are abandoned (no commits in 6+ months)
- Have frequent breaking changes
- Lock you into specific infrastructure
- Are difficult to abstract/wrap
- Require global state

### 🔍 Evaluation Checklist:
- [ ] Check GitHub activity (commits, issues, PRs)
- [ ] Review changelog for breaking change frequency
- [ ] Test isolation (can we wrap it in an adapter?)
- [ ] Check for alternatives (are there better options?)
- [ ] Assess upgrade difficulty (major version migration path?)

---

## Emergency Response Plan

### If a Critical Framework is Deprecated:

1. **Assess Impact** (Week 1)
   - Identify all usage locations
   - Measure effort for migration
   - Check for viable alternatives

2. **Create Isolation Layer** (Weeks 2-4)
   - If not already isolated, create adapters
   - Define framework-agnostic interfaces
   - Prevent further coupling

3. **Select Alternative** (Week 5)
   - Evaluate replacement frameworks
   - Create proof-of-concept
   - Test with real workloads

4. **Gradual Migration** (Weeks 6-12)
   - Implement new adapter
   - Add feature flag for switching
   - Test in non-production
   - Gradual rollout

5. **Deprecate Old** (Weeks 13-16)
   - Mark old adapter as deprecated
   - Update documentation
   - Remove after 1 minor version

---

## Metrics & Success Criteria

### Target Metrics:

| Metric | Current | Target (2025) |
|--------|---------|---------------|
| Service layer framework imports | Unknown | 0 |
| Framework coupling in domain | Unknown | 0% |
| Isolated frameworks (%) | 40% | 80% |
| Frameworks with adapters | 2 | 4 |
| Critical dependencies | 4 | 2 |

### Success Indicators:

✅ **Good Health:**
- All critical frameworks have adapter layers
- Service layer has no direct framework imports
- Can swap major framework in <1 week
- Dependency updates don't break tests

⚠️ **Needs Attention:**
- Some services directly import frameworks
- Framework upgrade requires code changes
- No clear migration path for critical dependency

🔴 **High Risk:**
- Business logic depends on framework-specific APIs
- Framework is unmaintained
- No alternative framework available
- Migration would require rewrite

---

**Next Review Date:** 2025-12-25  
**Responsible:** Architecture Team  
**Escalation:** If any dependency reaches 🔴 HIGH RISK, escalate immediately
