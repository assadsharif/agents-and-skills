# Testing Validation Agent

Autonomous agent for comprehensive project testing and validation. Auto-detects project type and runs appropriate test workflows.

## Purpose

Executes testing workflows autonomously to verify build quality, test suite health, API endpoint correctness, and deployment readiness. Supports Python/FastAPI backends, Node.js/Docusaurus frontends, and hybrid deployments.

## Capabilities

### Python/FastAPI Backend Testing
- Test suite execution (`pytest tests/`)
- Import and syntax validation (`py_compile`)
- API endpoint health checks (health, docs, openapi.json)
- Dependency conflict detection
- Response schema validation

### Frontend Testing (Docusaurus/Next.js)
- Build verification (`npm run build`)
- Content validation (responsive issues, broken links)
- Static accessibility checks
- Lighthouse performance audits (if CLI available)

### Deployment Verification
- Render.com API health checks
- GitHub Pages content validation
- Vercel deployment status
- CORS cross-origin testing
- HTTPS verification

## Quick Usage

### Backend Test Suite
```
"Run full test suite for the Stock Signal API"
"Validate the Python backend"
```

**Agent will:**
- Run `pytest tests/ -q --tb=short`
- Validate all modules import cleanly
- Check key API endpoints
- Create testing report

### Deployment Smoke Test
```
"Verify the deployed API at https://backend-api-project-1-d2vu.onrender.com"
"Check if the dashboard works on GitHub Pages"
```

**Agent will:**
- Check health endpoint
- Verify docs accessible
- Test CORS headers
- Report pass/fail status

### Hybrid Validation
```
"Validate both the API on Render and dashboard on GitHub Pages"
```

**Agent will:**
- Test backend API health and endpoints
- Test frontend page loads
- Verify cross-origin API calls work
- Generate comprehensive report

## Output

Agent creates `testing-results.md` with:
- Overall pass/fail status
- Test suite results (pass/fail counts)
- Build/import verification
- API endpoint response codes
- Deployment status
- Actionable recommendations

## Safety

**Will Do:**
- Read files and configurations
- Run test suites (pytest, npm test)
- Execute build commands
- Run HTTP checks (curl)
- Create testing reports

**Will NOT Do:**
- Modify source code
- Delete files
- Commit changes (without approval)
- Install/uninstall packages (without approval)
- Start long-running servers (without approval)

## Requirements

**Minimum:**
- Bash (for commands)
- pytest (Python testing)
- curl (HTTP checks)

**Optional:**
- Node.js/npm (frontend builds)
- Lighthouse CLI (performance audits)
- jq (JSON parsing)

## Version

**Agent Version**: 2.0.0
**Compatible With**:
- Python 3.11+ / FastAPI 0.100+
- pytest 7.x+
- Node.js 18.x, 20.x (frontend)
- Docusaurus 3.x (frontend)
- Render.com, GitHub Pages, Vercel

---

**Status**: Production Ready
**Last Updated**: 2026-02-15
