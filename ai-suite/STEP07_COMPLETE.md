# STEP 07: SEO META OPTIMIZER - COMPLETION DOCUMENTATION

**Status**: ✅ COMPLETE
**Date**: 2025-11-03
**Total Implementation**: ~620 lines of Python code

---

## Executive Summary

Step 07 implements the **SEO Meta Optimizer** - the first AI automation module that analyzes WordPress pages and generates optimized meta titles and descriptions. The module integrates with the governance system (Step 03), prompt library (Step 05), and RAG service (Step 04) to create AI-suggested changes that appear in the review queue dashboard (Step 06).

### Implementation Overview

| Component | File | Lines | Purpose |
|-----------|------|-------|---------|
| SEO Meta Optimizer | `app/services/ai_modules/seo_meta_optimizer.py` | ~270 | Core AI module, prompt execution, change log creation |
| WordPress Service | `app/services/wordpress_service.py` | ~120 | WordPress API integration (mock) |
| SEO Meta Job | `app/jobs/seo_meta_job.py` | ~150 | Scheduled job runner |
| AI Jobs API | `app/api/routes/ai_jobs.py` | ~80 | Manual trigger endpoints |
| **TOTAL** | | **~620** | |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                   SEO META OPTIMIZER FLOW                        │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────────┐
│  Triggers            │
│  • Scheduler         │────┐
│  • Manual API        │    │
│  • Webhook           │    │
└──────────────────────┘    │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                     SEO META JOB (seo_meta_job.py)               │
├─────────────────────────────────────────────────────────────────┤
│  1. Create task log (status: running)                           │
│  2. Fetch WordPress pages (limit: 10)                           │
│  3. For each page:                                              │
│     • Get primary keyword                                        │
│     • Run SEO Meta Optimizer                                     │
│  4. Update task log (status: completed, results)                │
└─────────────────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────────┐
│           SEO META OPTIMIZER (seo_meta_optimizer.py)             │
├─────────────────────────────────────────────────────────────────┤
│  analyze_page(page_id, content, current_meta, keyword):         │
│                                                                  │
│  Step 1: Retrieve Context via RAG                               │
│    • Query: "{keyword} meta tags commercial cleaning"           │
│    • Get competitor examples from Qdrant                        │
│                                                                  │
│  Step 2: Execute Prompt Template                                │
│    • Template: "meta_optimization" v1.0.0                       │
│    • Inputs: page_content, current_meta, keyword, competitors   │
│    • Output: 3 title variants, 3 description variants           │
│    • Validation: Length constraints, JSON schema                │
│    • Auto-retry: Up to 3 attempts                               │
│                                                                  │
│  Step 3: Select Best Variant                                    │
│    • Pick first variant (highest quality)                       │
│                                                                  │
│  Step 4: Create Change Log Entry                                │
│    • Module: "seo_meta_optimizer"                               │
│    • Action: "update_meta_tags"                                 │
│    • Status: "pending" (awaits governance review)               │
│    • Confidence: AI confidence score (0.0-1.0)                  │
└─────────────────────────────────────────────────────────────────┘
           │                                    │
           ▼                                    ▼
┌────────────────────────┐        ┌──────────────────────────────┐
│  RAG SERVICE           │        │  PROMPT LIBRARY              │
│  (Step 04)             │        │  (Step 05)                   │
├────────────────────────┤        ├──────────────────────────────┤
│  • Retrieve context    │        │  • Load template             │
│  • Competitor examples │        │  • Execute with inputs       │
│  • Keyword data        │        │  • Validate output schema    │
└────────────────────────┘        │  • Retry on failure          │
                                  └──────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────────┐
│                 GOVERNANCE API (Step 03)                         │
├─────────────────────────────────────────────────────────────────┤
│  create_change_log():                                           │
│    • Insert into change_log table                               │
│    • Status: "pending"                                          │
│    • Appears in Review Queue Dashboard (Step 06)                │
│                                                                  │
│  User Reviews Change:                                           │
│    • Approve → execute_change() → WordPress update              │
│    • Reject → mark as rejected                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Core Components

### 1. SEO Meta Optimizer Service

**File**: `app/services/ai_modules/seo_meta_optimizer.py` (270 lines)

**Purpose**: Core AI module that analyzes pages and generates meta tag suggestions.

#### Key Methods

**`analyze_page()`**:
```python
async def analyze_page(
    page_id: int,
    page_url: str,
    page_content: str,
    current_title: str,
    current_description: str,
    primary_keyword: str,
    secondary_keywords: List[str] = None
) -> Dict[str, Any]:
    """
    Analyzes a page and generates meta tag optimization suggestions.

    Returns:
        {
            "success": True,
            "page_id": 123,
            "change_id": "meta_123_abc123",
            "optimization": {
                "titles": ["variant1", "variant2", "variant3"],
                "descriptions": ["variant1", "variant2", "variant3"],
                "reasoning": "...",
                "confidence": 0.87
            },
            "execution_time_ms": 2340
        }
    """
```

**Flow**:
1. **Retrieve Context** → Get competitor examples via RAG
2. **Execute Prompt** → Run "meta_optimization" template
3. **Select Best** → Pick first variant
4. **Create Change Log** → Submit for governance review

#### Prompt Template

Auto-created on first run:

```python
PromptTemplate(
    template_name="meta_optimization",
    version="1.0.0",
    system_message=(
        "You are an expert SEO consultant specializing in meta tag optimization "
        "for commercial cleaning services..."
    ),
    user_prompt_template="""
Analyze this page and generate optimized meta tags:

PAGE CONTENT: {page_content}
CURRENT META: Title: {current_title} | Desc: {current_description}
PRIMARY KEYWORD: {primary_keyword}
COMPETITOR EXAMPLES: {competitor_examples}

REQUIREMENTS:
1. Meta Title: 50-60 characters
2. Meta Description: 150-160 characters
3. Generate 3 variants each
4. Include primary keyword naturally
    """,
    output_schema={
        "type": "object",
        "properties": {
            "titles": {"type": "array", "items": {"minLength": 50, "maxLength": 60}},
            "descriptions": {"type": "array", "items": {"minLength": 150, "maxLength": 160}},
            "reasoning": {"type": "string"},
            "confidence": {"type": "number", "minimum": 0, "maximum": 1}
        }
    }
)
```

#### Change Log Entry Created

```python
ChangeLogCreate(
    change_id="meta_123_abc123",
    module="seo_meta_optimizer",
    action="update_meta_tags",
    target_type="wordpress_page",
    target_id=123,
    old_value={
        "title": "Commercial Cleaning Portland",
        "description": "Top-rated commercial cleaning..."
    },
    new_value={
        "title": "Commercial Cleaning Portland | Professional Office Cleaners",
        "description": "Expert commercial cleaning services in Portland, OR. Free quote..."
    },
    reasoning="Optimized for primary keyword placement and CTR improvement",
    ai_confidence=0.87,
    evidence={
        "all_title_variants": ["variant1", "variant2", "variant3"],
        "all_description_variants": ["variant1", "variant2", "variant3"]
    }
)
```

---

### 2. WordPress Service

**File**: `app/services/wordpress_service.py` (120 lines)

**Purpose**: Integration with WordPress REST API for fetching/updating pages.

**Note**: Currently uses **mock data** for testing. Real WordPress API integration pending.

#### Methods

**`get_pages()`**:
```python
async def get_pages(limit: int = 10) -> List[Dict]:
    """Fetch WordPress pages."""
    # Returns mock pages:
    [
        {
            "id": 123,
            "title": "Commercial Cleaning Services Portland",
            "url": "https://example.com/commercial-cleaning",
            "content": "Professional commercial cleaning...",
            "meta_title": "Commercial Cleaning Portland",
            "meta_description": "Top-rated commercial cleaning...",
            "status": "publish"
        }
    ]
```

**`update_page_meta()`**:
```python
async def update_page_meta(
    page_id: int,
    meta_title: str,
    meta_description: str
) -> bool:
    """Update page meta tags in WordPress."""
    # TODO: Implement actual WordPress API call
    # For now, logs and returns True
```

**`get_page_primary_keyword()`**:
```python
async def get_page_primary_keyword(page_id: int) -> str:
    """Get primary keyword from Yoast SEO or RankMath."""
    # TODO: Fetch from WordPress SEO plugin meta
    # Returns mock keywords for now
```

#### Real WordPress Integration (TODO)

```python
# Example implementation:
import httpx

class WordPressService:
    def __init__(self):
        self.base_url = os.getenv("WORDPRESS_API_URL")
        self.api_key = os.getenv("WORDPRESS_API_KEY")

    async def get_pages(self, limit: int = 10):
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/pages",
                headers={"Authorization": f"Bearer {self.api_key}"},
                params={"per_page": limit, "orderby": "modified"}
            )
            return response.json()

    async def update_page_meta(self, page_id: int, meta_title: str, meta_description: str):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/pages/{page_id}",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "yoast_head_json": {
                        "title": meta_title,
                        "description": meta_description
                    }
                }
            )
            return response.status_code == 200
```

---

### 3. SEO Meta Job

**File**: `app/jobs/seo_meta_job.py` (150 lines)

**Purpose**: Scheduled job that runs the SEO meta optimizer on multiple pages.

#### Job Flow

```python
async def run(limit: int = 10, triggered_by: str = "scheduler"):
    """
    1. Create task log (status: running)
    2. Fetch {limit} pages from WordPress
    3. For each page:
       • Get primary keyword
       • Run seo_meta_optimizer.analyze_page()
       • Collect results
    4. Update task log (status: completed, results)
    """
```

#### Task Log Entry

**Created at job start**:
```python
TaskLogCreate(
    job_name="seo_meta_optimizer",
    job_id="seo_meta_optimizer_20251103_100000",
    triggered_by="scheduler",  # or "manual_user_1"
    inputs={"limit": 10}
)
```

**Updated at job completion**:
```python
TaskLogUpdate(
    status="completed",
    outputs={
        "results": [
            {"page_id": 123, "change_id": "meta_123_abc", "confidence": 0.87},
            {"page_id": 124, "change_id": "meta_124_def", "confidence": 0.92}
        ]
    },
    records_processed=10,
    changes_generated=8,  # 8 successful, 2 errors
    errors_count=2
)
```

#### Scheduling (TODO)

To run on a schedule, use APScheduler or similar:

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.jobs.seo_meta_job import run_seo_meta_optimization

scheduler = AsyncIOScheduler()

# Run daily at 3 AM
scheduler.add_job(
    run_seo_meta_optimization,
    'cron',
    hour=3,
    minute=0,
    args=[10, "scheduler"]
)

scheduler.start()
```

---

### 4. AI Jobs API

**File**: `app/api/routes/ai_jobs.py` (80 lines)

**Purpose**: REST API endpoints for manually triggering AI jobs.

#### Endpoints

**`POST /ai-jobs/seo-meta-optimizer`**:

Manually trigger the SEO meta optimization job.

**Request**:
```json
{
  "limit": 10
}
```

**Response**:
```json
{
  "job_id": "seo_meta_optimizer_20251103_100000",
  "status": "completed",
  "pages_processed": 10,
  "changes_generated": 8,
  "errors_count": 2
}
```

**Authorization**: Requires `ADMIN` role.

**`GET /ai-jobs/seo-meta-optimizer/status`**:

Get module status and recent job history.

**Response**:
```json
{
  "module": "seo_meta_optimizer",
  "enabled": true,
  "operating_mode": "review",
  "recent_jobs": []
}
```

---

## Integration with Existing System

### Step 03: Governance API

**Change Logs Created**:
- Module: `seo_meta_optimizer`
- Action: `update_meta_tags`
- Status: `pending` (awaits review)
- Stored in `change_log` table

**Task Logs Created**:
- Job Name: `seo_meta_optimizer`
- Status: `running` → `completed` or `failed`
- Stored in `task_log` table

### Step 04: RAG Service

**Context Retrieval**:
- Query: `"{primary_keyword} meta tags commercial cleaning"`
- Collection: `pages`
- Retrieves: Competitor meta tag examples

**Used For**:
- Providing context to AI prompt
- Examples of high-performing meta tags

### Step 05: Prompt Library

**Template Used**:
- Name: `meta_optimization`
- Version: `1.0.0`
- Auto-created on first run

**Features Used**:
- JSON Schema validation
- Auto-retry (up to 3 attempts)
- Structured output

### Step 06: Dashboard UI

**Appears in Review Queue**:
- Changes appear in `/governance` dashboard
- Reviewers can approve/reject
- Confidence scores displayed
- Details modal shows old/new values

---

## End-to-End Workflow

### 1. Job Execution

```bash
# Manual trigger via API
curl -X POST http://localhost:8001/api/v1/ai-jobs/seo-meta-optimizer \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"limit": 5}'
```

**What Happens**:
1. Job fetches 5 WordPress pages
2. For each page:
   - Gets primary keyword (e.g., "commercial cleaning Portland")
   - Retrieves competitor examples via RAG
   - Executes "meta_optimization" prompt
   - AI generates 3 title + 3 description variants
   - Validates output (length, schema)
   - Selects best variant
   - Creates change log entry (status: pending)
3. Task log updated with results

### 2. Governance Review

**Review Queue Dashboard** (`/governance`):
```
┌──────────────────────────────────────────────────────────────┐
│ Review Queue Widget                            23 pending     │
├──────────────────────────────────────────────────────────────┤
│ seo_meta_optimizer → update_meta_tags → wordpress_page #123  │
│ Confidence: 87%  |  Age: 2h ago                              │
│                                                               │
│ Old: "Commercial Cleaning Portland"                          │
│ New: "Commercial Cleaning Portland | Expert Office Cleaners" │
│                                                               │
│ [✗ Reject]  [✓ Approve]                                      │
└──────────────────────────────────────────────────────────────┘
```

**Actions**:
- **Approve** → Change status = "approved"
- **Execute** → Calls `wordpress_service.update_page_meta()`
- **Reject** → Change status = "rejected"

### 3. Execution

When change is **approved and executed**:

```python
# governance.py: execute_change_log()
change = get_change_log(change_id)

if change.module == "seo_meta_optimizer":
    await wordpress_service.update_page_meta(
        page_id=change.target_id,
        meta_title=change.new_value["title"],
        meta_description=change.new_value["description"]
    )

change.status = "executed"
change.executed_at = datetime.utcnow()
```

**Result**: WordPress page meta tags updated!

---

## Testing

### Manual Testing Steps

**1. Trigger Job**:
```bash
curl -X POST http://localhost:8001/api/v1/ai-jobs/seo-meta-optimizer \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"limit": 2}'
```

**Expected Result**:
- 2 change log entries created
- Status: "pending"
- Confidence scores: 0.7-0.95

**2. View in Dashboard**:
- Navigate to `/governance`
- See 2 pending changes in Review Queue Widget
- Click "View All Changes"
- Click row to see details modal

**3. Approve Change**:
- Click "Approve" button
- Enter reason (optional)
- Change status → "approved"

**4. Execute Change**:
- Click "Execute" button
- Change status → "executed"
- WordPress page updated (mock for now)

### Unit Tests (TODO)

```python
# tests/test_seo_meta_optimizer.py

async def test_analyze_page():
    """Test page analysis generates valid output."""
    result = await seo_meta_optimizer.analyze_page(
        page_id=123,
        page_url="https://example.com/test",
        page_content="Commercial cleaning services...",
        current_title="Test Page",
        current_description="Test description",
        primary_keyword="commercial cleaning"
    )

    assert result["success"] is True
    assert "change_id" in result
    assert result["optimization"]["confidence"] > 0.0

async def test_prompt_template_creation():
    """Test prompt template is auto-created."""
    template = prompt_library_service.get_template(
        template_name="meta_optimization",
        version="1.0.0"
    )

    assert template is not None
    assert template.output_type == OutputType.META_VARIANTS

async def test_change_log_creation():
    """Test change log is created correctly."""
    # ... test change log creation
```

---

## Configuration

### Environment Variables

```bash
# .env

# WordPress Integration
WORDPRESS_API_URL=https://your-site.com/wp-json/wp/v2
WORDPRESS_API_KEY=your_api_key_here

# OpenAI (for prompt execution)
OPENAI_API_KEY=sk-...

# Qdrant (for RAG context retrieval)
QDRANT_HOST=localhost
QDRANT_PORT=6333
```

### Module Configuration (Database)

```sql
-- automation_module_config table (Step 03)
INSERT INTO automation_module_config (module, operating_mode, enabled, confidence_threshold_review)
VALUES ('seo_meta_optimizer', 'review', true, 0.70);
```

**Operating Modes**:
- **review**: All changes go to review queue (current)
- **auto**: High-confidence changes (>threshold) execute automatically

---

## Performance

### Metrics (Estimated)

| Metric | Value |
|--------|-------|
| Page analysis time | ~2-3 seconds |
| Prompt execution | ~2 seconds |
| RAG context retrieval | ~100ms |
| Change log creation | ~50ms |
| **Total per page** | **~2.5 seconds** |

**10 pages**: ~25 seconds total
**100 pages**: ~4 minutes total

### Optimization Opportunities

1. **Parallel Processing**: Analyze multiple pages concurrently
2. **Caching**: Cache competitor examples for 1 hour
3. **Batch Prompts**: Send multiple pages in single prompt
4. **Rate Limiting**: Respect OpenAI rate limits

---

## Known Limitations

1. **WordPress Integration**: Currently mock data only
   - **TODO**: Implement real WordPress REST API calls
   - **TODO**: Handle authentication (API keys, OAuth)
   - **TODO**: Fetch Yoast/RankMath keyword data

2. **Keyword Extraction**: Manual input only
   - **TODO**: Auto-extract from page content
   - **TODO**: Use NLP to identify semantic keywords

3. **No A/B Testing**: Best variant selection is naive
   - **TODO**: Track CTR performance of executed changes
   - **TODO**: Learn which variants perform best

4. **Limited Context**: RAG retrieves only 3 competitor examples
   - **TODO**: Retrieve more diverse examples
   - **TODO**: Include SERP data, keyword rankings

5. **No Scheduling**: Manual trigger only
   - **TODO**: Add APScheduler for daily runs
   - **TODO**: Configurable schedule per module

---

## Next Steps: Steps 08-16

Now that Step 07 is complete, the foundation is in place for additional AI modules:

- **Step 08**: FAQ Generator
- **Step 09**: Internal Link Builder
- **Step 10**: Content Gap Analyzer
- **Step 11**: SERP Position Tracker
- **Step 12**: Competitor Monitor
- **Step 13**: Keyword Cluster Analyzer
- **Step 14**: Backlink Opportunity Finder
- **Step 15**: Health Monitor
- **Step 16**: Auto-Pilot Mode

All future modules will follow the same pattern:
1. Create AI module service (`app/services/ai_modules/{module}.py`)
2. Create prompt template (auto-created or seeded)
3. Create job runner (`app/jobs/{module}_job.py`)
4. Add API endpoint (`app/api/routes/ai_jobs.py`)
5. Integrate with governance (change logs, task logs)

---

## Conclusion

✅ **Step 07 Complete**: SEO Meta Optimizer - First AI Module

**Delivered**:
- 620 lines of Python code
- 4 new files (optimizer, WordPress service, job, API)
- Full integration with Steps 03-06
- Auto-created prompt template
- Change log generation for governance review
- Manual trigger API endpoint

**Key Achievements**:
- ✅ First end-to-end AI automation workflow
- ✅ Generates AI suggestions that appear in review queue
- ✅ Integrates RAG (Step 04) for context retrieval
- ✅ Uses Prompt Library (Step 05) with validation
- ✅ Creates governance change logs (Step 03)
- ✅ Visible in Dashboard UI (Step 06)

**Foundation Established**: All future AI modules (Steps 08-16) will follow this same pattern!

---

**Files Created**:
- ✅ `app/services/ai_modules/__init__.py` (package)
- ✅ `app/services/ai_modules/seo_meta_optimizer.py` (270 lines)
- ✅ `app/services/wordpress_service.py` (120 lines)
- ✅ `app/jobs/seo_meta_job.py` (150 lines)
- ✅ `app/api/routes/ai_jobs.py` (80 lines)
- ✅ `ai-suite/STEP07_COMPLETE.md` (this document)

**Integration Points**:
- ✅ Step 03: Governance API (change logs, task logs)
- ✅ Step 04: RAG Service (context retrieval)
- ✅ Step 05: Prompt Library (template execution)
- ✅ Step 06: Dashboard UI (review queue)

**Next Step**: Step 08 - FAQ Generator
