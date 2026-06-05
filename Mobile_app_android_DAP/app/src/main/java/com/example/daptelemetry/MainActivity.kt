package com.example.daptelemetry

import android.os.Bundle
import android.os.SystemClock
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ExperimentalLayoutApi
import androidx.compose.foundation.layout.FlowRow
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.ElevatedFilterChip
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.util.Locale

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            DapTelemetryTheme {
                TelemetryScreen()
            }
        }
    }
}

@Composable
private fun DapTelemetryTheme(content: @Composable () -> Unit) {
    MaterialTheme(
        colorScheme = MaterialTheme.colorScheme.copy(
            primary = Color(0xFF176D6B),
            secondary = Color(0xFF6F5E00),
            background = Color(0xFFF7F8FA),
            surface = Color(0xFFF7F8FA),
        ),
        content = content,
    )
}

@OptIn(ExperimentalLayoutApi::class)
@Composable
private fun TelemetryScreen() {
    val context = LocalContext.current
    val scope = rememberCoroutineScope()
    var braceletSyncCount by remember { mutableStateOf("") }
    var selectedHours by remember { mutableStateOf<Set<Int>>(emptySet()) }
    var isSubmitting by remember { mutableStateOf(false) }
    var statusText by remember { mutableStateOf<String?>(null) }

    fun submitMetric(
        inProgressText: String,
        submit: suspend () -> SubmissionSummary,
    ) {
        isSubmitting = true
        statusText = inProgressText
        val startedAtMs = SystemClock.elapsedRealtime()
        scope.launch {
            val result = runCatching {
                withContext(Dispatchers.IO) {
                    submit()
                }
            }
            val elapsedMs = SystemClock.elapsedRealtime() - startedAtMs
            isSubmitting = false
            statusText = result.fold(
                onSuccess = {
                    val averageMs = elapsedMs / it.reportCount.coerceAtLeast(1)
                    "Submitted ${it.metricName}: ${it.reportCount} report(s) in " +
                        "${formatDuration(elapsedMs)} (${formatDuration(averageMs)} avg/report)."
                },
                onFailure = {
                    "Submission failed after ${formatDuration(elapsedMs)}: " +
                        (it.message ?: it::class.java.simpleName)
                },
            )
        }
    }

    Surface(modifier = Modifier.fillMaxSize()) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .verticalScroll(rememberScrollState())
                .padding(20.dp),
            verticalArrangement = Arrangement.spacedBy(18.dp),
        ) {
            Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                Text(
                    text = "DAP telemetry",
                    style = MaterialTheme.typography.headlineMedium,
                )
                Text(
                    text = "Submit and time each statistic separately",
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }

            Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                Text("Bracelet sync count", style = MaterialTheme.typography.titleMedium)
                NumberField(
                    value = braceletSyncCount,
                    onValueChange = { braceletSyncCount = it },
                    label = "Sync count",
                    suffix = "syncs",
                )
                Button(
                    modifier = Modifier.fillMaxWidth(),
                    enabled = !isSubmitting,
                    onClick = {
                        val input = parseBraceletSyncInput(braceletSyncCount)
                        if (input == null) {
                            statusText = "Enter bracelet sync count between 0 and ${sumMeasurementMax()}."
                            return@Button
                        }

                        submitMetric("Submitting bracelet sync...") {
                            DivviUpTelemetrySender(context).submitBraceletSync(input)
                        }
                    },
                ) {
                    Text(if (isSubmitting) "Submitting..." else "Submit bracelet sync")
                }
            }

            Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                Text("Usage time buckets", style = MaterialTheme.typography.titleMedium)
                FlowRow(
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                    verticalArrangement = Arrangement.spacedBy(8.dp),
                ) {
                    (0..23).forEach { hour ->
                        ElevatedFilterChip(
                            selected = hour in selectedHours,
                            onClick = {
                                selectedHours = if (hour in selectedHours) {
                                    selectedHours - hour
                                } else {
                                    selectedHours + hour
                                }
                            },
                            label = { Text(hour.toString().padStart(2, '0')) },
                        )
                    }
                }
                Button(
                    modifier = Modifier.fillMaxWidth(),
                    enabled = !isSubmitting,
                    onClick = {
                        val input = parseUsageHoursInput(selectedHours)
                        if (input == null) {
                            statusText = "Select at least one usage hour."
                            return@Button
                        }

                        submitMetric("Submitting usage hours...") {
                            DivviUpTelemetrySender(context).submitUsageHours(input)
                        }
                    },
                ) {
                    Text(if (isSubmitting) "Submitting..." else "Submit usage hours")
                }
            }

            statusText?.let {
                Text(
                    text = it,
                    style = MaterialTheme.typography.bodyMedium,
                    color = if (it.startsWith("Submitted")) {
                        MaterialTheme.colorScheme.primary
                    } else {
                        MaterialTheme.colorScheme.onSurface
                    },
                )
            }

            Spacer(modifier = Modifier.height(8.dp))
        }
    }
}

@Composable
private fun NumberField(
    value: String,
    onValueChange: (String) -> Unit,
    label: String,
    suffix: String,
) {
    OutlinedTextField(
        modifier = Modifier.fillMaxWidth(),
        value = value,
        onValueChange = { next ->
            if (next.all(Char::isDigit)) {
                onValueChange(next)
            }
        },
        label = { Text(label) },
        suffix = { Text(suffix) },
        singleLine = true,
        keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
    )
}

private fun parseBraceletSyncInput(syncCount: String): BraceletSyncInput? {
    val parsed = syncCount.toIntOrNull() ?: return null
    if (parsed.toLong() !in 0L..sumMeasurementMax()) {
        return null
    }
    return BraceletSyncInput(syncCount = parsed)
}

private fun parseUsageHoursInput(selectedHours: Set<Int>): UsageHoursInput? =
    if (selectedHours.isEmpty()) {
        null
    } else {
        UsageHoursInput(usageHours = selectedHours)
    }

private fun sumMeasurementMax(): Long = (1L shl TelemetryTaskConfig.SUM_BITS.toInt()) - 1L

private fun formatDuration(durationMs: Long): String =
    if (durationMs < 1_000L) {
        "$durationMs ms"
    } else {
        String.format(Locale.US, "%.2f s", durationMs / 1_000.0)
    }
