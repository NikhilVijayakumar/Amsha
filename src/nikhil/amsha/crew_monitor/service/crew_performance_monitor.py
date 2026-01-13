import time
import psutil
from typing import Any, Dict, Optional
from amsha.common.logger import get_logger

try:
    import pynvml
    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False

class CrewPerformanceMonitor:
    def __init__(self, model_name: Optional[str] = None):
        self.logger = get_logger("crew_monitor.performance")
        self.model_name = model_name
        self.total_tokens = 0
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.start_time = 0
        self.end_time = 0
        self.start_cpu_percent = 0
        self.end_cpu_percent = 0
        self.start_memory_usage = 0
        self.end_memory_usage = 0
        
        # GPU stats
        self.gpu_stats = {}

    def start_monitoring(self):
        """Starts the monitoring of time and resources."""
        self.start_time = time.time()
        # Get initial CPU and memory usage
        self.start_cpu_percent = psutil.cpu_percent(interval=None) 
        self.start_memory_usage = psutil.virtual_memory().used
        
        if GPU_AVAILABLE:
            try:
                pynvml.nvmlInit()
                device_count = pynvml.nvmlDeviceGetCount()
                for i in range(device_count):
                    handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                    mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                    self.gpu_stats[f"gpu_{i}_start_mem"] = mem_info.used
            except Exception as e:
                self.logger.warning("GPU monitoring failed to start", extra={
                    "error": str(e)
                })

    def stop_monitoring(self):
        """Stops the monitoring of time and resources."""
        self.end_time = time.time()
        self.end_cpu_percent = psutil.cpu_percent(interval=None)
        self.end_memory_usage = psutil.virtual_memory().used
        
        if GPU_AVAILABLE:
            try:
                device_count = pynvml.nvmlDeviceGetCount()
                for i in range(device_count):
                    handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                    mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                    utilization = pynvml.nvmlDeviceGetUtilizationRates(handle)
                    self.gpu_stats[f"gpu_{i}_end_mem"] = mem_info.used
                    self.gpu_stats[f"gpu_{i}_utilization"] = utilization.gpu
                pynvml.nvmlShutdown()
            except Exception as e:
                self.logger.warning("GPU monitoring failed to stop", extra={
                    "error": str(e)
                })

    def log_usage(self, result: Any):
        """
        Parses the CrewOutput result to extract token usage.
        Expected result.token_usage to be a dictionary or object with token counts.
        """
        if hasattr(result, 'token_usage'):
            usage = result.token_usage
            
            # CrewAI 1.8.0: token_usage might be None
            if usage is None:
                self.logger.debug("Token usage is None in CrewAI 1.8.0 result")
                return
            
            # Handle if usage is a dict or object
            if isinstance(usage, dict):
                self.total_tokens = usage.get('total_tokens', 0)
                self.prompt_tokens = usage.get('prompt_tokens', 0)
                self.completion_tokens = usage.get('completion_tokens', 0)
            else:
                # Assuming object with attributes
                self.total_tokens = getattr(usage, 'total_tokens', 0)
                self.prompt_tokens = getattr(usage, 'prompt_tokens', 0)
                self.completion_tokens = getattr(usage, 'completion_tokens', 0)
        else:
            self.logger.warning("Token usage not found in result")

    def get_metrics(self) -> Dict[str, Any]:
        """
        Returns a dictionary containing calculated metrics.
        Useful for logging to external systems (MLflow, DBs, JSON).
        """
        duration = self.end_time - self.start_time
        memory_diff_mb = (self.end_memory_usage - self.start_memory_usage) / (1024 * 1024)

        metrics = {
            "general": {
                "model_name": self.model_name,
                "total_tokens": self.total_tokens,
                "prompt_tokens": self.prompt_tokens,
                "completion_tokens": self.completion_tokens,
                "duration_seconds": round(duration, 4),
                "cpu_usage_end_percent": self.end_cpu_percent,
                "memory_usage_change_mb": round(memory_diff_mb, 2),
                "memory_usage_start_bytes": self.start_memory_usage,
                "memory_usage_end_bytes": self.end_memory_usage,
            },
            "gpu": {}
        }

        if GPU_AVAILABLE and self.gpu_stats:
            # Identify how many GPUs were tracked by looking at utilization keys
            gpu_indices = [k.split('_')[1] for k in self.gpu_stats.keys() if 'utilization' in k]

            for i in gpu_indices:
                start_mem = self.gpu_stats.get(f"gpu_{i}_start_mem", 0) / (1024 * 1024)
                end_mem = self.gpu_stats.get(f"gpu_{i}_end_mem", 0) / (1024 * 1024)
                util = self.gpu_stats.get(f"gpu_{i}_utilization", 0)

                metrics["gpu"][f"gpu_{i}"] = {
                    "utilization_percent": util,
                    "memory_change_mb": round(end_mem - start_mem, 2),
                    "memory_start_mb": round(start_mem, 2),
                    "memory_end_mb": round(end_mem, 2)
                }

        return metrics

    def get_summary(self) -> str:
        """Returns a formatted summary string of the monitoring data."""
        metrics = self.get_metrics()
        gen = metrics["general"]
        gpu_data = metrics["gpu"]

        gpu_summary = ""
        if gpu_data:
            gpu_summary = "\nGPU Usage:\n"
            for gpu_name, stats in gpu_data.items():
                gpu_summary += (f"  - {gpu_name.upper()}: Util {stats['utilization_percent']}%, "
                                f"Mem Change {stats['memory_change_mb']} MB "
                                f"(Start: {stats['memory_start_mb']} MB, End: {stats['memory_end_mb']} MB)\n")

        model_info = f"Model: {gen['model_name']}\n" if gen['model_name'] else ""

        summary = (
            f"\n--- Execution Performance Summary ---\n"
            f"{model_info}"
            f"Total Tokens: {gen['total_tokens']}\n"
            f"  - Prompt Tokens: {gen['prompt_tokens']}\n"
            f"  - Completion Tokens: {gen['completion_tokens']}\n"
            f"Time Taken: {gen['duration_seconds']:.2f} seconds\n"
            f"CPU Usage: {gen['cpu_usage_end_percent']}% (End)\n"
            f"Memory Usage Change: {gen['memory_usage_change_mb']} MB"
            f"{gpu_summary}"
            f"-------------------------------------\n"
        )
        return summary
