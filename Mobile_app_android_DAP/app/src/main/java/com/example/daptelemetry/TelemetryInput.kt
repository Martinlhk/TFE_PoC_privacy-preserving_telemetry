package com.example.daptelemetry

data class BraceletSyncInput(
    val syncCount: Int,
)

data class UsageHoursInput(
    val usageHours: Set<Int>,
)

data class SubmissionSummary(
    val metricName: String,
    val reportCount: Int,
)
