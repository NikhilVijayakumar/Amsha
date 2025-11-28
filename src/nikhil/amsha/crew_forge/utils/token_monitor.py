import time
import psutil
from typing import Any, Dict, Optional

try:
    import pynvml
    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False

class TokenMonitor:
    def __init__(self):
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
                print(f"[TokenMonitor] GPU monitoring failed to start: {e}")

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
                print(f"[TokenMonitor] GPU monitoring failed to stop: {e}")

    def log_usage(self, result: Any):
        """
        Parses the CrewOutput result to extract token usage.
        Expected result.token_usage to be a dictionary or object with token counts.
        """
        if hasattr(result, 'token_usage'):
            usage = result.token_usage
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
            print("[TokenMonitor] Warning: 'token_usage' not found in result.")

    def get_summary(self) -> str:
        """Returns a formatted summary of the monitoring data."""
        duration = self.end_time - self.start_time
        memory_diff_mb = (self.end_memory_usage - self.start_memory_usage) / (1024 * 1024)
        
        gpu_summary = ""
        if GPU_AVAILABLE and self.gpu_stats:
            gpu_summary = "\nGPU Usage:\n"
            count = len([k for k in self.gpu_stats if "utilization" in k])
            for i in range(count):
                start_mem = self.gpu_stats.get(f"gpu_{i}_start_mem", 0) / (1024 * 1024)
                end_mem = self.gpu_stats.get(f"gpu_{i}_end_mem", 0) / (1024 * 1024)
                util = self.gpu_stats.get(f"gpu_{i}_utilization", 0)
                gpu_summary += (f"  - GPU {i}: Util {util}%, "
                                f"Mem Change {end_mem - start_mem:.2f} MB "
                                f"(Start: {start_mem:.2f} MB, End: {end_mem:.2f} MB)\n")
        
        summary = (
            f"\n--- Execution Performance Summary ---\n"
            f"Total Tokens: {self.total_tokens}\n"
            f"  - Prompt Tokens: {self.prompt_tokens}\n"
            f"  - Completion Tokens: {self.completion_tokens}\n"
            f"Time Taken: {duration:.2f} seconds\n"
            f"CPU Usage: {self.end_cpu_percent}% (End)\n"
            f"Memory Usage Change: {memory_diff_mb:.2f} MB"
            f"{gpu_summary}"
            f"-------------------------------------\n"
        )
        return summary
