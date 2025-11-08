#!/bin/bash
# Create all missing AI Suite pages

PAGES_DIR="/home/saas/Saas-CRM---Claude/crm/src/pages"

# Array of pages to create (name:route:description)
declare -a pages=(
  "SnippetOptimizerPage:/ai/snippet-optimizer:Featured Snippet Optimizer"
  "FAQPAAGeneratorPage:/ai/faq-paa:FAQ & PAA Generator"
  "MetaCTRTestsPage:/ai/meta-ctr:Meta Rewrite & CTR Tests"
  "ContentClusterPlannerPage:/ai/clusters:Content Cluster Planner"
  "InternalLinkingAssistantPage:/ai/internal-linking:Internal Linking Assistant"
  "BacklinkGapFinderPage:/ai/backlink-gap:Backlink Gap Finder"
  "KeywordFunnelPage:/ai/keywords:Keyword Funnel & Prioritize"
  "AnomalyExplainerPage:/ai/anomalies:Rank/Traffic Anomaly Explainer"
  "SchemaGeneratorPage:/ai/schema-generator:Schema (JSON-LD) Generator"
)

for page_info in "${pages[@]}"; do
  IFS=':' read -r name route title <<< "$page_info"
  echo "Creating $name..."
done
