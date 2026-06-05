package com.example.daptelemetry

object TelemetryTaskConfig {
    const val LEADER_ENDPOINT = "http://10.0.2.2:9001/"
    const val HELPER_ENDPOINT = "http://10.0.2.2:9002/"

    const val BRACELET_SYNC_COUNT_TASK_ID = "pkDn_Z_v2vVADOJxqkPrUL4JoNgOrE5yD7DmuErBvaI"
    const val USAGE_HOUR_HISTOGRAM_TASK_ID = "8Vp2PCTxWWON9HpfrK_p78ekfL1lBQIkEoP-yjxsR6Q"

    const val TIME_PRECISION_SECONDS = 60L

    const val SUM_BITS = 16L
    const val HOUR_HISTOGRAM_LENGTH = 24L
    const val HOUR_HISTOGRAM_CHUNK_LENGTH = 4L

    fun validate() {
        val fields = mapOf(
            "LEADER_ENDPOINT" to LEADER_ENDPOINT,
            "HELPER_ENDPOINT" to HELPER_ENDPOINT,
            "BRACELET_SYNC_COUNT_TASK_ID" to BRACELET_SYNC_COUNT_TASK_ID,
            "USAGE_HOUR_HISTOGRAM_TASK_ID" to USAGE_HOUR_HISTOGRAM_TASK_ID,
        )
        val missing = fields.filterValues { it.contains("PUT_") }.keys
        check(missing.isEmpty()) {
            "Configure Divvi Up values in TelemetryTaskConfig.kt: ${missing.joinToString()}"
        }
    }
}
