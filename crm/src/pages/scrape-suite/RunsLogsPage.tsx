/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * Runs & Logs Page
 * View job history, trigger manual jobs, and monitor live progress
 */

import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import scrapeApi, { JobStatus } from '@/lib/scrape-api';
import { useAllJobsStream } from '@/hooks/useScrapeJobStream';
import JobStartDrawer from '@/components/scrape/JobStartDrawer';
import RunRow from '@/components/scrape/RunRow';
import RunDetailsPanel from '@/components/scrape/RunDetailsPanel';

export default function RunsLogsPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [jobs, setJobs] = useState<JobStatus[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  const [selectedJob, setSelectedJob] = useState<JobStatus | null>(null);
  const [page, setPage] = useState(1);
  const [totalJobs, setTotalJobs] = useState(0);

  // Real-time job updates
  const { jobs: liveJobs, isConnected } = useAllJobsStream('scrape_suite', true);

  // Load job history
  const loadJobs = async () => {
    try {
      setLoading(true);
      setError(null);

      // Note: The API doesn't have a dedicated jobs list endpoint yet
      // For now, we'll use the dashboard to show recent activity
      // In a full implementation, you'd call something like:
      // const response = await scrapeApi.getJobHistory({ page, page_size: 20 });

      // Placeholder for now
      setJobs([]);
      setTotalJobs(0);

    } catch (err: any) {
      console.error('Failed to load jobs:', err);
      setError(err.message || 'Failed to load job history');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadJobs();
  }, [page]);

  // Handle deep-link to specific job
  useEffect(() => {
    const jobId = searchParams.get('job_id');
    if (jobId) {
      // Load and select the job
      scrapeApi.getJobStatus(jobId)
        .then(job => setSelectedJob(job))
        .catch(err => console.error('Failed to load job:', err));
    }
  }, [searchParams]);

  // Handle job completion to refresh list
  const handleJobComplete = () => {
    loadJobs();
  };

  return (
    <div className="container mx-auto px-4 py-6 max-w-7xl">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            Runs & Logs
          </h1>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
            Monitor scrape jobs and view execution history
          </p>
        </div>

        <div className="flex items-center gap-3">
          {/* Live indicator */}
          {isConnected && (
            <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
              <span>Live</span>
            </div>
          )}

          {/* Start Job button */}
          <button
            onClick={() => setIsDrawerOpen(true)}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors"
          >
            Start Job
          </button>
        </div>
      </div>

      {/* Live Jobs Section */}
      {Object.keys(liveJobs).length > 0 && (
        <div className="mb-6">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
            Active Jobs ({Object.keys(liveJobs).length})
          </h2>
          <div className="space-y-2">
            {Object.entries(liveJobs).map(([jobId, job]) => (
              <RunRow
                key={jobId}
                job={{
                  job_id: jobId,
                  task_id: jobId,
                  status: job.status || 'running',
                  task_name: job.task_name || 'Job',
                  queued_at: null,
                  started_at: job.started_at || null,
                  completed_at: null,
                  duration_seconds: null,
                  items_processed: job.items_processed || 0,
                  items_succeeded: job.items_succeeded || 0,
                  items_failed: job.items_failed || 0,
                  error_message: null,
                  output_summary: null,
                }}
                isLive={true}
                onClick={() => {
                  scrapeApi.getJobStatus(jobId)
                    .then(fullJob => setSelectedJob(fullJob))
                    .catch(err => console.error(err));
                }}
              />
            ))}
          </div>
        </div>
      )}

      {/* Job History */}
      <div>
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
          Job History
        </h2>

        {loading ? (
          <div className="flex justify-center items-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
          </div>
        ) : error ? (
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md p-4">
            <p className="text-sm text-red-800 dark:text-red-400">{error}</p>
          </div>
        ) : jobs.length === 0 ? (
          <div className="bg-gray-50 dark:bg-gray-800 rounded-md p-8 text-center">
            <p className="text-gray-600 dark:text-gray-400">
              No jobs found. Start your first job to see it here!
            </p>
          </div>
        ) : (
          <>
            <div className="space-y-2">
              {jobs.map(job => (
                <RunRow
                  key={job.job_id}
                  job={job}
                  isLive={false}
                  onClick={() => setSelectedJob(job)}
                />
              ))}
            </div>

            {/* Pagination */}
            {totalJobs > 20 && (
              <div className="mt-4 flex justify-center items-center gap-2">
                <button
                  onClick={() => setPage(p => Math.max(1, p - 1))}
                  disabled={page === 1}
                  className="px-3 py-1 text-sm border border-gray-300 dark:border-gray-700 rounded-md hover:bg-gray-50 dark:hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Previous
                </button>
                <span className="text-sm text-gray-600 dark:text-gray-400">
                  Page {page} of {Math.ceil(totalJobs / 20)}
                </span>
                <button
                  onClick={() => setPage(p => p + 1)}
                  disabled={page >= Math.ceil(totalJobs / 20)}
                  className="px-3 py-1 text-sm border border-gray-300 dark:border-gray-700 rounded-md hover:bg-gray-50 dark:hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Next
                </button>
              </div>
            )}
          </>
        )}
      </div>

      {/* Job Start Drawer */}
      <JobStartDrawer
        isOpen={isDrawerOpen}
        onClose={() => setIsDrawerOpen(false)}
        onJobStarted={handleJobComplete}
      />

      {/* Job Details Panel */}
      {selectedJob && (
        <RunDetailsPanel
          job={selectedJob}
          onClose={() => setSelectedJob(null)}
        />
      )}
    </div>
  );
}
