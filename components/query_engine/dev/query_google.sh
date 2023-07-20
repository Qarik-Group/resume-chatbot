#!/usr/bin/env bash

QUERY='{"query": "Give me a short answer. How many total years of experience across all his jobs and positions does Steven Kim have?", "page_size": "5", "offset": 0, "contentSearchSpec": {"summarySpec": {"summaryResultCount": 1}}}'

curl -X POST -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "Content-Type: application/json" \
  "https://discoveryengine.googleapis.com/v1alpha/projects/467250963576/locations/global/collections/default_collection/dataStores/skills-search_1688081193007/servingConfigs/default_search:search" \
  -d "${QUERY}"
