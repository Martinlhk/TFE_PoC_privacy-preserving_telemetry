package com.example.daptelemetry

import android.content.Context
import org.divviup.android.Client
import org.divviup.android.TaskId
import java.net.URI

class DivviUpTelemetrySender(context: Context) {
    private val appContext = context.applicationContext

    fun submitBraceletSync(input: BraceletSyncInput): SubmissionSummary {
        TelemetryTaskConfig.validate()

        val leaderEndpoint = URI(TelemetryTaskConfig.LEADER_ENDPOINT)
        val helperEndpoint = URI(TelemetryTaskConfig.HELPER_ENDPOINT)

        prio3SumClient(
            leaderEndpoint,
            helperEndpoint,
            TelemetryTaskConfig.BRACELET_SYNC_COUNT_TASK_ID,
            TelemetryTaskConfig.SUM_BITS,
        ).sendMeasurement(input.syncCount.toLong())

        return SubmissionSummary(metricName = "bracelet sync", reportCount = 1)
    }

    fun submitUsageHours(input: UsageHoursInput): SubmissionSummary {
        TelemetryTaskConfig.validate()

        val leaderEndpoint = URI(TelemetryTaskConfig.LEADER_ENDPOINT)
        val helperEndpoint = URI(TelemetryTaskConfig.HELPER_ENDPOINT)

        val hourHistogramClient = Client.createPrio3Histogram(
            appContext,
            leaderEndpoint,
            helperEndpoint,
            TaskId.parse(TelemetryTaskConfig.USAGE_HOUR_HISTOGRAM_TASK_ID),
            TelemetryTaskConfig.TIME_PRECISION_SECONDS,
            TelemetryTaskConfig.HOUR_HISTOGRAM_LENGTH,
            TelemetryTaskConfig.HOUR_HISTOGRAM_CHUNK_LENGTH,
        )
        input.usageHours.sorted().forEach { hour ->
            hourHistogramClient.sendMeasurement(hour.toLong())
        }

        return SubmissionSummary(metricName = "usage hours", reportCount = input.usageHours.size)
    }

    private fun prio3SumClient(
        leaderEndpoint: URI,
        helperEndpoint: URI,
        taskId: String,
        bits: Long,
    ): Client<Long> = Client.createPrio3Sum(
        appContext,
        leaderEndpoint,
        helperEndpoint,
        TaskId.parse(taskId),
        TelemetryTaskConfig.TIME_PRECISION_SECONDS,
        bits,
    )
}
